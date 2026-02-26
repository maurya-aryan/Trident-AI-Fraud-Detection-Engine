"""Run a set of sample emails through the local TRIDENT API (/detect).

Usage: activate your venv then run `python scripts/run_samples.py`.
The script posts several test emails and prints the JSON responses.
"""
import json
import sys
from urllib import request

API_URL = "http://127.0.0.1:8000/detect"

SAMPLES = [
    {
        "name": "Urgent phishing",
        "body": {
            "email_text": "URGENT: Your account has been suspended due to suspicious activity. To restore access, click the link below and verify your identity immediately: http://secure-alert.xyz/login Please complete verification within 24 hours to avoid permanent suspension.",
            "email_subject": "Important: Account Verification Required",
            "sender": "no-reply@bank.example",
        },
    },
    {
        "name": "Credential leak",
        "body": {
            "email_text": "Hi team, I accidentally included a credential in the last message. For testing: password=Test@1234 and my API key is sk-live_ABCD1234EFGH5678IJKL Please rotate it ASAP.",
            "email_subject": "Credentials attached",
            "sender": "dev@example.com",
        },
    },
    {
        "name": "Benign email",
        "body": {
            "email_text": "Hi all, Please find attached the Q3 planning notes. Let's meet Wednesday at 10am to discuss milestones and action items. Thanks, Alice",
            "email_subject": "Meeting notes / Q3 planning",
            "sender": "alice@example.com",
        },
    },
]


def post_json(url: str, data: dict):
    b = json.dumps(data).encode("utf-8")
    req = request.Request(url, data=b, headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main():
    for s in SAMPLES:
        print("\n===", s["name"], "===")
        try:
            r = post_json(API_URL, s["body"])
            print(json.dumps(r, indent=2))
        except Exception as e:
            print("Request failed:", e)


if __name__ == "__main__":
    main()
