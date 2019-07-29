from App.admin.admin import admin_router
from App.admin.user import user_router
from App.admin.role import role_router
from App.admin.auth import auth_router
from App.admin.menu import menu_router


def init_router(app):
    # 后台管理路由
    app.register_blueprint(admin_router, url_prefix="/admin-api")
    app.register_blueprint(user_router, url_prefix="/admin-api/manage/user")
    app.register_blueprint(role_router, url_prefix="/admin-api/manage/role")
    app.register_blueprint(menu_router, url_prefix="/admin-api/manage/menu")
    app.register_blueprint(auth_router, url_prefix="/admin-api/manage/auth")
