from flask import Flask, jsonify, request
from config import config
from models import db, User
import redis

# Create a Redis client
redis_client = redis.Redis()

# Define a caching decorator
def cache_response(timeout=300):
    def decorator(view_func):
        def wrapper(*args, **kwargs):
            # Generate a cache key based on the request URL
            cache_key = f'api:{request.url}'

            # Check if the response is already cached
            response = redis_client.get(cache_key)
            if response is not None:
                return jsonify(response.decode())

            # Execute the view function and cache the response
            result = view_func(*args, **kwargs)
            redis_client.setex(cache_key, timeout, jsonify(result).encode())

            return result

        return wrapper

    return decorator

def create_app(environment):
    app = Flask(__name__)
    app.config.from_object(environment)
    
    with app.app_context():
        db.init_app(app)
        db.create_all()
        
    return app

environment = config['development']
app = create_app(environment)

@app.route('/api/users', methods=['GET'])
@cache_response(timeout=3600)
def get_users():
    users = [user.json() for user in User.query.all()]
    return jsonify({'users': users})

@app.route('/api/users/<id>', methods=['GET'])
@cache_response(timeout=3600)
def get_user(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        return jsonify({'message': 'User does not exist'}), 404

    return jsonify({'user': user.json()})

@app.route('/api/users/', methods=['POST'])
def create_user():
    json = request.get_json(force=True)
    
    if json.get('username') is None:
        return jsonify({'message': 'Bad Request'}), 400
    
    user = User(username=json['username'])
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'success'})

@app.route('/api/users/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        return jsonify({'message': 'User does not exist'}), 404

    json = request.get_json(force=True)
    if json.get('username') is None:
        return jsonify({'message': 'Bad request'}), 400

    user.username = json['username']
    db.session.commit()

    return jsonify({'user': user.json()})

@app.route('/api/users/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        return jsonify({'message': 'User does not exist'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'user': user.json()})

if __name__ == '__main__':
    app.run(debug=True)
