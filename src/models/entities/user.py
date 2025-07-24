from werkzeug.security import check_password_hash
from flask_login import UserMixin

class Usuarios (UserMixin):

    def __init__(self, id_usuarios, usuario, password, fullname="", is_locked=False, failed_attempts=0) -> None:
        self.id = id_usuarios
        self.usuario = usuario
        self.password = password # Nota: este será el hash en la BD, no la contraseña en texto plano
        self.fullname = fullname
        self.is_locked = is_locked
        self.failed_attempts = failed_attempts

    @classmethod    
    def check_password (cls, hashed_password, password):        
        return check_password_hash(hashed_password, password)

    # Puedes añadir un método para determinar si el usuario es admin.
    # Esto requeriría un campo 'rol' en la tabla de usuarios.
    # Por ahora, para simplificar, asumiremos que un usuario con un ID específico es admin,
    # o que el primer usuario registrado es el admin.
    # Lo ideal es tener un campo 'role' en la tabla de usuarios (ej. 'admin', 'user').
    def is_admin(self):
        # Suponiendo que el usuario con id=1 es el admin.
        # En un sistema real, usarías un campo 'role' en la base de datos.
        return self.id == 1