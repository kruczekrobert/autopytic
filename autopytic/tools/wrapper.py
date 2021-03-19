import inspect
import os, glob
from pathlib import Path  # Python 3.6

from dotenv import load_dotenv
from datetime import datetime
import time
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
    def __init__(self, func, description, pos):
        self.pos = pos
        self.func = func
        self.description = description
        
    def __str__(self):
        return f'{self.pos}: {self.func.__name__}, {self.description}'

class Wrapper:

    events = []
    counter = 0 

    @staticmethod
    def log(logfile, func_name, args, kwargs, description, timming, trace, status):
        with open(logfile, "a") as log:
            log.write(f' {status} | {str(datetime.now())} | {func_name} | {args} | {kwargs} | {description} | {timming}ms | {trace} \n')


    @staticmethod
    def send_mail_with_exception(logfile, trace, subject, description):
        mailserver = smtplib.SMTP(os.environ.get("SMTP_HOST"), os.environ.get("SMTP_PORT"))
        mailserver.ehlo()
        mailserver.starttls()
        username = os.environ.get("SENDER_EMAIL")
        password = os.environ.get("SENDER_PASS")
        mailserver.login(username, password)
        msg = MIMEMultipart()
        msg['From'] = os.environ.get("SENDER_EMAIL")
        msg['To'] = os.environ.get("RECIVER_EMAIL")
        msg['Subject'] = subject
        msg.attach(MIMEText(str(trace) + "\nRobot exit at: " + str(description)))

        attachment = MIMEApplication(open(logfile, "rb").read(), Name=str(logfile))
        attachment['Content-Disposition'] = 'attachment; filename="{}"'.format(logfile)
        msg.attach(attachment)
        mailserver.sendmail(username, os.environ.get("RECIVER_EMAIL"), msg.as_string())
        mailserver.quit()

    @staticmethod
    def get_events():
        return Wrapper.events

    @staticmethod
    def register_event(description, logfile, in_loop=False):
        def decorator(function):
            def wrapper(*args, **kwargs):
                Wrapper.events.append(Event(function, description, Wrapper.counter))
                Wrapper.counter += 1
                result = None
                try:
                    t1 = time.time()
                    result = function(*args, **kwargs)
                    t2 = time.time()
                    if os.environ.get("DEBUG_MODE") == "true":
                        if not in_loop:
                            print(f"{bcolors.WARNING}[DEBUG MODE] {bcolors.ENDC}{description}{bcolors.OKGREEN} [✓] {bcolors.ENDC} | {function.__name__}{args}{kwargs} ")
                        else:
                            print(f"{bcolors.WARNING}[DEBUG MODE]{bcolors.OKCYAN} [LOOP] {bcolors.ENDC}{description}{bcolors.OKGREEN} [✓] {bcolors.ENDC} | {function.__name__}{args}{kwargs} ")
                    else:
                        if not in_loop:
                            print(f"{bcolors.OKBLUE}[ROBOT]{bcolors.ENDC} {description}{bcolors.OKGREEN} [✓] {bcolors.ENDC}")
                        else:
                            print(f"{bcolors.OKBLUE}[ROBOT]{bcolors.OKCYAN} [LOOP]{bcolors.ENDC} {description}{bcolors.OKGREEN} [✓] {bcolors.ENDC}")
                    Wrapper.log(logfile, function.__name__, args, kwargs, description, (t2 - t1) * 1000, " - ", "PASS")
                except Exception as e:
                    if os.environ.get("DEBUG_MODE") == "true":
                        if not in_loop:
                            print(f"{bcolors.WARNING}[DEBUG MODE] {bcolors.ENDC}{description}{bcolors.FAIL} [x] {bcolors.ENDC} | {function.__name__}{args}{kwargs}, {str(e)}")
                        else:
                            print(f"{bcolors.WARNING}[DEBUG MODE]{bcolors.OKCYAN} [LOOP] {bcolors.ENDC}{description}{bcolors.FAIL} [x] {bcolors.ENDC} | {function.__name__}{args}{kwargs}, {str(e)}")
                    else:
                        if not in_loop:
                            print(f"{bcolors.OKBLUE}[ROBOT]{bcolors.ENDC} {description}{bcolors.FAIL} [x] {bcolors.ENDC}")
                        else:
                            print(f"{bcolors.OKBLUE}[ROBOT]{bcolors.OKCYAN} [LOOP]{bcolors.ENDC} {description}{bcolors.FAIL} [x] {bcolors.ENDC}")
                    if os.environ.get("SEND_EXCEPTIONS") == "true":
                        Wrapper.send_mail_with_exception(logfile, str(e), "ROBOT EXCEPTION", description)
                    if os.environ.get("ERROR_RAISE") == "true":
                        raise Exception(str(e))
                    Wrapper.log(logfile, function.__name__, args, kwargs, description, " - ", str(e), "FAIL")
                return result
            return wrapper
        return decorator

    @staticmethod
    def build_docs():
        with open("docs.txt", 'w') as docs:
            docs.write("")
        for event in Wrapper.events:
            with open("docs.txt", "a") as docs:
                docs.write(f'Step {event.pos} use function {event.func.__name__} to do {event.description}\n')