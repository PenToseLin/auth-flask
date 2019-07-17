from flask import Blueprint, jsonify, request
from App.model.user import User, UserSchema
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

admin_router = Blueprint("admin_router", __name__)


@admin_router.route('/login', methods=['POST'])
def login():
    post_data = request.get_json()
    username = post_data.get('username')
    password = post_data.get('password')

    if not username:
        return jsonify(code=400, msg='请输入用户名')

    if not password:
        return jsonify(code=400, msg='请输入密码')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(code=400, msg='该用户不存在')

    if not user.check_password(password):
        return jsonify(code=400, msg='密码或用户名错误')

    access_token = create_access_token(identity=user)

    ret_data = {
        'user_info': UserSchema().dump(user).data,
        'auth_list': user.get_auth_list(),
        'access_token': access_token,
    }

    return jsonify(code=200, msg='登录成功', data=ret_data)


@admin_router.route('/current_user', methods=['GET'])
@jwt_required
def current_user():
    # username = request.args.get('username')

    user = get_jwt_identity()

    print('current_user: ')
    print(user)
    #
    # if not username:
    #     return jsonify(code=400, msg='参数有误')
    #
    # user = User.query.filter_by(username=username).first()
    # if not user:
    #     return jsonify(code=400, msg='该用户不存在')

    ret_data = {
        'user_info': UserSchema().dump(user).data,
        'auth_list': user.get_auth_list()
    }

    return jsonify(code=200, msg='成功', data=ret_data)
