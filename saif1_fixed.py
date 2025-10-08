import os
import zipfile
import glob
import shutil
import asyncio
import logging
import time
import json
import re
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InaccessibleMessage
from aiogram.filters import Command
from aiogram.exceptions import TelegramRetryAfter
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.auth import ResetAuthorizationsRequest

# ---------------- CONFIG -----------------
API_ID = 123456  # Replace with your actual API_ID
API_HASH = 'your_api_hash_here'  # Replace with your actual API_HASH
BOT_TOKEN = 'your_bot_token_here'  # Replace with your actual BOT_TOKEN
CONCURRENCY = 3
LOG_GROUP_ID = -1001234567890  # Replace with your actual log group ID
TEMP_FOLDER = "Sessions"
CONFIG_FOLDER = "config"
ADMIN_ID = "8326702690"
SELLING_BOTS = {
    "STTAR1": "@STTAR1_BOT",
    "TGLion": "@TGLion_API"
}
PAID_PASSWORD = "Saifk0"
RETRY_DELAY = 4

# Helper function to safely edit messages
async def safe_edit_message(call: CallbackQuery, text: str, reply_markup=None, parse_mode=None):
    """Safely edit a callback query message, handling type issues"""
    if call.message and isinstance(call.message, Message):
        try:
            await call.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception as e:
            # If editing fails, send a new message
            await call.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
UPDATE_INTERVAL = 1
TIME_THRESHOLD = 15
DEV_USERNAME = "@Saifistiak1"
DEV_TELEGRAM_LINK = "https://t.me/Saifistiak1"
DEV_CHANNEL_LINK = "https://t.me/Saifistiak1"
DEV_WEBSITE = "https://t.me/Saifistiak1"
DEV_ID = "8326702690"
SPAM_BOT_USERNAME = "@SpamBot"
# -----------------------------------------

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_data = {}
running_tasks = {}
account_sales_data = {}
pending_requests = set()
approved_users = set()
data_lock = asyncio.Lock()
maintenance_mode = False
user_approval_required = True

