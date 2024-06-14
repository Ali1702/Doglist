from flask import Flask, request, jsonify, redirect, url_for, render_template_string
from flask_cors import CORS
import mysql.connector
from keycloak import KeycloakOpenID, KeycloakGetError
from functools import wraps
import os

app = Flask(__name__)
CORS(app)

app.config.from_object('config.Config')

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
public_keycloak_url = os.getenv('PUBLIC_KEYCLOAK_URL', 'http://localhost:5000/')

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
            keycloak_openid.userinfo(token)
        except KeycloakGetError as e:
            if e.response_code == 401:
                return jsonify({'message': 'Token is invalid or expired!'}), 401
            else:
                return jsonify({'message': 'Internal server error'}), 500
        return f(*args, **kwargs)
    return decorated

@app.route('/login')
def login():
    redirect_uri = url_for('callback', _external=True)
    redirect_uri = redirect_uri.replace(request.host_url, public_keycloak_url)
    auth_url = keycloak_openid.auth_url(redirect_uri=redirect_uri)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    redirect_uri = url_for('callback', _external=True)
    redirect_uri = redirect_uri.replace(request.host_url, public_keycloak_url)
    token = keycloak_openid.token(code=code, redirect_uri=redirect_uri, session_state = request.args.get('session_state'), grant_type='authorization_code')
    tokens['token'] = token['access_token']
    next_url = request.args.get('next')
    return redirect(url_for(next_url) if next_url else url_for('home'))

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

@app.route('/', methods=['GET'])
def home():
    if not tokens.get('token'):
        return redirect(url_for('login', next='home'))
    home_page_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Doglist API</title>
    </head>
    <body>
        <h1>Welcome to the Doglist API!</h1>
        <button onclick="location.href='{{ url_for('list_dogs') }}'">See the Doglist</button>
        <button onclick="location.href='/add-dog-form'">Add a Dog</button>
    </body>
    </html>
    '''
    return render_template_string(home_page_html)

@app.route('/add-dog-form', methods=['GET'])
@token_required
def add_dog_form():
    add_dog_form_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add a Dog</title>
    </head>
    <body>
        <h1>Add a Dog</h1>
        <form action="{{ url_for('add_dog') }}" method="post">
            <label for="name">Name:</label>
            <input type="text" id="name" name="name"><br><br>
            <label for="breed">Breed:</label>
            <input type="text" id="breed" name="breed"><br><br>
            <input type="submit" value="Add Dog">
        </form>
    </body>
    </html>
    '''
    return render_template_string(add_dog_form_html)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development', host='0.0.0.0')
