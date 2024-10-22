
from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Article, User  # Ensure these models are defined

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

# Resource to clear session data
class ClearSession(Resource):
    def delete(self):
        session.clear()  # Clear all session data
        return {}, 204

# Resource to return all articles
class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

# Resource to show a specific article, with session-based page view tracking
class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = session.get('page_views', 0) + 1

        if session['page_views'] <= 3:
            article = Article.query.get(id)
            if article:
                return make_response(article.to_dict(), 200)
            else:
                return {'message': 'Article not found'}, 404
        else:
            return {'message': 'Maximum pageview limit reached'}, 401

# Resource to handle user login
class Login(Resource):
    def post(self):
        data = request.get_json() if request.is_json else request.form
        username = data.get("username")
        user = User.query.filter_by(username=username).first()
        if not user:
            return make_response({"message": "User not found"}, 404)
        session["user_id"] = user.id
        return make_response(user.to_dict(), 200)

# Resource to handle user logout
class Logout(Resource):
    def delete(self):
        session.clear()  # Clear all session data
        return make_response({"message": "Logged out"}, 204)

# Resource to check the current session
class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            return make_response(user.to_dict(), 200)
        return make_response({}, 401)

# Adding resources to API
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
