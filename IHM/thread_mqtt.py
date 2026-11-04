from threading import Thread
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import time

id_pc = 42900
id_capt = 42900
topic_version = f"/iot/VERSION_{id_capt}"
topic_temperature = f"/iot/TEMPERATURE_{id_capt}"
topic_humidite = f"/iot/HUMIDITY_{id_capt}"
topic_datetime = f"/iot/GET_DATE_{id_capt}"
topics={topic_version,topic_temperature,topic_humidite,topic_datetime}
class ThreadMQTT(Thread):
    def __init__(self, client_mqtt):
        Thread.__init__(self)
        self.mqtt = client_mqtt
        self.stop = False
    def run(self):
        
        # Configuration du broker MQTT
        print("Connexion au brocker")
        client = self.mqtt.connect_mqtt()
        
        for topic in topics:
            self.mqtt.subscribe_mqtt(topic)
        
        while not self.stop:
            self.mqtt.wait_mqtt(timeout=1.0)
    def stopthread(self):
        self.mqtt.disconnect_mqtt()
        self.stop = True
        
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
                print("Connexion MQTT réussie !")
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
            print("Déconnexion MQTT.")

    def publish_mqtt(self, topic, message, qos=0):
        #Publication d'un message MQTT.

        if self.client is None:
            print("Client MQTT non connecté.")
            return

        result = self.client.publish(
            topic,
            message,
            qos=qos
        )

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Message publié sur {topic}")
        else:
            print("Erreur lors de la publication.")
        
    def subscribe_mqtt(self, topic, qos=0):
        #Souscription à un topic MQTT.

        if self.client is None:
            print("Client MQTT non connecté.")
            return

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
            
            
#Ecriture
if __name__ == '__main__':
    mqtt_client = ClientMQTT(
                    ip_address="192.168.1.1",
                    port=1883,
                    client_id="LECT_"+str(id_pc),
                    username="mos_user",
                    password="mos_user"
                )
    threadMQTT=ThreadMQTT(mqtt_client)
    threadMQTT.start()
    try:
        car = ' '
        while car.upper() != 'Q':
            print("Console capteur IdO")
            print("-------------------")
            print("1 - Mise à l'heure du capteur")
            print("2 - Démarrage des mesures")
            print("3 - Arrêt des mesures")
            print("4 - Clignotement lent")
            print("5 - Clignotement rapide")
            print("6 - Clignotement personnalisé")
            print("7 - Ecriture du bargraphe")
            print("Q - Quitter")
            car = input("Votre choix : ")
            match car.upper():
                case '1':
                    mqtt_client.publish_mqtt("/iot/COMMAND_"+str(id_capt),"10")
                    print("1 - Mise à l'heure du capteur")
                case '2':
                    mqtt_client.publish_mqtt("/iot/COMMAND_"+str(id_capt),"20")
                    print("2 - Démarrage des mesures")
                case '3':
                    mqtt_client.publish_mqtt("/iot/COMMAND_"+str(id_capt),"30")
                    print("3 - Arrêt des mesures")
                case '4':
                    mqtt_client.publish_mqtt("/iot/COMMAND_"+str(id_capt),"40")
                    print("4 - Clignotement lent")
                case '5':
                    mqtt_client.publish_mqtt("/iot/COMMAND_"+str(id_capt),"50")
                    print("5 - Clignotement rapide")
                case '6':
                    print("6 - Clignotement personnalisé")

                    while True:
                        delay = input("Insérez un délai ou Q pour sortir : ")

                        if delay.upper() == 'Q':
                            mqtt_client.publish_mqtt("/iot/BLINK_" + str(id_capt), delay)
                            time.sleep(1)
                            mqtt_client.publish_mqtt("/iot/COMMAND_" + str(id_capt), "60")
                            break

                        try:
                            delay_value = int(delay)

                            if delay_value > 0:
                                mqtt_client.publish_mqtt("/iot/BLINK_" + str(id_capt), delay)
                                time.sleep(1)
                                mqtt_client.publish_mqtt("/iot/COMMAND_" + str(id_capt), "60")
                                break
                            else:
                                print("Le délai doit être supérieur à 0.")

                        except ValueError:
                            print("Veuillez saisir un nombre valide ou Q.")
                    
                case '7':
                    print("7 - Ecriture du bargraphe")

                    while True:
                        number = input("Insérez un nombre entre 0 et 1023 ou Q pour sortir : ")

                        if number.upper() == 'Q':
                            print("Annulation")
                            break

                        try:
                            number_value = int(number)

                            if 0 <= number_value <= 1023:
                                mqtt_client.publish_mqtt(
                                    "/iot/BARGRAPH_" + str(id_capt),
                                    str(number_value)
                                )
                                break
                            else:
                                print("Valeur incorrecte : entre 0 et 1023.")

                        except ValueError:
                            print("Veuillez saisir un nombre valide ou Q.")
                case '8':
                    print(f"Version: {mqtt_client.version}\nTemperature:{mqtt_client.temperature}\nHumidite:{mqtt_client.humidite}\nDate:{mqtt_client.date}")
                case 'Q':
                    print("Arrêt du client MQTT")
                    mqtt_client.disconnect_mqtt()
                    threadMQTT.stopthread()
                    print("Fin de l'application")
    except KeyboardInterrupt:
        mqtt_client.disconnect_mqtt()
        threadMQTT.stopthread()
        print("Fin de l'application")
