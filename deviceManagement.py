from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId, json_util
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://visaaln2:visaal456@ec530.qevqtrc.mongodb.net/healthmonitoring?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Custom JSON serializer for ObjectId
def custom_json_serializer(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# Updated to use MongoDB's json_util for handling BSON types
def jsonify_with_objectid(data):
    return json.loads(json_util.dumps(data))

@app.route('/devices', methods=['POST'])
def register_device():
    data = request.json
    # Ensure required fields are in the request
    if not all(k in data for k in ("deviceType", "manufacturer", "model", "status")):
        return jsonify({'error': 'Missing required fields'}), 400
    if data['status'] not in ["active", "inactive"]:
        return jsonify({'error': 'Invalid status value'}), 400

    result = mongo.db.medicalDevices.insert_one(data)
    return jsonify({'message': 'Device registered', 'device_id': str(result.inserted_id)}), 201

@app.route('/devices', methods=['GET'])
def list_devices():
    devices = list(mongo.db.medicalDevices.find({}))
    return jsonify(jsonify_with_objectid(devices)), 200

@app.route('/devices/<deviceId>', methods=['PUT'])
def update_device(deviceId):
    data = request.json
    if 'status' in data and data['status'] not in ["active", "inactive"]:
        return jsonify({'error': 'Invalid status value'}), 400

    result = mongo.db.medicalDevices.update_one({'_id': ObjectId(deviceId)}, {'$set': data})
    if result.modified_count:
        return jsonify({'message': 'Device updated successfully'}), 200
    else:
        return jsonify({'error': 'Device not found or data unchanged'}), 404

@app.route('/devices/<deviceId>', methods=['DELETE'])
def delete_device(deviceId):
    result = mongo.db.medicalDevices.delete_one({'_id': ObjectId(deviceId)})
    if result.deleted_count:
        return jsonify({'message': 'Device deleted successfully'}), 200
    else:
        return jsonify({'error': 'Device not found'}), 404

@app.route('/devices/<deviceId>/data', methods=['POST'])
def submit_device_data(deviceId):
    data = request.json
    data['deviceId'] = ObjectId(deviceId)
    mongo.db.deviceData.insert_one(data)
    return jsonify({'message': 'Data submitted successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)

