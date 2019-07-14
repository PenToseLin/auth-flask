from flask import Flask
from App.ext import init_ext
from App.url import init_router
from config.setting import envs


def create_app():

    app = Flask(__name__)
    # 初始化app
    app.config.from_object(envs.get("develop"))

    # 初始化路由
    init_router(app)

    # 初始化第三方库
    init_ext(app)

    return app
