import os
from fastapi import FastAPI, Depends, HTTPException,Query
from sqlalchemy import text,select,func
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta


from app.Sensor import Sensor, SensorCreate, SendCommandRequest
from app.Database import get_db, Base, engine
from app import DB_Tables
from app.DB_Tables import SensorTable, Reading
from app.ClientMQTT import ClientMQTT
from app.MQTT_reader import MQTTReader


app = FastAPI()

Base.metadata.create_all(bind=engine)

sensor = Sensor("42900")

print(sensor.serialnumber)

mqtt_reader = MQTTReader(
    ip_address=os.getenv("MQTT_HOST", "192.168.1.1"),
    port=int(os.getenv("MQTT_PORT", "1883")),
    client_id="TempHumiX_Reader_42900",
    username="mos_user",
    password="mos_user"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


mqtt_client = ClientMQTT(
    ip_address=os.getenv("MQTT_HOST", "192.168.1.1"),
    port=int(os.getenv("MQTT_PORT", "1883")),
    client_id="TempHumiX_Backend_42900",
    username="mos_user",
    password="mos_user"
)

@app.on_event("startup")
def startup():
    mqtt_reader.start()

    client = mqtt_client.connect_mqtt()

    if client is not None:
        client.loop_start()
    else:
        print("Impossible de connecter le client MQTT")

@app.on_event("shutdown")
def shutdown():
    mqtt_client.disconnect_mqtt()
    mqtt_reader.stop();

@app.post("/api/sensors", status_code=201)
def add_sensor(sensor_data: SensorCreate, db: Session = Depends(get_db)):

    try:
        # Création de l'objet métier Sensor
        sensor = Sensor(sensor_data.serialnumber)

        # Vérification de l'existence du capteur
        existing = db.execute(
            select(SensorTable).where(
                SensorTable.serialnumber == sensor.serialnumber
            )
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Ce capteur existe déjà."
            )


        dernier_id = db.scalar(
            select(func.max(SensorTable.id))
        )

        nouvel_id = (dernier_id or 0) + 1
        # Création du modèle SQLAlchemy
        new_sensor = SensorTable(
            serialnumber=sensor.serialnumber,
            name=sensor_data.name or f"Capteur {sensor.serialnumber}",
            id=nouvel_id,
            topic_t=sensor_data.TempTopic or sensor.TempTopic,
            topic_h=sensor_data.HumiTopic or sensor.HumiTopic,
            topic_date=sensor_data.dateTopic or sensor.dateTopic,
            topic_version=sensor_data.versTopic or sensor.versTopic,

            topic_command=sensor_data.CommandTopic or sensor.CommandTopic,
            topic_blink=sensor_data.BlinkTopic or sensor.BlinkTopic,
            topic_bargraph=sensor_data.BargraphTopic or sensor.BargraphTopic,

            version=None,
            autoimported=False
        )

        # Enregistrement dans MariaDB
        db.add(new_sensor)
        db.commit()
        db.refresh(new_sensor)
        #refresh des subscriptions
        mqtt_reader.refresh_subscriptions()
        return {
            "status": "success",
            "message": "Capteur ajouté avec succès",
            "sensor": {
                "serialnumber": new_sensor.serialnumber,
                "name": new_sensor.name,
                "topic_t": new_sensor.topic_t,
                "topic_h": new_sensor.topic_h,
                "topic_date": new_sensor.topic_date,
                "topic_version": new_sensor.topic_version,
                "topic_command": new_sensor.topic_command,
                "topic_blink": new_sensor.topic_blink,
                "topic_bargraph": new_sensor.topic_bargraph,
                "autoimported": new_sensor.autoimported
            }
        }

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Numéro de série invalide : {str(e)}"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'ajout du capteur : {str(e)}"
        )


