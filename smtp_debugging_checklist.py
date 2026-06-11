"""Comprehensive SMTP debugging checklist for Docker + Airflow."""

import os
import sys
import re

print("=" * 80)
print("SMTP DEBUGGING CHECKLIST - COMPREHENSIVE ANALYSIS")
print("=" * 80)

# ===== CHECK 1: .env file =====
print("\n" + "=" * 80)
print("CHECK 1: .env FILE VALIDATION")
print("=" * 80)

env_file = "/Users/apple/Main/project/DataPipeline/ETL/.env"
if not os.path.exists(env_file):
    print(f"❌ .env file NOT FOUND at {env_file}")
    sys.exit(1)

print(f"✅ .env file exists at {env_file}")

# Parse .env
env_vars = {}
with open(env_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()

# Check SMTP variables
smtp_checks = {
    "AIRFLOW__SMTP__SMTP_HOST": ("smtp.gmail.com", "Gmail SMTP host"),
    "AIRFLOW__SMTP__SMTP_PORT": ("587", "Port for STARTTLS"),
    "AIRFLOW__SMTP__SMTP_STARTTLS": ("True", "Enable STARTTLS"),
    "AIRFLOW__SMTP__SMTP_SSL": ("False", "Disable SSL when using STARTTLS"),
    "AIRFLOW__SMTP__SMTP_USER": (None, "Gmail email address"),
    "AIRFLOW__SMTP__SMTP_PASSWORD": (None, "App Password"),
    "AIRFLOW__SMTP__SMTP_MAIL_FROM": (None, "Sender email (should match USER)"),
}

print("\n📋 SMTP Variables in .env:")
print("-" * 80)

all_smtp_ok = True
for var_name, (expected, description) in smtp_checks.items():
    if var_name not in env_vars:
        print(f"❌ {var_name:45} MISSING")
        all_smtp_ok = False
        continue
    
    value = env_vars[var_name]
    if not value:
        print(f"❌ {var_name:45} EMPTY")
        all_smtp_ok = False
        continue
    
    if expected and value != expected:
        print(f"⚠️  {var_name:45} = {value}")
        print(f"    Expected: {expected}")
        all_smtp_ok = False
    else:
        if 'PASSWORD' in var_name:
            display = '*' * len(value)
        else:
            display = value
        print(f"✅ {var_name:45} = {display}")

# ===== CHECK 2: Password format validation =====
print("\n" + "=" * 80)
print("CHECK 2: PASSWORD FORMAT ANALYSIS")
print("=" * 80)

smtp_password = env_vars.get("AIRFLOW__SMTP__SMTP_PASSWORD", "")
print(f"\nPassword analysis:")
print(f"  Length: {len(smtp_password)} characters")
print(f"  Contains spaces: {' ' in smtp_password}")
has_special = any(c in smtp_password for c in '@#$%^&*()[]{}')
print(f"  Contains special chars: {has_special}")
is_quoted = (smtp_password.startswith('"') or smtp_password.startswith("'"))
print(f"  Quoted: {is_quoted}")

if ' ' in smtp_password:
    print(f"\n⚠️  WARNING: Password contains SPACES")
    print(f"  Raw value: '{smtp_password}'")
    print(f"  This might cause parsing issues in Docker!")
    print(f"\n  💡 SOLUTION: Quote the password in .env:")
    print(f'  AIRFLOW__SMTP__SMTP_PASSWORD="gcah vmih oskb jolp"')
    all_smtp_ok = False
else:
    print(f"✅ Password format looks OK")

# ===== CHECK 3: Docker Compose configuration =====
print("\n" + "=" * 80)
print("CHECK 3: DOCKER-COMPOSE SMTP ENV INJECTION")
print("=" * 80)

docker_compose_file = "/Users/apple/Main/project/DataPipeline/ETL/docker-compose.yml"
with open(docker_compose_file, 'r') as f:
    compose_content = f.read()

print("\nLooking for SMTP environment variable definitions in docker-compose.yml...")
smtp_in_compose = []
for line in compose_content.split('\n'):
    if 'AIRFLOW__SMTP__' in line:
        smtp_in_compose.append(line.strip())

if not smtp_in_compose:
    print("❌ NO SMTP variables found in docker-compose.yml!")
    all_smtp_ok = False
else:
    print(f"✅ Found {len(smtp_in_compose)} SMTP variable definitions:")
    for var_line in smtp_in_compose[:5]:
        if len(var_line) > 75:
            print(f"  {var_line[:75]}...")
        else:
            print(f"  {var_line}")

# Check if compose references .env file
print("\nChecking .env file usage in docker-compose.yml:")
if '${' in compose_content and 'SMTP' in compose_content:
    print("✅ docker-compose.yml uses variable substitution (${...})")
    print("✅ Should load from .env file in same directory")
else:
    print("❌ Cannot confirm variable substitution for SMTP")
    all_smtp_ok = False

# ===== CHECK 4: Airflow configuration =====
print("\n" + "=" * 80)
print("CHECK 4: AIRFLOW CONFIGURATION FILES")
print("=" * 80)

config_paths = [
    "/Users/apple/Main/project/DataPipeline/ETL/config",
    "/Users/apple/Main/project/DataPipeline/ETL/dags/config",
]

airflow_cfg_found = False
for config_path in config_paths:
    if os.path.exists(config_path):
        print(f"\n📁 Checking {config_path}:")
        for filename in os.listdir(config_path):
            filepath = os.path.join(config_path, filename)
            if os.path.isfile(filepath):
                print(f"  - {filename}")
                # Check for SMTP config in python files
                if filename.endswith('.py'):
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if 'smtp' in content.lower():
                            print(f"    ⚠️  Contains SMTP configuration - check for hardcoded values!")

# ===== CHECK 5: Service configuration =====
print("\n" + "=" * 80)
print("CHECK 5: AIRFLOW SERVICES SMTP ENV")
print("=" * 80)

services_to_check = ['airflow-scheduler', 'airflow-apiserver', 'airflow-init']

print("\nServices in docker-compose.yml that need SMTP env:")
for service_name in services_to_check:
    if service_name in compose_content:
        print(f"  ✅ {service_name} defined")
    else:
        print(f"  ❌ {service_name} NOT found")

# Check x-airflow-common
if '&airflow-common' in compose_content and '*airflow-common' in compose_content:
    print("✅ Using x-airflow-common YAML anchor")
    print("  (SMTP env should be inherited by all services)")
else:
    print("⚠️  Not using YAML anchors - services might not share SMTP env")
    all_smtp_ok = False

# ===== CHECK 6: Known issues =====
print("\n" + "=" * 80)
print("CHECK 6: COMMON ISSUES DETECTION")
print("=" * 80)

issues_found = []

# Issue 1: Port/TLS mismatch
port = env_vars.get("AIRFLOW__SMTP__SMTP_PORT", "")
starttls = env_vars.get("AIRFLOW__SMTP__SMTP_STARTTLS", "").lower()
ssl = env_vars.get("AIRFLOW__SMTP__SMTP_SSL", "").lower()

print("\n1. Port/TLS Configuration Match:")
if port == "587" and starttls == "true" and ssl == "false":
    print("   ✅ Correct: Port 587 + STARTTLS=True + SSL=False")
elif port == "465" and starttls == "false" and ssl == "true":
    print("   ✅ Correct: Port 465 + STARTTLS=False + SSL=True")
else:
    print(f"   ❌ MISMATCH: Port={port}, STARTTLS={starttls}, SSL={ssl}")
    issues_found.append("Port/TLS configuration mismatch")

# Issue 2: User/From mismatch
user = env_vars.get("AIRFLOW__SMTP__SMTP_USER", "")
mail_from = env_vars.get("AIRFLOW__SMTP__SMTP_MAIL_FROM", "")

print("\n2. SMTP_USER vs SMTP_MAIL_FROM:")
if user == mail_from:
    print(f"   ✅ Match: Both are {user}")
else:
    print(f"   ⚠️  MISMATCH: USER={user}, FROM={mail_from}")
    print("   (Usually should be the same for Gmail)")

# Issue 3: Empty password
if not smtp_password:
    print("\n3. Password Status:")
    print("   ❌ PASSWORD IS EMPTY!")
    issues_found.append("Empty SMTP password")
else:
    print("\n3. Password Status:")
    print(f"   ✅ Password configured (length: {len(smtp_password)})")

# ===== FINAL SUMMARY =====
print("\n" + "=" * 80)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 80)

