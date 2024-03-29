from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates, relationship

from config import db, bcrypt


snippets_tags_join_table = db.Table('snippet_to_tag',
                                    db.Column("snippet_id", db.Integer, db.ForeignKey("snippet.id")),
                                    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
                                    )

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    # _password_hash = db.Column(db.String)

    snippets = db.relationship("Snippet", backref='user')

    @validates('username')
    def validate_username(self, key, username):
        username_exists = db.session.query(User).filter(User.username == username).first()
        if not username:
            raise ValueError("username field is required")
        if username_exists:
            raise ValueError("username must be unique")
        elif key == 'username':
            if len(username) >= 100:
                raise ValueError("username must be 100 characters or less")
        return username
    
    @validates('email')
    def validate_username(self, key, email):
        email_exists = db.session.query(User).filter(User.email == email).first()
        if not email:
            raise ValueError("email field is required")
        if email_exists:
            raise ValueError("email must be unique")
        if "@" not in email: 
            raise ValueError("failed simplified email validation")
        elif key == 'email':
            if len(email) >= 100:
                raise ValueError("email must be 100 characters or less")
        return email
    
    # from wtforms.validators import InputRequired, Email
    # Validate email here. https://wtforms.readthedocs.io/en/2.3.x/validators/ 
    
    @validates('first_name')
    def validate_username(self, key, first_name):
        if not first_name:
            raise ValueError("first_name field is required")
        elif key == 'first_name':
            if len(first_name) >= 100:
                raise ValueError("first_name must be 100 characters or less")
        return first_name
    
    @validates('last_name')
    def validate_username(self, key, last_name):
        if not last_name:
            raise ValueError("last_name field is required")
        elif key == 'last_name':
            if len(last_name) >= 100:
                raise ValueError("last_name must be 100 characters or less")
        return last_name

    @hybrid_property # Restrict access to the password hash.
    def password_hash(self):
        raise Exception("Password hashes may not be viewed.")

    @password_hash.setter # Generate a Bcrypt password hash and set it to the _password_hash attribute
    def password_hash(self, password):
        bcrypt_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        self._password_hash = bcrypt_hash

    def authenticate(self, password): # Check if the provided password matches the one stored in the db
        return bcrypt.check_password_hash(self._password_hash, password)

    def __repr__(self):
        return f"User {self.username}"

class Snippet(db.Model):
    __tablename__ = "snippet"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)
    language_select = db.Column(db.String)
    code = db.Column(db.String(500), nullable=False)
    explanation = db.Column(db.String(1000))

    # Associates snippet with user in one to many relationship 
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

    # Assocaites tag 
    tag = db.relationship('Tag', secondary=snippets_tags_join_table, backref="snippet")



    @validates('title')
    def validate_title(self, key, title):
        title_exists = db.session.query(Snippet).filter(Snippet.title == title).first()
        if not title:
            raise ValueError("title field is required")
        if title_exists:
            raise ValueError("title must be unique")
        elif key == 'title':
            if len(title) >= 50:
                raise ValueError("title must be 50 characters or less")
        return title 
    
    @validates("code")
    def validate_code(self, key, code):
        if not code:
            raise ValueError("code field is required")
        elif key == 'code':
            if len(code) >= 500:
                raise ValueError("code must be 500 characters or less")
        return code 
    
    @validates("explanation")
    def validate_explanation(self, key, explanation):
        if not explanation: 
            raise ValueError("explanation field is required")
        elif key == 'explanation':
            if len(explanation) >= 1000:
                raise ValueError("explanation must be 1000 characters or less")
        return explanation 
        
class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String)
    # snippets = db.relationship('Tag', backref='tag')


