from flask import Flask, redirect, jsonify, request, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import random

load_dotenv()

app = Flask(__name__)

verification_code = {}


def send_verification_email(email, code):
    sender_email = os.getenv("EMAIL_USER")
    email_code = os.getenv("EMAIL_APP_CODE")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Your Verification Code"

    body = f"Your Verification code is {code}. it expires in 10 minutes"
    msg.attach(MIMEText(body, 'plain'))
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, email_code)
            server.send_message(msg)
        print(f"Verification email send to {email} {code}")
    except Exception as e:
        print(f"Error sending email {e}")


@app.route('/<email>')
def send_email(email):
    if not email or '@' not in email:
        return jsonify(
            {
            "message": "Please enter a valid email address",
            'code': '400'
            } ), 400

    code = str(random.randint(1000, 9999))
    verification_code[email] = {
        'code': code,
        'expires_at': datetime.now() + timedelta(minutes=10)
    }

    send_verification_email(email=email, code=code)
    return jsonify(
        {"message": f"Email sent to {email} and code is {code}", 'code':'200'}
    ), 200


@app.route('/verify/<code>', methods=['POST'])
def verify_code(code):
    data = request.get_json()
    email = data.get('email')

    if not email or not code:
        return jsonify({"message": "Email and code are required.", 'code': '400'}), 400

    if email not in verification_code:
        return jsonify({"message": "No verification code found for this email", 'code': '404'}), 404

    stored_code_info = verification_code[email]
    if datetime.now() > stored_code_info['expires_at']:
        return jsonify({"message": "Verification code has expired", 'code':'400'}), 400

    if code != stored_code_info['code']:
        return jsonify({"message": "Invalid verification code", 'code':"400"}), 400

    return jsonify({"message": "Verification Successful", 'code':'200'}), 200



