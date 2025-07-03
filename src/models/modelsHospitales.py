from .entities.hospitales import Hospitales

class modelsHospitales():
    def __init__(self, mysql_instance):
        self.mysql = mysql_instance

    def registrarHospital(self, id_hospital, nombreHospital):
        try:
            cursor = self.mysql.connection.cursor()
            query = """
                INSERT INTO hospitales (id_hospital, nombreHospital)
                VALUES (%s, %s)
            """
            cursor.execute(query, (id_hospital, nombreHospital))
            self.mysql.connection.commit()
            last_inserted_id = cursor.lastrowid
            cursor.close()
            return last_inserted_id
        
        except Exception as ex:
            print(f"Error al registrar hospital: {ex}")
            self.mysql.connection.rollback()
            raise Exception(ex)

    def get_last_hospital_id(self):
        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT MAX(id_hospital) FROM hospitales")
            last_id_hospital = cursor.fetchone()[0]
            cursor.close()
            return last_id_hospital if last_id_hospital is not None else 0
        except Exception as e:
            print(f"Error al obtener el último ID de hospital: {str(e)}")
            return 0
    
    def get_all_hospitales(self):
        try:
            cursor = self.mysql.connection.cursor()
            sql = "SELECT id_hospital, nombreHospital FROM hospitales"
            cursor.execute(sql)
            users = cursor.fetchall()
            cursor.close()
            return users
        except Exception as ex:
            print(f"Error al obtener todos los hospitales: {ex}")
            return []