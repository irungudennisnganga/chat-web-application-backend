from config import db

class User(db.Model):
    __tablename__ ='user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    profile_picture = db.Column(db.String)
    
    Message =db.relationship("Message", backref='user')
    conversation =db.relationship("Conversation", backref='user')
 
class Conversation(db.Model):
    __tablename__ ='conversation'
    
    id = db.Column(db.Integer, primary_key=True)
    # participants = db.relationship('User', secondary='conversation_participant', backref='conversations')
    user_1__id=db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False )
    user_2_id=db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False )
    
    messages = db.relationship('Message', backref='conversation')
       
class Message(db.Model):
    __tablename__ ='message'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    


# Many-to-Many association table for Conversation and User
# conversation_participant = db.Table('conversation_participant',
#     db.Column('conversation_id', db.Integer, db.ForeignKey('conversation.id'), primary_key=True),
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
# )

