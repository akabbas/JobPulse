#!/usr/bin/env python3
"""
Simple Flask test app
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Flask is working!", "status": "success"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "message": "Server is running"})

if __name__ == "__main__":
    print("🚀 Starting simple Flask test server...")
    print("📍 Server will run on http://localhost:5001")
    print("🔍 Test with: curl http://localhost:5001/api/health")
    app.run(debug=True, host='127.0.0.1', port=5001) 