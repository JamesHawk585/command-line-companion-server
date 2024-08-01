from flask_restful import Resource
from flask_marshmallow import Marshmallow, fields
from flask import make_response, jsonify, request, Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import fields
import ipdb
from marshmallow_sqlalchemy import SQLAlchemySchema
from sqlalchemy_serializer import SerializerMixin
from flask_cors import CORS, cross_origin
from flask_session import Session
from config import app, db, api, ma
from sqlalchemy.exc import IntegrityError
from builtins import ValueError


# This line will run the config.py file and initialize our app
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
    _password_hash = ma.auto_field(load_only=True)

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
    tag = ma.auto_field()
    language_select = ma.auto_field()
    code = ma.auto_field()
    explanation = ma.auto_field()
    user_id = ma.auto_field()

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


@app.route("/cookies", methods=["GET"])
def cookies():
    resp = make_response({"message": "Hit cookies route!"}, 200)
    resp.set_cookie("hello", "world")
    return resp


@app.route("/")
def index():
    resp = make_response({"cli-companion": "Home route hit!"}, 200)
    resp.set_cookie("CLI-Companion")

    return resp


class Authentication(Resource):
    def get(self):
        user = User.query.filter(User.username == session.get("username")).first()
        if user:
            print(user.to_dict())
            return user.to_dict(), 200
        else:
            return {"errors": ["unauthorized"]}, 401


api.add_resource(Authentication, "/authorized")


def check_for_missing_values(data):
    errors = []
    for key, value in data.items():
        if not value:
            errors.append(f"{key} is required")
    return errors


class Users(Resource):
    def get(self):
        users_list = [u.to_dict() for u in User.query.all()]
        resp = make_response(users_list, 200)

        print(session)

        return resp


api.add_resource(Users, "/users")


@app.route("/users/<int:id>", methods=["GET", "PATCH", "DELETE"])
def user_by_id(id):
    user = User.query.filter_by(id=id).first()
    if request.method == "GET":
        response = make_response(user_schema.dump(user), 200)
        return response 
    
    elif request.method == "PATCH":
        for attr in request.get_json():
            setattr(user, attr, request.get_json()[attr])
        
        db.session.add(user)
        db.session.commit()

        return make_response(user_schema.dump(user), 200)

    elif request.method == "DELETE":
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()


# Build out the backend infastructure to patch the user object here. 
# Update SecureSessionCookie
# Should we be returning the password hash in the SecureSessionCookie?




















class Signup(Resource):
    def post(self):
        data = request.get_json()


        print("data", data)

        errors = []
        if data['password'] != data['password_confirmation']:
            errors.append("Password confirmation failed")
            return {'errors': errors}, 400
        
        required_keys = [
            "username",
            "password",
            "password_confirmation",
            "email",
            "first_name",
            "last_name",
        ]

        for key in required_keys:
            if not data[key]:
                errors.append(f"{key} is required")

        if errors: 
            return {'errors': errors}, 400

        user = User(
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
        )

        session["username"] = user.username
        print(session)

        user.password_hash = data["password"]

        try:
            session["username"] = user.username
            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id

            return user.to_dict(), 201
        except IntegrityError as e:
            # Handle IntegrityError
            for error in e.orig.args:
                errors.append(str(error))
            return {'errors': errors}, 422
        except ValueError as value_error:
            # Handle ValueError
            for error in value_error.orig.args:
                errors.append(str(error))
            return {'errors': errors}, 422
        
api.add_resource(Signup, "/signup")


class Login(Resource):
    def post(self):
        username = request.get_json()["username"]
        password = request.get_json()["password"]

        if not username or not password:
            return {"errors": ["username and password are required"]}, 400

        user = User.query.filter(User.username == username).first()
        # user = User.query.filter(User.id == session.get("user_id")).first()

        if not user:
            return {"errors": ["username or password is incorrect"]}, 404

        if user.authenticate(password):
            print("user in Login route", user)
            session["user_id"] = user.id
            session["username"] = username
            print("session inside user.authenticate(password)", session)
            return user.to_dict(), 200
        else: 
            return {"errors": ["username or password is incorrect"]}, 401
    
api.add_resource(Login, "/login")


@app.route("/logout", methods=["DELETE"])
def logout():
    session["user_id"] = None
    session["username"] = None
    print(session)
    return {}, 204


@app.route("/snippets", methods=["GET", "POST"])
def snippets():

    # ipdb.set_trace()
    if request.method == "GET":

        snippets = Snippet.query.filter(Snippet.user_id == session.get("user_id"))


        response = make_response(snippets_schema.dump(snippets), 200)
        return response

    elif request.method == "POST":
        json_dict = request.get_json()

        user = User.query.filter(User.id == session.get("user_id")).first()

        snippet = Snippet(
            title=json_dict["title"],
            language_select=json_dict["language_select"],
            code=json_dict["code"],
            explanation=json_dict["explanation"],
            user_id=user.id
        )

        print(snippet)

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
