from models import User, Snippet, Tag
from flask import Flask
from config import db, app, bcrypt
from faker import Faker

fake = Faker()

print('Seeding db... 🌱')

with app.app_context():
    User.query.delete()
    Snippet.query.delete()
    Tag.query.delete()

    usernames = []

    print('Creating users...👽 ')

    for i in range(3):
        username = fake.first_name()
        while username in usernames:
            username = fake.first_name()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()

        usernames.append(username)

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        user.password_hash = user.username + 'password'

        # Add each user individually and commit
        db.session.add(user)
        db.session.commit()
