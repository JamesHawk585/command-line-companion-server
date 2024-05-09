from models import User, Snippet, Tag
from flask import Flask
from config import db, app, bcrypt
from faker import Faker

fake = Faker()

print("Seeding db... 🌱")

with app.app_context():
    User.query.delete()
    Snippet.query.delete()
    Tag.query.delete()

    db.session.commit()
