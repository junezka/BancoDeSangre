from .entities.user import Usuarios
from werkzeug.security import generate_password_hash

class modelsUser:

    def __init__(self, mysql_instance):
        self.mysql = mysql_instance
        self.MAX_LOGIN_ATTEMPTS = 3 

    def login(self, usuario):
        try:
            cursor = self.mysql.connection.cursor()
            sql = "SELECT id_usuarios, usuario, password, fullname, failed_attempts, is_locked FROM usuarios WHERE usuario = %s"
            cursor.execute(sql, (usuario.usuario,))
            row = cursor.fetchone()
            cursor.close()

            if row is not None:
                user_id, username, hashed_password_db, fullname, failed_attempts, is_locked = row

                # 1. Verificar si el usuario está ya bloqueado
                if is_locked:
                    return {"success": False, "message": "Tu cuenta ha sido bloqueada. Contacta al administrador."}

                # 2. Verificar la contraseña
                password_ok = Usuarios.check_password(hashed_password_db, usuario.password)
                
                if password_ok:
                    # 3. Contraseña correcta: Resetear intentos fallidos y retornar éxito
                    self._reset_failed_attempts(user_id)
                    logged_user = Usuarios(user_id, username, None, fullname, is_locked=False, failed_attempts=0)
                    return {"success": True, "user": logged_user}
                else:
                    # 4. Contraseña incorrecta: Incrementar intentos fallidos
                    new_attempts = failed_attempts + 1
                    is_now_locked = new_attempts >= self.MAX_LOGIN_ATTEMPTS
                    
                    self._update_failed_attempts(user_id, new_attempts, is_now_locked)

                    if is_now_locked:
                        return {"success": False, "message": f"Contraseña incorrecta. Tu cuenta ha sido bloqueada por exceder los {self.MAX_LOGIN_ATTEMPTS} intentos fallidos."}
                    else:
                        remaining_attempts = self.MAX_LOGIN_ATTEMPTS - new_attempts
                        return {"success": False, "message": f"Contraseña incorrecta. Te quedan {remaining_attempts} intentos."}
            else:
                return {"success": False, "message": "Usuario o contraseña incorrectos."}
        except Exception as ex:
            print(f"Error en login: {ex}")
            # En caso de un error inesperado, también se devuelve un diccionario
            return {"success": False, "message": "Ocurrió un error inesperado. Inténtalo de nuevo más tarde."}

    def _update_failed_attempts(self, user_id, new_attempts, is_locked_status):
        try:
            cursor = self.mysql.connection.cursor()
            sql = "UPDATE usuarios SET failed_attempts = %s, is_locked = %s WHERE id_usuarios = %s"
            cursor.execute(sql, (new_attempts, is_locked_status, user_id))
            self.mysql.connection.commit()
            cursor.close()
        except Exception as ex:
            print(f"Error al actualizar intentos fallidos: {ex}")

    def _reset_failed_attempts(self, user_id):
        try:
            cursor = self.mysql.connection.cursor()
            sql = "UPDATE usuarios SET failed_attempts = 0, is_locked = FALSE WHERE id_usuarios = %s"
            cursor.execute(sql, (user_id,))
            self.mysql.connection.commit()
            cursor.close()
        except Exception as ex:
            print(f"Error al resetear intentos fallidos: {ex}")
    
    def get_by_id(self, id_usuarios):
        try:
            cursor = self.mysql.connection.cursor()
            # Asegúrate de seleccionar todos los campos relevantes para la entidad Usuarios
            sql = "SELECT id_usuarios, usuario, password, fullname, is_locked, failed_attempts FROM usuarios WHERE id_usuarios = %s"
            cursor.execute(sql, (id_usuarios,))
            row = cursor.fetchone()
            cursor.close()

            if row is not None:
                return Usuarios(row[0], row[1], row[2], row[3], row[4], row[5])
            else:
                return None
        except Exception as ex:
            print(f"Error en get_by_id: {ex}")
            raise Exception(ex)
        
    def registroUsuario(self, usuario, password, fullname):
        try:
            cursor = self.mysql.connection.cursor()
            hashed_password = generate_password_hash(password)
            
            query = """ INSERT INTO usuarios (usuario, password, fullname, failed_attempts, is_locked)
                VALUES (%s, %s, %s, 0, FALSE)""" 
            
            cursor.execute(query, (usuario,hashed_password, fullname,))
            self.mysql.connection.commit()
            
            cursor.close()
            return True
            
        except Exception as ex:
            print(f"Error en el registro del usuario: {ex}")
            self.mysql.connection.rollback()
            raise Exception(ex)
        
    def get_all_users(self):
        try:
            cursor = self.mysql.connection.cursor()
            sql = "SELECT id_usuarios, usuario, fullname, is_locked FROM usuarios" 
            cursor.execute(sql)
            users = cursor.fetchall()
            cursor.close()
            return users
        except Exception as ex:
            print(f"Error al obtener todos los usuarios: {ex}")
            return []

    def toggle_user_lock_status(self, id_usuarios, current_status):
        try:
            cursor = self.mysql.connection.cursor()
            new_status = not current_status 

            # La consulta SQL para actualizar el estado de bloqueo y resetear intentos
            sql = "UPDATE usuarios SET is_locked = %s, failed_attempts = 0 WHERE id_usuarios = %s"
            cursor.execute(sql, (new_status, int(id_usuarios)))
            self.mysql.connection.commit()
            cursor.close()
            
            return True 
        except Exception as ex:
            self.mysql.connection.rollback() 
            return False