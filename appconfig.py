import os
import sys
from base64 import urlsafe_b64encode

VERSION = '1.0.0'

base_url = "https://api.monerosms.com/"
proxies = {}
if os.getenv("MONERO_SMS_TOR", None):
    base_url = "http://api.xmr4smsoncunkfgfjr6xmxl57afsmuu6rg2bwuysbgg4wdtoawamwxad.onion/"
    if not os.getenv("MONERO_SMS_TRANSPARENT_TOR", None):
        proxies = {
            'http': f'socks4a://127.0.0.1:{os.getenv("MONERO_SMS_TOR")}',
            'https': f'socks4a://127.0.0.1:{os.getenv("MONERO_SMS_TOR")}'
        }

user = os.getenv('MONERO_SMS_TOKEN')

auth_file = os.getenv('MONERO_SMS_AUTH_FILE', 'monerosms-auth')

generating = False
try:
    generating = sys.argv[1]
    if generating == "generate":
        generating = True
except IndexError:
    generating = False

if not user and not generating is True:
    try:
        with open(auth_file, 'r') as f:
            user = f.read()
    except FileNotFoundError:
        pass
    if not user:
        sys.stderr.write("Must set MONERO_SMS_TOKEN environment variable,\n")
        sys.stderr.write(
            f"or store it in a file named {auth_file} in the cwd directory\n")
        sys.stderr.write(f"Generate the file with $ {sys.argv[0]} generate")
        sys.exit(1)
