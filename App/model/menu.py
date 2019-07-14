from datetime import datetime
from marshmallow import Schema, fields
from App.ext import db
# from App.model.auth import AuthSchema


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    menu_name = db.Column(db.String(32), unique=True, nullable=False)  # 菜单名称
    version = db.Column(db.String(16), default='1.0')  # 版本
    queue = db.Column(db.String(32), default=0)
    grade = db.Column(db.Integer, default=0)  # 菜单层级
    url = db.Column(db.String(255), nullable=False)  # 菜单路径
    tree_path = db.Column(db.String(32), default=',')  # 菜单层级地址
    parent_id = db.Column(db.Integer, default=0)  # 父级菜单id
    status = db.Column(db.Integer, default=1)  # 状态 1.启用  0.禁用
    update_time = db.Column(db.DateTime, default=datetime.utcnow())  # 更新时间
    create_time = db.Column(db.DateTime, default=datetime.utcnow())  # 创建时间
    auth_list = db.relationship("Auth", backref='menu', lazy="dynamic")  # 权限

    def to_json(self):
        ret = self.__dict__
        if "_sa_instance_state" in ret:
            del ret["_sa_instance_state"]
        return ret


class MenuSchema(Schema):
    id = fields.Int()
    menu_name = fields.Str()
    queue = fields.Str()
    grade = fields.Str()
    url = fields.Str()
    parent_id = fields.Int()
    status = fields.Int()
    create_time = fields.DateTime()
    update_time = fields.DateTime()
    # auth_list = fields.Nested(
    #     AuthSchema,
    #     many=True,
    #     only=['id', 'auth_name', 'depict', 'method', 'queue',
    #           'url', 'update_time', 'create_time', 'status']
    # )
