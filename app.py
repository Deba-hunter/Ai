from flask import Flask, render_template, request, redirect, session
from instagrapi import Client
import os, time

app = Flask(__name__)
app.secret_key = "any-secret-key"
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

cl = Client()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        try:
            cl.login(session['username'], session['password'])
            session['logged_in'] = True
            return redirect('/message')
        except Exception as e:
            if "challenge_required" in str(e).lower():
                cl.challenge_code_handler = lambda x: input("Enter 2FA Code: ")
                session['2fa_pending'] = True
                return redirect('/2fa')
            return f"Login Failed: {e}"
    return render_template("login.html")

@app.route('/2fa', methods=['GET', 'POST'])
def two_factor():
    if request.method == 'POST':
        code = request.form['code']
        try:
            cl.challenge_resolve(code)
            session['logged_in'] = True
            return redirect('/message')
        except Exception as e:
            return f"2FA Failed: {e}"
    return render_template("twofactor.html")

@app.route('/message', methods=['GET', 'POST'])
def message():
    if not session.get('logged_in'):
        return redirect('/')
    
    if request.method == 'POST':
        receiver = request.form['receiver']
        delay = int(request.form['delay'])
        file = request.files['message_file']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        with open(filepath, 'r') as f:
            message = f.read().strip()

        try:
            user_id = cl.user_id_from_username(receiver)
            time.sleep(delay)
            cl.direct_send(message, [user_id])
            return "✅ Message Sent!"
        except Exception as e:
            return f"❌ Failed: {e}"

    return render_template("message.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    