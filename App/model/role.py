from datetime import datetime
from App.ext import db
from marshmallow import Schema, fields

# 多对多 角色与权限关系表
from App.model.auth import AuthSchema

role_auth = db.Table(
    'role_auth',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('auth_id', db.Integer, db.ForeignKey('auth.id'), primary_key=True)
)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(32), unique=True, nullable=False)  # 角色名称
    depict = db.Column(db.String(255))  # 描述
    is_root = db.Column(db.Integer, default=0, nullable=False)  # 是否是系统内置 0.否 1.是
    status = db.Column(db.Integer, default=1)  # 角色状态 1.启用  0.禁用
    update_time = db.Column(db.DateTime, default=datetime.utcnow())  # 更新时间
    create_time = db.Column(db.DateTime, default=datetime.utcnow())  # 创建时间
    auth_list = db.relationship("Auth", backref=db.backref('roles'), secondary=role_auth, lazy="dynamic")  # 角色

    def to_json(self):
        ret = self.__dict__
        if "_sa_instance_state" in ret:
            del ret["_sa_instance_state"]
        return ret


class RoleSchema(Schema):
    id = fields.Int()
    role_name = fields.Str()
    depict = fields.Str()
    is_root = fields.Int()
    status = fields.Int()
    create_time = fields.DateTime()
    update_time = fields.DateTime()
    auth_list = fields.Nested(AuthSchema, many=True, only=['id', 'auth_name', 'menu'])
