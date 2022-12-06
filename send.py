import sys

import requests

from appconfig import base_url, user, proxies

def send_message(num):
    if not num:
        num = int(input("Enter number to text: "))
    print("Enter the message to send, then EOF (Ctrl+D) to send")
    body = ''
    try:
        for i in sys.stdin:
            body += i
    except KeyboardInterrupt:
        return None
    body = body.strip()
    print('Sending...')
    req = requests.post(f"{base_url}{user}/send/{num}", data=body, proxies=proxies)
    return req
