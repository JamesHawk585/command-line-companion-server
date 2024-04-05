from flask import request, session
from flask_restful import Resource
from flask_marshmallow import Marshmallow, fields
from flask import make_response, jsonify, request, session, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import fields
import ipdb
from marshmallow_sqlalchemy import SQLAlchemySchema
from sqlalchemy_serializer import SerializerMixin


# migrate = Migrate(app, db)

from config import (
    app,
    db,
    api,
    ma,
)  # This line will run the config.py file and initialize our app
from models import User, Snippet, Tag


class UserSchema(ma.SQLAlchemySchema):
    id = fields.Int(dump_only=True)

    class Meta:
        model = User

    # id = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()
    first_name = ma.auto_field()
    last_name = ma.auto_field()
    # _password_hash = ma.auto_field(load_only=True)

    url = ma.Hyperlinks(
        {
            "self": ma.URLFor("user_by_id", values=dict(id="<id>")),
            "collection": ma.URLFor("users"),
        }
    )


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class SnippetSchema(ma.SQLAlchemySchema):
    id = fields.Int(dump_only=True)

    class Meta:
        model = Snippet

    title = ma.auto_field()
    # tags = ma.auto_field()
    language_select = ma.auto_field()
    code = ma.auto_field()
    explanation = ma.auto_field()

    url = ma.Hyperlinks(
        {
            "self": ma.URLFor("snippet_by_id", values=dict(id="<id>")),
            "collection": ma.URLFor("snippets"),
        }
    )


snippet_schema = SnippetSchema()
snippets_schema = SnippetSchema(many=True)


class TagSchema(ma.SQLAlchemySchema):
    id = fields.Int(dump_only=True)

    class Meta:
        model = Tag

    tag = ma.auto_field()

    url = ma.Hyperlinks(
        {
            "self": ma.URLFor("tag_by_id", values=dict(id="<id>")),
            "collection": ma.URLFor("tags"),
        }
    )


tag_schema = TagSchema()
tags_schema = TagSchema(many=True)


@app.route("/")
def index():
    return "<h1>CLI-Companion</h1>"

        # User object has no 'name' attribute. Must use either username, or email. Email must be unique if used. 
        # Will user = User.query.filter(User.id == data.id).first() work? Will React assign a different id to the object on the front-end than the object's server-side id?
        #  How to test?  


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    # Validations: Must have username and password!
    user = User.query.filter(User.id == data["id"]).first()

    # Is the user authenticated?

    session["user_id"] = user.id
    return user.to_dict(), 201

class Users(Resource):
    def get(self):
        users_list = [u.to_dict() for u in User.query.all()]
        response = make_response(
        users_list,
        200,
    )

        return response


    def post(self):
    # Declare data variable and set equal to the request body. Calling the get_json() method on the request body will serialize the request into json. 
        data = request.get_json()

    # Declare a user variable set as eaqual to a new sintance of the user class. Each attribute of the new user object will be populated with the corresponding attribute in the body of the request, which has been serialized into json. 
        user = User(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            username=data["username"]
        )

    # Add new user object to the sessiona and commit.  

        db.session.add(user)
        db.session.commit()

        # Declare a session id for the user. Set it equal to the new user objetcs id attribute. 

        session["user_id"] = user.id

        return user.to_dict(), 201
    
api.add_resource(Users, "/signup")


@app.route("/users/<int:id>", methods=["GET", "PATCH", "DELETE"])
def user_by_id(id):
    user = User.query.filter_by(id=id).first()
    if request.method == "GET":

        response = make_response(user_schema.dump(user), 200)
        return response

    elif request.method == "PATCH":
        for attr in request.get_json():
            # ipdb.set_trace()
            setattr(user, attr, request.get_json()[attr])

        db.session.add(user)
        db.session.commit()

        return make_response(user_schema.dump(user), 200)

    elif request.method == "DELETE":
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()

        return make_response(user_schema.dump(user), 200)


@app.route("/snippets", methods=["GET", "POST"])
def snippets():
    # ipdb.set_trace()
    if request.method == "GET":

        snippets = Snippet.query.all()

        response = make_response(snippets_schema.dump(snippets), 200)
        return response

    elif request.method == "POST":
        json_dict = request.get_json()

        snippet = Snippet(
            title=json_dict["title"],
            language_select=json_dict["language_select"],
            code=json_dict["code"],
            explanation=json_dict["explanation"],
        )

        db.session.add(snippet)
        db.session.commit()

        response = make_response(snippet_schema.dump(snippet), 201)

        return response


@app.route("/snippets/<int:id>", methods=["GET", "PATCH", "DELETE"])
def snippet_by_id(id):
    snippet = Snippet.query.filter_by(id=id).first()
    if request.method == "GET":

        response = make_response(snippet_schema.dump(snippet), 200)
        return response

    elif request.method == "PATCH":
        for attr in request.get_json():
            # ipdb.set_trace()
            setattr(snippet, attr, request.get_json()[attr])

        db.session.add(snippet)
        db.session.commit()

        return make_response(snippet_schema.dump(snippet), 200)

    elif request.method == "DELETE":
        snippet = Snippet.query.filter_by(id=id).first()
        db.session.delete(snippet)
        db.session.commit()

        return make_response(snippet_schema.dump(snippet), 200)


@app.route("/tags", methods=["GET", "POST"])
def tags():
    # ipdb.set_trace()
    if request.method == "GET":

        tags = Tag.query.all()

        response = make_response(tags_schema.dump(tags), 200)
        return response

    elif request.method == "POST":
        json_dict = request.get_json()

        tag = Tag(tag=json_dict["tag"])

        db.session.add(tag)
        db.session.commit()

        response = make_response(tag_schema.dump(tag), 201)

        return response


@app.route("/tags/<int:id>", methods=["GET", "PATCH", "DELETE"])
def tag_by_id(id):
    tag = Tag.query.filter_by(id=id).first()
    if request.method == "GET":

        response = make_response(tag_schema.dump(tag), 200)
        return response

    elif request.method == "PATCH":
        for attr in request.get_json():
            # ipdb.set_trace()
            setattr(tag, attr, request.get_json()[attr])

            db.session.add(tag)
            db.session.commit()

            return make_response(tag_schema.dump(tag), 200)

    elif request.method == "DELETE":
        tag = Tag.query.filter_by(id=id).first()
        db.session.delete(tag)
        db.session.commit()

        return make_response(tag_schema.dump(tag), 200)


# Snippets and tags routes here

if __name__ == "__main__":
    app.run(port=4000, debug=True)
