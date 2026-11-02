import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import time
class ClientMQTT:
    def __init__(self, ip_address, port, client_id, username, password):
        self.ip_address = ip_address
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password
        self.client = None
        self.version = "Inconnue"
        self.temperature = "Inconnue"
        self.humidite = "Inconnue"
        self.date = "Inconnue"

    def connect_mqtt(self):
        #Connexion au broker MQTT.

        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code == 0:
                return True
            else:
                print(f"Échec de connexion MQTT : {reason_code}")

        self.client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=self.client_id
        )

        self.client.username_pw_set(
            self.username,
            self.password
        )

        self.client.on_connect = on_connect

        try:
            self.client.connect(
                self.ip_address,
                self.port,
                keepalive=60
            )
            return self.client

        except Exception as e:
            print(f"Erreur de connexion : {e}")
            return None

    def disconnect_mqtt(self):
        #Déconnexion du broker MQTT.

        if self.client is not None:
            self.client.disconnect()
            self.client.loop_stop()
            #Déconnexion MQTT.")

    def publish_mqtt(self, topic, message, qos=0):
        #Publication d'un message MQTT.

        if self.client is None:
            #Client MQTT non connecté.")
            return

        result = self.client.publish(
            topic,
            message,
            qos=qos
        )

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Message publié sur {topic}")
        else:
            raise RuntimeError("Erreur lors de la publication.")
        
    def subscribe_mqtt(self, topic, qos=0):
        #Souscription à un topic MQTT.

        if self.client is None:
             raise RuntimeError("client MQTT non connecté")

        def on_message(client, userdata, msg):
            if "VERSION" in msg.topic:
                self.version = msg.payload.decode()
            elif "TEMPERATURE" in msg.topic:
                self.temperature = msg.payload.decode()
            elif "HUMIDITY" in msg.topic:
                self.humidite = msg.payload.decode()
            elif "GET_DATE" in msg.topic:
                self.date = msg.payload.decode()
        self.client.on_message = on_message

        self.client.subscribe(topic, qos=qos)
        print(f"Souscription au topic : {topic}")

    def wait_mqtt(self, timeout=0):
        #Gestion de la boucle MQTT.

        if self.client is None:
            return

        if timeout == 0:
            self.client.loop_forever()
        else:
            self.client.loop(timeout=timeout)
    def send_command(self,capteurs,command,value=""):
        for id_capt in capteurs:
            match command.upper():
                case '1':
                    self.publish_mqtt("/iot/COMMAND_"+str(id_capt),"10")
                    #1 - Mise à l'heure du capteur
                    return "Mise à l'heure du capteur"
                case '2':
                    self.publish_mqtt("/iot/COMMAND_"+str(id_capt),"20")
                    #2 - Démarrage des mesures
                    return "Démarrage des mesures"
                case '3':
                    self.publish_mqtt("/iot/COMMAND_"+str(id_capt),"30")
                    #3 - Arrêt des mesures
                    return "Arrêt des mesures"
                case '4':
                    self.publish_mqtt("/iot/COMMAND_"+str(id_capt),"40")
                    #4 - Clignotement lent
                    return "Clignotement lent"
                case '5':
                    self.publish_mqtt("/iot/COMMAND_"+str(id_capt),"50")
                    #5 - Clignotement rapide
                    return "Clignotement rapide"
                case '6':
                    #6 - Clignotement personnalisé
                    delay = int(value)
                    if delay > 0:
                        self.publish_mqtt("/iot/BLINK_" + str(id_capt), delay)
                        time.sleep(1)
                        self.publish_mqtt("/iot/COMMAND_" + str(id_capt), "60")
                        return "Clignotement personnalisé"
                    else:
                        #Le délai doit être supérieur à 0.
                        raise ValueError("Le délai doit être supérieur à 0.")
                case '7':
                    #7 - Ecriture du bargraphe

                    while True:
                        number = input("Insérez un nombre entre 0 et 1023 ou Q pour sortir : ")
                        number_value = int(number)

                        if 0 <= number_value <= 1023:
                            self.publish_mqtt(
                                "/iot/BARGRAPH_" + str(id_capt),
                                str(number_value)
                            )
                            break
                        else:
                            #Valeur incorrecte : entre 0 et 1023.
                            raise ValueError("Valeur incorrecte : entre 0 et 1023.")

                