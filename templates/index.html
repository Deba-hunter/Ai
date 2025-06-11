from flask import Flask, render_template, request, redirect, flash
from instagrapi import Client
import os
import time
import threading

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def login_to_instagram(username, password):
    cl = Client()
    try:
        cl.login(username, password)
        return cl
    except Exception as e:
        print(f"[LOGIN ERROR] {e}")
        return None

def send_looping_messages(cl, receiver_username, messages, delay):
    try:
        user_id = cl.user_id_from_username(receiver_username)
        while True:
            for msg in messages:
                cl.direct_send(msg, [user_id])
                print(f"[SENT] {msg}")
                time.sleep(delay)
    except Exception as e:
        print(f"[SEND LOOP ERROR] {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        receiver = request.form.get('receiver')
        delay = int(request.form.get('delay', 5))

        file = request.files.get('message_file')
        if not file or file.filename == '':
            flash('❌ Please upload a valid message file.')
            return redirect('/')

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            messages = [line.strip() for line in f if line.strip()]

        cl = login_to_instagram(username, password)
        if cl is None:
            flash('❌ Login failed. Check your credentials.')
            return redirect('/')

        # Start message loop in background
        threading.Thread(target=send_looping_messages, args=(cl, receiver, messages, delay), daemon=True).start()

        flash('✅ Message loop started successfully! (Don’t close the server)')
        return redirect('/')

    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    