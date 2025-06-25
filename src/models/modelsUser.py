from .entities.user import Usuarios
from werkzeug.security import generate_password_hash

# Creamos una clase model User
class modelsUser:

    def __init__(self, mysql_instance):
        self.mysql = mysql_instance

    def login(self, usuario):
        try:
            # Usamos self.mysql para acceder a la conexión guardada en el constructor.
            cursor = self.mysql.connection.cursor()
            
            # La consulta para buscar al usuario.
            sql = "SELECT id_usuarios, usuario, password, fullname FROM usuarios WHERE usuario = %s"
            cursor.execute(sql, (usuario.usuario,))
            row = cursor.fetchone() # Usamos 'row' para más claridad.
            cursor.close()

            if row is not None:
                # Comparamos la contraseña del formulario (usuario.password) con el hash de la DB (row[2])
                password_ok = Usuarios.check_password(row[2], usuario.password)
                
                if password_ok:
                    # Si la contraseña es correcta, creamos y devolvemos el objeto Usuario con los datos de la DB.
                    logged_user = Usuarios(row[0], row[1], None, row[3]) # No devolvemos el hash por seguridad
                    return logged_user
                else:
                    # Contraseña incorrecta
                    return None
            else:
                # Usuario no encontrado
                return None
        except Exception as ex:
            # Es una buena práctica registrar el error real para depuración.
            print(f"Error en login: {ex}")
            raise Exception(ex)

    def get_by_id(self, id_usuarios):
        try:
            # Usamos nuevamente self.mysql para acceder a la conexión guardada en el constructor.
            cursor = self.mysql.connection.cursor()
            
            # La consulta para buscar al usuario.
            sql = "SELECT id_usuarios, usuario, password, fullname FROM usuarios WHERE id_usuarios = %s"
            cursor.execute(sql, (id_usuarios,))
            row = cursor.fetchone() # Usamos 'row' para más claridad.
            cursor.close()

            if row is not None:                
             return Usuarios(row[1], row[2],row[3])              
            else:
                # Usuario no encontrado
                return None
        except Exception as ex:
            # Es una buena práctica registrar el error real para depuración.
            print(f"Error en login: {ex}")
            raise Exception(ex)
        
    def registroUsuario(self, usuario, password, fullname):
        try:
            cursor = self.mysql.connection.cursor()
            hashed_password = generate_password_hash(password)
            
            # La consulta correcta para insertar un nuevo paciente
            query = """ INSERT INTO usuarios (usuario, password, fullname)
                VALUES (%s, %s, %s)"""
            
            # Se ejecutan la consulta con los datos del formulario
            cursor.execute(query, (usuario,hashed_password, fullname,))
            self.mysql.connection.commit() # Confirma la transacción para guardar los cambios
            
            cursor.close()
            return True # Retorna True para indicar que el registro fue exitoso
            
        except Exception as ex:
            print(f"Error en el registro del usuario: {ex}")
            # En caso de error, deshacer la transacción
            self.mysql.connection.rollback()
            raise Exception(ex)
        
    def get_all_users(self):
        try:
            cursor = self.mysql.connection.cursor()
            sql = "SELECT id_usuarios, fullname FROM usuarios"
            cursor.execute(sql)
            users = cursor.fetchall()
            cursor.close()
            return users
        except Exception as ex:
            print(f"Error al obtener todos los usuarios: {ex}")
            return []