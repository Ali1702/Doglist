import logging
import os
import jwt
from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
import mysql.connector
from keycloak import KeycloakOpenID, KeycloakGetError
from functools import wraps

app = Flask(__name__)
CORS(app)

app.config.from_object('config.Config')

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Database configuration
db_config = {
    'user': os.getenv('DB_USER', 'maxscale_user'),
    'password': os.getenv('DB_PASSWORD', '12345678'),
    'host': os.getenv('DB_HOST', 'localhost'),  # Use localhost when using host network
    'port': os.getenv('DB_PORT', '4006'),
    'database': os.getenv('DB_NAME', 'dogs')
}

# Keycloak configuration
private_keycloak_url = os.getenv('PRIVATE_KEYCLOAK_URL', 'http://keycloak:8080/')
public_keycloak_url = os.getenv('PUBLIC_KEYCLOAK_URL', 'http://localhost:3000/')

keycloak_openid = KeycloakOpenID(
    server_url=private_keycloak_url,  # Private Keycloak address
    client_id=app.config['KEYCLOAK_CLIENT_ID'],
    realm_name=app.config['KEYCLOAK_REALM_NAME'],
    client_secret_key=app.config['KEYCLOAK_CLIENT_SECRET']
)

# In-memory store for tokens (since we're not using sessions)
tokens = {}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = tokens.get('token')
        if not token:
            return redirect(url_for('login', next=request.endpoint))
        try:
            # Decode the token to log the claims
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            logging.debug(f'Token claims: {decoded_token}')
            keycloak_openid.userinfo(token)
        except KeycloakGetError as e:
            logging.error(f'Keycloak error: {e}')
            if e.response_code == 401:
                return jsonify({'message': 'Token is invalid or expired!'}), 401
            else:
                return jsonify({'message': 'Internal server error'}), 500
        return f(*args, **kwargs)
    return decorated

@app.route('/login')
def login():
    redirect_uri = url_for('callback', _external=True)
    auth_url = keycloak_openid.auth_url(redirect_uri=redirect_uri, scope='openid email profile')
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    redirect_uri = url_for('callback', _external=True)
    logging.debug(f'Received code: {code}')
    try:
        token = keycloak_openid.token(code=code, redirect_uri=redirect_uri, session_state=request.args.get('session_state'), grant_type='authorization_code')
        logging.debug(f'Received token: {token}')
        access_token = token['access_token']
        next_url = request.args.get('next', '/')
        return redirect(f"http://localhost:3000?token={access_token}")
    except KeycloakGetError as e:
        logging.error(f'Error during token exchange: {e}')
        return jsonify({'message': 'Failed to obtain token from Keycloak'}), 500

@app.route('/dogs', methods=['GET'])
@token_required
def list_dogs():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM dogs")
    dogs = cursor.fetchall()
    connection.close()
    return jsonify(dogs), 200

@app.route('/dogs', methods=['POST'])
@token_required
def add_dog():
    dog_details = request.json
    name = dog_details['name']
    breed = dog_details['breed']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO dogs (name, breed) VALUES (%s, %s)", (name, breed))
    connection.commit()
    connection.close()
    return jsonify({'message': 'Dog added successfully!'}), 201

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development', host='0.0.0.0')
