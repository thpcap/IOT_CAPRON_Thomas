
import os
import threading
import logging
from decimal import Decimal, InvalidOperation

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion

from app.Database import SessionLocal
from app.DB_Tables import SensorTable, Reading


logger = logging.getLogger(__name__)


class MQTTReader:
    def __init__(
        self,
        ip_address: str,
        port: int = 1883,
        client_id: str = "TempHumiX_Reader",
        username: str = "",
        password: str = ""
    ):
        self.ip_address = ip_address
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password

        self.client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=self.client_id
        )

        if username:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        # Association topic -> (numéro de série, type de mesure)
        self.topics = {}
        self.lock = threading.Lock()

        self.connected = False
        self.thread = None
        self.running = False

    def start(self):
        #Démarre le lecteur MQTT dans son propre thread.
        if self.running:
            return

        self.running = True

        try:
            self.client.connect(
                self.ip_address,
                self.port,
                keepalive=60
            )

            self.thread = threading.Thread(
                target=self.client.loop_forever,
                name="MQTTReaderThread",
                daemon=True
            )
            self.thread.start()

            logger.info("Thread MQTT démarré")

        except Exception:
            self.running = False
            logger.exception("Impossible de démarrer le lecteur MQTT")

    def stop(self):
        """Arrête proprement le lecteur MQTT."""
        self.running = False

        if self.connected:
            self.client.disconnect()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

        logger.info("Thread MQTT arrêté")

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.connected = True
            logger.info("Connecté au broker MQTT")

            # Recharge les topics et s'abonne à tous les capteurs
            self.refresh_subscriptions()

        else:
            logger.error("Échec connexion MQTT : %s", reason_code)

    def on_disconnect(self, client, userdata, disconnect_flags,
                      reason_code, properties):
        self.connected = False
        logger.warning("Déconnexion du broker MQTT : %s", reason_code)

    def refresh_subscriptions(self):
        db = SessionLocal()

        try:
            sensors = db.query(SensorTable).all()

            new_topics = {}

            for sensor in sensors:
                if sensor.topic_t:
                    new_topics[sensor.topic_t] = (
                        sensor.serialnumber, "T"
                    )

                if sensor.topic_h:
                    new_topics[sensor.topic_h] = (
                        sensor.serialnumber, "H"
                    )

                if sensor.topic_version:
                    new_topics[sensor.topic_version] = (
                        sensor.serialnumber, "V"
                    )

            with self.lock:
                self.topics = new_topics

            if self.connected:
                for topic in new_topics:
                    self.client.subscribe(topic, qos=1)
                    logger.info("Abonnement MQTT : %s", topic)

        except Exception:
            logger.exception("Erreur lors du chargement des topics")

        finally:
            db.close()

    def on_message(self, client, userdata, msg):

        with self.lock:
            sensor_info = self.topics.get(msg.topic)

        if sensor_info is None:
            logger.warning("Topic MQTT inconnu : %s", msg.topic)
            return

        serialnumber, measure_type = sensor_info

        try:
            payload = msg.payload.decode("utf-8").strip()

            db = SessionLocal()

            try:
                # VERSION : mise à jour du capteur
                if measure_type == "V":

                    sensor = db.query(SensorTable).filter(
                        SensorTable.serialnumber == serialnumber
                    ).first()

                    if sensor is None:
                        logger.warning(
                            "Capteur introuvable : %s", serialnumber
                        )
                        return

                    sensor.version = payload
                    db.commit()

                    logger.info(
                        "Version mise à jour : SN=%s, version=%s",
                        serialnumber,
                        payload
                    )

                # TEMPÉRATURE et HUMIDITÉ : insertion d'un reading
                elif measure_type in ("T", "H"):

                    value = Decimal(payload.replace(",", "."))

                    if not value.is_finite():
                        raise ValueError("Valeur numérique non finie")

                    reading = Reading(
                        SN=serialnumber,
                        type=measure_type,
                        val=value
                    )

                    db.add(reading)
                    db.commit()

                    logger.info(
                        "Mesure enregistrée : SN=%s, type=%s, valeur=%s",
                        serialnumber,
                        measure_type,
                        value
                    )

            except Exception:
                db.rollback()
                logger.exception(
                    "Erreur de traitement MQTT pour le capteur %s",
                    serialnumber
                )

            finally:
                db.close()

        except (UnicodeDecodeError, InvalidOperation, ValueError):
            logger.warning(
                "Message MQTT invalide sur %s : %r",
                msg.topic,
                msg.payload
            )
