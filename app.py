from flask import Flask, render_template, request, jsonify
import subprocess
import threading
import sys

app = Flask(__name__)

# Variable to hold terminal output
terminal_output = []

# Function to capture terminal output
def capture_terminal_output():
    global terminal_output
    process = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Read output continuously
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            terminal_output.append(output.strip())
            # Keep the last 10 lines
            if len(terminal_output) > 10:
                terminal_output.pop(0)

# Start the terminal output capturing in a separate thread
def start_terminal_thread():
    terminal_thread = threading.Thread(target=capture_terminal_output)
    terminal_thread.daemon = True
    terminal_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.form['message']
    
    # Send the message to the terminal
    process = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    process.stdin.write(message + '\n')
    process.stdin.flush()

    # Capture the response from the terminal and return it
    terminal_response = ''
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            terminal_response += output.strip() + '\n'
    
    return jsonify({"response": terminal_response})

@app.route('/get_output', methods=['GET'])
def get_output():
    global terminal_output
    # Return the most recent terminal output to the web interface
    return jsonify({"output": '\n'.join(terminal_output)})

if __name__ == "__main__":
    start_terminal_thread()  # Start capturing terminal output
    app.run(host='0.0.0.0', port=5000, debug=True)
