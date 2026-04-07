import asyncio
import random
import time
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import config
import data
import os

# Automation state (can be toggled by .start / .stop)
IS_RUNNING = True

async def send_interaction(sender, clients, consecutive_count, chats_list):
    # Types of interactions: 
    # 0: Chat message
    # 1: Sticker
    action_type = random.choices([0, 1], weights=[0.8, 0.2])[0]
    
    current_last_sender = sender
    current_consecutive_count = consecutive_count
    
    try:
        if action_type == 0:
            if chats_list:
                msg = random.choice(chats_list)
                print(f"[{sender.name}] Sending chat message: {msg}")
                await sender.send_message(config.GROUP_ID, msg)
            else:
                print(f"[{sender.name}] Warning: chats_list is empty!")
        
        elif action_type == 1:
            if data.STICKERS:
                sticker_id = random.choice(data.STICKERS)
                if not sticker_id.startswith("CAAC"):
                    print(f"[{sender.name}] Skipping sticker: placeholder in data.py")
                else:
                    print(f"[{sender.name}] Sending sticker: {sticker_id}")
                    await sender.send_sticker(config.GROUP_ID, sticker_id)
            else:
                print(f"[{sender.name}] No stickers available in data.py")
    
    except FloodWait as e:
        print(f"[{sender.name}] Flood wait: Sleeping for {e.value} seconds")
        await asyncio.sleep(e.value)
    except Exception as e:
        print(f"[{sender.name}] Error sending message: {e}")
        
    return current_last_sender, current_consecutive_count

def load_chats():
    """Load chats from shortletters.txt in the same directory."""
    path = os.path.join(os.path.dirname(__file__), "shortletters.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    print(f"Error: {path} not found!")
    return []

async def main():
    # Load chats from file
    CHATS_LIST = load_chats()
    if not CHATS_LIST:
        print("Error: No chats loaded from shortletters.txt. Stopping.")
        return
    print(f"Loaded {len(CHATS_LIST)} chats from shortletters.txt")

    sessions = [config.SESSION1, config.SESSION2, config.SESSION3, config.SESSION4, config.SESSION5]
    all_clients = []
    
    print("Initializing all 5 accounts...")
    for i, session in enumerate(sessions):
        client = Client(
            name=f"bot_{i+1}",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=session,
            in_memory=True
        )
        all_clients.append(client)
        
    # Start all clients and verify group access
    started_clients = []
    for client in all_clients:
        try:
            await client.start()
            # Try to resolve group
            try:
                await client.get_chat(config.GROUP_ID)
                started_clients.append(client)
                print(f"Account {client.name} is READY.")
            except Exception as e:
                print(f"Warning: Account {client.name} could NOT access group {config.GROUP_ID}. ({e})")
                await client.stop()
        except Exception as e:
            print(f"Error: Account {client.name} failed to start: {e}")

    if len(started_clients) < 3:
        print(f"Critical Error: Only {len(started_clients)} accounts are ready. Need at least 3 for rotation logic. Stopping.")
        return

    # Global Run State
    global IS_RUNNING
    IS_RUNNING = True

    # Register .start / .stop command handler for Bot 1 (SESSION1)
    # This will work when the Owner sends the command to any chat SESSION1 is in
    @started_clients[0].on_message(filters.command(["start", "stop"], prefixes=".") & (filters.me | filters.user(config.OWNER_ID)))
    async def control_handler(client, message):
        global IS_RUNNING
        if ".stop" in message.text:
            if IS_RUNNING:
                IS_RUNNING = False
                await message.reply("🛑 **Automation PAUSED.**")
                print("\n[CONTROL] Automation PAUSED by Owner.")
            else:
                await message.reply("⚠️ Pehle se hi paused hai.")
        elif ".start" in message.text:
            if not IS_RUNNING:
                IS_RUNNING = True
                await message.reply("▶️ **Automation STARTED.**")
                print("\n[CONTROL] Automation STARTED by Owner.")
            else:
                await message.reply("⚠️")

    print(f"\n--- 24/7 Automation Started with {len(started_clients)} accounts ---")
    print(f"Control Bot: {started_clients[0].name} (Owner can use .start / .stop)")
    
    # State tracking
    active_clients = []
    last_rotation_time = 0
    ROTATION_INTERVAL = 60 # 60 seconds
    
    last_sender = None
    consecutive_count = 0
    
    try:
        while True:
            # If paused, just wait and check again
            if not IS_RUNNING:
                await asyncio.sleep(2)
                continue

            # Check for Rotation
            current_time = time.time()
            if current_time - last_rotation_time >= ROTATION_INTERVAL:
                # Select 3 random accounts from the ready pool
                active_clients = random.sample(started_clients, 3)
                last_rotation_time = current_time
                active_names = [c.name for c in active_clients]
                print(f"\n[ROTATION] New Active Set (3): {active_names} | Others are on 60s Cool-Down")
                # Reset consecutive count on rotation
                last_sender = None
                consecutive_count = 0

            # Message Logic using ONLY the active_clients
            if last_sender and consecutive_count >= 3:
                available_senders = [c for c in active_clients if c != last_sender]
            else:
                available_senders = active_clients
            
            sender = random.choice(available_senders)
            
            # Update tracking
            if sender == last_sender:
                consecutive_count += 1
            else:
                last_sender = sender
                consecutive_count = 1
                
            # Send interaction
            last_sender, consecutive_count = await send_interaction(sender, active_clients, consecutive_count, CHATS_LIST)
            
            # Random delay
            delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
            await asyncio.sleep(delay)
            
    except KeyboardInterrupt:
        print("\nStopping automation...")
    finally:
        for client in started_clients:
            await client.stop()

if __name__ == "__main__":
    asyncio.run(main())
