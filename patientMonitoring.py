from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from bson.errors import InvalidId

from datetime import datetime
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://visaaln2:visaal456@ec530.qevqtrc.mongodb.net/healthmonitoring?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Helper to parse ObjectId and datetime to string
def custom_json_encoder(data):
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, datetime):
        return data.isoformat()
    raise TypeError(f"Type {type(data)} not serializable")

# Helper to jsonify with custom encoder
def jsonify_custom(data):
    return json.loads(json.dumps(data, default=custom_json_encoder))

@app.route('/patients/<patientId>/measurements', methods=['GET'])
def get_patient_measurements(patientId):
    try:
        measurements = mongo.db.patientMeasurements.find({"patientId": ObjectId(patientId)})
        return jsonify(jsonify_custom(list(measurements))), 200
    except InvalidId:
        return jsonify({'error': 'Invalid patient ID'}), 400

@app.route('/patients/<patientId>/measurements', methods=['POST'])
def add_patient_measurement(patientId):
    data = request.json
    data['patientId'] = ObjectId(patientId)
    data['dateTime'] = datetime.strptime(data['dateTime'], '%Y-%m-%dT%H:%M:%S')
    mongo.db.patientMeasurements.insert_one(data)
    return jsonify({'message': 'Measurement added successfully'}), 201

@app.route('/patients/<patientId>/alerts', methods=['GET'])
def get_patient_alerts(patientId):
    try:
        alerts = mongo.db.patientAlerts.find({"patientId": ObjectId(patientId)})
        return jsonify(jsonify_custom(list(alerts))), 200
    except InvalidId:
        return jsonify({'error': 'Invalid patient ID'}), 400

@app.route('/patients/<patientId>/alerts', methods=['POST'])
def create_patient_alert(patientId):
    data = request.json
    data['patientId'] = ObjectId(patientId)
    # Assume dateTime or other relevant fields are included in your alert data
    mongo.db.patientAlerts.insert_one(data)
    return jsonify({'message': 'Alert created successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
