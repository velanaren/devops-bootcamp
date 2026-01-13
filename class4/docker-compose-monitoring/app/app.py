from flask import Flask, jsonify, request
import psycopg2
import os
import time
import random

app = Flask(__name__)

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)

@app.route('/')
def home():
    """Home endpoint - simple health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'Monitoring System Flask App',
        'timestamp': time.time()
    })

@app.route('/health')
def health():
    """Detailed health check with DB connection"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/cpu-test')
def cpu_test():
    """Simulate CPU-intensive task"""
    start = time.time()
    
    # CPU-intensive calculation
    result = 0
    for i in range(1000000):
        result += i ** 2
    
    duration = time.time() - start
    return jsonify({
        'test': 'cpu',
        'duration': duration,
        'result': result
    })

@app.route('/memory-test')
def memory_test():
    """Simulate memory-intensive task"""
    # Create large list in memory
    large_list = [random.random() for _ in range(1000000)]
    
    return jsonify({
        'test': 'memory',
        'items_created': len(large_list),
        'sample': large_list[:5]
    })

@app.route('/db-test')
def db_test():
    """Test database operations"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create test table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT
            )
        """)
        
        # Insert test record
        cursor.execute(
            "INSERT INTO test_logs (message) VALUES (%s) RETURNING id",
            (f"Test at {time.time()}",)
        )
        
        record_id = cursor.fetchone()[0]
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM test_logs")
        total_records = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'test': 'database',
            'new_record_id': record_id,
            'total_records': total_records
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/combined-test')
def combined_test():
    """Run all tests together - maximum load"""
    results = {}
    
    # CPU test
    cpu_start = time.time()
    result = sum([i**2 for i in range(500000)])
    results['cpu_time'] = time.time() - cpu_start
    
    # Memory test
    large_data = [random.random() for _ in range(500000)]
    results['memory_items'] = len(large_data)
    
    # DB test
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO test_logs (message) VALUES (%s)", 
                      ("Combined test",))
        conn.commit()
        cursor.close()
        conn.close()
        results['database'] = 'success'
    except Exception as e:
        results['database'] = f'error: {str(e)}'
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
