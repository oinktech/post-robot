from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_cors import CORS
import requests
import time
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS
socketio = SocketIO(app)

# Function to send code requests
def send_code(url, code, times, interval):
    for i in range(times):
        try:
            response = requests.post(url, data={'code': code})
            response_text = response.text  # Get the response text
            if response.status_code == 200:
                socketio.emit('update', f"Attempt {i + 1}: Successful - {response_text}")
            else:
                socketio.emit('update', f"Attempt {i + 1}: Failed - Status Code: {response.status_code}, Response: {response_text}")
        except requests.exceptions.RequestException as e:
            socketio.emit('update', f"Attempt {i + 1}: Request failed - {e}")
        except Exception as e:
            socketio.emit('update', f"Attempt {i + 1}: Error - {e}")
        
        time.sleep(interval)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        code = request.form.get('code')
        try:
            times = int(request.form.get('times'))
            interval = int(request.form.get('interval'))

            # Validate inputs
            if not url or not code or times <= 0 or interval < 0:
                return {"error": "Invalid input. Please ensure all fields are filled correctly."}, 400
            
            # Start the sending process in a separate thread
            thread = threading.Thread(target=send_code, args=(url, code, times, interval))
            thread.start()
            
            return {"message": "Request sent. Check for updates."}, 200
        
        except ValueError:
            return {"error": "Please enter valid numbers for attempts and interval."}, 400

    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=True,port=10000, host='0.0.0.0')
