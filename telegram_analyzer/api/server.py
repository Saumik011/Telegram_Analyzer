from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
import uvicorn
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.telegram_client import telegram_bot
from core.database import db
from core.models import Chat, Message, User, MessageAnalysis
from core.analyzer import analyzer

app = FastAPI(title="Telegram Intent Analyzer")

# Mount static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

@app.on_event("startup")
async def startup_event():
    # In a real app, strict handling of the loop is needed for Telethon + FastAPI
    # For now, we assume we might run Telethon in a separate thread or just connect here
    await telegram_bot.connect()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status():
    authorized = await telegram_bot.is_user_authorized()
    return {"authorized": authorized}

@app.post("/api/login")
async def login(phone: str):
    try:
        await telegram_bot.send_code_request(phone)
        return {"status": "code_sent"}
    except Exception as e:
        print(f"Login Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/verify")
async def verify(phone: str, code: str, password: str = None):
    try:
        await telegram_bot.sign_in(phone, code, password)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/chats")
async def get_chats():
    # Only return chats that are in the DB or fetch recent ones
    with db.get_session() as session:
        chats = session.query(Chat).order_by(Chat.last_updated.desc()).limit(50).all()
        return [{"id": c.id, "title": c.title, "type": c.type} for c in chats]

@app.post("/api/chats/sync")
async def sync_chats(background_tasks: BackgroundTasks):
    # This triggers a sync of dialogs
    async def _sync():
        dialogs = await telegram_bot.get_dialogs()
        with db.get_session() as session:
             for d in dialogs:
                chat_id = d.id
                title = d.title
                # Check if exists
                existing = session.query(Chat).filter(Chat.id == chat_id).first()
                if not existing:
                    new_chat = Chat(id=chat_id, title=title, type='unknown')
                    session.add(new_chat)
             session.commit()
    
    background_tasks.add_task(_sync)
    return {"status": "sync_started"}

@app.get("/api/chats/{chat_id}/analyze")
async def analyze_chat(chat_id: int, background_tasks: BackgroundTasks):
    # Trigger sync history then analyze
    async def _process_chat():
        try:
            print(f"Syncing history for {chat_id}...")
            await telegram_bot.sync_history(chat_id, limit=50) # Fetch last 50
            
            print(f"Analyzing messages for {chat_id}...")
            with db.get_session() as session:
                messages = session.query(Message).filter(Message.chat_id == chat_id).order_by(Message.date.asc()).all()
                print(f"Found {len(messages)} messages to analyze.")
                
                # Analyze each message
                prev_msg = None
                count = 0
                for msg in messages:
                    # Calculate time gap
                    time_gap = 0
                    if prev_msg:
                        time_gap = (msg.date - prev_msg.date).total_seconds()
                    
                    # Intent
                    intent, confidence = analyzer.predict_intent(msg.text)
                    
                    # Urgency
                    urgency = analyzer.calculate_urgency(msg.text, time_gap)
                    
                    # Sentiment
                    sentiment = analyzer.calculate_sentiment(msg.text)
                    tone = analyzer.analyze_emotional_tone(sentiment)
                    
                    # Update DB
                    existing_analysis = session.query(MessageAnalysis).filter(MessageAnalysis.message_id == msg.id).first()
                    if not existing_analysis:
                        analysis_entry = MessageAnalysis(
                            message_id=msg.id,
                            intent=intent,
                            intent_confidence=confidence,
                            urgency_score=urgency,
                            engagement_score=0, # Placeholder
                            sentiment_score=sentiment,
                            emotional_tone=tone,
                            future_reply_prob_5min=0, # Placeholder
                            future_reply_prob_1hr=0, # Placeholder
                            future_reply_prob_24hr=0 # Placeholder
                        )
                        session.add(analysis_entry)
                        count += 1
                    else:
                        existing_analysis.intent = intent # Update existing
                        existing_analysis.sentiment_score = sentiment
                        existing_analysis.emotional_tone = tone
                    
                    prev_msg = msg
                
                session.commit()
                print(f"Successfully analyzed {count} new messages.")
        except Exception as e:
            print(f"ERROR inside _process_chat: {e}")
            import traceback
            traceback.print_exc()
    
    background_tasks.add_task(_process_chat)
    return {"status": "analysis_started"}

@app.get("/api/chats/{chat_id}/results")
async def get_chat_results(chat_id: int):
    with db.get_session() as session:
        messages = (session.query(Message, MessageAnalysis)
                    .outerjoin(MessageAnalysis, Message.id == MessageAnalysis.message_id) # Fix join
                    .filter(Message.chat_id == chat_id)
                    .order_by(Message.date.asc())
                    .limit(50)
                    .all())
        
        results = []
        for msg, analysis in messages:
            intent = analysis.intent if analysis else "unknown"
            urgency = analysis.urgency_score if analysis else 0
            sentiment = analysis.sentiment_score if analysis else 0
            tone = analysis.emotional_tone if analysis else "Neutral"
            
            results.append({
                "id": msg.id,
                "text": msg.text,
                "date": msg.date.isoformat(),
                "sender_id": msg.sender_id,
                "intent": intent,
                "urgency": urgency,
                "sentiment": sentiment,
                "tone": tone
            })
            
        return results

if __name__ == "__main__":
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True)
