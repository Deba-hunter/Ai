from flask import Flask, render_template, request
from instagrapi import Client
import os, time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        receiver = request.form['receiver']
        delay = int(request.form['delay'])

        file = request.files['message_file']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Read message from file
        with open(filepath, 'r') as f:
            message = f.read().strip()

        # Login and send message
        cl = Client()

        try:
            cl.login(username, password)
        except Exception as e:
            # Handle 2FA
            if "challenge_required" in str(e).lower():
                cl.get_timeline_feed()
                print("🔐 Two-factor authentication required.")
                code = input("Enter 2FA code sent to your phone/email: ")
                cl.challenge_resolve(code)
            else:
                return f"❌ Login Failed: {e}"

        time.sleep(delay)
        user_id = cl.user_id_from_username(receiver)
        cl.direct_send(message, [user_id])

        return "✅ Message Sent Successfully!"

    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    
