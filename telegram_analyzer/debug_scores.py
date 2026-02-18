import sys
import os
import io
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Fix for Windows Unicode printing
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import core.models as from_module
from core.analyzer import analyzer
from core.models import MessageAnalysis, Message, Chat
from config import Config

def debug_scores():
    print("--- Debugging Sentiment Scores ---")
    
    # 1. Test Analyzer
    test_texts = [
        "I love this!",
        "This is terrible.",
        "Okay, fine.",
        "What are you doing?"
    ]
    print("\n[Analyzer Test]")
    for text in test_texts:
        score = analyzer.calculate_sentiment(text)
        tone = analyzer.analyze_emotional_tone(score)
        print(f"Text: '{text}' -> Score: {score}, Tone: {tone}")
        
    # 2. Check Database
    print("\n[Database Check]")
    engine = create_engine(f"sqlite:///{Config.DB_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        chat_count = session.query(from_module.Chat).count()
        if chat_count > 0:
            first_chat = session.query(from_module.Chat).first()
            print(f"Sample Chat ID: {first_chat.id}")
            
        msg_count = session.query(from_module.Message).count()
        print(f"Total Chats: {chat_count}")
        print(f"Total Messages: {msg_count}")

        results = session.query(MessageAnalysis).limit(5).all()
        if not results:
            print("No analysis results found in DB.")
        else:
            for res in results:
                print(f"Msg ID: {res.message_id}, Sentiment: {res.sentiment_score}, Tone: {res.emotional_tone}")
                
                # Check actual message text if possible
                msg = session.query(Message).filter(Message.id == res.message_id).first()
                if msg:
                     print(f"  -> Content: {msg.text}")
                     
    finally:
        session.close()

if __name__ == "__main__":
    debug_scores()
