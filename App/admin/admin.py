from flask import Blueprint, jsonify, request
from App.common.auth_check import AuthCheck
from App.model.user import User, UserSchema
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, jwt_refresh_token_required,
    create_refresh_token)

admin_router = Blueprint("admin_router", __name__)


@admin_router.route('/login', methods=['POST'])
@AuthCheck.check_login_auth
def login():
    post_data = request.get_json()
    username = post_data.get('username')

    user = User.query.filter_by(username=username).first()
    user_info = UserSchema().dump(user).data

    access_token = create_access_token(identity=user_info)
    refresh_token = create_refresh_token(identity=user_info)

    ret_data = {
        'user_info': user_info,
        'auth_list': user.get_auth_list(),
        'access_token': access_token,
        'refresh_token': refresh_token,
    }

    return jsonify(code=200, msg='登录成功', data=ret_data)


@admin_router.route('/current_user', methods=['GET'])
@jwt_required
def current_user():
    user = get_jwt_identity()
    user_info = User().get(user['id'])

    if not user_info:
        return jsonify(code=400, msg='该用户不存在')

    ret_data = {
        'user_info': UserSchema().dump(user_info).data,
        'auth_list': user_info.get_auth_list()
    }

    return jsonify(code=200, msg='成功', data=ret_data)


@admin_router.route('/refresh_access', methods=['POST'])
@jwt_refresh_token_required
def refresh_access():
    user = get_jwt_identity()
    ret_data = {
        'access_token': create_access_token(identity=user)
    }
    return jsonify(code=200, msg='成功', data=ret_data)
