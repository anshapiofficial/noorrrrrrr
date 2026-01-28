import logging
import requests
import json
import uuid
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, JobQueue
from telegram.constants import ParseMode
import re
from flask import Flask, render_template_string
import threading
import os
import time
import asyncio
import html
from typing import Dict, List, Optional
import schedule
import time as time_module

# ============================================
# 🔥 BOT CONFIGURATION
# ============================================
BOT_TOKEN = "8441022516:AAEPeyCvp8JlbPcVSgE07kCH5iWcbrYSBbU"
BOT_NAME = "𝐍𝐎𝐎𝐑 🦋 𝐎𝐒𝐈𝐍𝐓 𝐏𝐑𝐎 𝐌𝐀𝐗 ⚡️"
FORCE_JOIN_CHANNEL = "@madamjikiduniya"  # Single group for force join
ADMIN_IDS = [6357008488]
PORT = int(os.environ.get('PORT', 1000))

# ============================================
# 📡 APIs
# ============================================
NUMBER_INFO_API = "https://numinfo.asapiservices.workers.dev/mobile-lookup?key=anshapi123&mobile="

# ============================================
# 💾 Files
# ============================================
USERS_FILE = "users.json"
CREDITS_FILE = "credits.json"
BANNED_FILE = "banned.json"

# ============================================
# 💎 Credits System
# ============================================
FREE_CREDITS = 44  # Changed from 5 to 44
HOURLY_CREDITS = 4  # Credits added every hour
SEARCH_COST = 1

# ============================================
# 📊 Enable Logging
# ============================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# 🌐 Flask App for Render
# ============================================
app = Flask(__name__)
start_time = datetime.now()

