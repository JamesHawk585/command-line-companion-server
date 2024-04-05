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

    usernames = []

    print("Creating users...👽 ")

    for i in range(3):
        username = fake.first_name()
        while username in usernames:
            username = fake.first_name()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()

        usernames.append(username)

        user = User(
            username=username, first_name=first_name, last_name=last_name, email=email
        )

        user.password_hash = user.username + "password"

        # Add each user individually and commit
        db.session.add(user)
        db.session.commit()

    snippets = []

    s1 = Snippet(
        title="Start JSON Server",
        language_select="Terminal Commands",
        code="json-server --watch db.json -p 5555",
        explanation="Starts json server on the specified port, 5555 in this case. ",
    )

    s2 = Snippet(
        title="Delete Object from Stateful Array",
        language_select="JavaScript",
        code="setSnippets(snippets.filter((snippet) => snippet.id !== snippetId));",
        explanation="calls the filter method on the snippets state-ful array of objects, compares each object with the specified snippetId, and creates a new array with each object whose id does not match snippetId. It then passes the new array into the setSnippets state method. Since it omits the curly braces, calling setSnippets is intended to take up only one line. ",
    )

    s3 = Snippet(
        title="Run Python Script",
        language_select="Python",
        code="python app.py",
        explanation='Runs a script on the command line. Replace "App" with the name of the file you want to run.',
    )

    s4 = Snippet(
        title="Python Format Method",
        language_select="Python",
        code='def role_call(self):    \n        return "This is {}. He is is {}".format(self.title, self.department)',
        explanation="This method uses placeholders {} in the string and replaces them with the values of self.title and self.department respectively. The .format() method is a powerful tool in Python for creating formatted strings by embedding variables and values into placeholders within a template string. It offers a flexible and versatile way to construct textual output for various applications.",
    )

    s5 = Snippet(
        title="Print Secret Key",
        language_select="Python",
        code="python -c 'import os; print(os.urandom(16))'",
        explanation="To generate random bytes in Python for cryptographic use, you can use the os.urandom() method. This method returns a string representing random bytes suitable for cryptographic purposes. The size parameter determines the number of random bytes to generate.\n\n\nEach time you run this code, a different set of random bytes will be output. \n\nWhen working with the output of os.urandom(), it's important to understand that the result is in bytes format. You can manipulate these bytes further for cryptographic operations or convert them into a different format as needed.",
    )

    snippets.append(s1)
    snippets.append(s2)
    snippets.append(s3)
    snippets.append(s4)
    snippets.append(s5)

    db.session.add_all(snippets)
    db.session.commit()
