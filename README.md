# autopytic
Improve your RPA python code with wrapper 🤯


# Feautes

```text
- Easy to use on existing scripts
- Send email notifications on exception
- Auto-timmings
- Auto-logging 
- Auto-documentation
...
```


# Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install autopytic
```
In  your main python script localization create file named .pytic with:

```bash
# Settings
DEBUG_MODE=false
ERROR_RAISE=false

# Email Settings
SEND_EXCEPTIONS=false
SMTP_HOST=
SMTP_PORT=
SENDER_EMAIL=
SENDER_PASS=
RECIVER_EMAIL=
```

# Usage example

```python
from autopytic.tools.wrapper import Wrapper
import requests

logfile = "log.txt"


class Robot:

    @Wrapper.register_event(logfile=logfile, description="Send requests to get scrapping page")
    def get_page(self, url):
        r = requests.get(url)
        self.process_and_response(r)

    @Wrapper.register_event(logfile=logfile, description="Try to scrap something and return value")
    def process_and_response(self, request):
        ## some processing
        return request.status_code

    @Wrapper.register_event(logfile=logfile, description="Say hello")
    def say_hello(self):
        return 'hello'

    def run(self):
        self.say_hello()
        self.get_page("https://www.google.pl/")



r = Robot()
r.run()
```

# Console output
![alt text](https://scontent-frt3-1.xx.fbcdn.net/v/t1.15752-9/162526532_489456259129970_6749466983417023895_n.png?_nc_cat=102&ccb=1-3&_nc_sid=ae9488&_nc_ohc=Ka9SYCl0TGwAX-0sbIX&_nc_ht=scontent-frt3-1.xx&oh=50bcab9310805410040c793846b4ba22&oe=6079EFC9)

# Debug mode console output

![alt text](https://scontent-frx5-1.xx.fbcdn.net/v/t1.15752-9/162138034_490965622313447_943137998617763135_n.png?_nc_cat=110&ccb=1-3&_nc_sid=ae9488&_nc_ohc=qMTae1WzWLkAX8Kc7Vj&_nc_ht=scontent-frx5-1.xx&oh=e0e6526137d2972e8d19137d2fde271a&oe=607A6F45)

# Tips

## Error handling
```bash
ERROR_RAISE=false # Wrapper will not return any exception after a failed action easy to debug step actions
```
![alt text](https://scontent-frx5-1.xx.fbcdn.net/v/t1.15752-9/162112125_491316998918806_8913073512464101177_n.png?_nc_cat=111&ccb=1-3&_nc_sid=ae9488&_nc_ohc=GuyjH5_yyBoAX8p2Woy&_nc_ht=scontent-frx5-1.xx&oh=87ee73ca5134676a47f6121b2fd8a6b0&oe=6079A2CA)

```bash
ERROR_RAISE=true # Wrapper will return exception after a failed action
```

![alt text](https://scontent-frt3-1.xx.fbcdn.net/v/t1.15752-9/162488260_1076633426139679_6936695617478056847_n.png?_nc_cat=108&ccb=1-3&_nc_sid=ae9488&_nc_ohc=EDhQ9h8iF1QAX_HLXAy&_nc_ht=scontent-frt3-1.xx&oh=0a331e7f5f3e740d34c5f0af51f86f48&oe=60791311)


# Email reports
![alt text](https://scontent.xx.fbcdn.net/v/t1.15752-9/s720x720/162541731_478836726825561_4977739555938880918_n.png?_nc_cat=105&ccb=1-3&_nc_sid=58c789&_nc_ohc=yw-Z-q4xR5YAX-LokyH&_nc_ad=z-m&_nc_cid=0&_nc_ht=scontent.xx&_nc_tp=30&oh=7f5f54d162ea79063398992ff22711c9&oe=6077A881)

# Auto-logging
```text
 FAIL | 2021-03-18 20:01:19.479666 | say_hello | (<__main__.Robot object at 0x105d20460>,) | Say hello |  - ms | unsupported operand type(s) for +: 'int' and 'str' 
 PASS | 2021-03-18 20:01:19.789123 | process_and_response | (<__main__.Robot object at 0x105d20460>, <Response [200]>) | Try to scrap something and return value | 0.0019073486328125ms |  -  
 PASS | 2021-03-18 20:01:19.789445 | get_page | (<__main__.Robot object at 0x105d20460>, 'https://www.google.pl/') | Send requests to get scrapping page | 307.56616592407227ms |  -  
```

# Auto-documentation
To make auto-documentation file add to the end of the script:

```python
Wrapper.build_docs()
```
## Output

```text
Step 0 use function say_hello to do Say hello
Step 1 use function get_page to do Send requests to get scrapping page
Step 2 use function process_and_response to do Try to scrap something and return value
```









