#!/usr/bin/env python3
"""Retrieves the latest spot price for your Flick account.
"""

import requests
import http.cookiejar
from requests import session
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path
import getpass
from datetime import datetime


# These are files required for the script:
credential_file = Path(".credentials")
cookie_file = Path(".cookies")
price_file = Path(".price")


def save_credentials():
    """Prompts you for your credentials and tries to save them to disk.

    Returns:
        A list of credentials: [username, password]
    """

    print("We need to save your credentials to access the website.")
    username = input("Please enter your username (email address): ")
    password = getpass.getpass(
        "And your password (this won't be shown on the screen): "
    )

    try:
        with open(credential_file, "w") as cred_file:
            cred_file.write(username + "\n" + password)
            cred_file.close()
        os.chmod(credential_file, 0o600)
    except EnvironmentError as err:
        print(
            "Unable to save the credential file to disk. We can continue, but you will be prompted for credentials again next time you run this script."
        )
        print("The error message was:", err)
    credentials = [username, password]
    return credentials


def get_credentials():
    """Reads credentials from disk and returns them as a list. If they don't 
    exist, then use the save_credentials function to prompt and save them.

    Returns:
        A list of credentials: [username, password]
    """
    try:
        with open(credential_file) as cred_file:
            content = cred_file.readlines()
            # content should be two lines, the first line is the username, the second line is the password
            if len(content) == 2:
                credentials = [content[0], content[1]]
            else:
                credentials = save_credentials()
    except:
        credentials = save_credentials()
    return credentials


def get_online_price():
    """This gets the spot price from the website first trying with the saved
    cookie file if it exists, or by reading your saved credentials with the
    get_credentials function, or if no credentials have been saved, you will 
    be prompted to enter your credentials which will then be saved using the 
    save_credentials function.

    Returns:
        A float of the spot price in cents.
    """
    cj = http.cookiejar.LWPCookieJar()
    try:
        cj.load(cookie_file)
    except:
        pass

    s = requests.Session()
    s.cookies = cj

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"
    }
    s.headers.update(headers)

    # These are the two URLs required:
    dashboard_url = "https://myflick.flickelectric.co.nz/dashboard/snapshot"
    auth_url = "https://id.flickelectric.co.nz/identity/users/sign_in"

    # Try to retrieve the dashboard, but if you end up on another url, it
    # means you're not logged in.
    req = s.get(dashboard_url)
    if req.url != dashboard_url:
        # Get the credentials to log in with
        credentials = get_credentials()
        username = credentials[0]
        password = credentials[1]

        # We need to get the authenticity_token and the UTF hidden form fields
        soup = BeautifulSoup(req.content, "html.parser")
        token_value = soup.find("input", {"name": "authenticity_token"})["value"]
        utf_value = soup.find("input", {"name": "utf8"})["value"]

        # Create the form payload to be submitted
        payload = {
            "user[email]": username,
            "user[password]": password,
            "user[remember_me]": "1",
            "authenticity_token": token_value,
            "utf8": utf_value,
        }

        # Add some headers required to submit the form
        headers.update(
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "id.flickelectric.co.nz",
                "Origin": "https://id.flickelectric.co.nz",
                "Referer": auth_url,
            }
        )

        # Submit the form...
        req = s.post(auth_url, headers=headers, data=payload)

        # Now we should be authed, we can get the dashboard page:
        req = s.get(dashboard_url)

        # Check that we're on the right URL, if not then clear credentials and
        # exit.
        if req.url != dashboard_url:
            print("Unable to log in. Clearing the saved credential, please try again.")
            os.remove(credential_file)
            exit(1)

    # Let's try saving the cookies to a reasonably secure file
    try:
        cj.save(filename=cookie_file, ignore_discard=True, ignore_expires=True)
        os.chmod(cookie_file, 0o600)
    except:
        # Unable to save cookies to file. You will need to reauthenticate with
        # the website each time you run the script.
        pass

    # Get the spot price
    soup = BeautifulSoup(req.text, "html.parser")
    div = soup.select_one("div[data-react-class=FlickNeedle]")
    div_json = json.loads(div["data-react-props"])
    price_value = div_json["currentPeriod"]["price"]["value"]
    end_at = div_json["currentPeriod"]["end_at"]

    # Write the spot price to file
    try:
        with open(price_file, "w") as file:
            out_json = {}
            out_json["current_price"] = price_value
            out_json["end_at"] = end_at
            file.write(json.dumps(out_json))
            file.close()
    except:
        # Unable to write the spot price to file - this will lead to excessive
        # calls to the website if run frequently."
        pass

    return float(price_value)


def get_spot_price():
    """This returns the spot price from the saved file if within the current 
    period, or from the website if required.
    
    Returns:
        A float of the spot price in cents.
    """
    if price_file.exists():
        with open(price_file) as file:
            json_data = json.load(file)
            end_at_date = datetime.strptime(json_data["end_at"], "%Y-%m-%dT%H:%M:%SZ")

        if datetime.utcnow() < end_at_date:
            return float(json_data["current_price"])
        else:
            return get_online_price()
    else:
        return get_online_price()


if __name__ == "__main__":
    print(round(get_spot_price(), 1))
