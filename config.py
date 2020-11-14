from os import path, getcwd

class Config:
    DEBUG = True
    FLASK_RUN_HOST = 'localhost'
    FLASK_RUN_PORT = 5000
    SUPPORTED_IMAGES_EXT = ['image/png', 'image/jpeg']
    SUPPORTED_VIDEOS_EXT = ['video/mp4', 'video/mpeg', 'video/quicktime', 'application/octet-stream']
    FILE_ALLOWED = SUPPORTED_IMAGES_EXT + SUPPORTED_VIDEOS_EXT
    ASSETS = path.join(getcwd(), 'assets')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'felipe.mantovanello@gmail.com'
    MAIL_PASSWORD = 'vnnavxodibgxfthi'
