from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import desc, asc
from App.common.auth_check import AuthCheck
from App.ext import db
from App.model.auth import Auth
from App.model.role import Role, RoleSchema

role_router = Blueprint("role_router", __name__)


@role_router.route('/list', methods=['GET'])
@jwt_required
@AuthCheck.check_api_auth
def query_list():
    page_no = request.args.get('pageNo', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    role_name = request.args.get('role_name', None, type=str)
    create_time = request.args.get('create_time', None, type=str)
    update_time = request.args.get('update_time', None, type=str)
    is_root = request.args.get('is_root', None, type=int)
    sorter = request.args.get('sorter', None, type=str)

    role_list = Role().query

    # 根据条件查询
    if role_name is not None:
        role_list = role_list.filter(Role.role_name.contains(role_name))
    if is_root is not None:
        role_list = role_list.filter(Role.is_root == is_root)
    if create_time is not None:
        create_time_list = create_time.split('~')
        role_list = role_list.filter(Role.create_time.between(create_time_list[0], create_time_list[1]))
    if update_time is not None:
        update_time_list = update_time.split('~')
        role_list = role_list.filter(Role.create_time.between(update_time_list[0], update_time_list[1]))
    if sorter is not None:
        sorter_list = sorter.split('~')
        role_list = role_list.order_by(globals()[sorter_list[1]](sorter_list[0]))

    total = role_list.count()
    role_list = role_list.offset((page_no - 1) * page_size).limit(page_size)
    # json序列化
    ret_list = RoleSchema().dump(role_list, many=True)

    ret_data = {
        'list': ret_list.data,
        'pagination': {
            'pageNo': page_no,
            'pageSize': page_size,
            'total': total
        }
    }

    return jsonify({'code': 200, 'msg': 'success', 'data': ret_data})


@role_router.route('/add', methods=['POST'])
@jwt_required
@AuthCheck.check_api_auth
def add():
    post_data = request.get_json()
    role_name = post_data.get('role_name')
    depict = post_data.get('depict')
    auth_ids = post_data.get('auth_ids')

    if not role_name:
        return jsonify(code=400, msg='角色名称不能为空')

    role = Role()
    role.role_name = role_name
    role.depict = depict

    if auth_ids:
        for auth_id in auth_ids:
            auth = Auth.query.filter_by(id=auth_id).first()
            role.auth_list.append(auth)

    db.session.add(role)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '添加成功'})


@role_router.route('/update', methods=['PUT'])
@jwt_required
@AuthCheck.check_api_auth
def update():
    post_data = request.get_json()
    role_id = post_data.get('id')
    role_name = post_data.get('role_name')
    depict = post_data.get('depict') or ''
    auth_ids = post_data.get('auth_ids')

    if not all([role_id, role_name]):
        return jsonify(code=400, msg='参数有误')

    role = Role().query.filter_by(id=role_id).first()
    if not role:
        return jsonify(code=400, msg='不存在该角色')

    if auth_ids:
        for auth_id in auth_ids:
            auth = Auth.query.filter_by(id=auth_id).first()
            role.auth_list.append(auth)

    role.role_name = role_name
    role.depict = depict
    role.update_time = datetime.utcnow()
    db.session.add(role)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '修改成功'})


@role_router.route('/disable', methods=['PUT'])
@jwt_required
@AuthCheck.check_api_auth
def disable():
    post_data = request.get_json()
    role_id = post_data.get('id')

    if not role_id:
        return jsonify(code=400, msg='没有进行任何操作')

    role = Role.query.filter_by(id=role_id).first()
    if not role:
        return jsonify(code=400, msg='不存在该角色')

    role.status = 0
    db.session.add(role)
    db.session.commit()

    return jsonify(code=200, msg='操作成功')


@role_router.route('/enable', methods=['PUT'])
@jwt_required
@AuthCheck.check_api_auth
def enable():
    post_data = request.get_json()
    role_id = post_data.get('id')

    if not role_id:
        return jsonify(code=400, msg='没有进行任何操作')

    role = Role.query.filter_by(id=role_id).first()
    if not role:
        return jsonify(code=400, msg='不存在该角色')

    if role.is_root == 1:
        return jsonify(code=400, msg='该角色不可删除')

    role.status = 1
    db.session.add(role)
    db.session.commit()

    return jsonify(code=200, msg='操作成功')


@role_router.route('/remove', methods=['DELETE'])
@jwt_required
@AuthCheck.check_api_auth
def remove():
    post_data = request.get_json()
    id_list = post_data.get('id_list')

    if not id_list:
        return jsonify(code=400, msg='没有进行任何操作')

    for role_id in id_list:
        role = Role.query.filter_by(id=role_id).first()
        if not role:
            return jsonify(code=400, msg='不存在该角色')
        elif role.is_root == 1:
            return jsonify(code=400, msg='内置用户不可修改')
        else:
            db.session.delete(role)

    db.session.commit()

    return jsonify(code=200, msg='删除成功')


@role_router.route('/all', methods=['GET'])
@jwt_required
def query_all():
    role_list = Role.query.all()
    role_list = RoleSchema().dump(role_list, many=True)

    return jsonify(code=200, msg='成功', data=role_list.data)
