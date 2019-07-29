from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import desc, asc
from App.common.auth_check import AuthCheck
from App.ext import db
from App.model.auth import Auth
from App.model.menu import Menu

menu_router = Blueprint("menu_router", __name__)


def get_menu_children(menu_id):
    menu_list = Menu.query.filter_by(parent_id=menu_id).all()
    if menu_list:
        for child in menu_list:
            child.children = []
            child_list = get_menu_children(child.id)
            for child_item in child_list:
                child.children.append(child_item.to_json())
        return menu_list
    else:
        return []


@menu_router.route('/list')
@jwt_required
@AuthCheck.check_api_auth
def query_list():
    page_no = request.args.get('pageNo', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    menu_name = request.args.get('menu_name', None, type=str)
    create_time = request.args.get('create_time', None, type=str)
    update_time = request.args.get('update_time', None, type=str)
    version = request.args.get('version', None, type=str)
    parent_id = request.args.get('parent_id', None, type=int)
    sorter = request.args.get('sorter', None, type=str)

    menu_list = Menu().query.filter_by(grade=0)
    # 根据条件查询
    if menu_name is not None:
        menu_list = Menu().query.filter(Menu.menu_name.contains(menu_name))
    if version is not None:
        menu_list = menu_list.filter(Menu.version == version)
    if parent_id is not None:
        menu_list = menu_list.filter(Menu.parent_id == parent_id)
    if create_time is not None:
        create_time_list = create_time.split('~')
        menu_list = menu_list.filter(Menu.create_time.between(create_time_list[0], create_time_list[1]))
    if update_time is not None:
        update_time_list = update_time.split('~')
        menu_list = menu_list.filter(Menu.create_time.between(update_time_list[0], update_time_list[1]))
    if sorter is not None:
        sorter_list = sorter.split('~')
        menu_list = menu_list.order_by(globals()[sorter_list[1]](sorter_list[0]))

    total = menu_list.count()
    menu_list = menu_list.offset((page_no - 1) * page_size).limit(page_size)
    # json序列化
    ret_list = []
    for parent_item in menu_list:
        parent_item.children = []
        for item in get_menu_children(parent_item.id):
            parent_item.children.append(item.to_json())
        ret_list.append(parent_item.to_json())

    ret_data = {
        'list': ret_list,
        'pagination': {
            'pageNo': page_no,
            'pageSize': page_size,
            'total': total
        }
    }

    return jsonify({'code': 200, 'msg': 'success', 'data': ret_data})


@menu_router.route('/add', methods=['POST'])
def add():
    post_data = request.get_json()
    menu_name = post_data.get('menu_name')
    queue = post_data.get('queue')
    url = post_data.get('url')
    parent_id = post_data.get('parent_id')

    if not menu_name:
        return jsonify(code=400, msg='菜单名称不能为空')
    if not url:
        return jsonify(code=400, msg='菜单路径不能为空')
    if Menu.query.filter_by(menu_name=menu_name).first():
        return jsonify(code=400, msg='该菜单已经存在')

    menu = Menu()
    menu.menu_name = menu_name
    menu.url = url

    menu.queue = queue or 0

    # 是否有上级菜单，若没有则是一级菜单，若存在则保存菜单层级路径 和 菜单层级
    if parent_id:
        menu.parent_id = parent_id
        parent_menu = Menu().query.filter(Menu.id == parent_id).first()
        if not parent_menu:
            return jsonify(code=400, msg='上级菜单参数有误')
        menu.tree_path = '%s%d,' % (parent_menu.tree_path, menu.parent_id)
        menu.grade = parent_menu.grade + 1

    db.session.add(menu)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '添加成功'})


@menu_router.route('/update', methods=['PUT'])
def update():
    post_data = request.get_json()
    menu_id = post_data.get('id')
    menu_name = post_data.get('menu_name')
    queue = post_data.get('queue')

    if not menu_id:
        return jsonify(code=400, msg='参数有误')
    if not menu_name:
        return jsonify(code=400, msg='菜单名称不能为空')

    menu = Menu.query.filter_by(id=menu_id).first()
    if not menu:
        return jsonify(code=400, msg='不存在该菜单')
    menu.menu_name = menu_name
    menu.queue = queue or 0
    menu.update_time = datetime.utcnow()

    db.session.add(menu)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '修改成功'})


@menu_router.route('/disable', methods=['PUT'])
def disable():
    post_data = request.get_json()
    menu_id = post_data.get('id')

    if not menu_id:
        return jsonify(code=400, msg='没有进行任何操作')

    menu = Menu.query.filter_by(id=menu_id).first()
    if not menu:
        return jsonify(code=400, msg='不存在该菜单')

    menu.status = 0
    db.session.add(menu)
    db.session.commit()

    return jsonify(code=200, msg='操作成功')


@menu_router.route('/enable', methods=['PUT'])
def enable():
    post_data = request.get_json()
    menu_id = post_data.get('id')

    if not menu_id:
        return jsonify(code=400, msg='没有进行任何操作')

    menu = Menu.query.filter_by(id=menu_id).first()
    if not menu:
        return jsonify(code=400, msg='不存在该菜单')

    menu.status = 1
    db.session.add(menu)
    db.session.commit()

    return jsonify(code=200, msg='操作成功')


@menu_router.route('/remove', methods=['DELETE'])
def remove():
    post_data = request.get_json()
    id_list = post_data.get('id_list')

    if not id_list:
        return jsonify(code=400, msg='没有进行任何操作')

    id_list.sort()
    id_list.reverse()
    for menu_id in id_list:
        menu = Menu.query.filter_by(id=menu_id).first()
        if not menu:
            return jsonify(code=400, msg='不存在该菜单')

        if Auth.query.filter_by(menu_id=menu_id).all():
            return jsonify(code=400, msg='%s存在下级权限，不可删除' % menu.menu_name)

        if Menu.query.filter_by(parent_id=menu_id).all():
            return jsonify(code=400, msg='%s存在下级菜单，不可删除' % menu.menu_name)

        db.session.delete(menu)

    db.session.commit()

    return jsonify(code=200, msg='删除成功')
