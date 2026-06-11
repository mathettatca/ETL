"""Test SMTP connection to Gmail with Airflow credentials."""

import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Read environment variables from docker.env file
def load_env_file(filepath):
    env_vars = {}
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error reading env file: {e}")
    return env_vars

env_vars = load_env_file("/Users/apple/Main/project/DataPipeline/ETL/src/building_block/env/docker.env")

# Extract SMTP configuration
SMTP_HOST = env_vars.get("AIRFLOW__SMTP__SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(env_vars.get("AIRFLOW__SMTP__SMTP_PORT", 587))
SMTP_USER = env_vars.get("AIRFLOW__SMTP__SMTP_USER", "")
SMTP_PASSWORD = env_vars.get("AIRFLOW__SMTP__SMTP_PASSWORD", "")
SMTP_FROM = env_vars.get("AIRFLOW__SMTP__SMTP_MAIL_FROM", "")
SMTP_STARTTLS = env_vars.get("AIRFLOW__SMTP__SMTP_STARTTLS", "True").lower() == "true"
SMTP_SSL = env_vars.get("AIRFLOW__SMTP__SMTP_SSL", "False").lower() == "true"

print("=" * 60)
print("GMAIL SMTP CONNECTION TEST")
print("=" * 60)
print(f"\n📋 Configuration:")
print(f"   Host: {SMTP_HOST}")
print(f"   Port: {SMTP_PORT}")
print(f"   User: {SMTP_USER}")
print(f"   Password: {'*' * len(SMTP_PASSWORD)}")
print(f"   From: {SMTP_FROM}")
print(f"   STARTTLS: {SMTP_STARTTLS}")
print(f"   SSL: {SMTP_SSL}")

if not SMTP_USER or not SMTP_PASSWORD:
    print("\n❌ ERROR: SMTP_USER or SMTP_PASSWORD not configured!")
    sys.exit(1)

# Test 1: Connection
print("\n" + "=" * 60)
print("TEST 1: Connection to SMTP Server")
print("=" * 60)
try:
    if SMTP_SSL:
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
    else:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
    print("✅ Connected to SMTP server successfully")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    sys.exit(1)

# Test 2: STARTTLS (if enabled)
if SMTP_STARTTLS and not SMTP_SSL:
    print("\n" + "=" * 60)
    print("TEST 2: STARTTLS Upgrade")
    print("=" * 60)
    try:
        server.starttls()
        print("✅ STARTTLS upgrade successful")
    except Exception as e:
        print(f"❌ STARTTLS failed: {e}")
        server.quit()
        sys.exit(1)

# Test 3: Authentication
print("\n" + "=" * 60)
print("TEST 3: SMTP Authentication")
print("=" * 60)
try:
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("✅ Authentication successful!")
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ Authentication failed: {e}")
    print("\n   🔧 Troubleshooting:")
    print("   • Check if 2FA is enabled on Gmail account")
    print("   • Verify App Password is correct: https://myaccount.google.com/apppasswords")
    print("   • Ensure password has no spaces or is properly quoted")
    server.quit()
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    server.quit()
    sys.exit(1)

# Test 4: Send test email
print("\n" + "=" * 60)
print("TEST 4: Send Test Email")
print("=" * 60)
try:
    subject = "[Test] Airflow SMTP Configuration Verification"
    body = "This is a test email from Airflow SMTP configuration test.\n\nIf you received this, SMTP is working correctly!"
    
    msg = MIMEMultipart()
    msg["From"] = SMTP_FROM
    msg["To"] = SMTP_USER  # Send to self
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    server.sendmail(SMTP_FROM, [SMTP_USER], msg.as_string())
    print(f"✅ Test email sent successfully to {SMTP_USER}")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
    server.quit()
    sys.exit(1)

# Cleanup
server.quit()

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\n📧 SMTP configuration is working correctly.")
print(f"   Check your inbox at {SMTP_USER} for the test email.")
