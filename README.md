# spotprice

This Python script retrieves the current spot price for your Flick account by scraping the Flick dashboard.

## Overview
The first time this script is run, you will be prompted to save your credentials to a file. You can also create this file yourself by creating a file called ".credentials" in the same directory as this script with your username and password in the file. The username (your email address) must be on the first line and your password must be on the second line. Save the file with appropriate permissions so that only you can read the file. The cookies associated with your logon details will also be saved to disk to prevent unnecessary authentication.

Once the price has been retrieved it will be written to disk along with the time that the price will be refreshed online. This means you can run this script as often as you like but it will only retrieve the current price from the website when it needs to.

## Requirements
You need to be a Flick customer to use this script. It has been tested on Python 3.6 but should work on other versions of Python 3. Python 2 is not supported. Requirements have been added to a Piplock file so you'll need to have pipenv installed and then can use `pipenv install` to install requirements. If you want to install requirements manually, you'll need the following:
* requests
* beautifulsoup4
* html5lib

## Installation
1. Git clone this repository to your computer
2. Change to the directory that you've just cloned
3. pipenv install
4. pipenv shell
5. ./spotprice.py
6. pipenv exit

## Running the script
To run the script without activating the pipenv shell, use the following command: `pipenv run python spotprice.py`

## Output
The script will prompt you for credentials if it doesn't have a .credentials file, otherwise it will only output the current spot price rounded to one decimal.
