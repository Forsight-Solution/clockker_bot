import telebot
import datetime
import gspread
# import time
import pytz
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


import dotenv
import os
from geopy.geocoders import Nominatim

# Create a Geopy geocoder
geolocator = Nominatim(user_agent="worker_location")

dotenv.load_dotenv()

sgt_timezone = pytz.timezone('Asia/Singapore')
# current_date = datetime.date.today(sgt_timezone)
# overtime_start = datetime.datetime.combine(current_date, datetime.time(hour=17, tzinfo=sgt_timezone))
# overtime_end = datetime.datetime.combine(current_date, datetime.time(hour=8, tzinfo=sgt_timezone)) + datetime.timedelta(days=1)

# Set your Telegram bot token
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))


# Set your Google Sheets API key and spreadsheet ID
gc = gspread.service_account(os.getenv('GOOGLE_SHEETS_API_KEY'))
sh = gc.open_by_key(os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'))
worksheet = sh.worksheet('Input')

# Create a dictionary to store the check-in and check-out times of each worker
workers = {}
workers_location = {}
# Define a function to handle incoming messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):

    # print(message)
    user_name = message.from_user.first_name 
    if message.from_user.last_name:
        user_name += ' ' + message.from_user.last_name

    # Get the sender's Telegram ID
    sender_id = message.from_user.id

    # Get the sender's message
    message_text = message.text

    
        
 
    

    if message_text.startswith('/location'):
        if sender_id in workers and workers[sender_id]['check_in_time']:
            if sender_id in workers_location and workers_location[sender_id]:
                bot.send_message(message.chat.id, 'You have already provided your location.')
            else:
                if message.chat.type == 'group':
                    
                    manual_location = message_text[10:]  # You can modify this line to capture the location in a format you prefer
                    if len(manual_location) == 0:
                        bot.send_message(message.chat.id, 'Please provide a location.')
                    else:
                        workers_location[sender_id] = manual_location
                        bot.send_message(message.chat.id, f'Location added successfully: {manual_location}')

                elif message.chat.type == 'private':
                    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                    button = KeyboardButton("Send Location", request_location=True)
                    markup.add(button)
                    bot.send_message(message.chat.id, "Please share your location by clicking the 'Send Location' button below:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'You must check in before providing your location.')

    
    


    # If the sender is checking in
    elif message_text == '/in':
        if sender_id in workers and workers[sender_id]['check_in_time']:
            bot.send_message(message.chat.id, 'You have already checked in.')
        else:
            # Set the sender's check-in time to SGT
            user_local_time = datetime.datetime.now(sgt_timezone)
            workers[sender_id] = {
                'check_in_time': datetime.datetime.now(sgt_timezone),
                'check_out_time': None
            }
            bot.send_message(message.chat.id, f'{user_name}, you have successfully checked in at {user_local_time.strftime("%I:%M %p")} SGT.')


    # If the sender is checking out
    elif message_text == '/out':
        if sender_id not in workers or not workers[sender_id]['check_in_time']:
            bot.send_message(message.chat.id, 'You must check in before checking out.')
        elif workers[sender_id]['check_out_time']:
            bot.send_message(message.chat.id, 'You have already checked out. Please check in again.')
        else:
            # Check if the worker has provided their location
            if sender_id not in workers_location or not workers_location[sender_id]:
                bot.send_message(message.chat.id, 'You must provide your location before checking out. Please use the /location command.')
            else:
                check_in_time = workers[sender_id]['check_in_time']

                # Set the sender's check-out time to SGT
                workers[sender_id]['check_out_time'] = datetime.datetime.now(sgt_timezone)
                check_out_time = workers[sender_id]['check_out_time']

                # overtime_formatted = '00:00:00'  

                # if overtime_start <= check_out_time < overtime_end:
                #     overtime_timedelta = check_out_time - overtime_start
                #     overtime_hours = overtime_timedelta.total_seconds() / 3600
                #     overtime_hours_int = int(overtime_hours)
                #     overtime_minutes = int((overtime_hours % 1) * 60)
                #     overtime_seconds = int((overtime_minutes % 1) * 60)
                #     overtime_formatted = '{:02}:{:02}:{:02}'.format(overtime_hours_int, overtime_minutes, overtime_seconds)

                # Calculate the total hours worked
                total_hours_worked = check_out_time - check_in_time
                hours, remainder = divmod(total_hours_worked.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                total_hours_worked = '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)

                bot.send_message(message.chat.id, '{}, you have successfully checked out at {} SGT. You worked a total hours of {}.'.format(user_name, check_out_time.strftime('%I:%M %p'), total_hours_worked))
                worksheet.append_row([
                    user_name,
                    check_in_time.astimezone(sgt_timezone).strftime('%Y-%m-%d'),
                    check_in_time.strftime('%I:%M %p'),
                    check_out_time.astimezone(sgt_timezone).strftime('%Y-%m-%d'),
                    check_out_time.strftime('%I:%M %p'),
                    total_hours_worked,
                    workers_location[sender_id]  # Add the location to the spreadsheet data
                ])
                workers[sender_id] = {
                    'check_in_time': None,
                    'check_out_time': check_out_time
                }
                workers_location[sender_id] = None



    else:
        bot.send_message(message.chat.id, 'Please Retry with correct Commands [/in, /out, or /location].')




# Define a function to handle location updates for groups
@bot.message_handler(content_types=['location'])
def handle_location(message):
    # Get the location details from the user's message
    sender_id = message.from_user.id
    latitude = message.location.latitude
    longitude = message.location.longitude

    # Use Geopy to reverse geocode the location and get the place name
    location = geolocator.reverse(f"{latitude}, {longitude}")
    place_name = location.address if location else "Unknown Location"

    workers_location[sender_id] = place_name
    bot.send_message(message.chat.id, f'Location added successfully: {place_name}')
    
# Start the Telegram bot
def start_bot():
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(10)

if __name__ == "__main__":
    start_bot()
