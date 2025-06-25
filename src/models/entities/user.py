from werkzeug.security import check_password_hash
from flask_login import UserMixin

class Usuarios (UserMixin):

    def __init__(self, id_usuarios, usuario, password, fullname = "")  -> None:
        self.id = id_usuarios
        self.usuario = usuario
        self.password = password
        self.fullname = fullname

    @classmethod    
    def check_password (cls, hashed_password, password):        
        return check_password_hash(hashed_password, password)

