from flask import Flask, jsonify, request, render_template_string
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
import socket
from datetime import datetime

app = Flask(__name__)

# MongoDB configuration from environment variables
MONGO_HOST = os.getenv('MONGO_HOST', 'flask-db')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
MONGO_DB = os.getenv('MONGO_DB', 'flaskdb')

# Initialize MongoDB connection
def get_mongo_client():
    """Get MongoDB client connection"""
    try:
        client = MongoClient(
            host=MONGO_HOST,
            port=MONGO_PORT,
            serverSelectionTimeoutMS=5000
        )
        # Test connection
        client.admin.command('ping')
        return client
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        return None

# HTML Template for home page
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Flask + MongoDB Network Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background-color: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
        }
        h2 {
            color: #764ba2;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .info-box {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #667eea;
        }
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .info-item:last-child {
            border-bottom: none;
        }
        .label {
            font-weight: bold;
            color: #555;
        }
        .value {
            color: #667eea;
            font-family: monospace;
        }
        .success {
            color: #28a745;
            font-weight: bold;
        }
        .error {
            color: #dc3545;
            font-weight: bold;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            justify-content: center;
        }
        button, .button {
            background-color: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            display: inline-block;
        }
        button:hover, .button:hover {
            background-color: #764ba2;
        }
        .visitors-list {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .visitor-item {
            padding: 10px;
            background-color: white;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐍 Flask + MongoDB Network Test</h1>
        <p style="text-align: center; color: #666;">Docker Network Isolation Demo</p>
        
        <div class="info-box">
            <h2>Application Info</h2>
            <div class="info-item">
                <span class="label">Container Hostname:</span>
                <span class="value">{{ hostname }}</span>
            </div>
            <div class="info-item">
                <span class="label">MongoDB Host:</span>
                <span class="value">{{ mongo_host }}</span>
            </div>
            <div class="info-item">
                <span class="label">MongoDB Port:</span>
                <span class="value">{{ mongo_port }}</span>
            </div>
            <div class="info-item">
                <span class="label">Database Name:</span>
                <span class="value">{{ mongo_db }}</span>
            </div>
            <div class="info-item">
                <span class="label">Database Status:</span>
                <span class="{{ 'success' if db_connected else 'error' }}">
                    {{ 'Connected ✓' if db_connected else 'Disconnected ✗' }}
                </span>
            </div>
        </div>

        {% if db_connected %}
        <div class="info-box">
            <h2>Visitor Log</h2>
            <p>Total Visitors: <strong>{{ visitor_count }}</strong></p>
            {% if visitors %}
            <div class="visitors-list">
                {% for visitor in visitors %}
                <div class="visitor-item">
                    <strong>Visitor #{{ visitor.visitor_number }}</strong> - {{ visitor.timestamp }}
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endif %}

        <div class="button-group">
            <a href="/health" class="button">Health Check</a>
            <a href="/add-visitor" class="button">Add Visitor</a>
            <a href="/stats" class="button">Statistics</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    """Home page with MongoDB connection info"""
    hostname = socket.gethostname()
    
    # Try to connect to MongoDB
    client = get_mongo_client()
    db_connected = client is not None
    
    visitors = []
    visitor_count = 0
    
    if db_connected:
        try:
            db = client[MONGO_DB]
            collection = db.visitors
            
            # Get visitor count
            visitor_count = collection.count_documents({})
            
            # Get last 5 visitors
            visitors = list(collection.find().sort('_id', -1).limit(5))
            
            client.close()
        except Exception as e:
            print(f"Error fetching visitors: {e}")
    
    return render_template_string(
        HOME_TEMPLATE,
        hostname=hostname,
        mongo_host=MONGO_HOST,
        mongo_port=MONGO_PORT,
        mongo_db=MONGO_DB,
        db_connected=db_connected,
        visitor_count=visitor_count,
        visitors=visitors
    )

@app.route('/health')
def health():
    """Health check endpoint - tests MongoDB connection"""
    client = get_mongo_client()
    
    if client:
        try:
            # Get server info
            server_info = client.server_info()
            db = client[MONGO_DB]
            collection_count = len(db.list_collection_names())
            
            client.close()
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'mongo_version': server_info.get('version'),
                'mongo_host': MONGO_HOST,
                'mongo_port': MONGO_PORT,
                'database_name': MONGO_DB,
                'collections_count': collection_count
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'database': 'error',
                'error': str(e),
                'mongo_host': MONGO_HOST
            }), 500
    else:
        return jsonify({
            'status': 'unhealthy',
            'database': 'connection_failed',
            'mongo_host': MONGO_HOST,
            'mongo_port': MONGO_PORT
        }), 500

@app.route('/add-visitor')
def add_visitor():
    """Add a visitor to MongoDB"""
    client = get_mongo_client()
    
    if not client:
        return jsonify({'error': 'Cannot connect to MongoDB'}), 500
    
    try:
        db = client[MONGO_DB]
        collection = db.visitors
        
        # Get current count for visitor number
        visitor_count = collection.count_documents({})
        
        # Add new visitor
        visitor = {
            'visitor_number': visitor_count + 1,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'hostname': socket.gethostname()
        }
        
        result = collection.insert_one(visitor)
        client.close()
        
        return jsonify({
            'message': 'Visitor added successfully',
            'visitor_number': visitor_count + 1,
            'id': str(result.inserted_id)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def stats():
    """Get database statistics"""
    client = get_mongo_client()
    
    if not client:
        return jsonify({'error': 'Cannot connect to MongoDB'}), 500
    
    try:
        db = client[MONGO_DB]
        collection = db.visitors
        
        total_visitors = collection.count_documents({})
        collections = db.list_collection_names()
        
        client.close()
        
        return jsonify({
            'database_name': MONGO_DB,
            'mongo_host': MONGO_HOST,
            'total_visitors': total_visitors,
            'collections': collections
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Starting Flask + MongoDB Network Test App...")
    print(f"MongoDB Host: {MONGO_HOST}")
    print(f"MongoDB Port: {MONGO_PORT}")
    print(f"Database: {MONGO_DB}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)

