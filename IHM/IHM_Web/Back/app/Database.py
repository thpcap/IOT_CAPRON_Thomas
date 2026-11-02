
import mariadb

class Database:

    def __init__(self):
        try:
            self.conn = mariadb.connect(
                host="localhost",
                port=3306,
                user="iot_user",
                password="mot_de_passe",
                database="TempHumiX"
            )

            self.cursor = self.conn.cursor()
            print("Connexion à MariaDB réussie !")

        except mariadb.Error as e:
            raise ConnectionError(
                f"Erreur de connexion à MariaDB : {e}"
            )

    def close(self):
        self.cursor.close()
        self.conn.close()
