class modelsHospitales:
    def __init__(self, mysql_instance):
        self.mysql = mysql_instance
    
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