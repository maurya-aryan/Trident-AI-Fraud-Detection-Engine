"""
Send 10 demo emails to trigger live alerts via IMAP poller
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time

# Email configuration
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "test@example.com")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))

# Demo email scenarios
DEMO_EMAILS = [
    {
        "subject": "🚨 URGENT: Account Security Alert - Verify Now!",
        "body": """Dear User,

We have detected suspicious activity on your account. Your password needs immediate verification.

Username: user@domain.com
Password: SecurePass123!

Click here to verify: http://phishing-site.xyz/verify

Failure to verify within 24 hours will result in account suspension.

Best regards,
Security Team""",
        "from_name": "Security Alert"
    },
    {
        "subject": "PayPal: Unusual Activity Detected",
        "body": """Hello,

We noticed unusual login attempts from an unknown device.

Please confirm your identity by clicking the link below:
http://paypa1-secure.tk/login?verify=true

Account credentials may be compromised. Update immediately.

PayPal Security Team""",
        "from_name": "PayPal Security"
    },
    {
        "subject": "You've Won $5,000,000 - Claim Your Prize!",
        "body": """🎉 CONGRATULATIONS! 🎉

You have been selected as the winner of our international lottery!

Prize Amount: $5,000,000 USD

To claim your prize, please provide:
- Full Name
- Credit Card Number: 4532-1234-5678-9012
- CVV: 123
- Bank Account Details

Contact us immediately at winner@lottery-scam.com

Hurry! Offer expires in 48 hours!""",
        "from_name": "Lottery Commission"
    },
    {
        "subject": "Team Meeting - Q1 Planning Session",
        "body": """Hi Team,

Reminder: We have our Q1 planning session tomorrow at 10 AM in Conference Room B.

Agenda:
- Budget review
- Project timeline updates
- New hiring plans

Please bring your quarterly reports.

Best regards,
Sarah Johnson
Project Manager""",
        "from_name": "Sarah Johnson"
    },
    {
        "subject": "UPS Delivery Failed - Update Address",
        "body": """Dear Customer,

Your package delivery failed due to incorrect address information.

Tracking Number: UPS-1234567890

Update your address here: http://ups-delivery-update.click/track

Package will be returned to sender if not updated within 72 hours.

UPS Customer Service""",
        "from_name": "UPS Delivery"
    },
    {
        "subject": "Netflix: Update Payment Method",
        "body": """Your Netflix subscription payment failed.

To continue watching, please update your payment information:
http://netflix-billing.pw/update-payment

Account Details:
Email: user@domain.com
Card: **** **** **** 1234

Your account will be suspended in 3 days if payment is not received.

Netflix Billing Team""",
        "from_name": "Netflix Billing"
    },
    {
        "subject": "API Key Renewal Required",
        "body": """Hello Developer,

Your API key is expiring soon. Please renew to maintain service access.

Current API Key: sk-live-ABC123DEF456GHI789JKL012
Secret Token: secret_abc123xyz789

Renew here: http://api-renewal.xyz/renew

Failure to renew will result in service interruption.

API Support Team""",
        "from_name": "API Support"
    },
    {
        "subject": "Re: Budget Proposal Review",
        "body": """Hi Michael,

I've reviewed the budget proposal you sent. Everything looks good!

A few minor suggestions:
- Consider allocating more to marketing in Q2
- IT infrastructure costs seem reasonable
- HR budget might need slight adjustment

Let's discuss in tomorrow's meeting.

Best regards,
Emily Davis
Finance Director""",
        "from_name": "Emily Davis"
    },
    {
        "subject": "Microsoft Account Security Check Required",
        "body": """Microsoft Account Alert

Unusual sign-in activity detected from unknown location.

Location: Russia
IP Address: 192.168.1.100
Device: Unknown Windows PC

If this wasn't you, secure your account immediately:
http://microsoft-security.xyz/verify

Your current password: TempPass2024!

Microsoft Security Team""",
        "from_name": "Microsoft Security"
    },
    {
        "subject": "Your Amazon Order #123456 Has Shipped",
        "body": """Hello,

Your Amazon order has been shipped!

Order Number: 123-4567890-1234567
Tracking: http://amaz0n-tracking.link/order/123456

Expected Delivery: March 5, 2026

Items:
- Wireless Headphones (1x)

Track your package using the link above.

Amazon Shipping""",
        "from_name": "Amazon Shipping"
    }
]

def send_email(subject, body, from_name, delay=2):
    """Send a single email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{SENDER_EMAIL}>"
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect and send
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✓ Sent: {subject[:60]}...")
        time.sleep(delay)  # Delay to avoid rate limiting
        return True
    except Exception as e:
        print(f"✗ Failed to send: {subject[:40]}... Error: {e}")
        return False

def main():
    if not RECIPIENT_EMAIL:
        print("❌ Error: RECIPIENT_EMAIL not set")
        print("\nUsage:")
        print('  $env:SENDER_EMAIL="your-sender@gmail.com"')
        print('  $env:SENDER_PASSWORD="your-app-password"')
        print('  $env:RECIPIENT_EMAIL="recipient@gmail.com"')
        print('  python scripts\\send_demo_emails.py')
        return
    
    if not SENDER_PASSWORD:
        print("❌ Error: SENDER_PASSWORD not set (use Gmail App Password)")
        return
    
    print("=" * 80)
    print("SENDING 10 DEMO EMAILS FOR LIVE ALERT TESTING")
    print("=" * 80)
    print(f"From: {SENDER_EMAIL}")
    print(f"To: {RECIPIENT_EMAIL}")
    print(f"SMTP: {SMTP_SERVER}:{SMTP_PORT}")
    print("=" * 80)
    print()
    
    success_count = 0
    for i, email_data in enumerate(DEMO_EMAILS, 1):
        print(f"[{i}/10] ", end="")
        if send_email(
            email_data["subject"],
            email_data["body"],
            email_data["from_name"]
        ):
            success_count += 1
    
    print()
    print("=" * 80)
    print(f"✓ Successfully sent {success_count}/10 demo emails")
    print("=" * 80)
    print()
    print("📧 Emails sent! The IMAP poller will detect them and create live alerts.")
    print("   Check your dashboard's 'Alerts Dashboard' tab in a few moments.")
    print()

if __name__ == "__main__":
    main()
