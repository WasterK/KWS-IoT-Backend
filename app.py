# Python standard libraries
import json
import os

from Database_Access import DatabaseAccess  # Import your DatabaseAccess class

# Instantiate DatabaseAccess with your PostgreSQL database URL
DATABASE_URL= os.environ.get('DATABASE_URL')
from user import User

# Third-party libraries
from flask import Flask, redirect, request, url_for, jsonify
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

from flask_cors import CORS

# Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = os.environ.get('GOOGLE_DISCOVERY_URL')

# Flask app setup
app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
login_manager = LoginManager()
login_manager.init_app(app)


# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/")
def index():
    # print(f'current user: {current_user}')
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/login", methods=['GET'])
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    db = DatabaseAccess(DATABASE_URL)
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]

        if not db.isUsernameExists(users_email):
            # Create a new user in the database
            db.create_new_user(users_name, unique_id, users_email, picture)
        else:
            # Update user information if necessary
            # Note: You might want to implement an update method in your database access class
            pass  # Placeholder for updating user information

    else:
        return "User email not available or not verified by Google.", 400

    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    login_user(user)

    devices = db.get_all_devices(unique_id)

    user_data = {"data":{
            'name': users_name,
            'email': users_email,
            'picture': picture,
            'unique_id': unique_id
            # Add more user data as needed
        }}
    # Encode user data as query parameters
    query_params = "&".join([f'{key}={value}' for key, value in user_data.items()])

    # Hardcoded redirect URL with user data as query parameters
    redirect_url = 'https://localhost:4200/dashboard' + f'?{query_params}'

    # Redirect back to Angular app with user data as query parameters
    return redirect(redirect_url)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/get-all-devices/<int:userId>", methods=['GET'])
def get_all_devices(userId):
    # print(f'user id {userId} type: {type(userId)}')
    db = DatabaseAccess(DATABASE_URL)
    # Assuming db.get_all_devices(userId) returns data from the database
    allDeviceData = db.get_all_devices(userId)
    # print(allDeviceData)
    # Check if data is successfully retrieved
    if allDeviceData != -1:
        return jsonify({'body': allDeviceData}), 200
    else:
        return jsonify({'error': 'Data not found'}), 404

@app.route('/add-new-device', methods=['POST'])
def add_new_device():
    data = request.get_json()
    print(data)
    deviceName = data.get('device_name')
    deviceUrl = data.get('device_url')
    userId = data.get('user_id')
    db = DatabaseAccess(DATABASE_URL)
    status = db.create_new_device(deviceName, deviceUrl, userId)
    if status == -1:
        pass
    return jsonify({'msg': "Login successful!", "status": "success"}), 200

if __name__ == "__main__":
    app.run(debug=True, ssl_context=("cert.pem", "key.pem"))


