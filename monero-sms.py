#!/usr/bin/env python3
import sys
import secrets
import os
import json
import datetime
from time import sleep
import traceback

import requests

from send import send_message
from appconfig import VERSION, base_url, user, auth_file, proxies

try:
    arg = sys.argv[1]
except IndexError:
    arg = ''

req = None


def watch_thread(thread_num):
    n = 0
    rest_secs = 5
    try:
        rest_secs = sys.argv[3]
    except IndexError:
        pass
    try:
        while True:
            req = requests.get(f"{base_url}{user}/thread/{thread_num}/{n}", proxies=proxies)
            if req.status_code == 404:
                if n == 0:
                    print('No such thread.')
                sleep(rest_secs)
                continue
            else:
                if req.text.strip():
                    n += 1
                    print(req.text)
            sleep(rest_secs)
    except KeyboardInterrupt:
        pass


def menu():
    offset = 0
    req = None
    match arg:
        case "generate":
            if os.path.exists(auth_file):
                print("Auth file already exists, delete to generate a new one or change the MONERO_SMS_AUTH_FILE env variable")
                return None
            if not os.getenv("MONEROSMS_I_AGREE_TO_TOS", False):
                print(f"By using the service you agree to the terms of service, at {base_url}tos")
                print("The terms of service is human readable")
                agree = input("Have you read the terms of service and do you agree to them? y/n ").lower()
                if agree not in ['y', 'yes']:
                    print("You are not permitted to use the service unless you agree.")
                    return None
            with open(auth_file, 'w') as f:
                f.write(secrets.token_hex(25))
            print(f'Account number generated {auth_file}')
            print('Back it up to keep access to your account')
            return None
        case "disableemail":
            req = requests.post(f'{base_url}{user}/setemail/none')
        case "setemail":
            try:
                email = sys.argv[2]
            except IndexError:
                email = input("Email address: ")
            req = requests.post(f'{base_url}{user}/setemail/{email}', proxies=proxies)
        case "pricing":
            req = requests.get(f'{base_url}pricing', proxies=proxies)
        case "listnumbers":
            req = requests.get(f'{base_url}availablenumbers', proxies=proxies)
            if not req.text:
                print("No numbers available currently, check back later")
                return None
            return req
        case "buynumber":
            try:
                num = int(sys.argv[2])
            except (IndexError, ValueError) as _:
                sys.stderr.write("Must specify number to buy")
                sys.exit(5)
            req = requests.post(f"{base_url}{user}/buynumber/{num}", proxies=proxies)
        case "number":
            req = requests.get(f"{base_url}{user}/number", proxies=proxies)
        case "credits":
            req = requests.get(f"{base_url}{user}/creditbal", proxies=proxies)
        case "threads":
            req = requests.get(f"{base_url}{user}/list", proxies=proxies)
        case "xmraddress":
            req = requests.get(f"{base_url}{user}/get_user_wallet", proxies=proxies)
        case "tos":
            req = requests.get(f"{base_url}tos", proxies=proxies)
        case "delete":
            try:
                req = requests.delete(
                    f"{base_url}{user}/delete/{int(sys.argv[2])}", proxies=proxies)
            except (IndexError, ValueError) as _:  # noqa
                sys.stderr.write(
                    "Must specify thread to delete by phone number\n")
                sys.exit(4)
        case "send":
            try:
                to = sys.argv[2]
            except IndexError:
                to = 0
            try:
                req = send_message(to)
            except ValueError:
                sys.stderr.write("Invalid phone number")
        case "watch":
            watch_thread(int(sys.argv[2]))
            return None
        case "get" | "thread":
            try:
                thread_num = sys.argv[2]
            except IndexError:
                sys.stderr.write(
                    "Must specify thread to view by phone number\n")
                sys.exit(4)
            try:
                offset = int(sys.argv[3])
            except IndexError:
                pass
            req = requests.get(
                f"{base_url}{user}/thread/{thread_num}/{offset}", proxies=proxies)
            if req.status_code != 200:
                sys.stderr.write(f"Error {req.status_code} \n{req.text}")
                sys.exit(1)
            for message in req.json():
                if message['Incoming']:
                    # EpochMili to human readable
                    print(datetime.datetime.fromtimestamp(
                            message['EpochMili'] / 1000).strftime(
                                '%Y-%m-%d %H:%M:%S'),
                          f"From {thread_num}:\n{message['Body']}")
                else:
                    print(datetime.datetime.fromtimestamp(
                            message['EpochMili'] / 1000).strftime(
                                '%Y-%m-%d %H:%M:%S'),
                          f"To {thread_num}:\n{message['Body']}")
            sys.exit(0)

        case "":
            print(f"MoneroSMS Client v{VERSION}")
            sys.exit(0)
        case _:
            print("No such command")
    return req


try:
    req = menu()
except requests.exceptions.ConnectionError as e:
    sys.stderr.write("Error connecting to server: ")
    sys.stderr.write(str(e))
    sys.exit(2)
except requests.exceptions.InvalidSchema:
    sys.stderr.write("Missing requests[socks] support but MONERO_SMS_TOR was set")
    sys.exit(2)
except Exception:
    sys.stderr.write("An Error occurred: ")
    sys.stderr.write(traceback.format_exc())
    sys.exit(3)
except KeyboardInterrupt:
    sys.exit(1)


if req is not None:

    if req.status_code != 200:
        sys.stderr.write(f"Error {req.status_code} \n{req.text}")
        sys.exit(1)
    print(req.text)
