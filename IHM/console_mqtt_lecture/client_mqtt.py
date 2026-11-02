import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion


class ClientMQTT:

    def __init__(self, ip_address, port, client_id, username, password):
        self.ip_address = ip_address
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password
        self.client = None

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
            print(f"Topic : {msg.topic}")
            print(f"Message reçu : {msg.payload.decode('utf-8')}")

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


id_pc = 42900
id_capts =  {42900}
if __name__ == '__main__':
    print("Démarrage de l'application")
    print("==========================")
    print("Instanciation de votre ClientMQTT")
    # Configuration du broker MQTT
    mqtt_client = ClientMQTT(
        ip_address="192.168.1.1",
        port=1883,
        client_id="LECT_"+str(id_pc),
        username="mos_user",
        password="mos_user"
    )
    print("Connexion au brocker")
    client = mqtt_client.connect_mqtt()

    print(f"Souscription aux données du capteur : 'Client_{id_pc}'")
    # Souscription
    for id_capt in id_capts:
        mqtt_client.subscribe_mqtt("/iot/TEMPERATURE_"+str(id_capt))    
        mqtt_client.subscribe_mqtt("/iot/HUMIDITY_"+str(id_capt))    
        mqtt_client.subscribe_mqtt("/iot/GET_DATE_"+str(id_capt))    
        mqtt_client.subscribe_mqtt("/iot/VERSION_"+str(id_capt))    

    
    # Maintien du programme actif
    try:
        mqtt_client.wait_mqtt(0)
    except KeyboardInterrupt:
        mqtt_client.disconnect_mqtt()
        print("Fin de l'application")
    