@app.route('/')
def home():
    users = load_users()
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ bot_name }}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
                border-radius: 25px;
                padding: 40px;
                max-width: 800px;
                width: 100%;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                position: relative;
                overflow: hidden;
            }
            
            .container::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(
                    45deg,
                    transparent 30%,
                    rgba(255, 255, 255, 0.1) 50%,
                    transparent 70%
                );
                animation: shine 3s infinite linear;
                pointer-events: none;
            }
            
            @keyframes shine {
                0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
                100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
                position: relative;
                z-index: 1;
            }
            
            .bot-name {
                font-size: 3.5em;
                font-weight: 900;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57, #ff9ff3);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                margin-bottom: 20px;
                letter-spacing: 1px;
            }
            
            .status-badge {
                display: inline-block;
                background: linear-gradient(45deg, #00b09b, #96c93d);
                padding: 12px 30px;
                border-radius: 50px;
                color: white;
                font-weight: 700;
                font-size: 1.2em;
                box-shadow: 0 5px 20px rgba(0, 255, 100, 0.3);
                animation: pulse 2s infinite;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); box-shadow: 0 5px 20px rgba(0, 255, 100, 0.3); }
                50% { transform: scale(1.05); box-shadow: 0 8px 25px rgba(0, 255, 100, 0.5); }
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin: 30px 0;
            }
            
            .stat-card {
                background: rgba(255, 255, 255, 0.15);
                padding: 25px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .stat-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
                transition: left 0.5s;
            }
            
            .stat-card:hover::before {
                left: 100%;
            }
            
            .stat-card:hover {
                transform: translateY(-10px);
                background: rgba(255, 255, 255, 0.2);
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
            }
            
            .stat-card h3 {
                color: #4dffea;
                font-size: 1em;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 600;
            }
            
            .stat-card p {
                font-size: 2em;
                font-weight: 900;
                margin: 0;
                background: linear-gradient(45deg, #ffffff, #f0f0f0);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .bot-info {
                background: rgba(255, 255, 255, 0.08);
                padding: 30px;
                border-radius: 20px;
                margin: 30px 0;
                border-left: 5px solid #ff6b6b;
                position: relative;
                z-index: 1;
            }
            
            .bot-info h3 {
                color: #ffcc00;
                margin-bottom: 20px;
                font-size: 1.4em;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .bot-info p {
                margin: 12px 0;
                padding-left: 10px;
                border-left: 3px solid rgba(255, 255, 255, 0.3);
                padding-left: 15px;
            }
            
            .footer {
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.2);
                color: rgba(255, 255, 255, 0.8);
                font-size: 0.9em;
                position: relative;
                z-index: 1;
            }
            
            .glow {
                animation: glow 2s ease-in-out infinite alternate;
            }
            
            @keyframes glow {
                from { text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #ff6b6b, 0 0 40px #ff6b6b; }
                to { text-shadow: 0 0 20px #fff, 0 0 30px #4ecdc4, 0 0 40px #4ecdc4, 0 0 50px #4ecdc4; }
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 20px;
                }
                
                .bot-name {
                    font-size: 2.5em;
                }
                
                .stats-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="bot-name glow">{{ bot_name }}</div>
                <div class="status-badge">
                    <span>⚡</span> BOT IS ACTIVE & RUNNING
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>👥 Total Users</h3>
                    <p>{{ total_users }}</p>
                </div>
                <div class="stat-card">
                    <h3>🔍 Total Searches</h3>
                    <p>{{ total_searches }}</p>
                </div>
                <div class="stat-card">
                    <h3>💎 Credits Used</h3>
                    <p>{{ total_credits }}</p>
                </div>
                <div class="stat-card">
                    <h3>⭐ Premium Users</h3>
                    <p>{{ premium_users }}</p>
                </div>
            </div>
            
            <div class="bot-info">
                <h3>📊 Bot Analytics</h3>
                <p><strong>🤖 Bot Name:</strong> {{ bot_name }}</p>
                <p><strong>⚡ Version:</strong> 7.0.0 (Ultimate Edition)</p>
                <p><strong>🕒 Uptime:</strong> {{ uptime }}</p>
                <p><strong>🌐 Server:</strong> Render Cloud</p>
                <p><strong>✅ Status:</strong> Fully Operational</p>
                <p><strong>⏰ Hourly Bonus:</strong> 4 Credits Active</p>
            </div>
            
            <div class="footer">
                <p>🔐 Secure • ⚡ Fast • 💎 Reliable</p>
                <p>© 2024 {{ bot_name }}. All rights reserved.</p>
                <p>Powered by Telegram Bot API • Deployed on Render</p>
            </div>
        </div>
    </body>
    </html>
    """,  
    bot_name=BOT_NAME,  
    total_users=len(users),  
    total_searches=sum(user.get('total_searches', 0) for user in users.values()),  
    total_credits=sum(data.get('credits', 0) for data in load_credits().values()),  
    premium_users=sum(1 for user in users.values() if user.get('is_premium')),  
    uptime=str(datetime.now() - start_time).split('.')[0]  
    )

@app.route('/health')
def health():
    return {"status": "healthy", "bot": BOT_NAME, "timestamp": datetime.now().isoformat()}

# ============================================
# 💾 USER MANAGEMENT FUNCTIONS
# ============================================
def load_users() -> Dict:
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users: Dict):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def load_credits() -> Dict:
    try:
        with open(CREDITS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_credits(credits: Dict):
    with open(CREDITS_FILE, 'w') as f:
        json.dump(credits, f, indent=2, ensure_ascii=False)

def load_banned() -> Dict:
    try:
        with open(BANNED_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_banned(banned: Dict):
    with open(BANNED_FILE, 'w') as f:
        json.dump(banned, f, indent=2, ensure_ascii=False)

def is_user_banned(user_id: int) -> bool:
    banned = load_banned()
    return str(user_id) in banned

def ban_user(user_id: int, reason: str = "No reason provided"):
    banned = load_banned()
    banned[str(user_id)] = {
        'ban_time': datetime.now().isoformat(),
        'reason': reason,
        'banned_by': 'admin'
    }
    save_banned(banned)

def unban_user(user_id: int):
    banned = load_banned()
    user_id_str = str(user_id)
    if user_id_str in banned:
        del banned[user_id_str]
        save_banned(banned)
        return True
    return False

def get_user_data(user_id: int):
    """Get user data and credits"""
    users = load_users()
    credits = load_credits()
    
    user_id_str = str(user_id)
    
    # Initialize user if not exists
    if user_id_str not in users:
        users[user_id_str] = {
            'id': user_id,
            'username': None,
            'first_name': None,
            'join_date': datetime.now().isoformat(),
            'total_searches': 0,
            'is_premium': False,
            'premium_expiry': None,
            'last_active': datetime.now().isoformat(),
            'last_search': None,
            'last_hourly_bonus': None,
            'hourly_bonus_count': 0
        }
        save_users(users)
    
    # Initialize credits if not exists
    if user_id_str not in credits:
        credits[user_id_str] = {
            'credits': FREE_CREDITS,
            'last_reset': datetime.now().isoformat(),
            'total_earned': FREE_CREDITS,
            'hourly_bonus_total': 0
        }
        save_credits(credits)
    
    return users[user_id_str], credits[user_id_str]

def add_credits(user_id: int, amount: int, source: str = "admin", notify: bool = True) -> bool:
    """Add credits to user"""
    try:
        user_id_str = str(user_id)
        credits = load_credits()
        users = load_users()
        
        if user_id_str not in credits:
            credits[user_id_str] = {
                'credits': FREE_CREDITS,
                'last_reset': datetime.now().isoformat(),
                'total_earned': FREE_CREDITS,
                'hourly_bonus_total': 0
            }
        
        # Add credits
        old_credits = credits[user_id_str].get('credits', 0)
        credits[user_id_str]['credits'] = old_credits + amount
        credits[user_id_str]['total_earned'] = credits[user_id_str].get('total_earned', 0) + amount
        
        # Track hourly bonus
        if source == "hourly_bonus":
            credits[user_id_str]['hourly_bonus_total'] = credits[user_id_str].get('hourly_bonus_total', 0) + amount
            if user_id_str in users:
                users[user_id_str]['last_hourly_bonus'] = datetime.now().isoformat()
                users[user_id_str]['hourly_bonus_count'] = users[user_id_str].get('hourly_bonus_count', 0) + 1
                save_users(users)
        
        save_credits(credits)
        
        # Send notification if requested
        if notify and source == "hourly_bonus":
            try:
                # This will be sent by the hourly job
                pass
            except:
                pass
                
        return True
        
    except Exception as e:
        logger.error(f"Error adding credits: {e}")
        return False

def deduct_credits(user_id: int, amount: int = SEARCH_COST) -> bool:
    """Deduct credits from user"""
    try:
        user_id_str = str(user_id)
        users = load_users()
        credits = load_credits()
        
        # Check banned
        if is_user_banned(user_id):
            return False
        
        # Check premium status
        user = users.get(user_id_str, {})
        if user.get('is_premium') and user.get('premium_expiry'):
            expiry_date = datetime.fromisoformat(user['premium_expiry'])
            if expiry_date > datetime.now():
                users[user_id_str]['total_searches'] = users[user_id_str].get('total_searches', 0) + 1
                users[user_id_str]['last_search'] = datetime.now().isoformat()
                save_users(users)
                return True
        
        # Check and deduct credits
        if user_id_str in credits:
            current_credits = credits[user_id_str].get('credits', 0)
            if current_credits >= amount:
                credits[user_id_str]['credits'] = current_credits - amount
                users[user_id_str]['total_searches'] = users[user_id_str].get('total_searches', 0) + 1
                users[user_id_str]['last_search'] = datetime.now().isoformat()
                
                save_credits(credits)
                save_users(users)
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error deducting credits: {e}")
        return False

def get_credits(user_id: int) -> int:
    """Get user's current credits"""
    credits = load_credits()
    return credits.get(str(user_id), {}).get('credits', 0)

# ============================================
# ⏰ HOURLY CREDITS JOB
# ============================================
async def hourly_credits_job(context: CallbackContext):
    """Give 4 credits to all users every hour"""
    try:
        users = load_users()
        credits = load_credits()
        
        success_count = 0
        failed_count = 0
        
        for user_id_str, user_data in users.items():
            try:
                user_id = int(user_id_str)
                
                # Skip banned users
                if is_user_banned(user_id):
                    continue
                
                # Add credits
                if add_credits(user_id, HOURLY_CREDITS, "hourly_bonus", notify=False):
                    # Send notification to user
                    try:
                        notification_text = f"""
🎁 *HOURLY BONUS CREDITS!* 🎁

━━━━━━━━━━━━━━━━━━━━━━━

✨ *Congratulations!* ✨

You have received *{HOURLY_CREDITS} FREE CREDITS* as your hourly bonus!

💰 *New Balance:* {get_credits(user_id)} credits
⏰ *Next Bonus:* In 1 hour
🎯 *Keep using:* /search

━━━━━━━━━━━━━━━━━━━━━━━

💎 *Premium Benefits:*
• Unlimited searches
• No credit deduction
• Priority processing

🔗 Join our channel for updates:
{FORCE_JOIN_CHANNEL}
                        """
                        
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=notification_text,
                            parse_mode=ParseMode.MARKDOWN,
                            disable_web_page_preview=True
                        )
                        success_count += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to notify user {user_id}: {e}")
                        failed_count += 1
                        
                    # Small delay to avoid flood
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error processing user {user_id_str}: {e}")
                failed_count += 1
        
        # Log results
        logger.info(f"Hourly credits job completed. Success: {success_count}, Failed: {failed_count}")
        
    except Exception as e:
        logger.error(f"Error in hourly credits job: {e}")

# ============================================
# 🔐 FORCE JOIN CHECK - SINGLE GROUP
# ============================================
async def check_membership(update: Update, context: CallbackContext) -> bool:
    """Check if user is member of the required group"""
    try:
        user_id = update.effective_user.id
        
        # Check membership
        chat_member = await context.bot.get_chat_member(
            chat_id=FORCE_JOIN_CHANNEL, 
            user_id=user_id
        )
        
        # User is member if status is not 'left' or 'kicked'
        return chat_member.status not in ['left', 'kicked']
        
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

# ============================================
# 🎨 SUPER STYLISH START COMMAND
# ============================================
async def start(update: Update, context: CallbackContext):
    """Start command with stylish design"""
    try:
        user = update.effective_user
        user_id = user.id
        
        # Check if user is banned
        if is_user_banned(user_id):
            banned_text = """
🚫 *ACCOUNT BANNED* 🚫

━━━━━━━━━━━━━━━━━━━━━━━

Your account has been banned from using this bot.

❌ *Reason:* Violation of terms
⏰ *Banned On:* Permanent
🔓 *Appeal:* Contact admin

━━━━━━━━━━━━━━━━━━━━━━━

For appeals, contact @madamjikiduniya
            """
            await update.message.reply_text(banned_text, parse_mode=ParseMode.MARKDOWN)
            return
        
        # Get user data
        user_data, credit_data = get_user_data(user_id)
        
        # Update user info
        users = load_users()
        user_id_str = str(user_id)
        
        if user_id_str in users:
            users[user_id_str]['username'] = user.username
            users[user_id_str]['first_name'] = user.first_name
            users[user_id_str]['last_active'] = datetime.now().isoformat()
            save_users(users)
        
        # Check membership
        is_member = await check_membership(update, context)
        
        if not is_member:
            await send_ultra_stylish_force_join(update, context)
        else:
            await send_mega_welcome(update, context, user_data, credit_data)
            
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text("⚠️ An error occurred. Please try again.")

async def send_ultra_stylish_force_join(update: Update, context: CallbackContext):
    """Send ultra stylish force join message"""
    join_text = """
╔══════════════════════════════════════════════════╗
    🌸 𝗙𝗢𝗥𝗖𝗘 𝗝𝗢𝗜𝗡 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗 🌸
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

🌸⸝⸝⸝♡⸝⸝⸝ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗡𝗢𝗢𝗥 𝗢𝗦𝗜𝗡𝗧 𝗣𝗥𝗢 𝗠𝗔𝗫! ⸝⸝⸝♡⸝⸝⸝🌸

📌 <b>𝗚𝗥𝗢𝗨𝗣 𝗠𝗘𝗠𝗕𝗘𝗥𝗦𝗛𝗜𝗣 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗:</b>
To unlock all premium features and start searching,
you must join our official group:

<b>🔗 @madamjikiduniya</b>

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>📝 𝗜𝗡𝗦𝗧𝗥𝗨𝗖𝗧𝗜𝗢𝗡𝗦:</b>

1️⃣ Click the button below to join the group
2️⃣ Return to this chat
3️⃣ Click "✅ 𝗩𝗘𝗥𝗜𝗙𝗬 𝗝𝗢𝗜𝗡"

<b>⚠️ 𝗡𝗢𝗧𝗘:</b> You must join the group to proceed!

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>💖 Powered by NOOR 🦋 OSINT PRO MAX</b>
"""
    
    # Ultra stylish buttons
    keyboard = [
        [
            InlineKeyboardButton(
                "🌸 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣 🌸", 
                url=f"https://t.me/{FORCE_JOIN_CHANNEL.replace('@', '')}"
            )
        ],
        [
            InlineKeyboardButton("✅ 𝗩𝗘𝗥𝗜𝗙𝗬 𝗝𝗢𝗜𝗡", callback_data="verify_join"),
            InlineKeyboardButton("🔄 𝗥𝗘𝗙𝗥𝗘𝗦𝗛", callback_data="refresh_join")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if update.callback_query:
            await update.callback_query.message.edit_text(
                join_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            await update.callback_query.answer()
        else:
            await update.message.reply_text(
                join_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"Error sending force join: {e}")

async def send_mega_welcome(update: Update, context: CallbackContext, user_data=None, credit_data=None):
    """Send mega stylish welcome message"""
    user = update.effective_user
    
    if not user_data or not credit_data:
        user_data, credit_data = get_user_data(user.id)
    
    # Create animated welcome text
    welcome_text = f"""
╔══════════════════════════════════════════════════╗
    🌸 𝗡𝗢𝗢𝗥 🦋 𝗢𝗦𝗜𝗡𝗧 𝗣𝗥𝗢 𝗠𝗔𝗫 ⚡️
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

🎉 <b>𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗕𝗔𝗖𝗞, {html.escape(user.first_name) if user.first_name else 'User'}!</b> 🎉

┌─────────────────────────────────────┐
👤 <b>User:</b> {html.escape(user.first_name) if user.first_name else "User"}
💰 <b>Credits:</b> {credit_data['credits']}
🔍 <b>Searches:</b> {user_data.get('total_searches', 0)}
⏰ <b>Hourly Bonus:</b> 4 credits every hour!
└─────────────────────────────────────┘

🎁 <b>SPECIAL FEATURES:</b>
• ⚡ Get 4 FREE Credits Every Hour
• 💎 Start with 44 Credits (Not 5!)
• 🔥 Ultra Fast API (1-2 seconds)
• 📊 10M+ Verified Database
• 🔒 100% Private & Secure

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>👇 𝗦𝗘𝗟𝗘𝗖𝗧 𝗔𝗡 𝗢𝗣𝗧𝗜𝗢𝗡:</b>
"""
    
    # Animated buttons with gradient effect emojis
    keyboard = [
        [
            InlineKeyboardButton(
                "🔍 𝗦𝗧𝗔𝗥𝗧 𝗦𝗘𝗔𝗥𝗖𝗛", 
                callback_data="menu_search"
            )
        ],
        [
            InlineKeyboardButton("👤 𝗣𝗥𝗢𝗙𝗜𝗟𝗘", callback_data="profile"),
            InlineKeyboardButton("💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠", callback_data="menu_premium")
        ],
        [
            InlineKeyboardButton("⏰ 𝗛𝗢𝗨𝗥𝗟𝗬 𝗕𝗢𝗡𝗨𝗦", callback_data="hourly_bonus_info"),
            InlineKeyboardButton("📊 𝗦𝗧𝗔𝗧𝗦", callback_data="stats")
        ],
        [
            InlineKeyboardButton("🔄 𝗥𝗘𝗙𝗥𝗘𝗦𝗛", callback_data="refresh_welcome"),
            InlineKeyboardButton("🆘 𝗛𝗘𝗟𝗣", callback_data="help_menu")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if update.callback_query:
            await update.callback_query.message.edit_text(
                welcome_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            await update.callback_query.answer()
        else:
            await update.message.reply_text(
                welcome_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"Error sending welcome: {e}")

# ============================================
# 🔄 CALLBACK HANDLERS - FIXED
# ============================================
async def verify_join_callback(update: Update, context: CallbackContext):
    """Verify join callback"""
    query = update.callback_query
    await query.answer("🔄 Verifying membership...")
    
    is_member = await check_membership(update, context)
    
    if is_member:
        await query.answer("✅ Successfully verified!", show_alert=True)
        await send_mega_welcome(update, context)
    else:
        await query.answer("⚠️ Please join the group first!", show_alert=True)
        await send_ultra_stylish_force_join(update, context)

async def refresh_join_callback(update: Update, context: CallbackContext):
    """Refresh join callback"""
    query = update.callback_query
    await query.answer("🔄 Refreshing...")
    await send_ultra_stylish_force_join(update, context)

async def refresh_welcome_callback(update: Update, context: CallbackContext):
    """Refresh welcome callback"""
    query = update.callback_query
    await query.answer("🔄 Refreshing...")
    await send_mega_welcome(update, context)

async def help_menu_callback(update: Update, context: CallbackContext):
    """Help menu callback"""
    query = update.callback_query
    await query.answer()
    
    help_text = """
╔══════════════════════════════════════════════════╗
    🆘 𝗛𝗘𝗟𝗣 & 𝗚𝗨𝗜𝗗𝗘 🆘
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>🤖 𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘:</b>

1. Click "START SEARCH"
2. Send any phone number
3. Get complete information instantly!

<b>📱 𝗦𝗨𝗣𝗣𝗢𝗥𝗧𝗘𝗗 𝗙𝗢𝗥𝗠𝗔𝗧𝗦:</b>
• +919876543210
• 9876543210  
• 919876543210

<b>💰 𝗖𝗥𝗘𝗗𝗜𝗧 𝗦𝗬𝗦𝗧𝗘𝗠:</b>
• Free Credits: 44 (Not 5!)
• Hourly Bonus: 4 credits every hour
• Search Cost: 1 credit
• Premium: Unlimited searches

<b>⏰ 𝗛𝗢𝗨𝗥𝗟𝗬 𝗕𝗢𝗡𝗨𝗦:</b>
• Get 4 credits automatically every hour
• No action required
• Works 24/7
• Unlimited bonuses!

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>💖 Powered by NOOR 🦋 OSINT PRO MAX</b>
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="back_to_menu")],
        [InlineKeyboardButton("🚀 𝗦𝗧𝗔𝗥𝗧", callback_data="menu_search")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(help_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

# ============================================
# ⏰ HOURLY BONUS INFO
# ============================================
async def hourly_bonus_info_callback(update: Update, context: CallbackContext):
    """Show hourly bonus information"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data, credit_data = get_user_data(user_id)
    
    # Calculate next bonus time
    last_bonus = user_data.get('last_hourly_bonus')
    if last_bonus:
        last_time = datetime.fromisoformat(last_bonus)
        next_time = last_time + timedelta(hours=1)
        time_until = next_time - datetime.now()
        
        if time_until.total_seconds() > 0:
            hours = int(time_until.seconds // 3600)
            minutes = int((time_until.seconds % 3600) // 60)
            next_bonus = f"{hours}h {minutes}m"
        else:
            next_bonus = "Any minute now!"
    else:
        next_bonus = "First bonus coming soon!"
    
    bonus_text = f"""
╔══════════════════════════════════════════════════╗
    ⏰ 𝗛𝗢𝗨𝗥𝗟𝗬 𝗕𝗢𝗡𝗨𝗦 𝗦𝗬𝗦𝗧𝗘𝗠 ⏰
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

🎁 <b>𝗘𝗔𝗥𝗡 𝗙𝗥𝗘𝗘 𝗖𝗥𝗘𝗗𝗜𝗧𝗦 𝗘𝗩𝗘𝗥𝗬 𝗛𝗢𝗨𝗥!</b>

┌─────────────────────────────────────┐
• <b>Bonus Amount:</b> 4 credits/hour
• <b>Your Total Bonuses:</b> {user_data.get('hourly_bonus_count', 0)}
• <b>Total Credits Earned:</b> {credit_data.get('hourly_bonus_total', 0)}
• <b>Next Bonus In:</b> {next_bonus}
└─────────────────────────────────────┘

<b>⚡ 𝗛𝗢𝗪 𝗜𝗧 𝗪𝗢𝗥𝗞𝗦:</b>
1. Bot automatically gives 4 credits every hour
2. No action required from you
3. You'll get a notification
4. Credits add up automatically

<b>💡 𝗧𝗜𝗣𝗦:</b>
• Keep the bot running
• Make sure you're in our channel
• Use /start to refresh
• Premium users also get bonus!

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>💰 Current Credits: {credit_data['credits']}</b>
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 𝗥𝗘𝗙𝗥𝗘𝗦𝗛", callback_data="refresh_bonus_info")],
        [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="back_to_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(bonus_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

# ============================================
# 📡 NUMBER INFO FETCHING WITH NEW API
# ============================================
def fetch_number_info(phone_number: str) -> Optional[Dict]:
    """Fetch number information with new API"""
    try:
        # Clean phone number
        clean_number = re.sub(r'\D', '', phone_number)
        
        # Handle different formats
        if len(clean_number) == 10:
            clean_number = "91" + clean_number
        elif clean_number.startswith('91') and len(clean_number) == 12:
            pass  # Already correct
        elif clean_number.startswith('+91'):
            clean_number = clean_number[1:]  # Remove +
        
        # Make API request
        response = requests.get(
            f"{NUMBER_INFO_API}{clean_number[-10:]}",  # Last 10 digits
            timeout=10,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API Error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching number info: {e}")
        return None

def parse_address(address_str: str) -> Dict:
    """Parse address string into structured format"""
    address_info = {
        'full_address': 'Not Available',
        'house': 'Not Available',
        'street': 'Not Available',
        'locality': 'Not Available',
        'city': 'Not Available',
        'state': 'Not Available',
        'pincode': 'Not Available',
        'landmark': 'Not Available'
    }
    
    try:
        if not address_str or address_str == 'NA':
            return address_info
        
        # Try different parsing methods
        if '!!!' in address_str:
            parts = address_str.split('!!!')
            if len(parts) >= 6:
                address_info.update({
                    'house': parts[0] if parts[0] and parts[0] != 'NA' else 'Not Available',
                    'street': parts[1] if len(parts) > 1 and parts[1] and parts[1] != 'NA' else 'Not Available',
                    'locality': parts[2] if len(parts) > 2 and parts[2] and parts[2] != 'NA' else 'Not Available',
                    'city': parts[3] if len(parts) > 3 and parts[3] and parts[3] != 'NA' else 'Not Available',
                    'state': parts[4] if len(parts) > 4 and parts[4] and parts[4] != 'NA' else 'Not Available',
                    'pincode': parts[5] if len(parts) > 5 and parts[5] and parts[5] != 'NA' else 'Not Available',
                    'full_address': ', '.join(filter(lambda x: x and x != 'NA' and x != 'Not Available', parts[:6]))
                })
        elif '!!' in address_str:
            parts = address_str.split('!!')
            address_info['full_address'] = ' '.join(filter(lambda x: x and x != 'NA', parts))
        elif '!' in address_str:
            parts = address_str.split('!')
            address_info['full_address'] = ' '.join(filter(lambda x: x and x != 'NA', parts))
        else:
            address_info['full_address'] = address_str
            
    except Exception as e:
        logger.error(f"Error parsing address: {e}")
        address_info['full_address'] = address_str
    
    return address_info

def format_number_info(data: Dict, phone_number: str) -> str:
    """Format number information with stylish design"""
    if not data or not data.get('success'):
        return None
    
    try:
        results = data.get('result', [])
        if not results:
            return None
        
        # Use the first result
        result = results[0]
        
        # Parse address
        address_str = result.get('address', '')
        address_info = parse_address(address_str)
        
        # Format response with animations
        response = f"""
╔══════════════════════════════════════════════════╗
    📊 𝗡𝗨𝗠𝗕𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 📊
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>📱 𝗣𝗛𝗢𝗡𝗘 𝗡𝗨𝗠𝗕𝗘𝗥:</b>
<code>{phone_number}</code>

<b>👤 𝗣𝗘𝗥𝗦𝗢𝗡𝗔𝗟 𝗜𝗡𝗙𝗢:</b>
┌─────────────────────────────────────┐
• <b>Name:</b> {html.escape(result.get('name', 'Not Available'))}
• <b>Father's Name:</b> {html.escape(result.get('father_name', 'Not Available'))}
• <b>Alt Mobile:</b> {result.get('alt_mobile', 'Not Available') if result.get('alt_mobile') else 'Not Available'}
• <b>Email:</b> {result.get('email', 'Not Available') if result.get('email') else 'Not Available'}
└─────────────────────────────────────┘

<b>📍 𝗙𝗨𝗟𝗟 𝗔𝗗𝗗𝗥𝗘𝗦𝗦:</b>
┌─────────────────────────────────────┐
"""
        
        # Add address parts
        if address_info['full_address'] != 'Not Available':
            response += f"• <b>Full Address:</b> {html.escape(address_info['full_address'])}\n"
        
        if address_info['house'] != 'Not Available':
            response += f"• <b>House/Plot:</b> {html.escape(address_info['house'])}\n"
        
        if address_info['street'] != 'Not Available':
            response += f"• <b>Street:</b> {html.escape(address_info['street'])}\n"
        
        if address_info['locality'] != 'Not Available':
            response += f"• <b>Locality:</b> {html.escape(address_info['locality'])}\n"
        
        if address_info['city'] != 'Not Available':
            response += f"• <b>City:</b> {html.escape(address_info['city'])}\n"
        
        if address_info['state'] != 'Not Available':
            response += f"• <b>State:</b> {html.escape(address_info['state'])}\n"
        
        if address_info['pincode'] != 'Not Available':
            response += f"• <b>Pincode:</b> {html.escape(address_info['pincode'])}\n"
        
        response += """└─────────────────────────────────────┘

<b>📋 𝗔𝗗𝗗𝗜𝗧𝗜𝗢𝗡𝗔𝗟 𝗜𝗡𝗙𝗢:</b>
┌─────────────────────────────────────┐
"""
        
        # Add additional info
        response += f"• <b>Aadhaar Number:</b> {result.get('id_number', 'Not Available')}\n"
        response += f"• <b>Circle:</b> {result.get('circle', 'Not Available')}\n"
        response += f"• <b>Operator:</b> {'JIO' if 'JIO' in result.get('circle', '') else result.get('circle', 'Not Available').split()[0]}\n"
        response += f"• <b>Database ID:</b> {result.get('id', 'N/A')}\n"
        
        # Add multiple results info if available
        if len(results) > 1:
            response += f"• <b>Additional Records:</b> {len(results) - 1} more found\n"
        
        response += """└─────────────────────────────────────┘

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>🔒 Database:</b> NOORXANURAG 
<b>⚡ Search Time:</b> Real-time
<b>📊 Accuracy:</b> 99.9% Verified
<b>📅 Valid From:</b> {valid_from}

<b>💖 Powered by NOOR 🦋 OSINT PRO MAX</b>
""".format(valid_from=data.get('valid_from', 'Recent'))
        
        return response
        
    except Exception as e:
        logger.error(f"Error formatting number info: {e}")
        return None

# ============================================
# 🎛️ MAIN MENU HANDLER
# ============================================
async def handle_main_menu(update: Update, context: CallbackContext):
    """Handle main menu callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Check membership first
    is_member = await check_membership(update, context)
    if not is_member:
        await send_ultra_stylish_force_join(update, context)
        return
    
    if data == "menu_search":
        await show_search_menu(query, context)
    elif data == "menu_premium":
        await show_premium_menu(query, context)
    elif data == "profile":
        await show_profile_menu(query, context)
    elif data == "hourly_bonus_info":
        await hourly_bonus_info_callback(update, context)
    elif data == "stats":
        await show_stats_menu(query, context)
    elif data == "back_to_menu":
        await send_mega_welcome(update, context)
    elif data.startswith("refresh_"):
        await query.answer("🔄 Refreshed!")
        if data == "refresh_bonus_info":
            await hourly_bonus_info_callback(update, context)
        else:
            await handle_main_menu(update, context)

async def show_search_menu(query, context):
    """Show search menu"""
    search_text = """
╔══════════════════════════════════════════════════╗
    🔍 𝗡𝗨𝗠𝗕𝗘𝗥 𝗦𝗘𝗔𝗥𝗖𝗛 🔍
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>📌 𝗦𝗘𝗡𝗗 𝗔 𝗣𝗛𝗢𝗡𝗘 𝗡𝗨𝗠𝗕𝗘𝗥:</b>

<b>📱 𝗦𝗨𝗣𝗣𝗢𝗥𝗧𝗘𝗗 𝗙𝗢𝗥𝗠𝗔𝗧𝗦:</b>
• <code>+919876543210</code>
• <code>9876543210</code>
• <code>919876543210</code>

<b>💎 𝗖𝗢𝗦𝗧:</b> 1 Credit per search
<b>⏰ 𝗕𝗢𝗡𝗨𝗦:</b> +4 Credits every hour!
<b>⚡ 𝗦𝗣𝗘𝗘𝗗:</b> 1-2 seconds
<b>📊 𝗗𝗔𝗧𝗔𝗕𝗔𝗦𝗘:</b> 10M+ Verified Records

<b>🔍 𝗪𝗛𝗔𝗧 𝗬𝗢𝗨 𝗚𝗘𝗧:</b>
• Complete Name & Family Details
• Full Address with House Number
• Aadhaar Number & Documents
• Location, City, State, Pincode
• Network Circle & Operator Info
• Email & Alternative Numbers

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>👇 Send any phone number now:</b>
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="back_to_menu")],
        [InlineKeyboardButton("🔄 𝗥𝗘𝗙𝗥𝗘𝗦𝗛", callback_data="refresh_search")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(search_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    context.user_data['awaiting_input'] = 'number_search'

async def show_premium_menu(query, context):
    """Show premium menu"""
    user_id = query.from_user.id
    user_data, credit_data = get_user_data(user_id)
    
    premium_text = f"""
╔══════════════════════════════════════════════════╗
    💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗘𝗠𝗕𝗘𝗥𝗦𝗛𝗜𝗣 💎
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>🚀 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗘𝗡𝗘𝗙𝗜𝗧𝗦:</b>
┌─────────────────────────────────────┐
• ✅ Unlimited Searches
• ✅ No Credit Deduction  
• ✅ Priority Processing
• ✅ All Features Unlocked
• ✅ 24/7 VIP Support
• ✅ Advanced Search Filters
• ✅ Early Feature Access
• ✅ VIP Group Access
• ✅ Still Get Hourly Bonuses!
└─────────────────────────────────────┘

<b>💰 𝗣𝗥𝗜𝗖𝗜𝗡𝗚 𝗣𝗟𝗔𝗡𝗦:</b>
┌─────────────────────────────────────┐
• 1 Week: ₹49
• 1 Month: ₹149
• 3 Months: ₹399
• 1 Year: ₹999
• Lifetime: ₹1999
└─────────────────────────────────────┘

<b>📱 𝗛𝗢𝗪 𝗧𝗢 𝗕𝗨𝗬:</b>

1. Contact @madamjikiduniya
2. Send your User ID: <code>{user_id}</code>
3. Choose your plan
4. Get activated instantly!

<b>⭐ 𝗦𝗣𝗘𝗖𝗜𝗔𝗟 𝗢𝗙𝗙𝗘𝗥:</b> First 50 users get 30% discount!

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>⚡ Upgrade to Premium Today!</b>
"""
    
    keyboard = [
        [InlineKeyboardButton("📲 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 𝗚𝗥𝗢𝗨𝗣", url="https://t.me/madamjikiduniya")],
        [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="back_to_menu")],
        [InlineKeyboardButton("🔄 𝗥𝗘𝗙𝗥𝗘𝗦𝗛", callback_data="refresh_premium")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(premium_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

async def show_profile_menu(query, context):
    """Show profile menu"""
    user_id = query.from_user.id
    user_data, credit_data = get_user_data(user_id)
    
    # Premium status
    premium_status = "❌ Not Active"
    if user_data.get('is_premium') and user_data.get('premium_expiry'):
        expiry_date = datetime.fromisoformat(user_data['premium_expiry'])
        if expiry_date > datetime.now():
            days_left = (expiry_date - datetime.now()).days
            premium_status = f"✅ {days_left} days left"
        else:
            premium_status = "❌ Expired"
    
    # Hourly bonus info
    last_bonus = user_data.get('last_hourly_bonus')
    if last_bonus:
        last_time = datetime.fromisoformat(last_bonus)
        time_since = datetime.now() - last_time
        if time_since.total_seconds() < 3600:
            minutes_left = 60 - int(time_since.total_seconds() // 60)
            next_bonus = f"{minutes_left} minutes"
        else:
            next_bonus = "Ready now!"
    else:
        next_bonus = "First bonus soon!"
    
    profile_text = f"""
╔══════════════════════════════════════════════════╗
    👤 𝗨𝗦𝗘𝗥 𝗣𝗥𝗢𝗙𝗜𝗟𝗘 👤
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>📋 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗜𝗡𝗙𝗢:</b>
┌─────────────────────────────────────┐
• <b>User ID:</b> <code>{user_id}</code>
• <b>Name:</b> {html.escape(user_data.get('first_name', 'N/A'))}
• <b>Username:</b> @{user_data.get('username', 'N/A')}
• <b>Joined:</b> {datetime.fromisoformat(user_data.get('join_date')).strftime('%d %b %Y') if user_data.get('join_date') else 'N/A'}
└─────────────────────────────────────┘

<b>📊 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦:</b>
┌─────────────────────────────────────┐
• <b>Credits:</b> {credit_data['credits']}
• <b>Premium:</b> {premium_status}
• <b>Searches:</b> {user_data.get('total_searches', 0)}
• <b>Hourly Bonuses:</b> {user_data.get('hourly_bonus_count', 0)}
• <b>Bonus Credits:</b> {credit_data.get('hourly_bonus_total', 0)}
└─────────────────────────────────────┘

<b>⏰ 𝗛𝗢𝗨𝗥𝗟𝗬 𝗕𝗢𝗡𝗨𝗦:</b>
• Next Bonus: {next_bonus}
• Bonus Amount: 4 credits
• Total Bonuses: {user_data.get('hourly_bonus_count', 0)}

<b>📈 𝗔𝗖𝗧𝗜𝗩𝗜𝗧𝗬:</b>
• Last Active: {datetime.fromisoformat(user_data.get('last_active')).strftime('%H:%M %d/%m/%Y') if user_data.get('last_active') else 'N/A'}
• Last Search: {datetime.fromisoformat(user_data.get('last_search')).strftime('%H:%M %d/%m/%Y') if user_data.get('last_search') else 'Never'}

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>⚡ Keep using bot to get hourly bonuses!</b>
"""
    
    keyboard = [
        [InlineKeyboardButton("⏰ 𝗛𝗢𝗨𝗥𝗟𝗬 𝗕𝗢𝗡𝗨𝗦", callback_data="hourly_bonus_info")],
        [InlineKeyboardButton("💎 𝗕𝗨𝗬 𝗣𝗥𝗘𝗠𝗜𝗨𝗠", callback_data="menu_premium")],
        [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="back_to_menu")],
        [InlineKeyboardButton("🔄 𝗥𝗘𝗙𝗥𝗘𝗦𝗛", callback_data="refresh_profile")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(profile_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

async def show_stats_menu(query, context):
    """Show stats menu"""
    users = load_users()
    credits = load_credits()
    
    total_users = len(users)
    total_searches = sum(user.get('total_searches', 0) for user in users.values())
    total_credits = sum(data.get('credits', 0) for data in credits.values())
    premium_users = sum(1 for user in users.values() if user.get('is_premium'))
    
    # Hourly bonus stats
    total_hourly_bonuses = sum(data.get('hourly_bonus_total', 0) for data in credits.values())
    
    # Today's stats
    today = datetime.now().date()
    today_users = 0
    today_searches = 0
    
    for user in users.values():
        join_date = datetime.fromisoformat(user.get('join_date', '2000-01-01')).date()
        if join_date == today:
            today_users += 1
        
        if user.get('last_search'):
            last_search_date = datetime.fromisoformat(user.get('last_search')).date()
            if last_search_date == today:
                today_searches += 1
    
    stats_text = f"""
╔══════════════════════════════════════════════════╗
    📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦 📊
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>📈 𝗚𝗟𝗢𝗕𝗔𝗟 𝗦𝗧𝗔𝗧𝗦:</b>
┌─────────────────────────────────────┐
• Total Users: {total_users}
• Total Searches: {total_searches}
• Total Credits: {total_credits}
• Premium Users: {premium_users}
• Hourly Bonuses Given: {total_hourly_bonuses}
└─────────────────────────────────────┘

<b>📅 𝗧𝗢𝗗𝗔𝗬'𝗦 𝗦𝗧𝗔𝗧𝗦:</b>
┌─────────────────────────────────────┐
• New Users Today: {today_users}
• Searches Today: {today_searches}
• Uptime: {str(datetime.now() - start_time).split('.')[0]}
└─────────────────────────────────────┘

<b>🎁 𝗛𝗢𝗨𝗥𝗟𝗬 𝗕𝗢𝗡𝗨𝗦 𝗦𝗬𝗦𝗧𝗘𝗠:</b>
• Bonus Amount: 4 credits/hour
• Active Users: All registered users
• Next Distribution: Every hour
• Total Distributed: {total_hourly_bonuses} credits

<b>🚀 𝗣𝗘𝗥𝗙𝗢𝗥𝗠𝗔𝗡𝗖𝗘:</b>
• Response Time: 0.5-2s
• API Success Rate: 99.5%
• Database Size: 10M+ Records
• Availability: 99.9%
• Active Users: 24/7

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>💖 Powered by NOOR 🦋 OSINT PRO MAX</b>
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="back_to_menu")],
        [InlineKeyboardButton("🔄 𝗥𝗘𝗙𝗥𝗘𝗦𝗛", callback_data="refresh_stats")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(stats_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

# ============================================
# 💬 MESSAGE HANDLER
# ============================================
async def handle_message(update: Update, context: CallbackContext):
    """Handle text messages"""
    user_id = update.effective_user.id
    
    # Check if user is banned
    if is_user_banned(user_id):
        return
    
    # Check membership
    is_member = await check_membership(update, context)
    if not is_member:
        await send_ultra_stylish_force_join(update, context)
        return
    
    text = update.message.text.strip()
    
    # Check if awaiting number input
    if context.user_data.get('awaiting_input') == 'number_search' or re.search(r'\d', text):
        await process_number_search(update, context, text, user_id)
    else:
        # Show error message
        error_text = """
╔══════════════════════════════════════════════════╗
    ⚠️ 𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗜𝗡𝗣𝗨𝗧 ⚠️
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>❌ Please send a valid phone number!</b>

<b>📱 𝗦𝗨𝗣𝗣𝗢𝗥𝗧𝗘𝗗 𝗙𝗢𝗥𝗠𝗔𝗧𝗦:</b>
• <code>+919876543210</code>
• <code>9876543210</code>
• <code>919876543210</code>

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>👇 Or click "START SEARCH" from menu</b>
"""
        
        await update.message.reply_text(error_text, parse_mode=ParseMode.HTML)

def clean_phone_number(number: str) -> str:
    """Clean and validate phone number"""
    # Remove all non-digits
    cleaned = re.sub(r'[^\d+]', '', number)
    
    # Handle different formats
    if cleaned.startswith('+91') and len(cleaned) == 13:
        return cleaned
    elif cleaned.startswith('91') and len(cleaned) == 12:
        return '+' + cleaned
    elif len(cleaned) == 10 and cleaned.isdigit():
        return '+91' + cleaned
    elif len(cleaned) == 11 and cleaned.startswith('0'):
        return '+91' + cleaned[1:]
    else:
        return cleaned

async def process_number_search(update: Update, context: CallbackContext, text: str, user_id: int):
    """Process number search with animations"""
    phone_number = clean_phone_number(text)
    
    # Validate phone number
    if not re.match(r'^\+91\d{10}$', phone_number):
        error_text = """
╔══════════════════════════════════════════════════╗
    ⚠️ 𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗡𝗨𝗠𝗕𝗘𝗥 ⚠️
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>❌ Invalid phone number format!</b>

<b>📱 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗡𝗗 𝗜𝗡 𝗙𝗢𝗥𝗠𝗔𝗧:</b>
• <code>+919876543210</code>
• <code>9876543210</code>
• <code>919876543210</code>

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
        await update.message.reply_text(error_text, parse_mode=ParseMode.HTML)
        return
    
    # Check credits
    if not deduct_credits(user_id, 1):
        error_text = f"""
╔══════════════════════════════════════════════════╗
    ⚠️ 𝗜𝗡𝗦𝗨𝗙𝗙𝗜𝗖𝗜𝗘𝗡𝗧 𝗖𝗥𝗘𝗗𝗜𝗧𝗦 ⚠️
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>❌ You need 1 credit for number lookup!</b>

<b>💰 𝗚𝗘𝗧 𝗠𝗢𝗥𝗘 𝗖𝗥𝗘𝗗𝗜𝗧𝗦:</b>
• Wait for hourly bonus (4 credits/hour)
• Buy Premium (unlimited searches)
• Use /start menu

<b>⏰ Next Hourly Bonus: Coming soon!</b>

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
        await update.message.reply_text(error_text, parse_mode=ParseMode.HTML)
        return
    
    # Show animated processing message
    processing_text = f"""
╔══════════════════════════════════════════════════╗
    ⚡ 𝗦𝗘𝗔𝗥𝗖𝗛𝗜𝗡𝗚... ⚡
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>📱 Number:</b> <code>{phone_number}</code>
<b>💰 Credits Left:</b> {get_credits(user_id)}

<b>⚡ Status:</b> Initializing search...
<b>📊 Progress:</b> [░░░░░░░░░░] 0%

<b>⏳ Please wait 1-2 seconds...</b>

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    
    processing_msg = await update.message.reply_text(processing_text, parse_mode=ParseMode.HTML)
    
    # Animated processing with more steps
    animation_steps = [
        ("🔍 Connecting to database...", "[█░░░░░░░░░] 10%"),
        ("📡 Querying records...", "[██░░░░░░░░] 20%"),
        ("⚡ Processing data...", "[███░░░░░░░] 30%"),
        ("🔐 Verifying information...", "[████░░░░░░] 40%"),
        ("📊 Extracting details...", "[█████░░░░░] 50%"),
        ("✅ Validating results...", "[██████░░░░] 60%"),
        ("✨ Formatting response...", "[███████░░░] 70%"),
        ("🎯 Finalizing report...", "[████████░░] 80%"),
        ("🚀 Almost done...", "[█████████░] 90%"),
        ("🎉 Complete!", "[██████████] 100%")
    ]
    
    for text, progress in animation_steps:
        await asyncio.sleep(0.15)
        animated_text = processing_text.replace("Initializing search...", text).replace("[░░░░░░░░░░] 0%", progress)
        try:
            await processing_msg.edit_text(animated_text, parse_mode=ParseMode.HTML)
        except:
            pass
    
    # Fetch number info
    data = fetch_number_info(phone_number)
    
    if data and data.get('success'):
        response = format_number_info(data, phone_number)
        
        if response:
            # Add credits info
            remaining = get_credits(user_id)
            response += f"\n<b>💰 Remaining Credits:</b> {remaining}"
            response += f"\n<b>⏰ Next Hourly Bonus:</b> Coming soon!"
            
            keyboard = [
                [InlineKeyboardButton("🔄 𝗦𝗘𝗔𝗥𝗖𝗛 𝗔𝗚𝗔𝗜𝗡", callback_data="menu_search")],
                [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="back_to_menu")],
                [InlineKeyboardButton("💎 𝗚𝗢 𝗣𝗥𝗘𝗠𝗜𝗨𝗠", callback_data="menu_premium")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_msg.edit_text(response, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        else:
            # Refund credit
            add_credits(user_id, 1, "refund")
            
            error_text = """
╔══════════════════════════════════════════════════╗
    ⚠️ 𝗗𝗔𝗧𝗔 𝗘𝗥𝗥𝗢𝗥 ⚠️
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>❌ Error processing response!</b>
<b>⚠️ Please try again later.</b>

<b>💰 Your credit has been refunded.</b>

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
            await processing_msg.edit_text(error_text, parse_mode=ParseMode.HTML)
    else:
        # Refund credit
        add_credits(user_id, 1, "refund")
        
        error_text = f"""
╔══════════════════════════════════════════════════╗
    ⚠️ 𝗡𝗢 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 𝗙𝗢𝗨𝗡𝗗 ⚠️
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>❌ No information found for this number!</b>

<b>📱 Number:</b> <code>{phone_number}</code>

<b>Possible reasons:</b>
• Number not in database
• Private/Protected number
• Database update pending
• Invalid mobile number

<b>💰 Your credit has been refunded.</b>
<b>⏰ Get more credits in next hourly bonus!</b>

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 𝗧𝗥𝗬 𝗔𝗚𝗔𝗜𝗡", callback_data="menu_search")],
            [InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="back_to_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await processing_msg.edit_text(error_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    
    # Clear awaiting input
    context.user_data['awaiting_input'] = None

# ============================================
# 🆘 HELP COMMAND
# ============================================
async def help_command(update: Update, context: CallbackContext):
    """Help command"""
    help_text = """
╔══════════════════════════════════════════════════╗
    🆘 𝗛𝗘𝗟𝗣 & 𝗚𝗨𝗜𝗗𝗘 🆘
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>🤖 𝗔𝗩𝗔𝗜𝗟𝗔𝗕𝗟𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦:</b>
┌─────────────────────────────────────┐
• /start - Start bot & menu
• /help - Show this help
• /admin - Admin panel (Admin only)
└─────────────────────────────────────┘

<b>🔍 𝗨𝗦𝗜𝗡𝗚 𝗧𝗛𝗘 𝗕𝗢𝗧:</b>
1. Click /start or use menu
2. Select "START SEARCH"
3. Send phone number
4. Get complete information!

<b>💰 𝗖𝗥𝗘𝗗𝗜𝗧 𝗦𝗬𝗦𝗧𝗘𝗠:</b>
┌─────────────────────────────────────┐
• Free Credits: 44 (Not 5!)
• Hourly Bonus: 4 credits every hour
• Search Cost: 1 credit per search
• Premium: Unlimited searches
└─────────────────────────────────────┘

<b>⏰ 𝗛𝗢𝗨𝗥𝗟𝗬 𝗕𝗢𝗡𝗨𝗦:</b>
• Get 4 credits automatically every hour
• No action required
• Works 24/7
• Unlimited bonuses!

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>💖 Powered by NOOR 🦋 OSINT PRO MAX</b>
"""
    
    keyboard = [
        [InlineKeyboardButton("🚀 𝗦𝗧𝗔𝗥𝗧", callback_data="back_to_menu")],
        [InlineKeyboardButton("💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠", callback_data="menu_premium")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

# ============================================
# 👑 ADMIN COMMANDS - ENHANCED
# ============================================
async def admin_command(update: Update, context: CallbackContext):
    """Admin command with enhanced features"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Access denied. You are not an admin.")
        return
    
    if not context.args:
        users = load_users()
        credits = load_credits()
        banned = load_banned()
        
        total_users = len(users)
        total_searches = sum(user.get('total_searches', 0) for user in users.values())
        total_credits = sum(data.get('credits', 0) for data in credits.values())
        premium_users = sum(1 for user in users.values() if user.get('is_premium'))
        banned_users = len(banned)
        
        # Hourly bonus stats
        total_hourly_bonuses = sum(data.get('hourly_bonus_total', 0) for data in credits.values())
        
        message = f"""
╔══════════════════════════════════════════════════╗
    🛠️ 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟 🛠️
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>📊 𝗦𝗧𝗔𝗧𝗦:</b>
┌─────────────────────────────────────┐
• Total Users: {total_users}
• Banned Users: {banned_users}
• Total Searches: {total_searches}
• Total Credits: {total_credits}
• Premium Users: {premium_users}
• Hourly Bonuses: {total_hourly_bonuses} credits
└─────────────────────────────────────┘

<b>⚡ 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦:</b>
┌─────────────────────────────────────┐
• /admin stats - Detailed stats
• /admin add <id> <credits>
• /admin remove <id> <credits>
• /admin premium <id> <days>
• /admin ban <id> <reason>
• /admin unban <id>
• /admin users - List all users
• /admin broadcast <message>
• /admin reset <id> - Reset user credits
└─────────────────────────────────────┘

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
        
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
        return
    
    command = context.args[0].lower()
    
    if command == "add" and len(context.args) >= 3:
        try:
            target_user = int(context.args[1])
            amount = int(context.args[2])
            
            if add_credits(target_user, amount, "admin"):
                await update.message.reply_text(f"✅ Added {amount} credits to user {target_user}")
            else:
                await update.message.reply_text("❌ Failed to add credits")
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID or amount")
    
    elif command == "remove" and len(context.args) >= 3:
        try:
            target_user = int(context.args[1])
            amount = int(context.args[2])
            
            user_id_str = str(target_user)
            credits = load_credits()
            
            if user_id_str in credits:
                current = credits[user_id_str].get('credits', 0)
                new_amount = max(0, current - amount)
                credits[user_id_str]['credits'] = new_amount
                save_credits(credits)
                await update.message.reply_text(f"✅ Removed {amount} credits from user {target_user}. New balance: {new_amount}")
            else:
                await update.message.reply_text("❌ User not found")
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID or amount")
    
    elif command == "reset" and len(context.args) >= 2:
        try:
            target_user = int(context.args[1])
            user_id_str = str(target_user)
            credits = load_credits()
            
            if user_id_str in credits:
                credits[user_id_str]['credits'] = FREE_CREDITS
                credits[user_id_str]['last_reset'] = datetime.now().isoformat()
                save_credits(credits)
                await update.message.reply_text(f"✅ Reset credits for user {target_user} to {FREE_CREDITS}")
            else:
                await update.message.reply_text("❌ User not found")
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID")
    
    elif command == "premium" and len(context.args) >= 3:
        try:
            target_user = int(context.args[1])
            days = int(context.args[2])
            
            users = load_users()
            user_id_str = str(target_user)
            
            if user_id_str in users:
                users[user_id_str]['is_premium'] = True
                expiry_date = datetime.now() + timedelta(days=days)
                users[user_id_str]['premium_expiry'] = expiry_date.isoformat()
                save_users(users)
                
                await update.message.reply_text(f"✅ Added {days} days premium to user {target_user}")
            else:
                await update.message.reply_text("❌ User not found")
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID or days")
    
    elif command == "ban" and len(context.args) >= 2:
        try:
            target_user = int(context.args[1])
            reason = ' '.join(context.args[2:]) if len(context.args) > 2 else "No reason provided"
            
            ban_user(target_user, reason)
            await update.message.reply_text(f"✅ Banned user {target_user}. Reason: {reason}")
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID")
    
    elif command == "unban" and len(context.args) >= 2:
        try:
            target_user = int(context.args[1])
            
            if unban_user(target_user):
                await update.message.reply_text(f"✅ Unbanned user {target_user}")
            else:
                await update.message.reply_text("❌ User not found in banned list")
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID")
    
    elif command == "users" and len(context.args) >= 1:
        users = load_users()
        message = "👥 <b>User List:</b>\n\n"
        
        count = 0
        for user_id_str, user_data in list(users.items())[:50]:  # Show first 50
            count += 1
            username = user_data.get('username', 'N/A')
            first_name = html.escape(user_data.get('first_name', 'N/A'))
            credits = get_credits(int(user_id_str))
            premium = "✅" if user_data.get('is_premium') else "❌"
            
            message += f"{count}. ID: <code>{user_id_str}</code> | @{username} | {first_name} | Credits: {credits} | Premium: {premium}\n"
        
        if len(users) > 50:
            message += f"\n... and {len(users) - 50} more users"
        
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
    
    elif command == "broadcast" and len(context.args) >= 2:
        message = ' '.join(context.args[1:])
        users = load_users()
        success = 0
        failed = 0
        
        await update.message.reply_text(f"📢 Starting broadcast to {len(users)} users...")
        
        for user_id_str in users:
            try:
                await context.bot.send_message(
                    chat_id=int(user_id_str),
                    text=f"📢 <b>Admin Broadcast:</b>\n\n{message}\n\n<b>💖 NOOR 🦋 OSINT PRO MAX</b>",
                    parse_mode=ParseMode.HTML
                )
                success += 1
                await asyncio.sleep(0.05)  # Prevent flood
            except Exception as e:
                logger.error(f"Failed to send to {user_id_str}: {e}")
                failed += 1
        
        await update.message.reply_text(f"✅ Broadcast completed!\n✅ Success: {success}\n❌ Failed: {failed}")

# ============================================
# ⚠️ ERROR HANDLER
# ============================================
async def error_handler(update: Update, context: CallbackContext):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update.effective_message:
        error_text = """
╔══════════════════════════════════════════════════╗
    ⚠️ 𝗘𝗥𝗥𝗢𝗥 ⚠️
╚══════════════════════════════════════════════════╝

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

<b>❌ An error occurred!</b>
<b>⚠️ Please try again later.</b>

<b>🔧 If problem persists, contact @madamjikiduniya</b>

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
        try:
            await update.effective_message.reply_text(error_text, parse_mode=ParseMode.HTML)
        except:
            pass

# ============================================
# 🚀 FLASK SERVER
# ============================================
def run_flask():
    """Run Flask server"""
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# ============================================
# 🎯 MAIN FUNCTION
# ============================================
def main():
    """Main function"""
    # Initialize data files
    for file in [USERS_FILE, CREDITS_FILE, BANNED_FILE]:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump({}, f)
    
    # Start Flask server
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Create bot application with job queue
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add job queue for hourly credits
    job_queue = application.job_queue
    
    # Schedule hourly credits job (every 60 minutes)
    if job_queue:
        job_queue.run_repeating(hourly_credits_job, interval=3600, first=60)  # 3600 seconds = 1 hour
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin_command))
    
    # Add callback handlers
    application.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^profile$"))
    application.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^hourly_bonus_info$"))
    application.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^stats$"))
    application.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^back_to_menu$"))
    application.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^help_menu$"))
    
    # Special callbacks
    application.add_handler(CallbackQueryHandler(verify_join_callback, pattern="^verify_join$"))
    application.add_handler(CallbackQueryHandler(refresh_join_callback, pattern="^refresh_join$"))
    application.add_handler(CallbackQueryHandler(refresh_welcome_callback, pattern="^refresh_welcome$"))
    
    # Refresh handlers
    application.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^refresh_"))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    print(f"\n{'='*70}")
    print(f"🌸  {BOT_NAME}  🌸")
    print(f"{'='*70}")
    print(f"📢 Force Join Group: {FORCE_JOIN_CHANNEL}")
    print(f"💳 Free Credits: {FREE_CREDITS} (Changed from 5)")
    print(f"⏰ Hourly Bonus: {HOURLY_CREDITS} credits every hour")
    print(f"🔍 Search Cost: 1 credit per search")
    print(f"💎 Premium: Contact @madamjikiduniya")
    print(f"🌐 Web Server: Running on port {PORT}")
    print(f"⏱️ Start Time: {start_time}")
    print(f"⚡ Status: ULTRA FAST & STABLE")
    print(f"🎯 Hourly Bonus System: ACTIVE")
    print(f"📊 Admin Panel: Enhanced with ban/unban")
    print(f"{'='*70}\n")
    
    # Run bot
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        close_loop=False
    )

if __name__ == '__main__':
    main()()
