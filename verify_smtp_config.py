"""Verify SMTP environment variables configuration for Docker/Airflow."""

import os
import sys

print("=" * 70)
print("SMTP ENVIRONMENT VARIABLES VERIFICATION REPORT")
print("=" * 70)

# Read docker.env
docker_env_path = "/Users/apple/Main/project/DataPipeline/ETL/src/building_block/env/docker.env"
env_vars = {}

with open(docker_env_path, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()

# Extract SMTP settings
smtp_vars = {k: v for k, v in env_vars.items() if 'SMTP' in k}

print("\n📋 CURRENT SMTP CONFIGURATION IN docker.env:")
print("-" * 70)
for key in sorted(smtp_vars.keys()):
    value = smtp_vars[key]
    if 'PASSWORD' in key:
        display_value = '*' * len(value)
    else:
        display_value = value
    print(f"  {key:40} = {display_value}")

print("\n" + "=" * 70)
print("✅ VERIFICATION AGAINST AIRFLOW STANDARDS")
print("=" * 70)

checks = []

# Check 1: SMTP_HOST
host = smtp_vars.get("AIRFLOW__SMTP__SMTP_HOST", "")
check1 = host == "smtp.gmail.com"
status1 = "✅" if check1 else "❌"
print(f"\n{status1} SMTP_HOST")
print(f"   Current: {host}")
print(f"   Expected: smtp.gmail.com")
print(f"   Status: {'Correct' if check1 else 'INCORRECT'}")
checks.append(check1)

# Check 2: SMTP_PORT
port = smtp_vars.get("AIRFLOW__SMTP__SMTP_PORT", "")
check2 = port == "587"
status2 = "✅" if check2 else "❌"
print(f"\n{status2} SMTP_PORT (STARTTLS)")
print(f"   Current: {port}")
print(f"   Expected: 587 (for STARTTLS) or 465 (for SSL)")
print(f"   Status: {'Correct' if check2 else 'INCORRECT'}")
checks.append(check2)

# Check 3: SMTP_STARTTLS
starttls = smtp_vars.get("AIRFLOW__SMTP__SMTP_STARTTLS", "")
check3 = starttls.lower() in ["true", "yes", "1"]
status3 = "✅" if check3 else "❌"
print(f"\n{status3} SMTP_STARTTLS")
print(f"   Current: {starttls}")
print(f"   Expected: True (for port 587)")
print(f"   Status: {'Correct' if check3 else 'INCORRECT'}")
checks.append(check3)

# Check 4: SMTP_SSL
ssl = smtp_vars.get("AIRFLOW__SMTP__SMTP_SSL", "")
check4 = ssl.lower() in ["false", "no", "0"]
status4 = "✅" if check4 else "❌"
print(f"\n{status4} SMTP_SSL")
print(f"   Current: {ssl}")
print(f"   Expected: False (should be False when using STARTTLS on port 587)")
print(f"   Status: {'Correct' if check4 else 'INCORRECT'}")
checks.append(check4)

# Check 5: SMTP_USER
user = smtp_vars.get("AIRFLOW__SMTP__SMTP_USER", "")
check5 = "@gmail.com" in user
status5 = "✅" if check5 else "❌"
print(f"\n{status5} SMTP_USER")
print(f"   Current: {user}")
print(f"   Expected: Valid Gmail address with @gmail.com")
print(f"   Status: {'Correct' if check5 else 'INCORRECT'}")
checks.append(check5)

# Check 6: SMTP_MAIL_FROM
mail_from = smtp_vars.get("AIRFLOW__SMTP__SMTP_MAIL_FROM", "")
check6 = mail_from == user
status6 = "✅" if check6 else "⚠️"
print(f"\n{status6} SMTP_MAIL_FROM")
print(f"   Current: {mail_from}")
print(f"   Expected: Should match SMTP_USER ({user})")
print(f"   Status: {'Correct' if check6 else 'Should match SMTP_USER'}")
checks.append(check6)

# Check 7: SMTP_PASSWORD exists
password = smtp_vars.get("AIRFLOW__SMTP__SMTP_PASSWORD", "")
check7 = len(password) > 0
status7 = "✅" if check7 else "❌"
print(f"\n{status7} SMTP_PASSWORD")
print(f"   Current: {'Set (length: ' + str(len(password)) + ')' if password else 'NOT SET'}")
print(f"   Expected: Must not be empty")
print(f"   Status: {'Correct' if check7 else 'MISSING'}")
checks.append(check7)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
passed = sum(checks)
total = len(checks)
print(f"\nPassed: {passed}/{total} checks")

if passed == total:
    print("\n✅ All SMTP environment variables are correctly configured!")
    print("\n💡 Next step: Restart Docker containers to apply changes")
    print("   $ docker-compose down && docker-compose up -d")
else:
    print(f"\n⚠️  {total - passed} issue(s) found. Please review above.")

print("\n" + "=" * 70)
print("DOCKER-COMPOSE ENV FILE CONFIGURATION")
print("=" * 70)

compose_file = "/Users/apple/Main/project/DataPipeline/ETL/docker-compose.yml"
with open(compose_file, 'r') as f:
    content = f.read()
    
if 'env_file:' in content:
    print("\n✅ docker-compose.yml uses 'env_file' directive")
    # Extract env_file references
    for line in content.split('\n'):
        if 'env_file:' in line:
            print(f"   Found: {line.strip()}")
else:
    print("\n⚠️  docker-compose.yml does NOT use 'env_file' directive")
    print("\n   How environment variables are loaded:")
    if '${' in content:
        print("   • Using variable substitution: ${VAR_NAME:-default_value}")
        print("   • This requires a .env file in the docker-compose directory")
        env_file_path = "/Users/apple/Main/project/DataPipeline/ETL/.env"
        if os.path.exists(env_file_path):
            print(f"\n   ✅ .env file exists at {env_file_path}")
        else:
            print(f"\n   ⚠️  .env file MISSING at {env_file_path}")
            print("   \n   💡 SOLUTION: Copy docker.env to .env in project root")
            print("   $ cp src/building_block/env/docker.env .env")

print("\n" + "=" * 70)
