from datetime import datetime
from marshmallow import Schema, fields
from App.ext import db
from App.model.menu import MenuSchema


class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    auth_name = db.Column(db.String(32),  nullable=False)  # 权限名称
    depict = db.Column(db.String(255))  # 描述
    method = db.Column(db.String(255), nullable=False)  # 权限控制的方法
    version = db.Column(db.String(16), default='1.0')  # 版本
    queue = db.Column(db.String(32), default=0)  # 排序序号
    grade = db.Column(db.Integer, default=0)  # 权限层级
    tree_path = db.Column(db.String(32), default=',')  # 权限层级地址
    url = db.Column(db.String(255), nullable=False)  # 权限路径
    parent_id = db.Column(db.Integer, default=0)  # 上级权限id
    status = db.Column(db.Integer, default=1)  # 权限状态 1.启用  0.禁用
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'))  # 菜单id
    update_time = db.Column(db.DateTime, default=datetime.utcnow())  # 更新时间
    create_time = db.Column(db.DateTime, default=datetime.utcnow())  # 创建时间

    def to_json(self):
        ret = self.__dict__
        if "_sa_instance_state" in ret:
            del ret["_sa_instance_state"]
        return ret


class AuthSchema(Schema):
    id = fields.Int()
    auth_name = fields.Str()
    depict = fields.Str()
    queue = fields.Str()
    grade = fields.Str()
    method = fields.Str()
    url = fields.Str()
    parent_id = fields.Int()
    status = fields.Int()
    create_time = fields.DateTime()
    update_time = fields.DateTime()
    children = fields.Nested('self', many=True)
    menu = fields.Nested(MenuSchema, only=['id', 'menu_name'])