if all_smtp_ok and not issues_found:
    print("\n✅ ALL CHECKS PASSED - Configuration looks correct!")
    print("\nIf SMTP is still failing:")
    print("  1. Restart Docker containers: docker-compose restart")
    print("  2. Check container logs: docker-compose logs airflow-scheduler")
    print("  3. Verify password inside container: docker-compose exec airflow-scheduler")
    print("     env | grep SMTP")
else:
    print("\n⚠️  ISSUES FOUND:\n")
    if issues_found:
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)

print("""
1. ✅ Verify .env is in project root:
   $ ls -la .env

2. ✅ Check password is quoted in .env (if has spaces):
   AIRFLOW__SMTP__SMTP_PASSWORD="gcah vmih oskb jolp"

3. ✅ Restart Docker with fresh containers:
   $ docker-compose down
   $ docker-compose up -d

4. ✅ Verify SMTP env inside container:
   $ docker-compose exec airflow-scheduler env | grep SMTP

5. ✅ Check Airflow scheduler logs:
   $ docker-compose logs airflow-scheduler | grep -i smtp

6. ✅ Run test email send:
   $ docker-compose exec airflow-scheduler bash
   $ python -c "from airflow.utils.email import send_email; \\
     send_email(to='test@gmail.com', subject='Test', \\
     html_content='<p>Test</p>')"
""")

print("=" * 80)
