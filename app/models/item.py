from app import db
from app.models.base_entity import BaseEntity


class Item(BaseEntity, db.Model):
    __tablename__ = "items"
    itemid = db.Column(db.Integer, primary_key=True)
    itemname = db.Column(db.String(255), nullable=False, index=True, unique=True)
    itemdescription = db.Column(db.Text, nullable=False)
    itemstock = db.Column(db.Integer, nullable=False, default=1)
    # Le db float va autorisé des entrée comme 1.236874102540014
    # itemprice = db.Column(db.Float, nullable=False, default=0.0)
    itemprice = db.Column(db.Numeric(10,2), nullable=False, default=0.0)