# Create directories
os.makedirs(CONFIG_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Load/Save functions
def load_data():
    global approved_users, account_sales_data, pending_requests, maintenance_mode, user_approval_required
    try:
        if os.path.exists(os.path.join(CONFIG_FOLDER, "approved_users.json")):
            with open(os.path.join(CONFIG_FOLDER, "approved_users.json"), "r") as f:
                approved_users = set(json.load(f))
    except Exception as e:
        logger.error(f"Error loading approved users: {e}")

    try:
        if os.path.exists(os.path.join(CONFIG_FOLDER, "sales_data.json")):
            with open(os.path.join(CONFIG_FOLDER, "sales_data.json"), "r") as f:
                account_sales_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading sales data: {e}")

    try:
        if os.path.exists(os.path.join(CONFIG_FOLDER, "pending_requests.json")):
            with open(os.path.join(CONFIG_FOLDER, "pending_requests.json"), "r") as f:
                pending_requests = set(json.load(f))
    except Exception as e:
        logger.error(f"Error loading pending requests: {e}")

    try:
        if os.path.exists(os.path.join(CONFIG_FOLDER, "settings.json")):
            with open(os.path.join(CONFIG_FOLDER, "settings.json"), "r") as f:
                settings = json.load(f)
                maintenance_mode = settings.get("maintenance_mode", False)
                user_approval_required = settings.get("user_approval_required", True)
    except Exception as e:
        logger.error(f"Error loading settings: {e}")

def save_data():
    try:
        with open(os.path.join(CONFIG_FOLDER, "approved_users.json"), "w") as f:
            json.dump(list(approved_users), f)
    except Exception as e:
        logger.error(f"Error saving approved users: {e}")

    try:
        with open(os.path.join(CONFIG_FOLDER, "sales_data.json"), "w") as f:
            json.dump(account_sales_data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving sales data: {e}")

    try:
        with open(os.path.join(CONFIG_FOLDER, "pending_requests.json"), "w") as f:
            json.dump(list(pending_requests), f)
    except Exception as e:
        logger.error(f"Error saving pending requests: {e}")

    try:
        settings = {"maintenance_mode": maintenance_mode, "user_approval_required": user_approval_required}
        with open(os.path.join(CONFIG_FOLDER, "settings.json"), "w") as f:
            json.dump(settings, f)
    except Exception as e:
        logger.error(f"Error saving settings: {e}")

load_data()

# Utility functions
async def extract_zip(zip_path, user_id):
    folder = os.path.join(TEMP_FOLDER, str(user_id))
    if os.path.exists(folder):
        shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(folder)
    except zipfile.BadZipFile:
        raise
    return folder

async def load_sessions(folder):
    return glob.glob(os.path.join(folder, "*.session"))

def progress_bar(done, total, length=20):
    if total == 0:
        return "🔷" * length + " 0%"
    filled = int(length * done / total)
    empty = length - filled
    bar = "🔥" * filled + "⚫" * empty
    percent = int(done / total * 100)
    return f"{bar} {percent}%"

async def log_to_channel(message, user_info=None):
    try:
        if user_info:
            log_message = f"📊 {message}\n\n👤 User: {user_info}"
        else:
            log_message = f"📊 {message}"
        
        await bot.send_message(LOG_GROUP_ID, log_message, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to log to channel: {e}")

def get_main_menu(user_id):
    if str(user_id) == ADMIN_ID:
        keyboard = [
            [
                InlineKeyboardButton(text="🤖 Auto Sell Accounts", callback_data="auto_sell")
            ],
            [
                InlineKeyboardButton(text="👥 User Management", callback_data="user_management"),
                InlineKeyboardButton(text="📊 Sales Stats", callback_data="sales_stats")
            ],
            [
                InlineKeyboardButton(text="⚙️ Admin Settings", callback_data="admin_settings"),
                InlineKeyboardButton(text="🗑️ Reset Database", callback_data="reset_database")
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton(text="📱 Session zip to OTP", callback_data="otp_tool"),
                InlineKeyboardButton(text="🤖 Check Spam Account", callback_data="check_spam")
            ],
            [
                InlineKeyboardButton(text="🆕 Create Session", callback_data="create_session"),
                InlineKeyboardButton(text="🤖 Auto Sell Accounts", callback_data="auto_sell")
            ]
        ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Account Seller Class
class AccountSeller:
    def __init__(self, selling_bot="STTAR1"):
        self.is_running = False
        self.current_task = None
        self.progress = {}
        self.main_client = None
        self.selling_bot = SELLING_BOTS.get(selling_bot, "@STTAR1_BOT")
        self.client_lock = asyncio.Lock()

    async def initialize_main_account(self):
        try:
            main_session = os.path.join(CONFIG_FOLDER, "main.session")
            if not os.path.exists(main_session):
                return False, "❌ Main account session not found. Place 'main.session' in config folder."
            
            async with self.client_lock:
                if self.main_client:
                    try:
                        if self.main_client.is_connected():
                            self.main_client.disconnect()
                    except Exception:
                        pass

                self.main_client = TelegramClient(main_session, API_ID, API_HASH)
                await self.main_client.connect()
                
                if not await self.main_client.is_user_authorized():
                    if self.main_client.is_connected():
                        self.main_client.disconnect()
                    return False, "❌ Main account not authorized."
                
                try:
                    await self.main_client.send_message(self.selling_bot, "/start")
                    await asyncio.sleep(2)
                except Exception as e:
                    return False, f"❌ Cannot message selling bot: {str(e)}"
            
            return True, "✅ Main account initialized!"
            
        except Exception as e:
            return False, f"❌ Error initializing main account: {str(e)}"
    
    async def sell_single_account(self, session_path, user_id, progress_msg=None):
        try:
            # Extract phone number
            client = TelegramClient(session_path, API_ID, API_HASH)
            await client.connect()

            if not await client.is_user_authorized():
                if client.is_connected():
                    client.disconnect()
                return False, "Session not authorized"

            await client.connect()
            me = await client.get_me()
            phone_number = getattr(me, "phone", "")
            phone_number = re.sub(r"\s+", "", phone_number)
            if phone_number and not phone_number.startswith("+"):
                phone_number = f"+{phone_number}"

            if client.is_connected():
                client.disconnect()

            if not phone_number:
                return False, "No phone number found in session"

            # Send phone number to selling bot
            if not self.main_client:
                return False, "Main client not initialized"
                
            await self.main_client.send_message(self.selling_bot, phone_number)
            await asyncio.sleep(3)

            # Wait for OTP request
            otp_requested = False
            start_time = time.time()
            while time.time() - start_time < 60:
                if not self.main_client:
                    break
                messages = await self.main_client.get_messages(self.selling_bot, limit=5)
                if messages:
                    # messages is already a list, no need to iterate if it's a single message
                    if not isinstance(messages, list):
                        messages = [messages]
                    for msg in messages:
                        txt = getattr(msg, 'text', '') or getattr(msg, 'message', '') or ""
                        if self.selling_bot == "@STTAR1_BOT":
                            if "Enter the code sent to the number" in txt.lower() or "code" in txt.lower():
                                otp_requested = True
                                break
                        elif self.selling_bot == "@TGLion_API":
                            if "send the code" in txt.lower() or "code" in txt.lower():
                                otp_requested = True
                                break
                if otp_requested:
                    break
                await asyncio.sleep(2)

            if not otp_requested:
                if self.main_client:
                    await self.main_client.send_message(self.selling_bot, "/cancel")
                return False, "OTP not requested"

            # Get OTP
            otp_code = await self.get_otp_code(session_path)
            if not otp_code:
                if self.main_client:
                    await self.main_client.send_message(self.selling_bot, "/cancel")
                return False, "OTP not found"

            # Send OTP
            if self.main_client:
                await self.main_client.send_message(self.selling_bot, otp_code)
                await asyncio.sleep(3)

            # Wait for confirmation
            confirmed = False
            start_time = time.time()
            while time.time() - start_time < 60:
                if not self.main_client:
                    break
                messages = await self.main_client.get_messages(self.selling_bot, limit=5)
                if messages:
                    # messages is already a list, no need to iterate if it's a single message
                    if not isinstance(messages, list):
                        messages = [messages]
                    for msg in messages:
                        txt = getattr(msg, 'text', '') or getattr(msg, 'message', '') or ""
                        if self.selling_bot == "@STTAR1_BOT":
                            if "account received" in txt.lower() and "log out" in txt.lower():
                                confirmed = True
                                break
                        elif self.selling_bot == "@TGLion_API":
                            if "account received" in txt.lower() or "completed" in txt.lower():
                                confirmed = True
                                break
                if confirmed:
                    break
                await asyncio.sleep(2)

            if not confirmed:
                if self.main_client:
                    await self.main_client.send_message(self.selling_bot, "/cancel")
                return False, "No confirmation received"

            return True, f"✅ Account {phone_number} sold successfully!"

        except Exception as e:
            try:
                if self.main_client:
                    await self.main_client.send_message(self.selling_bot, "/cancel")
            except Exception:
                pass
            return False, f"Error: {str(e)}"

    async def get_otp_code(self, session_path: str, timeout: int = 120) -> str:
        """Get OTP code from session by monitoring Telegram system messages"""
        client = TelegramClient(session_path, API_ID, API_HASH)
        otp_result = ""

        try:
            await client.connect()
            if not await client.is_user_authorized():
                return ""

            # Client is already connected, no need to start again
            loop = asyncio.get_event_loop()
            event_future = loop.create_future()

            @client.on(events.NewMessage(from_users=777000))
            async def handler(event):
                nonlocal otp_result
                text = event.raw_text or ""
                otp_match = re.search(r'\b\d{4,6}\b', text)
                if otp_match:
                    otp_result = otp_match.group(0)
                    if not event_future.done():
                        event_future.set_result(otp_result)

            try:
                await asyncio.wait_for(event_future, timeout=timeout)
            except asyncio.TimeoutError:
                pass

            return otp_result

        except Exception as e:
            logger.error(f"Error getting OTP: {e}")
            return ""
        finally:
            try:
                if client.is_connected():
                    client.disconnect()
            except Exception:
                pass

    async def start_selling(self, user_id, session_files, selling_bot="STTAR1"):
        self.selling_bot = SELLING_BOTS.get(selling_bot, "@STTAR1_BOT")
        
        if self.is_running:
            await bot.send_message(user_id, "⚠️ Selling process already running!")
            return
            
        self.is_running = True
        total = len(session_files)
        successful = []
        failed = []
        
        success, message = await self.initialize_main_account()
        if not success:
            await bot.send_message(user_id, message)
            self.is_running = False
            return
        
        progress_msg = await bot.send_message(
            user_id,
            f"🚀 <b>Starting Automated Account Selling</b>\n\n"
            f"🤖 Bot: {self.selling_bot}\n"
            f"📊 Total Accounts: {total}\n"
            f"✅ Successful: 0\n"
            f"❌ Failed: 0\n"
            f"🔄 Progress: {progress_bar(0, total)}\n\n"
            f"⚡ Status: Starting...",
            parse_mode="HTML"
        )
        
        for i, session_file in enumerate(session_files, 1):
            if not self.is_running:
                break
                
            try:
                success, message = await self.sell_single_account(session_file, user_id, progress_msg)
                
                async with data_lock:
                    today = datetime.now().strftime("%Y-%m-%d")
                    account_sales_data.setdefault("total_sold", 0)
                    account_sales_data.setdefault("total_failed", 0)
                    account_sales_data.setdefault("daily_sales", {})
                    account_sales_data.setdefault("user_sales", {})
                    
                    if success:
                        successful.append(session_file)
                        account_sales_data["total_sold"] += 1
                        account_sales_data["daily_sales"][today] = account_sales_data["daily_sales"].get(today, 0) + 1
                        account_sales_data["user_sales"][str(user_id)] = account_sales_data["user_sales"].get(str(user_id), 0) + 1
                    else:
                        failed.append(session_file)
                        account_sales_data["total_failed"] += 1
                    
                    save_data()
                
                if i % UPDATE_INTERVAL == 0 or i == total:
                    try:
                        await progress_msg.edit_text(
                            f"🚀 <b>Automated Account Selling</b>\n\n"
                            f"🤖 Bot: {self.selling_bot}\n"
                            f"📊 Total Accounts: {total}\n"
                            f"✅ Successful: {len(successful)}\n"
                            f"❌ Failed: {len(failed)}\n"
                            f"🔄 Progress: {progress_bar(i, total)}\n\n"
                            f"⚡ Status: Processing... ({i}/{total})",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
                        
                await log_to_channel(
                    f"🔰 Account Sale {'✅ Successful' if success else '❌ Failed'}\n"
                    f"🤖 Bot: {self.selling_bot}\n"
                    f"📱 Session: {os.path.basename(session_file)}\n"
                    f"💬 Message: {message}\n"
                    f"📊 Progress: {i}/{total}",
                    f"ID: {user_id}"
                )
                
                await asyncio.sleep(3)
                
            except Exception as e:
                failed.append(session_file)
                logger.exception(f"Error selling account: {e}")
        
        # Create result ZIPs
        if successful:
            success_zip = f"successful_sales_{user_id}.zip"
            with zipfile.ZipFile(success_zip, 'w') as zipf:
                for session in successful:
                    zipf.write(session, os.path.basename(session))
        
        if failed:
            failed_zip = f"failed_sales_{user_id}.zip"
            with zipfile.ZipFile(failed_zip, 'w') as zipf:
                for session in failed:
                    zipf.write(session, os.path.basename(session))
        
        success_rate = (len(successful) / total) * 100 if total > 0 else 0
        
        result_text = (
            f"🎉 <b>Account Selling Completed!</b>\n\n"
            f"🤖 Bot: {self.selling_bot}\n"
            f"📊 Total Processed: {total}\n"
            f"✅ Successful Sales: {len(successful)}\n"
            f"❌ Failed Sales: {len(failed)}\n"
            f"💰 Success Rate: {success_rate:.2f}%"
        )
        
        await bot.send_message(user_id, result_text, parse_mode="HTML")
        
        if successful:
            with open(success_zip, 'rb') as f:
                await bot.send_document(user_id, types.BufferedInputFile(f.read(), filename="✅ Successful_Sales.zip"))
            os.remove(success_zip)
        
        if failed:
            with open(failed_zip, 'rb') as f:
                await bot.send_document(user_id, types.BufferedInputFile(f.read(), filename="❌ Failed_Sales.zip"))
            os.remove(failed_zip)
        
        self.is_running = False
        
        await log_to_channel(
            f"🏁 Selling Completed!\n"
            f"🤖 Bot: {self.selling_bot}\n"
            f"✅ Successful: {len(successful)}\n"
            f"❌ Failed: {len(failed)}\n"
            f"💰 Success Rate: {success_rate:.2f}%",
            f"ID: {user_id}"
        )

    async def stop_selling(self):
        self.is_running = False
        async with self.client_lock:
            if self.main_client and self.main_client.is_connected():
                try:
                    self.main_client.disconnect()
                except Exception:
                    pass

account_seller = AccountSeller()

# Bot handlers
@dp.message(Command("start"))
async def start(message: Message):
    if not message.from_user:
        await message.answer("❌ User information not available.")
        return
        
    user_id = message.from_user.id
    
    if maintenance_mode and str(user_id) != ADMIN_ID:
        await message.answer(
            "🔧 <b>System Under Maintenance</b>\n\n"
            "The bot is currently under maintenance. Please try again later.",
            parse_mode="HTML"
        )
        return
    
    if user_approval_required and str(user_id) != ADMIN_ID and user_id not in approved_users:
        pending_requests.add(user_id)
        save_data()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton(text="❌ Deny", callback_data=f"deny_{user_id}")
            ]
        ])
        
        user_name = message.from_user.full_name or f"User {user_id}"
        username = message.from_user.username or 'N/A'
        
        await bot.send_message(
            ADMIN_ID,
            f"🔔 New User Request\n\n"
            f"👤 User: {user_name}\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"📧 Username: @{username}\n\n"
            f"Choose action:",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        await message.answer(
            "👋 <b>Welcome!</b>\n\n"
            "📋 Your access request has been sent to the admin. Please wait for approval.",
            parse_mode="HTML"
        )
        return
    
    await message.answer(
        "🤖 <b>Welcome to Telegram Session Tools Bot!</b>\n\n"
        "Choose what you want to do:",
        reply_markup=get_main_menu(user_id),
        parse_mode="HTML"
    )

# Admin settings
@dp.callback_query(F.data == "admin_settings")
async def admin_settings_callback(call: CallbackQuery):
    if not call.from_user or str(call.from_user.id) != ADMIN_ID:
        await call.answer("❌ Only admin can access settings.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔧 Maintenance Mode", callback_data="toggle_maintenance"),
            InlineKeyboardButton(text="👥 User Approval", callback_data="toggle_approval")
        ],
        [
            InlineKeyboardButton(text="🤖 Switch Selling Bot", callback_data="switch_bot"),
            InlineKeyboardButton(text="🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ])
    
    status = "ON" if maintenance_mode else "OFF"
    approval = "ON" if user_approval_required else "OFF"
    current_bot = "STTAR1" if account_seller.selling_bot == "@STTAR1_BOT" else "TGLion"
    
    await safe_edit_message(
        call,
        f"⚙️ <b>Admin Settings</b>\n\n"
        f"🔧 Maintenance Mode: <b>{status}</b>\n"
        f"👥 User Approval Required: <b>{approval}</b>\n"
        f"🤖 Selling Bot: <b>{current_bot}</b>\n\n"
        f"Choose setting to toggle:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await call.answer()

@dp.callback_query(F.data == "toggle_maintenance")
async def toggle_maintenance(call: CallbackQuery):
    if not call.from_user or str(call.from_user.id) != ADMIN_ID:
        await call.answer("❌ Only admin.")
        return
    
    global maintenance_mode
    maintenance_mode = not maintenance_mode
    save_data()
    status = "ON" if maintenance_mode else "OFF"
    await call.answer(f"🔧 Maintenance Mode: {status}")
    await admin_settings_callback(call)

@dp.callback_query(F.data == "toggle_approval")
async def toggle_approval(call: CallbackQuery):
    if not call.from_user or str(call.from_user.id) != ADMIN_ID:
        await call.answer("❌ Only admin.")
        return
    
    global user_approval_required
    user_approval_required = not user_approval_required
    save_data()
    status = "ON" if user_approval_required else "OFF"
    await call.answer(f"👥 User Approval: {status}")
    await admin_settings_callback(call)

@dp.callback_query(F.data == "switch_bot")
async def switch_bot(call: CallbackQuery):
    if not call.from_user or str(call.from_user.id) != ADMIN_ID:
        await call.answer("❌ Only admin.")
        return
    
    current = "STTAR1" if account_seller.selling_bot == "@STTAR1_BOT" else "TGLion"
    new_bot = "TGLion" if current == "STTAR1" else "STTAR1"
    account_seller.selling_bot = SELLING_BOTS[new_bot]
    await call.answer(f"🤖 Switched to {new_bot}")
    await admin_settings_callback(call)

# Auto sell
@dp.callback_query(F.data == "auto_sell")
async def auto_sell_callback(call: CallbackQuery):
    if not call.from_user:
        await call.answer("❌ User data not available.")
        return
        
    user_id = call.from_user.id
    
    if str(user_id) != ADMIN_ID and user_id not in approved_users:
        await call.answer("❌ Access denied.")
        return
    
    await safe_edit_message(
        call,
        "🤖 <b>Automated Account Selling</b>\n\n"
        "🚀 Sell accounts automatically.\n\n"
        "Choose action:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Start Selling", callback_data="start_selling")],
            [InlineKeyboardButton(text="⏸️ Stop Selling", callback_data="stop_selling")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )
    await call.answer()

@dp.callback_query(F.data == "start_selling")
async def start_selling_callback(call: CallbackQuery):
    user_id = call.from_user.id
    
    if str(user_id) != ADMIN_ID and user_id not in approved_users:
        await call.answer("❌ Access denied.")
        return
    
    user_data[user_id] = {"action": "auto_sell_upload"}
    
    await bot.send_message(
        user_id,
        "📤 <b>Upload Session ZIP</b>\n\n"
        "Upload your ZIP file containing account sessions:",
        parse_mode="HTML"
    )
    await call.answer()

# Handle ZIP upload
@dp.message(F.content_type == types.ContentType.DOCUMENT)
async def handle_zip(message: Message):
    if not message.from_user:
        await message.reply("❌ User information not available.")
        return
        
    user_id = message.from_user.id
    data = user_data.get(user_id, {})
    
    if "action" not in data:
        await message.reply("❌ Select an action first.")
        return

    if not message.document:
        await message.reply("❌ No document found.")
        return

    doc = message.document
    if not doc.file_name or not doc.file_name.endswith(".zip"):
        await message.reply("❌ Upload a ZIP file.")
        return

    action = data["action"]

    if action == "auto_sell_upload":
        zip_path = os.path.join(TEMP_FOLDER, f"{user_id}_sell_{doc.file_name}")
        
        try:
            await bot.download(doc, destination=zip_path)
        except Exception as e:
            await message.reply(f"❌ Error downloading file: {e}")
            return

        user_name = message.from_user.full_name or f"User {user_id}"
        
        await log_to_channel(
            f"📦 Auto Sell ZIP Uploaded\n"
            f"📁 File: {doc.file_name}\n"
            f"👤 By: {user_name}",
            f"ID: {user_id}"
        )

        try:
            folder = await extract_zip(zip_path, user_id)
            user_data[user_id]["folder"] = folder

            session_files = await load_sessions(folder)
            total = len(session_files)
            
            if total == 0:
                await message.reply("❌ No session files found.")
                return

            await message.reply(
                f"✅ <b>ZIP Uploaded!</b>\n\n"
                f"📊 Accounts Found: {total}\n"
                f"🚀 Starting automated selling...",
                parse_mode="HTML"
            )

            asyncio.create_task(account_seller.start_selling(user_id, session_files))
        except Exception as e:
            await message.reply(f"❌ Error processing ZIP: {e}")

# Other handlers (user management, stats, etc.)
@dp.callback_query(F.data == "user_management")
async def user_management_callback(call: CallbackQuery):
    if not call.from_user or str(call.from_user.id) != ADMIN_ID:
        await call.answer("❌ Only admin.")
        return
    
    await safe_edit_message(
        call,
        "👥 <b>User Management</b>\n\n"
        "Manage user access:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 Pending Requests", callback_data="view_requests")],
            [InlineKeyboardButton(text="✅ Approved Users", callback_data="view_approved")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )
    await call.answer()

@dp.callback_query(F.data == "view_requests")
async def view_requests_callback(call: CallbackQuery):
    if str(call.from_user.id) != ADMIN_ID:
        await call.answer("❌ Only admin.")
        return
    
    if not pending_requests:
        users_text = "No pending requests."
    else:
        users_text = "\n".join([f"🆔 {user_id}" for user_id in pending_requests])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh", callback_data="view_requests")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="user_management")]
    ])
    
    await safe_edit_message(
        call,
        f"📋 <b>Pending Requests</b>\n\n{users_text}",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await call.answer()

@dp.callback_query(F.data == "view_approved")
async def view_approved_callback(call: CallbackQuery):
    if str(call.from_user.id) != ADMIN_ID:
        await call.answer("❌ Only admin.")
        return
    
    if not approved_users:
        users_text = "No approved users."
    else:
        users_text = "\n".join([f"🆔 {user_id}" for user_id in approved_users])
    
    await safe_edit_message(
        call,
        f"✅ <b>Approved Users</b>\n\n{users_text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data="user_management")]
        ]),
        parse_mode="HTML"
    )
    await call.answer()

