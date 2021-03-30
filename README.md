# autopytic
Improve your RPA python code with wrapper 🤯


# Feautes

```text
- Easy to use on existing scripts
- Auto-emails notifications at exception
- Auto-handling statuses on base worflow
- Auto-generate code timmings and save into file
- Auto-generate logs writer base on used functions workflow
- Auto-documentation code after every robot end
- Auto-progress with recalculation on-the-fly
- Auto-update robot status on management system using your own REST-API
- Auto-uploading logs into server using your own REST-API
- Auto-fetch config json from server using your own REST-API
- Simple VSC snippets to be fastest RPA Developers in the entire word...
...
```


# Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install autopytic
pip install python-dotenv
pip install requests
```
In  your main python script localization create file named .pytic with:

```bash
# Settings

# Turn on-off debug mode
DEBUG_MODE=false
# Turn on-off error raise after exception
ERROR_RAISE=false 

# Email Settings

# Turn on-off send email after exception with log file
SEND_EXCEPTIONS=false
# SMTP HOST ADRESS
SMTP_HOST=
# SMTP PORT
SMTP_PORT=
# SMTP SENDER EMAIL
SENDER_EMAIL=
# SMTP SENDER EMAIL PASSWORD
SENDER_PASS=
# List of email addresses to which messages are sent :: separated by comma
RECIVER_EMAIL=

# Coverage Settings

# Exclude given paths from code coverage (example ./venv):: separated by comma
EXCLUDE_VENV=

# Status Settings

# Default script execute first time in ms (does not need to be edited)
DEFAULT_EXECUTE_TIME=1000000000
# Address to which the response with the robot's status and progress is to be sent
RESPONSE_URL=
# Response refresh rate in ms
# If the robot is fast, it is recommended to lower the rate to indicate status other than 0-100
STATUS_REFRESH_RATE=0.1
# Active status name for response
STATUS_ACTIVE=Aktywny
# Completed status name for response
STATUS_COMPLETED=Zakonczony
# Error status name for response
STATUS_ERROR=Krytyczny
# Disalbled status name for response
STATUS_DISABLED=Wyłączony
# Returning together with the status of the place where the robot is located
STATUS_WITH_STATE=false
# This form is helpful for previewing progress in the console :: Turn on-off
STATUS_PRINTER=false

# Logs Settings

# Address to upload logs into server
UPLOAD_LOGS_URL=

# Config Settings

# Addres to fetch json config from server
GET_CONFIG_URL=
```

# Usage example

```python
from autopytic.tools.wrapper import Wrapper

Robot = Wrapper(robot_path='',log_file='logs.txt')


class _Robot:
    @Robot.register_event(description='Initialized robot')
    def __init__(self):
        pass

    @Robot.register_event(description='Run robot method', start=True)
    def run(self):
        pass

    @Robot.register_event(description='End method', end=True)
    def end(self):
        pass


r = _Robot()

try:
    r.run()
    r.end()
except (KeyboardInterrupt, Exception) as e:
    r.end()
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

