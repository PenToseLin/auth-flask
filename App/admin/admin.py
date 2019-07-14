from flask import Blueprint, jsonify, request
from App.ext import db
from App.model.role import Role
from App.model.user import User, UserSchema

admin_router = Blueprint("admin_router", __name__)


@admin_router.route('/login')
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    if not username:
        return jsonify(code=400, msg='请输入用户名')

    if not password:
        return jsonify(code=400, msg='请输入密码')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(code=400, msg='该用户不存在')

    return jsonify(code=200, msg='登录成功', data={})