@dp.callback_query(F.data.startswith("approve_"))
async def approve_callback(call: CallbackQuery):
    if not call.from_user or str(call.from_user.id) != ADMIN_ID:
        await call.answer("❌ Only admin.")
        return
    
    if not call.data:
        await call.answer("❌ Invalid callback data.")
        return
    
    try:
        user_id = int(call.data.split("_")[1])
        approved_users.add(user_id)
        if user_id in pending_requests:
            pending_requests.remove(user_id)
        save_data()
        
        await safe_edit_message(call, f"✅ User {user_id} approved!")
        await bot.send_message(user_id, "🎉 Access approved! Use /start.")
        await call.answer()
    except (ValueError, IndexError):
        await call.answer("❌ Invalid user ID.")

@dp.callback_query(F.data.startswith("deny_"))
async def deny_callback(call: CallbackQuery):
    if not call.from_user or str(call.from_user.id) != ADMIN_ID:
        await call.answer("❌ Only admin.")
        return
    
    if not call.data:
        await call.answer("❌ Invalid callback data.")
        return
    
    try:
        user_id = int(call.data.split("_")[1])
        if user_id in pending_requests:
            pending_requests.remove(user_id)
        save_data()
        
        await safe_edit_message(call, f"❌ User {user_id} denied.")
        await bot.send_message(user_id, "❌ Access denied.")
        await call.answer()
    except (ValueError, IndexError):
        await call.answer("❌ Invalid user ID.")

