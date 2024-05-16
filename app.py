from models import User, Conversation, Message
from config import app, api, db, bcrypt
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import cloudinary
import smtplib
import cloudinary.uploader
import cloudinary.api
import random
import string
import datetime

def send_email(email,subject,body):
    
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'irungud220@gmail.com'
    sender_password = 'qbpq uvgp rrqh bjky'
    subject=subject
    body=body

    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email,email,message)


class UserData(Resource):
    def post(self):
        data = request.json
        
        username = data.get('username')
        phone_number = data.get('contact')
        email = data.get('email')
        profile_picture = data.get('profile_picture')
        password = data.get('password_1')
        
        if not all([username, phone_number, password]):
            return make_response(jsonify({'errors': ['Missing required data']}), 400)

        if User.query.filter_by(phone_number=phone_number).first() or User.query.filter_by(username=username).first() or  User.query.filter_by(email=email).first():
            return make_response(jsonify({'message': 'User already exists'}), 400)
        
        # Generate OTP
        otp = self.generate_otp()

        # Store OTP temporarily
        message=f'Here is your otp use it to verify your account {otp} '
        # otp_expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)
        user = User(
            username=username,
            phone_number=phone_number,
            email=email,
            profile_picture=profile_picture,
            _password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
            otp=otp,
            
        )
        
        db.session.add(user)
        db.session.commit()
        
        send_email(email,f'OTP VERIFICATION',message)

        # In a real-world scenario, send the OTP via SMS here

        return make_response(jsonify({'message': 'Sign up successful, Verify OTP to continue'}), 200)
    
    def generate_otp(self):
        """Generate a random OTP."""
        return ''.join(random.choices(string.digits, k=6))
        
class VerifyOTP(Resource):
    def post(self):
        data = request.json
        phone_number = data.get('phone_number')
        otp = data.get('otp')

        user = User.query.filter_by(phone_number=phone_number).first()
        
        if not user:
            return make_response(jsonify({'error': 'No user found for the provided phone number'}), 404)
        print(user.otp)
        if user.otp != otp:
            return make_response(jsonify({'error': 'OTP is incorrect'}), 400)
        user.status ='active'

        db.session.commit()
        return make_response(jsonify({'message': 'OTP is correct'}), 200)
class Login(Resource):

    def post(self):
        email = request.json.get("email")
        password = request.json.get("password")

        if not email or not password:
            return make_response(jsonify({"message": "Please enter Email and Password to continue"}), 400)

        user = User.query.filter_by(email=email).first()
        if not user:
            return make_response(jsonify({"message": "Wrong credentials"}), 401)

        if check_password_hash(user._password_hash, password):
            access_token = create_access_token(identity=user.id)
            return make_response(jsonify(access_token=access_token), 200)

        return make_response(jsonify({"message": "Wrong password"}), 422)

class CheckSession(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        user = User.query.filter_by(id=user_id).first()

        if not user:
            return make_response(jsonify({"message": "user not found"}), 403)

        user_data = {
            "user_id": user.id,
            "username": user.useername,
            "email": user.email,
            "contact": user.contact,
            
        }

        return make_response(jsonify(user_data), 200)
           
api.add_resource(UserData, '/create_account')
api.add_resource(VerifyOTP, '/verify_otp')
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check_session')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
