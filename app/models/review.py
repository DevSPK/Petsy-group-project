from .db import db, environment, SCHEMA
from .user import User
from .product import Product
from datetime import datetime


class Review(db.Model):
    __tablename__ = 'reviews'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id))
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.today())

    user = db.relationship('User', back_populates='reviews', cascade="all, delete-orphan")
    product = db.relationship('Product', back_populates='reviews', cascade="all, delete-orphan")
    review_images = db.relationship('ReviewImage', back_populates='review_images')
