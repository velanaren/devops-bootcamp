from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Database file path (will be in mounted volume)
DB_PATH = os.getenv('DB_PATH', '/data/blog.db')

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with posts table"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

# Initialize database on startup
init_db()

@app.route('/')
def home():
    """API documentation"""
    return jsonify({
        'message': 'Blog API Server',
        'version': '1.0',
        'endpoints': {
            'GET /': 'API documentation',
            'GET /posts': 'Get all posts',
            'GET /posts/<id>': 'Get single post',
            'POST /posts': 'Create new post (JSON: title, content, author)',
            'DELETE /posts/<id>': 'Delete post',
            'GET /health': 'Health check',
            'GET /stats': 'Database statistics'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/stats')
def stats():
    """Get database statistics"""
    conn = get_db_connection()
    total_posts = conn.execute('SELECT COUNT(*) as count FROM posts').fetchone()['count']
    conn.close()
    
    return jsonify({
        'total_posts': total_posts,
        'database_path': DB_PATH,
        'database_exists': os.path.exists(DB_PATH)
    })

@app.route('/posts', methods=['GET'])
def get_posts():
    """Get all blog posts"""
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    conn.close()
    
    posts_list = [dict(post) for post in posts]
    return jsonify({
        'count': len(posts_list),
        'posts': posts_list
    })

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get single blog post by ID"""
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    
    return jsonify(dict(post))

@app.route('/posts', methods=['POST'])
def create_post():
    """Create new blog post"""
    data = request.get_json()
    
    # Validate input
    if not data or not all(key in data for key in ['title', 'content', 'author']):
        return jsonify({'error': 'Missing required fields: title, content, author'}), 400
    
    title = data['title']
    content = data['content']
    author = data['author']
    
    # Insert into database
    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO posts (title, content, author) VALUES (?, ?, ?)',
        (title, content, author)
    )
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'message': 'Post created successfully',
        'id': post_id,
        'title': title
    }), 201

@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete blog post by ID"""
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    
    if rows_deleted == 0:
        return jsonify({'error': 'Post not found'}), 404
    
    return jsonify({'message': 'Post deleted successfully', 'id': post_id})

if __name__ == '__main__':
    print("Starting Blog API Server...")
    print(f"Database location: {DB_PATH}")
    app.run(host='0.0.0.0', port=5000, debug=False)

