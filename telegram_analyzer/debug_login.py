import asyncio
import os
import sys
from telethon import TelegramClient

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

async def debug_login():
    print("--- Debugging Telethon Login ---")
    
    api_id = Config.API_ID
    api_hash = Config.API_HASH
    print(f"API_ID present: {bool(api_id)}")
    print(f"API_HASH present: {bool(api_hash)}")
    
    if not api_id or not api_hash:
        print("ERROR: API credentials missing in .env")
        return

    print("Initializing TelegramClient...")
    try:
        client = TelegramClient('anon_debug_session', api_id, api_hash)
        await client.connect()
        print("Connected to Telegram DC.")
        
        if await client.is_user_authorized():
            print("Client is ALREADY authorized.")
        else:
            print("Client is NOT authorized (Login needed).")
            
            # Ask for phone to test sending code
            phone = input("Enter phone number to test (or press Enter to skip): ").strip()
            if phone:
                print(f"Sending code to {phone}...")
                try:
                    await client.send_code_request(phone)
                    print("SUCCESS: Code sent successfully!")
                except Exception as e:
                    if "PhoneNumberInvalidError" in str(type(e).__name__):
                        print(f"\nERROR: Invalid Phone Number. Did you forget the country code? (e.g., +91 for India)")
                        print(f"You entered: {phone}\n")
                    print(f"ERROR: Failed to send code. Reason: {e}")
                    import traceback
                    traceback.print_exc()

        await client.disconnect()
        print("Disconnected.")
        
    except Exception as e:
        print(f"CRITICAL: Failed to initialize/connect client. Reason: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_login())
