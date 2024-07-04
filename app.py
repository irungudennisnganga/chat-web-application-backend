import base64 
from models import User, Conversation, Message
from config import app, api, db, bcrypt,socketio
from cryptography.fernet import Fernet, InvalidToken
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import cloudinary
import traceback
from flask_socketio import SocketIO, emit
import smtplib
import cloudinary.uploader
import cloudinary.api
import random
import string
import datetime


key = b'ehQGERS7-iWwpRAB3ShMPCy01eIcVGdzT-tsd3lR35Q='
cipher = Fernet(key)
print(cipher)

cloudinary.config(
    cloud_name='dups4sotm',
    api_key='141549863151677',
    api_secret='ml0oq6T67FZeXf6AFJqhhPsDfAs'
)
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
        data = request.form
        
        username = data.get('username')
        phone_number = data.get('phone_number')
        email = data.get('email')
        # profile_picture = data.get('profile_picture')
        password = data.get('password_1')
        image_file = request.files.get('image')
        # print(image_file)
        if not all([username, phone_number, password,image_file]):
            return make_response(jsonify({'errors': ['Missing required data']}), 400)

        if User.query.filter_by(phone_number=phone_number).first() or User.query.filter_by(username=username).first() or  User.query.filter_by(email=email).first():
            return make_response(jsonify({'message': 'User already exists'}), 400)
        
        if image_file.filename == '':
                return {'error': 'No image selected for upload'}, 400
        
        
        def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif' ,'webp'}
        if not allowed_file(image_file.filename):
                return {'error': 'Invalid file type. Only images are allowed'}, 400

            # Upload image to Cloudinary
        try:
            image_upload_result = cloudinary.uploader.upload(image_file)
        except Exception as e:
            # print(str(e))
            return {'error': f'Error uploading image: {str(e)}'}, 500
        
        # Generate OTP
        otp = self.generate_otp()

        # Store OTP temporarily
        message=f'Here is your otp use it to verify your account {otp} '
        # otp_expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)
        user = User(
            username=username,
            phone_number=phone_number,
            email=email,
            profile_picture=image_upload_result['secure_url'],
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
        # print(user.otp == int(otp))
        # print(int(otp))
        if user.otp != int(otp):
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
            "username": user.username,
            "email": user.email,
            "contact": user.phone_number,
            "profile_picture":user.profile_picture
            
        }

        return make_response(jsonify(user_data), 200)
 
