import urllib.request
import urllib.parse
import json
import os
import csv
import ssl

# --- CONFIGURATION ---
CPANEL_HOST = 'https://malicash.co.ke:2083'
CPANEL_USER = 'hjjyhurl'
API_TOKEN = 'A6W4U4ACL237YY8KUTRJXOZTPCJCEEUH'
DOMAIN = 'malicash.co.ke'

# Disable SSL verification if needed (sometimes cPanel has self-signed certs)
ssl_context = ssl._create_unverified_context()

def test_connection():
    url = f"{CPANEL_HOST.rstrip('/')}/execute/Email/list_pops"
    headers = {
        "Authorization": f"cpanel {CPANEL_USER}:{API_TOKEN}"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get('status') == 1:
                print("Connection successful!")
                return True
            else:
                print(f"Connection failed: {data.get('errors')}")
                return False
    except Exception as e:
        print(f"Error connecting to cPanel: {e}")
        return False

def create_email_account(email_user, password):
    params = {
        "email": email_user,
        "password": password,
        "domain": DOMAIN,
        "quota": 1024 # 1GB quota
    }
    query_string = urllib.parse.urlencode(params)
    url = f"{CPANEL_HOST.rstrip('/')}/execute/Email/add_pop?{query_string}"
    headers = {
        "Authorization": f"cpanel {CPANEL_USER}:{API_TOKEN}"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get('status') == 1:
                return True, None
            else:
                return False, data.get('errors')
    except Exception as e:
        return False, str(e)

def process_csv(file_path):
    results = []
    with open(file_path, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            full_name = row['Name'].strip()
            name_parts = full_name.split()
            
            if len(name_parts) >= 2:
                firstname = name_parts[0]
                lastname = name_parts[-1]
            else:
                firstname = full_name
                lastname = ""
            
            # Format Email: firstname.lastname@malicash.co.ke
            if lastname:
                email_user = f"{firstname.lower()}.{lastname.lower()}"
            else:
                email_user = firstname.lower()
            
            # Format Password: Firstname@2026 (first letter uppercase)
            password = f"{firstname.capitalize()}@2026"
            
            print(f"Creating account for {full_name}: {email_user}@{DOMAIN} with password {password}...")
            
            success, error = create_email_account(email_user, password)
            if success:
                print(f"  [SUCCESS]")
                results.append({"Name": full_name, "Email": f"{email_user}@{DOMAIN}", "Password": password, "Status": "Success"})
            else:
                print(f"  [FAILED] {error}")
                results.append({"Name": full_name, "Email": f"{email_user}@{DOMAIN}", "Password": password, "Status": f"Failed: {error}"})
    
    # Save results to a new CSV
    with open('creation_results.csv', mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "Email", "Password", "Status"])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    if test_connection():
        process_csv('new_accounts_2.csv')
    else:
        print("Aborting due to connection failure.")
