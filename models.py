from flask_login import UserMixin
import qrcode
from datetime import datetime
from io import BytesIO
from flask import url_for
from PIL import Image
import os
from datetime import datetime
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    contact_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    dogs = db.relationship('Dog', backref='owner', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
class Dog(db.Model):
    __tablename__ = 'dogs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100))
    age = db.Column(db.Integer)
    color = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    photo = db.Column(db.String(255))
    qr_code = db.Column(db.String(255))
    is_lost = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)

    def generate_qr(self):
        """Generate a QR code that links to the dog's public profile"""
        qr_data = f"https://yourapp.com/dog/{self.id}"
        qr_img = qrcode.make(qr_data)
        qr_path = os.path.join('static/qr_codes', f"dog_{self.id}.png")
        qr_img.save(qr_path)
        self.qr_code = qr_path
        return qr_path
    
class Vaccine(db.Model):
    __tablename__ = 'vaccines'
    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(db.Integer, db.ForeignKey('dogs.id'), nullable=False)
    vaccine_name = db.Column(db.String(100), nullable=False)
    date_administered = db.Column(db.Date)
    next_due_date = db.Column(db.Date)
    certificate = db.Column(db.String(255))
    notes = db.Column(db.String(300))

    dog = db.relationship('Dog', backref='vaccines', lazy=True)

    class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.message}>'
