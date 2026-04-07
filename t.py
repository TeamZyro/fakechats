import asyncio
import os
from PIL import Image
from pyrogram import Client
import config

# Account details with LOCAL image files
ACCOUNTS = [
    {
        "session": "BQGox7EAxgCUC-uiCPYsXiCnBFQkv4VkARmfxvqnlA-0qmAa6Rik215mxxwudPbcglhDoX38FcHyicmcpIk_7xOKpskhYfNoOnX9PSp4aVYpCsjOPy7sS54Q5J386Q3dlD7IRqpWk3ZFOf4OL7LA0V3R460TAKDGWFFr56nZp3Nlz76r9IvH5mbBfuMvgHD2PjRo_nVnWBW9xnr4nkqWxz28fSF1Mwwj3wQI_VbdPeuZBU7tYtdhnprE2IUmxP60Bhxhgf4p8xj0yEaQapJtJY_rGblmzCjudp9QP15aibML38kNxUysAq6dOC24gmq2OVs-iOp1hvZQN67sS2Czb52C3DGmwgAAAAGAUjuVAA",
        "name": "ᵈᵉᵛⁱˡ᭄𝒈𝒊𝒓𝒍",
        "photo": "pfp1.png"
    },
    {
        "session": "BQF253kAlKojgMdcNdlJNNlyYZbeVTOObSoiCMjajD0Ulc0pkokZAFbQQ4hnhiq0FHpnTk-Tt5Hqk3CHQer2EFsYxwhwIfZCd7JIpRuFQFTyHVffyURVeyyXyjeykpHRo95Z92XRLmyTr93irWOg_pbxwPlBwmf4rMzj5DfWbUpCH0_WMp6ewB_lRd9nUbI0zfP94egc8j37cqs4wjpzXOEJQltqam-cFyVEHW0b_mMqRYAgueq2nqGyt5NvXIXILxTji-MfuT2iuI5oV55ca7pEwucgIQp5CV5h1XF08W3PGErJ7HBSzzv8zYDQWCkvL9msE4T5e6XItzlij73j__I-53d7JQAAAAH5shVUAA",
        "name": "ડꪶꪖꪗⅈꪀᧁ么𝕢ꪊꫀꫀꪀ✿",
        "photo": "pfp2.png"
    }
]

async def process_photo(photo_path):
    """Check image dimensions and resize if too small for Telegram (min 160x160)."""
    if not os.path.exists(photo_path):
        return None
    
    try:
        with Image.open(photo_path) as img:
            width, height = img.size
            if width < 160 or height < 160:
                print(f"Warning: Photo {photo_path} is too small ({width}x{height}). Resizing to 512x512...")
                # Resize to standard size (512x512)
                img = img.resize((512, 512), Image.LANCZOS)
                temp_name = "ready_to_upload_" + photo_path
                img.save(temp_name)
                return temp_name
            else:
                return photo_path
    except Exception as e:
        print(f"Error processing image {photo_path}: {e}")
        return None

async def update_account(acc_data):
    session = acc_data["session"]
    name = acc_data["name"]
    original_photo = acc_data["photo"]
    
    print(f"\nProcessing Account: {name}...")
    
    async with Client(
        name="profiler",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=session,
        in_memory=True
    ) as app:
        # 1. Update Name & Remove Bio
        try:
            await app.update_profile(first_name=name, bio="")
            print(f"Successfully updated name to '{name}' and removed bio.")
        except Exception as e:
            if "USERNAME_NOT_MODIFIED" in str(e):
                pass
            else:
                print(f"Info: Name/Bio update: {e}")
            
        # 2. Remove Username
        try:
            me = await app.get_me()
            if me.username:
                await app.set_username(None)
                print("Successfully removed username.")
            else:
                print("Account already has no username.")
        except Exception as e:
            if "USERNAME_NOT_MODIFIED" in str(e):
                print("Username already removed.")
            else:
                print(f"Info: Username removal issue: {e}")

        # 3. Update DP
        photo_path = await process_photo(original_photo)
        if photo_path:
            try:
                # Use high-level method. If warning persists, it's a library notice.
                await app.set_profile_photo(photo=photo_path)
                print(f"Successfully updated profile photo using {photo_path}.")
                # Clean up if it was a temporary resized file
                if photo_path.startswith("ready_to_upload_"):
                    os.remove(photo_path)
            except Exception as e:
                print(f"Error updating profile photo: {e}")
        else:
            print(f"Error: Could not find or process {original_photo}!")

async def main():
    for acc in ACCOUNTS:
        await update_account(acc)
    print("\nAll tasks completed!")

if __name__ == "__main__":
    asyncio.run(main())
