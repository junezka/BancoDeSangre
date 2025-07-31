import os

class Config:
    SECRET_KEY = 'ec2b7f867d9cd541cd262a47d62b2970'

#Configuraciones de desarrollo
class DevelopmentConfig(Config):
    DEBUG=True
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")

config={
    'development':DevelopmentConfig
}