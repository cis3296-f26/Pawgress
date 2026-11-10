# Pawgress
A helpful study bot for discord that acts as a pet for you and your study group! The bot will track your time studying and will reward you for doing so. You may then use your rewards to keep your group pet alive and happy.

## Installation
To install the bot to your server, use the link: https://discord.com/oauth2/authorize?client_id=1562131394514255912&permissions=8&integration_type=0&scope=bot

To install, and run it locally all you need is the code in this repo and python, python dotenv, discord, and the aiosqulite library.

You can use the following commands:
py -m pip install discord.py
py -m pip install python-dotenv
py -m pip install aiosqlite

## Build
No build of the application is needed in order to run the Discord Bot as Pawgress runs on directly the Python Interpreter and the code is uploaded onto a server that is hosting it.

## Run
If you want to run the bot for yourself on your local machine, run the python file locally (main.py). Normally you should be able to access the hosted bot by downloading it into your discord server.

### Run commands:
/help - bot will list commands
/create_pet - will create a new pet for your group
/rename_pet - rename your group's pet
/study_info - display descriptions of each study method
/study_start - select a study method and start a study session
/study_stop - end your study session
/store_catalog - display food items and their prices
/store_buy - select and buy food for your pet
/user_balance - check how many coins you have
/user_inventory - check your inventory

## Testing
Install the test dependencies and run pytest from the project folder:

py -m pip install -r requirements-dev.txt
py -m pytest

The tests use a temporary database so they won't touch your real one, and they don't need a Discord token. There's also a checklist for testing the bot in a real server in tests/MANUAL_TESTS.md.
