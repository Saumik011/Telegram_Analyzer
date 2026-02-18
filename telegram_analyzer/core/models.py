from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True) # Telegram User ID
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_self = Column(Boolean, default=False)
    
    messages = relationship("Message", back_populates="sender")

class Chat(Base):
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True) # Telegram Chat ID
    title = Column(String, nullable=True)
    username = Column(String, nullable=True) # For channels/groups
    type = Column(String) # 'user', 'group', 'channel'
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", back_populates="chat")
    analysis = relationship("ChatAnalysis", back_populates="chat", uselist=False)

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True) # Internal DB ID
    telegram_id = Column(Integer) # Message ID in Telegram
    chat_id = Column(Integer, ForeignKey('chats.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    text = Column(Text, nullable=True)
    date = Column(DateTime)
    reply_to_msg_id = Column(Integer, nullable=True)
    
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="messages")
    analysis = relationship("MessageAnalysis", back_populates="message", uselist=False)

class MessageAnalysis(Base):
    __tablename__ = 'message_analysis'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'))
    
    intent = Column(String) # e.g., 'agreement', 'passive_ack'
    intent_confidence = Column(Float)
    
    urgency_score = Column(Float) # 0-100
    engagement_score = Column(Float) # 0-100
    sentiment_score = Column(Float, default=0.0)
    emotional_tone = Column(String, default="Neutral")
    
    future_reply_prob_5min = Column(Float)
    future_reply_prob_1hr = Column(Float)
    future_reply_prob_24hr = Column(Float)
    
    message = relationship("Message", back_populates="analysis")

class ChatAnalysis(Base):
    __tablename__ = 'chat_analysis'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'))
    
    current_engagement = Column(Float)
    overall_sentiment_trend = Column(String) # 'warming', 'cooling', 'stable'
    
    chat = relationship("Chat", back_populates="analysis")
