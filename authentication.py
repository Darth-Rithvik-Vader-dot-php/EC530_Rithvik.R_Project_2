from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS  # Import CORS
from datetime import datetime, timezone


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Configure MongoDB Atlas connection
# Ensure to replace <username>, <password>, and cluster0.xxxxx with your actual MongoDB Atlas details
app.config["MONGO_URI"] = "mongodb+srv://visaaln2:visaal456@ec530.qevqtrc.mongodb.net/healthmonitoring?retryWrites=true&w=majority"
mongo = PyMongo(app)



@app.route('/register', methods=['POST'])
def register():
    data = request.json
    # Check for the presence of required fields in the input data
    if not all(key in data for key in ['username', 'email', 'password', 'role', 'firstName', 'lastName', 'dateOfBirth']):
        return jsonify({'message': 'Missing required user information'}), 400

    # Check if the user already exists in either the authentication or users collection
    authentication_collection = mongo.db.authentication
    users_collection = mongo.db.users
    existing_user_auth = authentication_collection.find_one({'username': data['username']})
    existing_user_users = users_collection.find_one({'personalInfo.email': data['email']})

    if existing_user_auth or existing_user_users:
        return jsonify({'message': 'User already exists'}), 409

    # Hash the user's password for secure storage
    hashed_password = generate_password_hash(data['password'])
    date_of_birth = datetime.strptime(data['dateOfBirth'], '%Y-%m-%d')

    # Create and insert the user document into the users collection
    user_doc = {
        "personalInfo": {
            "firstName": data['firstName'],
            "lastName": data['lastName'],
            "email": data['email'],
            "dateOfBirth": date_of_birth,
            # Include other relevant personal information here
        },
        "roles": [data['role']],
        "status": "active",
        "registrationDate": datetime.now(timezone.utc)
    }
    user_id = users_collection.insert_one(user_doc).inserted_id

    # Create and insert the authentication document into the authentication collection
    auth_doc = {
        "username": data['username'],
        "password": hashed_password,
        "userId": user_id  # Link this authentication document to the user document
    }
    authentication_collection.insert_one(auth_doc)

    return jsonify({'message': 'User registered successfully', 'user_id': str(user_id)}), 201



# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    print("login requested")
    data = request.json
    print(data)
    authentication_collection = mongo.db.authentication
    user = authentication_collection.find_one({'username': data['username']})

    if user and check_password_hash(user['password'], data['password']):
        # Implement JWT token generation here for authenticated user
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

# Placeholder for logout - Implement token revocation or expiration handling
@app.route('/logout', methods=['POST'])
def logout():
    # Logic to handle logout, e.g., token blacklist or expiry
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/')
def hello_world():
    print("test")
    return "helloworld"

if __name__ == '__main__':
    app.run(debug=True)
