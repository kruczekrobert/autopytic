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

env_path = Path(".") / ".pytic"
load_dotenv(dotenv_path=env_path)

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
    events = []
    counter = 0 
    progress = 0
    start_time = None
    end_time = None
    avg_time = None
    status = None
    state = None

    @staticmethod
    def send_status(response_url, response):
        if response_url:
            try:
                requests.put(os.environ.get("RESPONSE_URL"), json=response)
            except:
                print("Cannot send status - check RESPONSE_URL or network")
            

    @staticmethod
    def progress_sender():
        while Wrapper.progress <= 101:
            if Wrapper.status != os.environ.get("STATUS_ERROR"):
                Wrapper.set_progress()
                if Wrapper.progress >= 100 and Wrapper.end_time is None:
                    Wrapper.progress = 99.00
                response = None
                if os.environ.get("STATUS_WITH_STATE") == 'true':
                    response = {'status': Wrapper.status, 'progress': Wrapper.progress, 'state': Wrapper.state}
                else:
                    response = {'status': Wrapper.status, 'progress': Wrapper.progress}
                if Wrapper.progress >= 100:
                    if os.environ.get("STATUS_PRINTER") == 'true':
                        print(os.environ.get("RESPONSE_URL"), response)
                    Wrapper.send_status(os.environ.get("RESPONSE_URL"), response)
                    break
                    re
                else:
                    if os.environ.get("STATUS_PRINTER") == 'true':
                        print(os.environ.get("RESPONSE_URL"), response)
                    Wrapper.send_status(os.environ.get("RESPONSE_URL"), response)
            else:
                response = {'status': Wrapper.status, 'progress': Wrapper.progress, 'state': Wrapper.state}
                if os.environ.get("STATUS_PRINTER") == 'true':
                    print(os.environ.get("RESPONSE_URL"), response)
                Wrapper.send_status(os.environ.get("RESPONSE_URL"), response)
                break
            time.sleep(float(os.environ.get("STATUS_REFRESH_RATE")))
              

    @staticmethod
    def calc_avarage_time(recalc=None):
        avg = 0
        re_avg = 0
        with open(".timmings", 'r') as timmings:
            try:
                lines = [float(line.strip()) for line in timmings]
    
                for timming in lines:
                    avg+=timming

                if len(lines) < 1:
                    Wrapper.avg_time = float(os.environ.get("DEFAULT_EXECUTE_TIME"))
                else:
                    if recalc:
                        re_avg=recalc+avg
                        Wrapper.avg_time = re_avg/(len(lines)+1)
                    else:
                        Wrapper.avg_time = avg/len(lines)
            except:
                Wrapper.avg_time = float(os.environ.get("DEFAULT_EXECUTE_TIME"))


    @staticmethod
    def start_timmings():
        Wrapper.start_time = time.time()

    @staticmethod
    def set_progress():
        if Wrapper.progress != 100:
            if Wrapper.status != os.environ.get("STATUS_ERROR"):
                left_time = (time.time() - Wrapper.start_time) * 1000
                Wrapper.calc_avarage_time(recalc=(time.time() - Wrapper.start_time))
                progress = abs(round((left_time / Wrapper.avg_time) * 100, 2))
                if progress >= 100:
                    Wrapper.progress = 100
                    Wrapper.status = os.environ.get("STATUS_COMPLETED")
                else:
                    Wrapper.progress = progress
                    Wrapper.status = os.environ.get("STATUS_ACTIVE")

    @staticmethod
    def end_timmings():
        Wrapper.end_time = time.time()
        with open('.timmings', 'a') as timmings:
            timmings.write(f'{(Wrapper.end_time - Wrapper.start_time)*1000}\n')

    @staticmethod
    def log(logfile, func_name, args, kwargs, description, timming, trace, status):
        with open(logfile, 'a') as log:
            try:
                log.write(f' {status} | {str(datetime.now())} | {func_name} | {args} | {kwargs} | {description} | {timming}ms | {trace} \n')
            except:
                pass


    @staticmethod
    def send_mail_with_exception(logfile, trace, subject, description):
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

            attachment = MIMEApplication(open(logfile, "rb").read(), Name=str(logfile))
            attachment['Content-Disposition'] = 'attachment; filename="{}"'.format(logfile)
            msg.attach(attachment)
            mailserver.sendmail(username, mail, msg.as_string())
            mailserver.quit()

    @staticmethod
    def get_events():
        return Wrapper.events

    @staticmethod
    def register_event(description, logfile, in_loop=None, start=None, end=None):
        def decorator(function):
            def wrapper(*args, **kwargs):
                thread = None
                if not Event.func_is_in(function, Wrapper.events) or not Event.last_is_loop(function, Wrapper.events, Wrapper.counter):
                    Wrapper.events.append(Event(function, description, Wrapper.counter, in_loop))
                    Wrapper.counter += 1
                result = None
                if start:
                    Wrapper.start_timmings()
                    Wrapper.calc_avarage_time()
                    Wrapper.progress = 0
                    thread = Thread(target=Wrapper.progress_sender)
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
                    Wrapper.state = description
                    result = function(*args, **kwargs)
                    t2 = time.time()
                    Wrapper.log(logfile, function.__name__, args, kwargs, description, (t2 - t1) * 1000, " - ", "PASS")
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
                        Wrapper.send_mail_with_exception(logfile, str(e), "ROBOT EXCEPTION", description)
                    if os.environ.get("ERROR_RAISE") == "true":
                        raise Exception(str(e))
                    Wrapper.status = os.environ.get("STATUS_ERROR")
                    Wrapper.log(logfile, function.__name__, args, kwargs, description, " - ", str(e), "FAIL")
                if end:
                    Wrapper.end_timmings()
                    Wrapper.progress = 100
                    Wrapper.status = os.environ.get("STATUS_COMPLETED")
                    Wrapper.build_docs()
                return result
            return wrapper
        return decorator

    @staticmethod
    def build_docs():
        with open("docs.txt", 'w') as docs:
            docs.write("")
        for i, event in enumerate(Wrapper.events):
            if event.loop:
                with open("docs.txt", "a") as docs:
                    docs.write(f'Step {event.pos} -> use function {event.func.__name__} in loop to do {event.description}\n')
            else:
                with open("docs.txt", "a") as docs:
                    docs.write(f'Step {event.pos} -> use function {event.func.__name__} to do {event.description}\n')