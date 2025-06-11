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

def get_recipient_id(cl, receiver):
    try:
        if receiver.startswith("group:"):
            thread_id = receiver.split("group:")[1]
            return thread_id, True
        else:
            user_id = cl.user_id_from_username(receiver)
            return user_id, False
    except Exception as e:
        print(f"[RECIPIENT ERROR] {e}")
        return None, None

def send_looping_messages(cl, receiver, messages, delay, person_name):
    try:
        recipient_id, is_group = get_recipient_id(cl, receiver)
        if not recipient_id:
            print("[ERROR] Invalid receiver.")
            return

        while True:
            for msg in messages:
                full_msg = f"{person_name} {msg}"
                if is_group:
                    cl.direct_send(full_msg, [], thread_ids=[recipient_id])
                else:
                    cl.direct_send(full_msg, [recipient_id])
                print(f"[SENT] {full_msg}")
                time.sleep(delay)
    except Exception as e:
        print(f"[SEND LOOP ERROR] {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        receiver = request.form.get('receiver')  # DM username or group:<thread_id>
        person_name = request.form.get('person_name', '').strip()
        delay = int(request.form.get('delay', 5))

        if not person_name:
            flash('❌ Person name is required.')
            return redirect('/')

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

        threading.Thread(target=send_looping_messages, args=(cl, receiver, messages, delay, person_name), daemon=True).start()

        flash('✅ Message loop started successfully! (Don’t close the server)')
        return redirect('/')

    return render_template('index.html')
    
# n on mobile-accessible network
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)    
