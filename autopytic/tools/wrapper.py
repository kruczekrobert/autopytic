import inspect
import asyncio
import os, glob
from pathlib import Path  # Python 3.6

from dotenv import load_dotenv
from datetime import datetime
import time
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread
import requests
import json


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Event:
    def __init__(self, func, description, pos, loop):
        self.pos = pos
        self.func = func
        self.description = description
        self.loop = loop

    @staticmethod
    def func_is_in(func, event_list):
        for event in event_list:
            if event.func == func:
                return True
        return False
    
    @staticmethod
    def last_is_loop(func, event_list, counter):
        if counter > 0:
            if func.__name__ == event_list[counter-1].func.__name__:
                return True
        else:
            return False
        
    def __str__(self):
        return f'{self.pos}: {self.func.__name__}, {self.description}'

class Wrapper:
    def __init__(self, robot_path, log_file):
        self.events = []
        self.counter = 0 
        self.progress = 0
        self.start_time = None
        self.end_time = None
        self.avg_time = None
        self.status = None
        self.state = None
        self.robot_path = robot_path
        self.log_file = log_file
    
    def send_status(self, response_url, response):
        if response_url:
            try:
                requests.post(os.environ.get("RESPONSE_URL"), json=json.dumps(response))
            except:
                print("Cannot send status - check RESPONSE_URL or network")
            

    def shortcut_of_desc(self, desc):
        if desc:
            if len(desc) > 22:
                return str(self.state[:22])+'...'
            else:
                return self.state
        else:
            return '---'

    def progress_sender(self):
        while self.progress <= 101:
            if self.status != os.environ.get("STATUS_ERROR"):
                self.set_progress()
                if self.progress >= 100 and self.end_time is None:
                    self.progress = 99.00
                    self.status = os.environ.get("STATUS_ACTIVE")
                response = None
                if os.environ.get("STATUS_WITH_STATE") == 'true':
                    response = {'status': self.status, 'progress': self.progress, 'state': self.shortcut_of_desc(self.state)}
                else:
                    response = {'status': self.status, 'progress': self.progress}
                if self.progress >= 100:
                    if os.environ.get("STATUS_PRINTER") == 'true':
                        print(os.environ.get("RESPONSE_URL"), response)
                    self.send_status(os.environ.get("RESPONSE_URL"), response)
                    break
                    re
                else:
                    if os.environ.get("STATUS_PRINTER") == 'true':
                        print(os.environ.get("RESPONSE_URL"), response)
                    self.send_status(os.environ.get("RESPONSE_URL"), response)
            else:
                response = {'status': self.status, 'progress': self.progress, 'state': self.shortcut_of_desc(self.state)}
                if os.environ.get("STATUS_PRINTER") == 'true':
                    print(os.environ.get("RESPONSE_URL"), response)
                self.send_status(os.environ.get("RESPONSE_URL"), response)
                break
            time.sleep(float(os.environ.get("STATUS_REFRESH_RATE")))
              

    def calc_avarage_time(self, recalc=None):
        avg = 0
        re_avg = 0
        with open(self.robot_path+".timmings", 'r+') as timmings:
            try:
                lines = [float(line.strip()) for line in timmings]
    
                for timming in lines:
                    avg+=timming

                if len(lines) < 1:
                    self.avg_time = float(os.environ.get("DEFAULT_EXECUTE_TIME"))
                else:
                    if recalc:
                        re_avg=recalc+avg
                        self.avg_time = re_avg/(len(lines)+1)
                    else:
                        self.avg_time = avg/len(lines)
            except Exception as e:
                self.avg_time = float(os.environ.get("DEFAULT_EXECUTE_TIME"))

    def start_timmings(self):
        self.start_time = time.time()

    def set_progress(self):
        if self.progress != 100:
            if self.status != os.environ.get("STATUS_ERROR"):
                left_time = (time.time() - self.start_time) * 1000
                self.calc_avarage_time(recalc=(time.time() - self.start_time))
                progress = abs(round((left_time / self.avg_time) * 100, 2))
                if progress >= 100:
                    self.progress = 100
                    self.status = os.environ.get("STATUS_COMPLETED")
                else:
                    self.progress = progress
                    self.status = os.environ.get("STATUS_ACTIVE")

    def end_timmings(self):
        self.end_time = time.time()
        with open(self.robot_path+'.timmings', 'a+') as timmings:
            timmings.write(f'{(self.end_time - self.start_time)*1000}\n')

    def log(self, func_name, args, kwargs, description, timming, trace, status):
        with open(self.robot_path+self.log_file, 'a+') as log:
            log.write(f' {status} | {str(datetime.now())} | {func_name} | {args} | {kwargs} | {description} | {timming}ms | {trace} \n')

    def send_mail_with_exception(self, trace, subject, description):
        for mail in os.environ.get("RECIVER_EMAIL").split(","):
            mailserver = smtplib.SMTP(os.environ.get("SMTP_HOST"), os.environ.get("SMTP_PORT"))
            mailserver.ehlo()
            mailserver.starttls()
            username = os.environ.get("SENDER_EMAIL")
            password = os.environ.get("SENDER_PASS")
            mailserver.login(username, password)
            msg = MIMEMultipart()
            msg['From'] = os.environ.get("SENDER_EMAIL")
            msg['To'] = mail
            msg['Subject'] = subject
            msg.attach(MIMEText(str(trace) + "\nRobot exit at: " + str(description)))

            attachment = MIMEApplication(open(self.log_file, "rb").read(), Name=str(self.log_file))
            attachment['Content-Disposition'] = 'attachment; filename="{}"'.format(self.log_file)
            msg.attach(attachment)
            mailserver.sendmail(username, mail, msg.as_string())
            mailserver.quit()

    def get_events(self):
        return self.events

    def register_event(self, description, in_loop=None, start=None, end=None):
        env_path = Path(str(self.robot_path)) / ".pytic"
        load_dotenv(dotenv_path=env_path)
        def decorator(function):
            def wrapper(*args, **kwargs):
                thread = None
                if not Event.func_is_in(function, self.events) or not Event.last_is_loop(function, self.events, self.counter):
                    self.events.append(Event(function, description, self.counter, in_loop))
                    self.counter += 1
                result = None
                if start:
                    self.start_timmings()
                    self.calc_avarage_time()
                    self.progress = 0
                    thread = Thread(target=self.progress_sender)
                    thread.start()
                try:
                    if os.environ.get("DEBUG_MODE") == "true":
                        if not in_loop:
                            print(f"{bcolors.WARNING}[DEBUG MODE]{bcolors.ENDC} {description}{bcolors.OKGREEN} [✓] {bcolors.ENDC} | {function.__name__}{args}{kwargs} ")
                        else:
                            print(f"{bcolors.WARNING}[DEBUG MODE]{bcolors.OKCYAN} [{in_loop}] {bcolors.ENDC}{description}{bcolors.OKGREEN} [✓] {bcolors.ENDC} | {function.__name__}{args}{kwargs} ")
                    else:
                        if not in_loop:
                            print(f"{bcolors.OKBLUE}[ROBOT]{bcolors.ENDC} {description}{bcolors.OKGREEN} [✓] {bcolors.ENDC}")
                        else:
                            print(f"{bcolors.OKBLUE}[ROBOT]{bcolors.OKCYAN} [{in_loop}]{bcolors.ENDC} {description}{bcolors.OKGREEN} [✓] {bcolors.ENDC}")
                    t1 = time.time()
                    self.state = description
                    result = function(*args, **kwargs)
                    t2 = time.time()
                    self.log(function.__name__, args, kwargs, description, (t2 - t1) * 1000, " - ", "PASS")
                except Exception as e:
                    if os.environ.get("DEBUG_MODE") == "true":
                        if not in_loop:
                            print(f"{bcolors.WARNING}[DEBUG MODE] {bcolors.ENDC}{description}{bcolors.FAIL} [x] {bcolors.ENDC} | {function.__name__}{args}{kwargs}, {str(e)}")
                        else:
                            print(f"{bcolors.WARNING}[DEBUG MODE]{bcolors.OKCYAN} [{in_loop}] {bcolors.ENDC}{description}{bcolors.FAIL} [x] {bcolors.ENDC} | {function.__name__}{args}{kwargs}, {str(e)}")
                    else:
                        if not in_loop:
                            print(f"{bcolors.OKBLUE}[ROBOT]{bcolors.ENDC}{description}{bcolors.FAIL} [x] {bcolors.ENDC}")
                        else:
                            print(f"{bcolors.OKBLUE}[ROBOT]{bcolors.OKCYAN} [{in_loop}]{bcolors.ENDC}{description}{bcolors.FAIL} [x] {bcolors.ENDC}")
                    if os.environ.get("SEND_EXCEPTIONS") == "true":
                        self.send_mail_with_exception(self.log_file, str(e), "ROBOT EXCEPTION", description)
                    if os.environ.get("ERROR_RAISE") == "true":
                        raise Exception(str(e))
                    self.status = os.environ.get("STATUS_ERROR")
                    self.log(function.__name__, args, kwargs, description, " - ", str(e), "FAIL")
                if end:
                    self.end_timmings()
                    self.progress = 100
                    self.status = os.environ.get("STATUS_COMPLETED")
                    self.build_docs()
                return result
            return wrapper
        return decorator

    def build_docs(self):
        with open(self.robot_path+"docs.txt", 'w+') as docs:
            docs.write("")
        for i, event in enumerate(self.events):
            if event.loop:
                with open(self.robot_path+"docs.txt", "a+") as docs:
                    docs.write(f'Step {event.pos} -> use function {event.func.__name__} in loop to do {event.description}\n')
            else:
                with open(self.robot_path+"docs.txt", "a+") as docs:
                    docs.write(f'Step {event.pos} -> use function {event.func.__name__} to do {event.description}\n')