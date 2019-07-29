from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from App.model.user import User


class AuthCheck:

    @staticmethod
    def check_api_auth(func):
        # api权限鉴定，获取角色权限url 对比 请求地址url
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取请求地址 转换成权限url
            # 设计的时候，菜单都去掉 "-api" ,而接口基本地址都加上 "-api"
            req_auth = request.path[1:]
            req_auth = req_auth.replace('-api', '').replace('/', ':')
            user_id = get_jwt_identity()['id']
            user = User().get(user_id)
            auth_list = user.get_auth_list()
            if req_auth not in auth_list:
                return jsonify(code=403, msg='无权访问')
            return func(*args, **kwargs)

        return wrapper

    @staticmethod
    def check_login_auth(func):
        # 登录鉴权，获取登录账号密码，获取角色登录权限，判断是否可登录当前应用
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取请求地址 转换成权限url
            post_data = request.get_json()
            username = post_data.get('username')
            password = post_data.get('password')

            if not username:
                return jsonify(code=400, msg='请输入用户名')

            if not password:
                return jsonify(code=400, msg='请输入密码')

            user = User.query.filter(User.username == username and User.status.__gt__(-1)).first()
            if not user:
                return jsonify(code=400, msg='该用户不存在')

            if not user.check_password(password):
                return jsonify(code=400, msg='密码或用户名错误')

            if user.status == 0:
                return jsonify(code=403, msg='该账号已被禁用')

            # 设计的时候，菜单都去掉 "-api" ,而接口基本地址都加上 "-api"
            req_auth = request.path.replace('-api', '', 1)[1:].replace('/', ':')
            auth_list = user.get_auth_list()
            if req_auth not in auth_list:
                return jsonify(code=403, msg='无权访问')
            return func(*args, **kwargs)

        return wrapper
