import pywhatkit
import pandas as pd
import datetime
import re

# Get the WhatsApp group ID

class Solution:
  def __init__(self):
    self.group_id = 'DTGz6kaKuLPGsoe9Mg4M3c'

    # Get the current date
    self.today = datetime.date.today()
    self.worker_messages = self.get_messages()
    print(self.worker_messages)
    # self.worker_data = pd.read_excel('worker_data.xlsx')
    # self.worker_names = self.worker_data['name'].tolist()
    # self.worker_map = self.map_worker_name_to_phone_number()
    # self.daily_data = self.get_the_daily_data()

  def map_worker_name_to_phone_number(self):    
    worker_name_map = {}
    for row in self.worker_data.itertuples():
        name = row[1]
        phone_number = row[2]
        decided_hrs_of_work = row[3]
        worker_name_map[phone_number] = [name, decided_hrs_of_work]
        #print(name, phone_number, decided_hrs_of_work)
    return worker_name_map
    

  def get_messages(self):
    messages = pywhatkit.get_chat_messages(self.group_id, start_date=self.today, end_date=self.today)
    worker_messages = []
    # Identify the worker check-in/check-out messages
    for message in messages:
        message = message.lower()
        if message.startswith('in') or message.startswith('out'):
            worker_messages.append(message)
    return worker_messages
    
    
  def get_the_daily_data(self):
    # Extract the worker's name and check-in/check-out time from the messages
    daily_data = {}
    for message in self.worker_messages:
        # Extract the worker's name
        name_regex = r'in|out by (\w+)'
        match = re.match(name_regex, message)
        name = match.group(1)

        # Extract the worker's check-in/check-out time
        time_regex = r'\d{2}:\d{2}'
        match = re.match(time_regex, message)
        time = match.group(0)

        # Add the worker's data to the dictionary
        if name in self.worker_names:
          daily_data[name] = {
              'time': time,
              'check_in_out': message.startswith('in')
          }
    return daily_data
    





  def notify_worker_overtime_undertime(self,worker_phone_number, worker_name, excel_data):
   

    # Read the worker_data.xlsx file.
    required_hours_per_day = self.worker_name_map[worker_phone_number][1]
    
    # Get the worker's check-in/check-out time.
    check_in_time = worker_data.loc[worker_data['name'] == worker_name]['check_in_time'].iloc[0]
    check_out_time = worker_data.loc[worker_data['name'] == worker_name]['check_out_time'].iloc[0]

    # Calculate the total hours worked.
    total_hours_worked = None if check_in_time is None or check_out_time is None else (check_out_time - check_in_time).total_seconds() / 3600

    # Calculate the overtime/undertime.
    overtime_undertime = total_hours_worked - required_hours_per_day

    # Notify the worker if they have worked overtime/undertime.
    if overtime_undertime > 0:
      message = f'Hi {worker_name}, you have worked {total_hours_worked:.2f} hours today, which is {overtime_undertime:.2f} hours overtime.'
    elif overtime_undertime < 0:
      message = f'Hi {worker_name}, you have worked {total_hours_worked:.2f} hours today, which is {overtime_undertime:.2f} hours undertime.'
    else:
      message = f'Hi {worker_name}, you have worked {total_hours_worked:.2f} hours today, which is the required number of hours.'

    # Send the message to the worker.
    pywhatkit.send_message(worker_phone_number, message)

  


# if __name__=='__main__':
#   worker_name_map, excel_data = map_worker_name_to_phone_number('worker_data.xlsx')
#   get_messages()

s= Solution()
