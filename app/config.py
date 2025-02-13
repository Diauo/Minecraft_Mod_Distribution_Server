import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GLOBAL_RESULT_FORMAT_EXCLUSION_INTERFACE = ['/api/file/download']
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 600
    DEFAULT_PATH = "C:\\Users\\admin\\Desktop\\工程调度中心\\mctest"


class Test_config(Config):
    TESTING = True
