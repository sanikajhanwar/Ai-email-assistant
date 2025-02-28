from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

@app.route("/")
def home():
    return jsonify({"message": "Backend is running successfully!"})

if __name__ == "__main__":
    app.run(debug=True)