@dp.callback_query(F.data == "sales_stats")
async def sales_stats_callback(call: CallbackQuery):
    if not call.from_user or str(call.from_user.id) != ADMIN_ID:
        await call.answer("❌ Only admin.")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_sales = account_sales_data.get("daily_sales", {}).get(today, 0)
    
    total_sold = account_sales_data.get('total_sold', 0)
    total_failed = account_sales_data.get('total_failed', 0)
    total_attempts = total_sold + total_failed
    success_rate = (total_sold / total_attempts * 100) if total_attempts > 0 else 0
    
    stats_text = (
        f"📊 <b>Sales Statistics</b>\n\n"
        f"💰 Total Sold: {total_sold}\n"
        f"❌ Total Failed: {total_failed}\n"
        f"📈 Today's Sales: {today_sales}\n"
        f"🎯 Success Rate: {success_rate:.2f}%\n\n"
        f"👥 Top Users:\n"
    )
    
    user_sales = sorted(account_sales_data.get("user_sales", {}).items(), key=lambda x: x[1], reverse=True)[:5]
    for i, (user_id, sales) in enumerate(user_sales, 1):
        stats_text += f"{i}. User {user_id}: {sales} sales\n"
    
    await safe_edit_message(call, stats_text, parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data == "stop_selling")
async def stop_selling_callback(call: CallbackQuery):
    if account_seller.is_running:
        await account_seller.stop_selling()
        await call.answer("🛑 Selling stopped!")
    else:
        await call.answer("⚠️ No selling running!")

@dp.callback_query(F.data == "main_menu")
async def main_menu_callback(call: CallbackQuery):
    if not call.from_user:
        await call.answer("❌ User data not available.")
        return
    
    await safe_edit_message(
        call,
        "<b>🤖 Welcome to Telegram Session Tools Bot!</b>\n\nChoose what you want to do:",
        reply_markup=get_main_menu(call.from_user.id),
        parse_mode="HTML"
    )
    await call.answer()

# Run bot
async def start_bot():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    print("🤖 Advanced Telegram Bot starting...")
    print("✅ Auto Account Selling System")
    print("👥 User Management System") 
    print("📊 Sales Statistics Tracking")
    print("🔒 Admin-Controlled Access")
    print("🚀 Bot started successfully!")
    
    asyncio.run(start_bot())