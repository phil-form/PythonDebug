from app import db
from app.models.base_entity import BaseEntity
from app.models.role import Role
from app.models.user_role import UserRole


class User(db.Model, BaseEntity):
    __tablename__ = "users"
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    useremail = db.Column(db.String(100), unique=True, nullable=False, index=True)
    userpassword = db.Column(db.String(100), nullable=False)
    userdescription = db.Column(db.String(255), nullable=False)
    roles = db.relationship('UserRole', back_populates="rel_user", cascade='delete, delete-orphan')
    baskets = db.relationship('Basket', back_populates="user", cascade='all')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tmp_roles = []

    def add_role(self, role: Role):
        # était On^2
        existing = {ur.rel_role.rolename for ur in self.roles}

        if role.rolename in existing:
            return

        userrole = UserRole()
        userrole.rel_role = role
        userrole.rel_user = self
        self.roles.append(userrole)

    def get_roles(self):
        return [role.rel_role.rolename for role in self.roles]

    def remove_role(self, role: Role):
        userrole: UserRole
        for userrole in self.roles:
            if userrole.roleid == role.roleid:
                self.roles.remove(userrole)
                break

    def is_admin(self):
        return "ADMIN" in self.get_roles()
