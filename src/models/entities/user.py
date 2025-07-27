from werkzeug.security import check_password_hash
from flask_login import UserMixin

class Usuarios (UserMixin):

    def __init__(self, id_usuarios, usuario, password, fullname="", is_locked=False, failed_attempts=0) -> None:
        self.id = id_usuarios
        self.usuario = usuario
        self.password = password
        self.fullname = fullname
        self.is_locked = is_locked
        self.failed_attempts = failed_attempts

    @classmethod    
    def check_password (cls, hashed_password, password):        
        return check_password_hash(hashed_password, password)

    def is_admin(self):
        return self.id == 1