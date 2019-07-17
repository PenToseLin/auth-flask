from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from App.ext import db
from marshmallow import Schema, fields
from App.model.role import RoleSchema

AVATAR = "https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png"

# 多对多 用户与角色关系表
user_role = db.Table(
    'user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), nullable=False)  # 用户名称
    password_hash = db.Column(db.String(255), nullable=False)  # 加密后的密码
    mobile = db.Column(db.String(11))  # 手机号码
    avatar = db.Column(db.String(255), default=AVATAR)  # 用户头像
    create_time = db.Column(db.DateTime, default=datetime.utcnow())  # 创建时间
    update_time = db.Column(db.DateTime, default=datetime.utcnow())  # 更新时间
    last_login = db.Column(db.DateTime, default=datetime.utcnow())  # 最后登录时间
    status = db.Column(db.Integer, default=1)  # 状态  0.禁用 1.启用 -1.删除
    roles = db.relationship("Role", backref=db.backref('users'), secondary=user_role, lazy="dynamic")  # 角色

    def to_json(self):
        ret = self.__dict__
        if "_sa_instance_state" in ret:
            del ret["_sa_instance_state"]
        return ret

    def get(self, user_id):
        return self.query.filter_by(id=user_id).first()

    @staticmethod
    def add(user):
        db.session.add(user)
        return db.session.commit()

    @staticmethod
    def update(user):
        db.session.add(user)
        return db.session.commit()

    @staticmethod
    def delete(user):
        db.session.add(user)
        return db.session.commit()

    @property
    def password(self):
        """读取属性函数"""
        # 读取值就是返回属性值
        return AttributeError("该属性只能录入, 不可读取")

    @password.setter
    def password(self, org_pwd):
        """设置属性函数, 密码加密"""
        self.password_hash = generate_password_hash(org_pwd, salt_length=16)

    def check_password(self, pwd):
        """校验密码"""
        return check_password_hash(self.password_hash, pwd)

    def get_auth_list(self):
        auth_list = []
        for role in self.roles:
            for auth in role.auth_list:
                if auth.url not in auth_list:
                    auth_list.append(auth.url)
        return auth_list


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    mobile = fields.Str()
    avatar = fields.Str()
    create_time = fields.DateTime()
    update_time = fields.DateTime()
    last_login = fields.DateTime()
    status = fields.Int()
    roles = fields.Nested(RoleSchema, many=True)
