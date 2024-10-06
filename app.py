from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
socketio = SocketIO(app)
db = SQLAlchemy(app)

# Define a Message model for the database
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Route to the login page
@app.route('/')
def login():
    return render_template('login.html')

# Route for the chat page
@app.route('/chat', methods=['POST'])
def chat():
    username = request.form['username']
    if username:
        session['username'] = username
        return render_template('index.html')
    return redirect(url_for('login'))

# Load previous messages from the database
@app.route('/load_messages', methods=['GET'])
def load_messages():
    messages = Message.query.order_by(Message.timestamp.asc()).all()
    return {'messages': [{'username': m.username, 'content': m.content, 'timestamp': m.timestamp.strftime('%H:%M:%S')} for m in messages]}

# Handle messages sent from clients
@socketio.on('message')
def handleMessage(msg):
    username = session.get('username')
    if username:
        new_message = Message(username=username, content=msg)
        db.session.add(new_message)
        db.session.commit()
        send({'username': username, 'content': msg, 'timestamp': datetime.now().strftime('%H:%M:%S')}, broadcast=True)

if __name__ == '__main__':
    with app.app_context():  # Use app context here
        db.create_all()  # Create database tables within the application context
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)