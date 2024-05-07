from config import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

class User(db.Model):
    __tablename__ ='user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    profile_picture = db.Column(db.String)
    status = db.Column(db.String, default='inactive')
    
    otp =db.Column(db.Integer)
    
    messages_sent = db.relationship("Message", foreign_keys='Message.sender_id', backref='sender')
    messages_received = db.relationship("Message", foreign_keys='Message.receiver_id', backref='receiver')
    # Specify the foreign keys explicitly
    conversations_as_user_1 = db.relationship("Conversation", foreign_keys='Conversation.user_1_id', backref='user_1')
    conversations_as_user_2 = db.relationship("Conversation", foreign_keys='Conversation.user_2_id', backref='user_2')
    
    @validates('email')
    def validate_email(self, key, value):
        if '@' not in value and '.com' not in value:
            raise ValueError("Invalid email")
        return value
    
    @hybrid_property
    def password_hash(self):
        return self._password_hash
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    def __repr__(self):
        return f"User('{self.username}', '{self.profile_picture}', '{self.phone_number}')"

class Conversation(db.Model):
    __tablename__ ='conversation'
    
    id = db.Column(db.Integer, primary_key=True)
    user_1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    messages = db.relationship('Message', backref='conversation')

class Message(db.Model):
    __tablename__ ='message'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
