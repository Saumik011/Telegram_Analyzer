from telethon import TelegramClient, events, types
import sys
import os
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from core.database import db, DatabaseManager
from core.models import User, Chat, Message

class TelegramManager:
    def __init__(self):
        self.api_id = Config.API_ID
        self.api_hash = Config.API_HASH
        self.session_name = Config.SESSION_NAME
        
        if self.api_id and self.api_hash:
            try:
                self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            except Exception as e:
                print(f"Failed to initialize TelegramClient: {e}")
                self.client = None
        else:
            print("API_ID or API_HASH missing. TelegramClient not initialized.")
            self.client = None
        
        self.db_manager = db

    async def connect(self):
        if self.client:
            await self.client.connect()
    
    async def is_user_authorized(self):
        if self.client:
            return await self.client.is_user_authorized()
        return False
    
    async def send_code_request(self, phone):
        if not self.client:
            raise Exception("Telegram Client not initialized. Check API_ID and API_HASH.")
        await self.client.send_code_request(phone)
        
    async def sign_in(self, phone, code, password=None):
        if not self.client:
            raise Exception("Telegram Client not initialized.")
        try:
            await self.client.sign_in(phone, code)
        except Exception as e:
            if "password" in str(e).lower() and password:
                await self.client.sign_in(password=password)
            else:
                raise e

    async def get_dialogs(self, limit=20):
        if not self.client:
            return []
        # Fetch dialogs and populate local DB if needed
        dialogs = await self.client.get_dialogs(limit=limit)
        return dialogs

    async def sync_history(self, chat_id, limit=100):
        """
        Syncs message history for a specific chat.
        """
        if not self.client:
            return
            
        # Resolve chat entity
        entity = await self.client.get_entity(chat_id)
        
        with self.db_manager.get_session() as session:
            # Ensure chat exists in DB
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            if not chat:
                chat_type = 'user'
                if isinstance(entity, types.Channel):
                    chat_type = 'channel'
                elif isinstance(entity, types.Chat):
                    chat_type = 'group'
                
                chat = Chat(
                    id=chat_id,
                    title=getattr(entity, 'title', None) or getattr(entity, 'first_name', 'Unknown'),
                    username=getattr(entity, 'username', None),
                    type=chat_type
                )
                session.add(chat)
                session.commit()

            # Create or get users
            # Optimization: Cache users to avoid N+1 queries during bulk sync
            
            async for msg in self.client.iter_messages(entity, limit=limit):
                if not msg.message:
                    continue
                
                # Check if message already exists
                exists = session.query(Message).filter(Message.telegram_id == msg.id, Message.chat_id == chat_id).first()
                if exists:
                    continue
                
                # Handle Sender
                sender_id = msg.sender_id
                if sender_id:
                    user = session.query(User).filter(User.id == sender_id).first()
                    if not user:
                        # Try to get sender info if possible, might need to fetch entity
                        # For now, just create ID
                        user = User(id=sender_id)
                        session.add(user)
                        session.commit() # Commit needed to reference it
                
                # Create Message
                db_msg = Message(
                    telegram_id=msg.id,
                    chat_id=chat_id,
                    sender_id=sender_id,
                    text=msg.message,
                    date=msg.date,
                    reply_to_msg_id=msg.reply_to_msg_id
                )
                session.add(db_msg)
            
            session.commit()

    async def start_listening(self):
        @self.client.on(events.NewMessage)
        async def handler(event):
            # Real-time processing would go here
            # For now, we can just print or log
            print(f"New message in {event.chat_id}: {event.message.message}")
            # Trigger analysis pipeline here
        
        await self.client.run_until_disconnected()

telegram_bot = TelegramManager()
