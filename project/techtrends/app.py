import sqlite3
import logging
from flask import Flask, jsonify, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime

# Initialize global counter for database connections
db_connection_count = 0

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

# Function to get a database connection.
# This function connects to the database with the name `database.db`
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    connection.close()
    return post

# Function to count total posts
def get_post_count():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()
    return post_count

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logging.info(f'{datetime.now()}, 404 - Article ID {post_id} not found')
        return render_template('404.html'), 404
    else:
        logging.info(f'{datetime.now()}, Article "{post["title"]}" retrieved!')
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info(f'{datetime.now()}, About Us page retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            connection.commit()
            connection.close()
            logging.info(f'{datetime.now()}, New article "{title}" created!')
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the health check endpoint
@app.route('/healthz')
def healthz():
    response = {
        "result": "OK - healthy"
    }
    return jsonify(response), 200

# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    response = {
        "db_connection_count": db_connection_count,
        "post_count": get_post_count()
    }
    return jsonify(response), 200

# Start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3111)
