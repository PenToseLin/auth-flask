
def get_db_uri(dbinfo):
    engine = dbinfo.get("ENGINE") or "mysql"
    driver = dbinfo.get("DRIVER") or "pymysql"
    user = dbinfo.get("USER") or "root"
    password = dbinfo.get("PASSWORD") or "123456"
    host = dbinfo.get("HOST") or "localhost"
    port = dbinfo.get("PORT") or "3306"
    name = dbinfo.get("NAME") or "mysql"

    return "{}+{}://{}:{}@{}:{}/{}".format(engine, driver, user, password, host, port, name)


class Config:

    DEBUG = False

    TESTING = False

    SECRET_KEY = "MiniAchvAuthApplication"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 600

    JWT_SECRET_KEY = "MiniAchvAuthApplication_JWT"
    JWT_HEADER_NAME = "access_token"
    JWT_HEADER_TYPE = ""
    JWT_ACCESS_TOKEN_EXPIRES = 604800  # 默认token时间7天


class DevelopConfig(Config):

    DEBUG = True

    DATABASE = {
        "ENGINE": "mysql",
        "DRIVER": "pymysql",
        "USER": "root",
        "PASSWORD": "123456",
        "HOST": "localhost",
        "PORT": "3306",
        "NAME": "auth_test"
    }

    SQLALCHEMY_DATABASE_URI = get_db_uri(DATABASE)


class TestingConfig(Config):

    TESTING = True

    DATABASE = {
        "ENGINE": "mysql",
        "DRIVER": "pymysql",
        "USER": "root",
        "PASSWORD": "123456",
        "HOST": "localhost",
        "PORT": "3306",
        "NAME": "auth_test"
    }

    SQLALCHEMY_DATABASE_URI = get_db_uri(DATABASE)


class ProductConfig(Config):

    TESTING = True

    DATABASE = {
        "ENGINE": "mysql",
        "DRIVER": "pymysql",
        "USER": "root",
        "PASSWORD": "123456",
        "HOST": "localhost",
        "PORT": "3306",
        "NAME": "auth_test"
    }

    SQLALCHEMY_DATABASE_URI = get_db_uri(DATABASE)


envs = {
    "develop": DevelopConfig,
    "testing": TestingConfig,
    "product": ProductConfig,
    "default": DevelopConfig
}
