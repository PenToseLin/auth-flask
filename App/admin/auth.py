from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import desc, asc
from App.common.auth_check import AuthCheck
from App.ext import db
from App.model.auth import Auth, AuthSchema
from App.model.menu import Menu
from App.model.role import Role

auth_router = Blueprint("auth_router", __name__)


def get_auth_children(auth_id):
    # 找到auth_id层级下面的所有元素
    auth_list = Auth.query.filter_by(parent_id=auth_id).all()
    if auth_list:
        for child in auth_list:
            child.children = []
            child_list = get_auth_children(child.id)
            for child_item in child_list:
                child.children.append(child_item)
        return auth_list
    else:
        return []


@auth_router.route('/list')
@jwt_required
@AuthCheck.check_api_auth
def query_list():
    page_no = request.args.get('pageNo', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    auth_name = request.args.get('auth_name', None, type=str)
    create_time = request.args.get('create_time', None, type=str)
    update_time = request.args.get('update_time', None, type=str)
    version = request.args.get('version', None, type=str)
    parent_id = request.args.get('parent_id', None, type=int)
    sorter = request.args.get('sorter', None, type=str)

    auth_list = Auth().query.filter_by(grade=0)
    # 根据条件查询
    if auth_name is not None:
        auth_list = auth_list.filter(Auth.auth_name.contains(auth_name))
    if version is not None:
        auth_list = auth_list.filter(Auth.version == version)
    if parent_id is not None:
        auth_list = auth_list.filter(Auth.parent_id == parent_id)
    if create_time is not None:
        create_time_list = create_time.split('~')
        auth_list = auth_list.filter(Auth.create_time.between(create_time_list[0], create_time_list[1]))
    if update_time is not None:
        update_time_list = update_time.split('~')
        auth_list = auth_list.filter(Auth.create_time.between(update_time_list[0], update_time_list[1]))
    if sorter is not None:
        sorter_list = sorter.split('~')
        auth_list = auth_list.order_by(globals()[sorter_list[1]](sorter_list[0]))

    total = auth_list.count()
    auth_list = auth_list.offset((page_no - 1) * page_size).limit(page_size).all()
    # json序列化
    for parent_item in auth_list:
        parent_item.children = get_auth_children(parent_item.id)
    ret_list = AuthSchema().dump(auth_list, many=True)

    ret_data = {
        'list': ret_list.data,
        'pagination': {
            'pageNo': page_no,
            'pageSize': page_size,
            'total': total
        }
    }

    return jsonify({'code': 200, 'msg': 'success', 'data': ret_data})


@auth_router.route('/query_by_menu')
def query_by_menu():
    menu_id = request.args.get('menu_id')
    auth_list = Auth.query.filter_by(menu_id=menu_id, grade=0).all()

    ret_list = []
    for parent_item in auth_list:
        parent_item.children = []
        for item in get_auth_children(parent_item.id):
            parent_item.children.append(item.to_json())
        ret_list.append(parent_item.to_json())

    return jsonify({'code': 200, 'msg': 'success', 'data': ret_list})


@auth_router.route('/add', methods=['POST'])
def add():
    post_data = request.get_json()
    auth_name = post_data.get('auth_name')
    method = post_data.get('method')
    depict = post_data.get('depict')
    queue = post_data.get('queue')
    parent_id = post_data.get('parent_id')
    menu_id = post_data.get('menu_id')

    if not all([auth_name, method, menu_id]):
        return jsonify(code=400, msg='参数不完整')

    menu = Menu.query.filter_by(id=menu_id).first()
    if not menu:
        return jsonify(code=400, msg='不存在改菜单')

    auth = Auth()

    # 是否有上级权限，如果有则从上级权限url后面添加，如果没有从权限url获取
    if parent_id:
        parent_auth = Auth.query.filter_by(id=parent_id).first()
        if not parent_auth:
            return jsonify(code=400, msg='上级菜单参数有误')
        menu_url = parent_auth.url.replace(':', '/')
        # 是否有上级权限，若没有则是一级权限，若存在则保存权限层级路径 和 权限层级
        auth.parent_id = parent_id
        auth.grade = parent_auth.grade + 1
        auth.tree_path = '%s%d,' % (parent_auth.tree_path, auth.parent_id)
    else:
        menu_url = menu.url

    if not menu_url.endswith('/'):
        menu_url = '{0}/'.format(menu_url)

    menu_url = '%s%s' % (menu_url.replace('/', ':'), method)

    if Auth.query.filter_by(url=menu_url).all():
        return jsonify(code=400, msg='该权限已存在')

    if depict:
        auth.depict = depict
    auth.menu_id = menu_id
    auth.url = menu_url
    auth.method = method
    auth.auth_name = auth_name
    auth.queue = queue or 0
    root_role = Role.query.filter_by(is_root=1).first()
    root_role.auth_list.append(auth)

    db.session.add(auth)
    db.session.add(root_role)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '添加成功'})


@auth_router.route('/update', methods=['PUT'])
def update():
    post_data = request.get_json()
    auth_id = post_data.get('id')
    auth_name = post_data.get('auth_name')
    queue = post_data.get('queue')
    depict = post_data.get('depict')

    if not auth_id:
        return jsonify(code=400, msg='参数有误')
    if not auth_name:
        return jsonify(code=400, msg='权限名称不能为空')

    auth = Auth.query.filter_by(id=auth_id).first()
    if not auth:
        return jsonify(code=400, msg='不存在该权限')
    auth.auth_name = auth_name
    auth.queue = queue
    if depict:
        auth.depict = depict

    auth.queue = queue or 0

    db.session.add(auth)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '修改成功'})


@auth_router.route('/disable', methods=['PUT'])
def disable():
    post_data = request.get_json()
    auth_id = post_data.get('id')

    if not auth_id:
        return jsonify(code=400, msg='没有进行任何操作')

    auth = Auth.query.filter_by(id=auth_id).first()
    if not auth:
        return jsonify(code=400, msg='不存在该权限')

    auth.status = 0
    db.session.add(auth)
    db.session.commit()

    return jsonify(code=200, msg='操作成功')


@auth_router.route('/enable', methods=['PUT'])
def enable():
    post_data = request.get_json()
    auth_id = post_data.get('id')

    if not auth_id:
        return jsonify(code=400, msg='没有进行任何操作')

    auth = Auth.query.filter_by(id=auth_id).first()
    if not auth:
        return jsonify(code=400, msg='不存在该权限')

    auth.status = 1
    db.session.add(auth)
    db.session.commit()

    return jsonify(code=200, msg='操作成功')


@auth_router.route('/remove', methods=['DELETE'])
def remove():
    post_data = request.get_json()
    id_list = post_data.get('id_list')

    if not id_list:
        return jsonify(code=400, msg='没有进行任何操作')

    id_list.sort()
    id_list.reverse()
    for auth_id in id_list:
        auth = Auth.query.filter_by(id=auth_id).first()

        if not auth:
            return jsonify(code=400, msg='不存在该权限')
        if Auth.query.filter_by(parent_id=auth_id).all():
            return jsonify(
                code=400,
                msg='%s-%s存在下级权限，不可删除' % (auth.auth_name, auth.menu.menu_name)
            )
        db.session.delete(auth)

    db.session.commit()

    return jsonify(code=200, msg='删除成功')


@auth_router.route('/all')
def query_all():

    auth_list = Auth().query.filter_by().all()
    # json序列化
    ret_list = AuthSchema().dump(auth_list, many=True)

    return jsonify({'code': 200, 'msg': 'success', 'data': ret_list.data})
