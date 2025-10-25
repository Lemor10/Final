from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    contact_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    dogs = db.relationship('Dog', backref='owner', lazy=True)

class Dog(db.Model):
    __tablename__ = 'dogs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(50))
    color = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    photo_url = db.Column(db.String(200))
    qr_code = db.Column(db.String(200))
    is_lost = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    vaccines = db.relationship('Vaccine', backref='dog', lazy=True)

class Vaccine(db.Model):
    __tablename__ = 'vaccines'
    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(db.Integer, db.ForeignKey('dogs.id'), nullable=False)
    vaccine_name = db.Column(db.String(100), nullable=False)
    date_given = db.Column(db.Date, nullable=False)
    next_due_date = db.Column(db.Date)
    vet_name = db.Column(db.String(100))
    certificate_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
