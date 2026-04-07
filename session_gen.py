import asyncio
from pyrogram import Client

async def main():
    print("Welcome to Session Generator for Fake Chats!")
    api_id = int(input("Enter API_ID: "))
    api_hash = input("Enter API_HASH: ")
    
    async with Client(":memory:", api_id=api_id, api_hash=api_hash) as app:
        session_str = await app.export_session_string()
        print("\nYour Session String is:\n")
        print(session_str)
        print("\nCopy this string and put it in config.py under SESSION1, SESSION2, or SESSION3.")

if __name__ == "__main__":
    asyncio.run(main())
