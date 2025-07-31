#
class Config:
    SECRET_KEY = 'ec2b7f867d9cd541cd262a47d62b2970'

#Configuraciones de desarrollo
class DevelopmentConfig(Config):
    DEBUG=True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_PORT = 3306
    MYSQL_DB = 'database_bs'

config={
    'development':DevelopmentConfig
}