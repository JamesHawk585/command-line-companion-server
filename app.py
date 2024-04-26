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



# This method checks if a user in the db has an id that matches the 
# 'user_id' value in the session object. It is currently returning null. 

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    # import ipdb; ipdb.set_trace()
    user = User.query.filter(User.username == data["username"]).first()

    session["user_id"] = user.id


    return user.to_dict(), 201

# UYsing a restful route seems to have eleminated the CORS error, but there is still no session to validate the db user id against. 

class Authentication(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get("user_id")).first()
        if user: 
            print(user.to_dict())
            return user.to_dict(), 200
        else: 
            return {"errors": ["unauthorized"]}, 401
        
    
api.add_resource(Authentication, "/authorized")

@app.route("/logout", methods=["DELETE"])
def logout():
    session['user_id'] = None
    print(session)
    return {}, 204

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    new_user = User(email=data["email"], first_name=data["first_name"], last_name=data["last_name"], username=data["username"])
    # new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id
    return jsonify({"message": "User created successfully"}), 201


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