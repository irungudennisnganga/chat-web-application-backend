import base64
from datetime import datetime, timedelta
from config import app, db, bcrypt
from models import User, Conversation, Message
from app import key,cipher
# Generate a key for encryption/decryption
# Ensure this key matches the one used in your application
# key = Fernet.generate_key()
# cipher = Fernet(key)

password_hash = bcrypt.generate_password_hash('mypassword').decode('utf-8')

# Sample user data
user_data = [
    {
        "email": "jiceyej601@mposhop.com",
        "id": 1,
        "phone_number": 2544567890,
        "profile_picture": None,
        "status": "active",
        "username": "James"
    },
    {
        "email": "dennis.irungu@student.moringaschool.com",
        "id": 2,
        "phone_number": 2543456789,
        "profile_picture": None,
        "status": "active",
        "username": "denis"
    },
    {
        "email": "irungud220@gmail.com",
        "id": 3,
        "phone_number": 254567890,
        "profile_picture": "https://res.cloudinary.com/dups4sotm/image/upload/v1719473598/pegctld3olsh8uvxngbc.webp",
        "status": "active",
        "username": "deno"
    },
    {
        "email": "locoma1349@kinsef.com",
        "id": 4,
        "phone_number": 2543455555,
        "profile_picture": "https://res.cloudinary.com/dups4sotm/image/upload/v1719476106/tj5asmfgg4jzvl520l2y.jpg",
        "status": "active",
        "username": "irungu"
    }
]

# Sample messages data
messages_data = [
    {"conversation_id": 1, "sender_id": 1, "receiver_id": 2, "content": "Hello Denis!"},
    {"conversation_id": 1, "sender_id": 2, "receiver_id": 1, "content": "Hey James!"},
    {"conversation_id": 2, "sender_id": 3, "receiver_id": 4, "content": "Hi Irungu!"},
    {"conversation_id": 2, "sender_id": 4, "receiver_id": 3, "content": "Hello Deno!"}
]

def clear_users():
    with app.app_context():
        db.session.query(User).delete()
        db.session.commit()

def clear_conversations():
    with app.app_context():
        db.session.query(Conversation).delete()
        db.session.commit()

def clear_messages():
    with app.app_context():
        db.session.query(Message).delete()
        db.session.commit()

def seed_users():
    with app.app_context():
        clear_users()
        for user_info in user_data:
            # Create a new user object
            new_user = User(
                id=user_info['id'],
                username=user_info['username'],
                email=user_info['email'],
                phone_number=user_info['phone_number'],
                profile_picture=user_info['profile_picture'],
                status=user_info['status'],
                _password_hash=password_hash
            )
            db.session.add(new_user)

        db.session.commit()

def seed_conversations():
    with app.app_context():
        clear_conversations()
        # Create conversations between all pairs of users
        for i in range(len(user_data)):
            user1 = user_data[i]
            for j in range(i + 1, len(user_data)):
                user2 = user_data[j]
                # Create conversation between user1 and user2
                conversation = Conversation(user_1_id=user1['id'], user_2_id=user2['id'])
                db.session.add(conversation)

        db.session.commit()

def seed_messages():
    with app.app_context():
        clear_messages()
        for message_info in messages_data:
            # Encrypt the message content and base64 encode it
            encrypted_content = base64.b64encode(cipher.encrypt(message_info['content'].encode())).decode('utf-8')

            # Create a new message object
            new_message = Message(
                conversation_id=message_info['conversation_id'],
                sender_id=message_info['sender_id'],
                receiver_id=message_info['receiver_id'],
                content=encrypted_content,
                timestamp=datetime.utcnow() - timedelta(days=1)  # Example: Set message timestamp in the past
            )
            db.session.add(new_message)

        db.session.commit()

if __name__ == '__main__':
    # Seed the database with users, conversations, and messages
    seed_users()
    seed_conversations()
    seed_messages()

    print("Database seeding completed.")
