"""Generate synthetic test datasets for model evaluation.

Creates:
- data/test_emails.csv         (400 rows: 200 phishing, 200 legitimate)
- data/test_task_emails.csv    (100 rows with task annotations)
- data/test_urls.csv           (200 rows: 100 malicious, 100 benign)
- data/README.md               (describes files)

Run: python scripts/generate_test_data.py
"""
from pathlib import Path
import csv
import random
import datetime

random.seed(42)
BASE_DIR = Path('data')
BASE_DIR.mkdir(exist_ok=True)

PHISH_TEMPLATES = [
    "Dear {name},\n\nWe detected suspicious activity on your account. Please verify your information here: {link}\n\nRegards, {org}",
    "{name},\n\nYour account will be suspended unless you confirm your identity at {link}. Act immediately.",
    "Hello,\n\nThere was a problem with your recent payment. Click {link} to review and avoid service interruption.",
    "Urgent: Confirm your login by visiting {link} to avoid account lockout.",
    "Security alert for {name}: Unusual sign-in attempt. Verify at {link} or we will restrict access.",
]

LEGIT_TEMPLATES = [
    "Hi {name},\n\nJust checking in about the report due next week. Can you share a draft?\n\nThanks, {sender}",
    "Hello team,\n\nReminder: meeting at 10am tomorrow in Conference Room A. Agenda attached.",
    "Dear {name},\n\nThanks for your submission. We'll review and get back to you within 3-5 business days.\n\nBest, {sender}",
    "FYI: The weekly status update is attached. Let me know if you'd like any changes.",
    "Happy birthday, {name}! Hope you have a great day.\n\nCheers, {sender}",
]

TASK_TEMPLATES = [
    ("Can you send the {doc} by {deadline}?", "send {doc}", "{deadline}", "medium"),
    ("Please prepare the {doc} for the meeting on {deadline}.", "prepare {doc}", "{deadline}", "high"),
    ("Remember to review the {doc} and share feedback by {deadline}.", "review {doc}", "{deadline}", "medium"),
    ("Could you help me with {task}? I'd like it done {deadline}.", "help with {task}", "{deadline}", "low"),
]

MALICIOUS_DOMAINS = [
    "badbank-login.com", "secure-verify.net", "account-check.io", "payment-confirm.org",
    "update-info.co", "accountsecure.xyz", "verify-payments.us", "secure-login.biz",
]
BENIGN_DOMAINS = [
    "example.com", "company.com", "service.org", "example.org", "trusted.co", "mybank.com",
]

NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Chris", "Sam", "Pat", "Lee"]
ORGS = ["SecureBank", "PayService", "Acme Corp", "ClientServices"]
SENDERS = ["Alice", "Bob", "Carol", "Dev Team"]


def make_link(domain):
    return f"https://{domain}/login?uid={random.randint(1000,9999)}"


def generate_emails(phish_count=200, legit_count=200, ai_synth_fraction=0.25):
    rows = []
    # Phishing
    for i in range(phish_count):
        name = random.choice(NAMES)
        template = random.choice(PHISH_TEMPLATES)
        domain = random.choice(MALICIOUS_DOMAINS)
        link = make_link(domain)
        org = random.choice(ORGS)
        text = template.format(name=name, link=link, org=org)
        source = "phish_corpus"
        # mark some as AI-synth
        if random.random() < ai_synth_fraction:
            source = "ai_synth"
            # slightly vary phrasing
            text = text + "\n\nP.S. Please respond as soon as possible to avoid delay."
        rows.append({"id": f"phish_{i}", "text": text, "label": 1, "source": source})

    # Legitimate
    for i in range(legit_count):
        name = random.choice(NAMES)
        template = random.choice(LEGIT_TEMPLATES)
        sender = random.choice(SENDERS)
        text = template.format(name=name, sender=sender)
        rows.append({"id": f"legit_{i}", "text": text, "label": 0, "source": "enron_sample"})

    random.shuffle(rows)
    return rows


def generate_task_emails(n=100):
    rows = []
    for i in range(n):
        doc = random.choice(["report", "slides", "budget", "summary", "proposal"])        
        days = random.choice([1,2,3,5,7,14])
        deadline = (datetime.date.today() + datetime.timedelta(days=days)).isoformat()
        template, task_fmt, deadline_fmt, priority = random.choice(TASK_TEMPLATES)
        task_desc = task_fmt.format(doc=doc, task=doc)
        text = template.format(doc=doc, deadline=deadline, task=doc)
        rows.append({"id": f"task_{i}", "text": text, "task_description": task_desc, "deadline": deadline, "priority": priority})
    return rows


def generate_urls(malicious=100, benign=100):
    rows = []
    for i in range(malicious):
        domain = random.choice(MALICIOUS_DOMAINS)
        path = f"/confirm?token={random.randint(100000,999999)}"
        url = f"http://{domain}{path}"
        rows.append({"url": url, "label": 1, "source": "phishtank_synth"})
    for i in range(benign):
        domain = random.choice(BENIGN_DOMAINS)
        url = f"https://{domain}/about"
        rows.append({"url": url, "label": 0, "source": "top_sites"})
    random.shuffle(rows)
    return rows


def write_csv(path: Path, rows, fieldnames):
    with path.open('w', newline='', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    emails = generate_emails(phish_count=200, legit_count=200, ai_synth_fraction=0.25)
    tasks = generate_task_emails(n=100)
    urls = generate_urls(malicious=100, benign=100)

    write_csv(BASE_DIR / 'test_emails.csv', emails, ['id','text','label','source'])
    write_csv(BASE_DIR / 'test_task_emails.csv', tasks, ['id','text','task_description','deadline','priority'])
    write_csv(BASE_DIR / 'test_urls.csv', urls, ['url','label','source'])

    readme = BASE_DIR / 'README.md'
    readme.write_text(
        """Test data files generated for TRIDENT model evaluation.

Files:
- test_emails.csv: id,text,label (1=phishing,0=legit),source
- test_task_emails.csv: id,text,task_description,deadline,priority
- test_urls.csv: url,label (1=malicious,0=benign),source

How generated: Synthetic templates + small variations. Use these for quick local testing of detectors.
"""
    )
    print('Wrote data/test_emails.csv, data/test_task_emails.csv, data/test_urls.csv')

if __name__ == '__main__':
    main()
