from email.mime import base

from flask import session

from app import db
from app.dtos.basket_dto import BasketDTO
from app.forms.basket.basket_add_item_form import BasketAddItemForm
from app.mappers.basket_mapper import BasketMapper
from app.models.basket import Basket
from app.models.basket_item import BasketItem
from app.models.item import Item
from app.models.user import User
from app.services.base_service import BaseService

from sqlalchemy import func


class BasketService(BaseService):
    def find_all(self):
        return [BasketDTO.build_from_entity(basket) for basket in Basket.query.all()]

    def find_one(self, entity_id: int):
        return BasketDTO.build_from_entity(Basket.query.filter_by(basketid=entity_id).one())

    def find_one_by(self, **kwargs):
        basket = Basket.query.filter_by(**kwargs).one()
        return BasketDTO.build_from_entity(basket)

    def order_report(self):
        rows = (
            db.session.query(
                Basket.basketid,
                User.username,
                User.useremail,
                func.coalesce(func.sum(Item.itemprice * BasketItem.itemquantity), 0),
                func.count(BasketItem.itemid)
            )
            .join(User, User.userid == BasketItem.userid)
            .outerjoin(BasketItem, BasketItem.basketid == Basket.basketid)
            .outerjoin(Item, Item.itemid == BasketItem.itemid)
            .filter(Basket.basketclosed.is_(True))
            .group_by(Basket.basketid, User.username, User.useremail)
        )

        return [
            {
                'basketid': basket.basketid,
                'username': user.username,
                'useremail': user.useremail,
                'total': total,
                'itemcount': cnt
            } for (basket, user, total, cnt) in rows
        ]

        # report = []
        # baskets = Basket.query.filter_by(basketclosed=True).all()
        # for basket in baskets:
        #     user = User.query.filter_by(userid=basket.userid).first()
        #     total = 0.0
        #     for basket_item in basket.items:
        #         total += basket_item.item.itemprice * basket_item.itemquantity
        #     report.append({
        #         'basketid': basket.basketid,
        #         'username': user.username,
        #         'useremail': user.useremail,
        #         'total': total,
        #         'itemcount': len(basket.items)
        #     })

        # return report

    def insert(self, data):
        basket = Basket()
        BasketMapper.form_to_entity(data, basket)

        try:
            db.session.add(basket)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()

        return self.find_one(basket.basketid)

    def update(self, entity_id: int, data):
        basket = Basket.query.filter_by(basketid=entity_id).one()
        if basket is None:
            return None

        BasketMapper.form_to_entity(data, basket)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()

        return self.find_one(entity_id)

    def delete(self, entity_id: int):
        basket = Basket.query.filter_by(basketid=entity_id).one()
        if basket is None:
            return None

        try:
            db.session.delete(basket)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()

        return basket.basketid

    def add_item(self, form: BasketAddItemForm):
        userid = session.get('userid')
        item = Item.query.filter_by(itemid=int(form.itemid.data)).one()
        basket = Basket.query.filter_by(userid=userid, basketclosed=False).first()

        if basket is None:
            basket = Basket()
            basket.user = User.query.filter_by(userid=userid).one()
            db.session.add(basket)

        basket_item, exist = basket.add_item(item, int(form.itemquantity.data))
        if not exist:
            db.session.add(basket_item)

        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return None

        return basket

    def remove_item(self, itemid):
        userid = session.get('userid')
        item = Item.query.filter_by(itemid=itemid).one()
        basket = Basket.query.filter_by(userid=userid, basketclosed=False).first()

        if basket is None:
            return None

        try:
            basket.remove_item(item)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()

    def checkout_basket(self):
        userid = session.get('userid')
        basket = Basket.query.filter_by(userid=userid, basketclosed=False).first()

        if basket is None:
            return None

        # forcer le typage
        bi: BasketItem
        for bi in basket.items:
            if bi.itemquantity > bi.item.itemstock:
                db.session.rollback()
                raise ValueError("stock insufficient")

            bi.item.itemquantity -= bi.itemquantity

        basket.basketclosed = True

        new_basket = Basket()
        new_basket.user = User.query.filter_by(userid=userid).one()
        db.session.add(new_basket)
        db.session.commit()