@app.get("/api/sensors")
def get_sensors(db: Session = Depends(get_db)):
    try:
        sensors = db.execute(
            select(SensorTable)
        ).scalars().all()

        return {
            "status": "success",
            "count": len(sensors),
            "sensors": [
                {
                    "id":sensor.id,
                    "serialnumber": sensor.serialnumber,
                    "name": sensor.name,
                    "topic_t": sensor.topic_t,
                    "topic_h": sensor.topic_h,
                    "topic_date": sensor.topic_date,
                    "topic_version": sensor.topic_version,
                    "topic_command": sensor.topic_command,
                    "topic_blink": sensor.topic_blink,
                    "topic_bargraph": sensor.topic_bargraph,
                    "version": sensor.version,
                    "autoimported": sensor.autoimported
                }
                for sensor in sensors
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des capteurs : {str(e)}"
        )







@app.post("/api/send-command")
def send_command_api(
    data: SendCommandRequest,
    db: Session = Depends(get_db)
):
    # Vérification des données
    if not data.capteurs:
        raise HTTPException(
            status_code=400,
            detail="Aucun capteur sélectionné."
        )

    if data.commande not in ["1", "2", "3", "4", "5", "6", "7","8"]:
        raise HTTPException(
            status_code=400,
            detail="Commande inconnue."
        )

    # Vérification de la valeur pour les commandes 6 et 7
    if data.commande in ["6", "7"] and data.value is None:
        raise HTTPException(
            status_code=400,
            detail="Une valeur est nécessaire pour cette commande."
        )

    # Récupération des capteurs dans MariaDB
    sensors_db = db.execute(
        select(SensorTable).where(
            SensorTable.serialnumber.in_(data.capteurs)
        )
    ).scalars().all()

    if len(sensors_db) != len(set(data.capteurs)):
        raise HTTPException(
            status_code=404,
            detail="Un ou plusieurs capteurs sont introuvables."
        )

    # Reconstruction des objets Sensor
    capteurs = [
        Sensor(
            id=s.id,
            serialnumber=s.serialnumber,
            TempTopic=s.topic_t,
            HumiTopic=s.topic_h,
            versTopic=s.topic_version,
            dateTopic=s.topic_date,
            CommandTopic=s.topic_command,
            BlinkTopic=s.topic_blink,
            BargraphTopic=s.topic_bargraph
        )
        for s in sensors_db
    ]

    try:
        # Envoi de la commande MQTT
        mqtt_client.send_command(
            capteurs,
            data.commande,
            data.value or ""
        )

        return {
            "status": "success",
            "message": "Commande envoyée avec succès.",
            "commande": data.commande,
            "capteurs": data.capteurs
        }

    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'envoi MQTT : {str(e)}"
        )




@app.get("/api/sensors/{serialnumber}/readings")
def get_sensor_readings(
    serialnumber: str,
    heure_debut: datetime | None = Query(default=None),
    heure_fin: datetime | None = Query(default=None),
    limit: int = Query(default=1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    try:
        # Vérifier que le capteur existe
        sensor = db.get(SensorTable, serialnumber)

        if sensor is None:
            raise HTTPException(
                status_code=404,
                detail="Capteur introuvable"
            )

        # Définir les dates par défaut
        maintenant = datetime.now()

        if heure_fin is None:
            heure_fin = maintenant

        if heure_debut is None:
            heure_debut = heure_fin - timedelta(hours=1)

        # Vérifier la cohérence des dates
        if heure_debut >= heure_fin:
            raise HTTPException(
                status_code=400,
                detail="L'heure de début doit être antérieure à l'heure de fin"
            )

        print(f"Capteur : {serialnumber}")
        print(f"Début : {heure_debut}")
        print(f"Fin : {heure_fin}")

        # Récupérer les mesures
        readings = db.execute(
            select(Reading)
            .where(
                Reading.SN == serialnumber,
                Reading.date >= heure_debut,
                Reading.date <= heure_fin
            )
            .order_by(Reading.date.asc(), Reading.read_id.asc())
            .limit(limit)
        ).scalars().all()

        print(f"Nombre de mesures trouvées : {len(readings)}")

        temperature = []
        humidity = []

        for reading in readings:

            mesure = {
                "time": reading.date.strftime("%Y-%m-%d %H:%M:%S"),
                "reading": str(reading.val)
            }

            if reading.type == "T":
                temperature.append(mesure)

            elif reading.type == "H":
                humidity.append(mesure)

        # Construire la réponse
        resultat = {
            "serialnumber": serialnumber,
            "heure_debut": heure_debut.strftime("%Y-%m-%d %H:%M:%S"),
            "heure_fin": heure_fin.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": temperature,
            "humidity": humidity
        }

        print("Réponse API :", resultat)

        return resultat

    except HTTPException:
        raise

    except Exception as e:
        print(f"Erreur get_sensor_readings : {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des mesures : {str(e)}"
        )



@app.delete("/api/sensors/{serialnumber}")
def delete_sensor(
    serialnumber: str,
    db: Session = Depends(get_db)
):
    # Rechercher le capteur
    sensor = db.get(SensorTable, serialnumber)

    if sensor is None:
        raise HTTPException(
            status_code=404,
            detail="Capteur introuvable"
        )

    try:
        db.delete(sensor)
        db.commit()
        mqtt_reader.refresh_subscriptions()
        return {
            "status": "success",
            "message": "Capteur supprimé",
            "serialnumber": serialnumber
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression : {str(e)}"
        )
        

@app.get("/api/db-test")
def test_database(db: Session = Depends(get_db)):
    try:
        # Récupération de la version MariaDB
        result = db.execute(text("SELECT VERSION()")).scalar()

        # Récupération de la liste des tables
        tables = db.execute(text("SHOW TABLES")).fetchall()

        # Conversion en liste Python
        tables_list = [table[0] for table in tables]

        return {
            "status": "connected",
            "database": "TempHumiX",
            "version": result,
            "tables": tables_list
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de connexion à MariaDB : {str(e)}"
        )