![alt text](https://scontent-frx5-1.xx.fbcdn.net/v/t1.15752-9/162576374_738313917056023_2227397670571772516_n.png?_nc_cat=105&ccb=1-3&_nc_sid=ae9488&_nc_ohc=eduEud5TNk0AX--WKMF&_nc_ht=scontent-frx5-1.xx&oh=cf67ba50d1cc8d78ad4625f86269a92f&oe=607A2BCC)

## Loop handling
If you want to read the code based on loops easier, use in_loop (default false), to avoid too much spam in the documentation, the display loops are slightly shortened:
```python
@Robot.register_event(description="Say hello", in_loop=True)
def say_hello():
        return 'hello'
```
![alt text](https://scontent-frx5-1.xx.fbcdn.net/v/t1.15752-9/162423911_3598383523622520_6294617938623607163_n.png?_nc_cat=111&ccb=1-3&_nc_sid=ae9488&_nc_ohc=HzMRXPeT1TIAX-10_hh&_nc_ht=scontent-frx5-1.xx&oh=c1e75260535233ec5ec1f933d4d2cff2&oe=607A2DE5)


# Email reports
![alt text](https://scontent.xx.fbcdn.net/v/t1.15752-9/s720x720/162541731_478836726825561_4977739555938880918_n.png?_nc_cat=105&ccb=1-3&_nc_sid=58c789&_nc_ohc=yw-Z-q4xR5YAX-LokyH&_nc_ad=z-m&_nc_cid=0&_nc_ht=scontent.xx&_nc_tp=30&oh=7f5f54d162ea79063398992ff22711c9&oe=6077A881)

# Auto-logging
```text
 FAIL | 2021-03-18 20:01:19.479666 | say_hello | (<__main__.Robot object at 0x105d20460>,) | Say hello |  - ms | unsupported operand type(s) for +: 'int' and 'str' 
 PASS | 2021-03-18 20:01:19.789123 | process_and_response | (<__main__.Robot object at 0x105d20460>, <Response [200]>) | Try to scrap something and return value | 0.0019073486328125ms |  -  
 PASS | 2021-03-18 20:01:19.789445 | get_page | (<__main__.Robot object at 0x105d20460>, 'https://www.google.pl/') | Send requests to get scrapping page | 307.56616592407227ms |  -  
```

# Auto-documentation
The code is automatically documented after each work completion and put into the docs.txt file
## Output

```text
Step 0 -> use function run to do Final Run robot method
Step 1 -> use function fetch_from_site to do Fetch something from site
Step 2 -> use function say_hello to do Say hello
Step 3 -> use function get_page to do Send requests to get scrapping page
Step 4 -> use function end to do Final End robot method

```

# Code coverage
To check code coverage use in main directory
```bash
python3 -m autopytic coverage
```
![alt text](https://scontent-frx5-1.xx.fbcdn.net/v/t1.15752-9/164395601_826109344641414_6244449682530667881_n.png?_nc_cat=111&ccb=1-3&_nc_sid=ae9488&_nc_ohc=Y61eKwbXd6QAX_ZUyFd&_nc_ht=scontent-frx5-1.xx&oh=d23b2418a8b88a48a0a2954449b76895&oe=607F703B)

# VisualStudio Code Snippet
In order not to focus on writing it every time, it is worth adding a snippet to your IDE as in this case:
```json
	"init_robot": {
		"prefix": "init",
		"body": [
			"from autopytic.tools.wrapper import Wrapper",
			"",
			"Robot = Wrapper(robot_path='${1:robot_path}',log_file='logs.txt')",
			"",
			"",
			"class Robot:",
			"    @Robot.register_event(description='Initialized robot')",
			"    def __init__(self):",
			"        pass",
			"",
			"    @Robot.register_event(description='Run robot method', start=True)",
			"    def run(self):",
			"        pass",
			"",
			"    @Robot.register_event(description='End method', end=True)",
			"    def end(self):",
			"        pass",
			"",
			"",
			"r = Robot()",
			"",
			"try:",
			"    r.run()",
			"    r.end()",
			"except (KeyboardInterrupt, Exception) as e:",
			"    r.end()"
		],
		"description": "Initialize new robot"
	},
	"register_event": {
		"prefix": "register",
		"body": [
			"@Robot.register_event(${1:description})"
		],
		"description": "Register new robot event"
	},
	"function_with_register": {
		"prefix": "_def",
		"body": [
			"@Robot.register_event(description='${1:description}')",
			"def ${2:method_name}(self):",
			"   pass",
			""
		],
		"description": "New method with registered event"
	}
```

![alt text](https://scontent-frt3-1.xx.fbcdn.net/v/t1.15752-9/164674548_784424118854973_357628764616796429_n.png?_nc_cat=108&ccb=1-3&_nc_sid=ae9488&_nc_ohc=L38QmFfZUiwAX8jErDQ&_nc_ht=scontent-frt3-1.xx&oh=46ab422716a8d34d4817683fa58c06f1&oe=607FA96E)


![alt text](https://scontent-frt3-2.xx.fbcdn.net/v/t1.15752-9/164489503_168141625135466_263825998897416945_n.png?_nc_cat=103&ccb=1-3&_nc_sid=ae9488&_nc_ohc=DgPw2WAC9nwAX8ejhqE&_nc_ht=scontent-frt3-2.xx&oh=1fd939672ba7e8d7b55aea7b22e5b926&oe=607FABE3)













