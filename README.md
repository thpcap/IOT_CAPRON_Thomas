# TP noté : Création d'un capteur de température et d'humidité

## Étapes du TP

### 3. SimulIDE

**Dossier :** `Simulide/`

#### 3.1.1 Clignotement de DEL

- **Code Arduino :** `clignotement_led/clignotement_led.ino`
- **Simulation :** `clignotement_led/clignotement_led.sim1`

#### 3.1.2 Bargraphe

- **Code Arduino :** `bargraphe/bargraph/bargraph.ino`
- **Simulation :** `bargraphe/bargraph/bargraph.sim1`

#### 3.1.3 Capteur DHT22

- **Code Arduino :** `capteur_dht22/capteur_dht22.ino`
- **Simulation :** `capteur_dht22/capteur_dht22.sim1`

#### 3.1.4 LCD I2C

- **Code Arduino :** `lcd_i2c/lcd_i2c.ino`
- **Simulation :** `lcd_i2c/lcd_i2c.sim1`

#### 3.1.5 LCD I2C et DHT22

- **Code Arduino :** `lcd_i2c_dht22/lcd_i2c_dht22.ino`
- **Simulation :** `lcd_i2c_dht22/lcd_i2c_dht22.sim1`

#### 3.2 TempHumiX

- **Code Arduino :** `TempHumiX/temphumix/temphumix.ino`
- **Simulation :** `TempHumiX/temphumix.sim1`

### 6. TempHumiX

**Dossier :** `TEMPHUMIX/`

#### 6.1 Développement du programme embarqué

- **6.1.1 :** Modification du programme d'acquisition de température.
  - Fichier : `TEMPHUMIX/temphumix/temphumix.ino`
- **6.1.2 :** Ajout du RTC.
- **6.1.3 :** Connexion Wi-Fi.
- **6.1.3.e :** Mise à jour du RTC à partir d'un serveur NTP.
- **6.1.6 :** Connexion à MQTT.

#### 6.2 Observation de MQTT

Observation des échanges MQTT entre le capteur et le broker.

### 7. IHM

#### 7.3 Développement du client MQTT

- **7.3.3 :** Implémentation du client MQTT en lecture.
  - Dossier : `IHM/console_mqtt_lecture/`
- **7.3.4 :** Écriture MQTT et envoi de commandes.
  - Dossier : `IHM/console_mqtt_ecriture/`
- **7.3.6 :** Mise en place d'un fonctionnement MQTT multithreadé.

#### 7.4 Développement de l'IHM

Choix d'une architecture Web plutôt que de la stack initialement proposée.

## 8. IHM Web

**Dossier :** `IHM/IHM_Web/`

**Programme Arduino utilisé :** `TEMPHUMIX/temphumix/temphumix.ino`

### Développement de l'interface Web

Développement d'une interface Web permettant notamment :

- La visualisation des capteurs.
- L'affichage des mesures de température et d'humidité.
- La consultation de l'historique des mesures.
- L'envoi de commandes aux capteurs.
- La gestion des capteurs et de leurs topics MQTT.

### Architecture Docker

Le projet repose sur trois conteneurs Docker :

- **temphumix-back :** conteneur Python hébergeant le backend FastAPI.
  - Dossier : `IHM/IHM_Web/Back/`
  - Bibliothèques utilisées :
    ```text
    fastapi              # Gestion des endpoints REST
    uvicorn[standard]    # Serveur ASGI pour FastAPI
    paho-mqtt            # Communication avec le broker MQTT
    python-dotenv        # Gestion des variables d'environnement
    sqlalchemy           # Gestion de la base de données sous forme d'objets
    pymysql              # Connexion à MariaDB
    ```

- **temphumix-front :** conteneur Nginx hébergeant les fichiers HTML, CSS et JavaScript.
  - Dossier : `IHM/IHM_Web/Front/`

- **temphumix-db :** conteneur MariaDB hébergeant la base de données TempHumiX.
  - Les données sont conservées dans un volume Docker afin de les préserver lors de la recréation du conteneur.

## Procédure de démarrage

### 1. Démarrage de l'environnement Docker

Le premier démarrage nécessite une connexion à un réseau Wi-Fi disposant d'un accès à Internet afin de permettre le téléchargement des images Docker et des dépendances nécessaires.

Depuis un terminal, se placer à la racine du projet :

```bash
cd IHM/IHM_Web
```

Rendre le script exécutable si nécessaire :

```bash
chmod +x start.sh
```

Lancer le script :

```bash
./start.sh
```

Le script permet de démarrer l'environnement Docker du projet.

### 2. Connexion au réseau Wi-Fi du broker MQTT

Une fois les conteneurs démarrés, connecter l'ordinateur au réseau Wi-Fi permettant d'accéder au broker MQTT, hébergé sur le routeur Teltonika.

Si le broker MQTT n'est pas accessible depuis le réseau Wi-Fi initial, il faut effectuer ce changement de réseau.

### 3. Redémarrage du backend

Après le changement de réseau Wi-Fi, le backend doit être redémarré afin de rétablir la connexion avec le broker MQTT.

Depuis le dossier `IHM/IHM_Web/`, exécuter :

```bash
docker compose restart backend
```

Vérifier ensuite les logs du backend :

```bash
docker compose logs -f backend
```

La connexion MQTT doit être établie avant de poursuivre.

### 4. Accès à l'interface Web

Depuis un navigateur, accéder à l'adresse suivante :

[http://localhost:8080](http://localhost:8080)

La documentation interactive de l'API FastAPI est également disponible :

[http://localhost:8080/docs](http://localhost:8080/docs)