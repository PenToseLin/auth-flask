import re
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import desc, asc
from App.common.auth_check import AuthCheck
from App.ext import db
from App.model.role import Role
from App.model.user import User, UserSchema

user_router = Blueprint("user_router", __name__)


@user_router.route('/list', methods=['GET'], endpoint='user_list')
@jwt_required
@AuthCheck.check_api_auth
def query_list():
    page_no = request.args.get('pageNo', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    username = request.args.get('username', None, type=str)
    mobile = request.args.get('mobile', None, type=str)
    status = request.args.get('status', None, type=int)
    create_time = request.args.get('create_time', None, type=str)
    update_time = request.args.get('update_time', None, type=str)
    last_login = request.args.get('last_login', None, type=str)
    sorter = request.args.get('sorter', None, type=str)

    user_list = User().query.filter(User.status.__gt__(-1))

    # 根据条件查询
    if username is not None:
        user_list = user_list.filter(User.username.contains(username))
    if mobile is not None:
        user_list = user_list.filter(User.mobile.contains(mobile))
    if status is not None:
        user_list = user_list.filter(User.status == status)
    if create_time is not None:
        create_time_list = create_time.split('~')
        user_list = user_list.filter(User.create_time.between(create_time_list[0], create_time_list[1]))
    if update_time is not None:
        update_time_list = update_time.split('~')
        user_list = user_list.filter(User.create_time.between(update_time_list[0], update_time_list[1]))
    if last_login is not None:
        last_login_list = last_login.split('~')
        user_list = user_list.filter(User.create_time.between(last_login_list[0], last_login_list[1]))
    if sorter is not None:
        sorter_list = sorter.split('~')
        user_list = user_list.order_by(globals()[sorter_list[1]](sorter_list[0]))

    total = user_list.count()
    user_list = user_list.offset((page_no - 1) * page_size).limit(page_size)
    users_dict = UserSchema().dump(user_list, many=True)

    ret_data = {
        'list': users_dict.data,
        'pagination': {
            'pageNo': page_no,
            'pageSize': page_size,
            'total': total
        }
    }

    return jsonify({'code': 200, 'msg': 'success', 'data': ret_data})


@user_router.route('/add', methods=['POST'], endpoint='user_add')
@jwt_required
@AuthCheck.check_api_auth
def add():
    post_data = request.get_json()
    username = post_data.get('username')
    mobile = post_data.get('mobile')
    password = post_data.get('password')
    password_confirm = post_data.get('password_confirm')
    role_ids = post_data.get('role_ids')

    if not all([username, mobile, password, password_confirm]):
        return jsonify(code=400, msg='参数不完整')

    if User.query.filter(User.username.__eq__(username), User.status.__gt__(-1)).first():
        return jsonify(code=400, msg='用户名已被使用')

    if not re.match(r"1[2-9]\d{9}", mobile):
        return jsonify(code=400, msg='手机号码格式有误')

    if User.query.filter(User.mobile.__eq__(mobile), User.status.__gt__(-1)).first():
        return jsonify(code=400, msg='手机号码已存在')

    if password != password_confirm:
        return jsonify(code=400, msg='两次输入密码不一致')

    role_list = []
    if role_ids:
        for role_id in role_ids:
            role_list.append(Role.query.filter_by(id=role_id).first())

    user = User()
    user.roles = role_list
    user.username = username
    user.mobile = mobile
    user.password = password
    db.session.add(user)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '注册成功'})


@user_router.route('/update', methods=['PUT'], endpoint='user_update')
@jwt_required
@AuthCheck.check_api_auth
def update():
    post_data = request.get_json()
    user_id = post_data.get('id')
    username = post_data.get('username')
    mobile = post_data.get('mobile')
    password = post_data.get('password')
    password_confirm = post_data.get('password_confirm')
    role_ids = post_data.get('role_ids')

    if not all([user_id, username, mobile]):
        return jsonify(cde=400, msg='参数有误')

    user = User.query.filter_by(id=user_id).first()

    if User.query.filter(User.username == username, User.id != user_id).first() is not None:
        return jsonify(code=400, msg='用户名已被使用')
    else:
        user.username = username

    if not re.match(r"1[2-9]\d{9}", mobile):
        return jsonify(code=400, msg='手机号码格式有误')
    elif User.query.filter(User.mobile == mobile, User.id != user_id).first() is not None:
        return jsonify(code=400, msg='手机号码已经存在')
    else:
        user.mobile = mobile

    if password is not None:
        if password != password_confirm:
            return jsonify(code=400, msg='两次输入密码不一致')
        else:
            user.password = password

    if role_ids:
        role_list = []
        for role_id in role_ids:
            role_list.append(Role.query.filter_by(id=role_id).first())
        user.roles = role_list

    user.update_time = datetime.utcnow()
    db.session.add(user)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '修改成功'})


@user_router.route('/disable', methods=['PUT'], endpoint='user_disable')
@jwt_required
@AuthCheck.check_api_auth
def disable():
    post_data = request.get_json()
    user_id = post_data.get('id')

    if not user_id:
        return jsonify(code=400, msg='没有进行任何操作')

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify(code=400, msg='不存在该用户')

    user.status = 0
    db.session.add(user)
    db.session.commit()

    return jsonify(code=200, msg='操作成功')


@user_router.route('/enable', methods=['PUT'], endpoint='user_enable')
@jwt_required
@AuthCheck.check_api_auth
def enable():
    post_data = request.get_json()
    user_id = post_data.get('id')

    if not user_id:
        return jsonify(code=400, msg='没有进行任何操作')

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify(code=400, msg='不存在该用户')

    user.status = 1
    db.session.add(user)
    db.session.commit()

    return jsonify(code=200, msg='操作成功')


@user_router.route('/remove', methods=['DELETE'], endpoint='user_remove')
@jwt_required
@AuthCheck.check_api_auth
def remove():
    post_data = request.get_json()
    id_list = post_data.get('id_list')

    if not id_list:
        return jsonify(code=400, msg='没有进行任何操作')

    for user_id in id_list:

        user = User.query.filter_by(id=user_id).first()
        if user:
            user.status = -1
            db.session.add(user)

    db.session.commit()

    return jsonify(code=200, msg='操作成功')

