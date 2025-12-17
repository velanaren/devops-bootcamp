from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    movies = [
        "The Shawshank Redemption",
        "Inception",
        "Interstellar",
        "The Dark Knight",
        "Pulp Fiction"
    ]
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Flask App</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f0f0f0;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
            }}
            .info {{
                margin: 20px 0;
                padding: 15px;
                background-color: #e3f2fd;
                border-left: 4px solid #2196F3;
            }}
            ul {{
                list-style-type: none;
                padding: 0;
            }}
            li {{
                padding: 10px;
                margin: 5px 0;
                background-color: #f5f5f5;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>My Docker Flask App</h1>
            <div class="info">
                <p><strong>Name:</strong> Vela </p>
                <p><strong>Current Date & Time:</strong> {current_time}</p>
            </div>
            <h2>🎬 My Favorite Movies</h2>
            <ul>
                {''.join([f'<li>• {movie}</li>' for movie in movies])}
            </ul>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