class UsersAvailable(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        user = User.query.filter_by(id=user_id, status='active').first()
        
        if not user:
            return make_response(jsonify({"message": "User not found", "status": 403}), 403)
        
        users = User.query.filter_by(status='active').all()
        users_data = [self.user_to_dict(u) for u in users]

        return make_response(jsonify({"users": users_data, "status": 200}), 200)
    
    def user_to_dict(self, user):
        return {
            "id": user.id,
            "username": user.username,
            "phone_number": user.phone_number,
            "email": user.email,
            "profile_picture": user.profile_picture,
            "status": user.status
        }


         
     
class UserConversation(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            return make_response(jsonify({"message": "User not found"}), 403)
        
        # Get all conversations where the user is either user_1 or user_2
        conversations = Conversation.query.filter(
            (Conversation.user_1_id == user_id) | (Conversation.user_2_id == user_id)
        ).all()

        if len(conversations) == 0:
            return make_response(jsonify({"message": "No Conversations", "status": 201}), 201)
        
        # Filter conversations to only include those with messages
        conversations_with_messages = []
        for conversation in conversations:
            if conversation.messages:  # Check if the conversation has messages
                conversations_with_messages.append(conversation.to_dict())

        if not conversations_with_messages:
            return make_response(jsonify({"message": "No Conversations with Messages", "status": 201}), 201)

        return make_response(jsonify({"conversations": conversations_with_messages, "status": 200}), 200)

class NewUserConversation(Resource):
    @jwt_required()
    def post(self, user_2):
        user_1 = get_jwt_identity()
        
        if not user_1:
            return make_response(jsonify({"message": "User not found", "status":403}), 403)
        
        # Check if there is an existing conversation
        conversation = Conversation.query.filter(
            ((Conversation.user_1_id == user_1) & (Conversation.user_2_id == user_2)) |
            ((Conversation.user_1_id == user_2) & (Conversation.user_2_id == user_1))
        ).first()
        
        if conversation:
            # If a conversation exists, return the connection ID
            return make_response(jsonify({"connection_id": conversation.id, "status":200}), 200)
        
        # If no conversation exists, create a new one
        new_conversation = Conversation(user_1_id=user_1, user_2_id=user_2)
        db.session.add(new_conversation)
        db.session.commit()
        
        return make_response(jsonify({"connection_id": new_conversation.id, "status":201}), 201)
class MessageResource(Resource):
    @jwt_required()
    def post(self, conversation_id):
        data = request.json
        sender_id = get_jwt_identity()

        conversation = Conversation.query.filter_by(id=conversation_id).first()
        if not conversation:
            return make_response(jsonify({'message': 'Conversation not found'}), 404)

        if conversation.user_1_id == sender_id:
            receiver_id = conversation.user_2_id
        elif conversation.user_2_id == sender_id:
            receiver_id = conversation.user_1_id
        else:
            return make_response(jsonify({'message': 'User not part of the conversation'}), 403)

        content = data.get('content')
        if not content:
            return make_response(jsonify({'message': 'Content is required'}), 400)

        try:
            # Encrypt the message content and base64 encode it
            encrypted_content = base64.b64encode(cipher.encrypt(content.encode())).decode('utf-8')
        except Exception as e:
            return make_response(jsonify({'message': 'Encryption error', 'error': str(e)}), 500)

        # Create a new message instance
        new_message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=encrypted_content
        )

        # Save the message to the database
        try:
            db.session.add(new_message)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Database error', 'error': str(e)}), 500)

        # Emit the message to the receiver using SocketIO
        message_data = new_message.to_dict()
        # Send encrypted content for storage, and decrypted content for display
        message_data['content'] = content  # Send the decrypted content to the receiver via SocketIO
        socketio.emit('receive_message', message_data, room=f'user_{receiver_id}')

        return make_response(jsonify({'message': 'Message sent successfully', 'data': message_data}), 200)

    @jwt_required()
    def get(self, conversation_id):
        if not conversation_id:
            return make_response(jsonify({'message': 'Missing conversation_id parameter'}), 400)

        sender_id = get_jwt_identity()
        conversation = Conversation.query.filter_by(id=conversation_id).first()
        if not conversation:
            return make_response(jsonify({'message': 'Conversation not found'}), 404)

        if conversation.user_1_id != sender_id and conversation.user_2_id != sender_id:
            return make_response(jsonify({'message': 'User not part of the conversation'}), 403)

        try:
            # Fetch messages based on the conversation_id
            messages = Message.query.filter_by(conversation_id=conversation_id).all()
            decrypted_messages = []
            for message in messages:
                try:
                    # Base64 decode and decrypt the message content
                    decrypted_content = cipher.decrypt(base64.b64decode(message.content)).decode('utf-8')
                    message_data = message.to_dict()
                    message_data['content'] = decrypted_content
                    decrypted_messages.append(message_data)
                except InvalidToken:
                    print(f"Error decrypting message {message.id}: Invalid token")
                    print(traceback.format_exc())
                except Exception as decrypt_error:
                    print(f"Error decrypting message {message.id}: {str(decrypt_error)}")
                    print(traceback.format_exc())
                    continue

            # Emit messages directly to the client using SocketIO
            socketio.emit('load_messages', decrypted_messages, room=f'conversation_{conversation_id}')

            return make_response(jsonify(decrypted_messages), 200)
        except Exception as e:
            print(f"Error fetching messages: {str(e)}")
            print(traceback.format_exc())
            return make_response(jsonify({'message': 'Error fetching messages', 'error': str(e)}), 500)
        
api.add_resource(UserData, '/create_account')
api.add_resource(VerifyOTP, '/verify_otp')
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check_session')
api.add_resource(UserConversation, '/conversations')
api.add_resource(UsersAvailable, '/users')
api.add_resource(MessageResource, '/messages/<int:conversation_id>')
api.add_resource(NewUserConversation, '/new_conversation/<int:user_2>')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
if __name__ == '__main__':
    socketio.run(app, port=5555, debug=True)