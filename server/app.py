from flask import request, session, jsonify, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models import User, Recipe
from config import db, bcrypt

class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_user = User(
                username=data['username'],
                password_hash=data['password'],  # Password setter will hash it
                image_url=data.get('image_url', ''),
                bio=data.get('bio', '')
            )
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return make_response(
                jsonify({
                    "id": new_user.id,
                    "username": new_user.username,
                    "image_url": new_user.image_url,
                    "bio": new_user.bio
                }),
                201
            )
        except IntegrityError:
            db.session.rollback()
            return make_response(
                jsonify({"error": ["Username already exists."]}),
                422
            )
        except KeyError as e:
            return make_response(
                jsonify({"error": [f"Missing required field: {str(e)}"]}),
                422
            )


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            return make_response(
                jsonify({
                    "id": user.id,
                    "username": user.username,
                    "image_url": user.image_url,
                    "bio": user.bio
                }),
                200
            )
        return make_response(
            jsonify({"error": "Unauthorized"}),
            401
        )


class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        if user and user.authenticate(data.get('password')):
            session['user_id'] = user.id
            return make_response(
                jsonify({
                    "id": user.id,
                    "username": user.username,
                    "image_url": user.image_url,
                    "bio": user.bio
                }),
                200
            )
        return make_response(
            jsonify({"error": "Invalid username or password"}),
            401
        )


class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id')
            return make_response('', 204)
        return make_response(
            jsonify({"error": "Unauthorized"}),
            401
        )


class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            recipes = Recipe.query.all()
            recipe_data = [
                {
                    "id": recipe.id,
                    "title": recipe.title,
                    "instructions": recipe.instructions,
                    "minutes_to_complete": recipe.minutes_to_complete,
                    "user": {
                        "id": recipe.user.id,
                        "username": recipe.user.username,
                        "image_url": recipe.user.image_url,
                        "bio": recipe.user.bio
                    }
                } for recipe in recipes
            ]
            return make_response(jsonify(recipe_data), 200)
        return make_response(
            jsonify({"error": "Unauthorized"}),
            401
        )

    def post(self):
        user_id = session.get('user_id')
        if user_id:
            data = request.get_json()
            try:
                new_recipe = Recipe(
                    title=data['title'],
                    instructions=data['instructions'],
                    minutes_to_complete=data.get('minutes_to_complete'),
                    user_id=user_id
                )
                db.session.add(new_recipe)
                db.session.commit()
                return make_response(
                    jsonify({
                        "id": new_recipe.id,
                        "title": new_recipe.title,
                        "instructions": new_recipe.instructions,
                        "minutes_to_complete": new_recipe.minutes_to_complete,
                        "user": {
                            "id": new_recipe.user.id,
                            "username": new_recipe.user.username,
                            "image_url": new_recipe.user.image_url,
                            "bio": new_recipe.user.bio
                        }
                    }),
                    201
                )
            except KeyError as e:
                return make_response(
                    jsonify({"error": [f"Missing required field: {str(e)}"]}),
                    422
                )
        return make_response(
            jsonify({"error": "Unauthorized"}),
            401
        )


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')
