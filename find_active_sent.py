import requests
import json
import os

HOST = 'https://mularcredit.co.ke:2083'
USER = 'mular'
TOKEN = 'M8GJSJK5MRU8EITT8OQ9J5SBU2423V38'
headers = {'Authorization': f'cpanel {USER}:{TOKEN}'}

def get_sent_sizes():
    print("Listing all POP accounts...")
    r = requests.get(f"{HOST}/execute/Email/list_pops", headers=headers, timeout=30)
    if r.status_code != 200:
        print("Error listing pops")
        return

    pops = r.json().get("data", [])
    print(f"Found {len(pops)} accounts. Checking folder sizes...")
    
    results = []
    for pop in pops:
        email = pop.get("email")
        user, domain = email.split("@")
        
        # Check .Sent folder
        sent_path = f"mail/{domain}/{user}/.Sent"
        r_sent = requests.get(f"{HOST}/execute/Fileman/list_files", headers=headers, params={
            "dir": sent_path,
            "showhidden": 1
        }, timeout=10)
        
        if r_sent.status_code == 200:
            data = r_sent.json()
            if data.get("status") == 1:
                # Calculate size of Sent folder? 
                # list_files doesn't give recursive size easily, but we can check if it has files.
                cur_path = f"{sent_path}/cur"
                r_cur = requests.get(f"{HOST}/execute/Fileman/list_files", headers=headers, params={
                    "dir": cur_path
                }, timeout=10)
                if r_cur.status_code == 200:
                    files = r_cur.json().get("data", [])
                    if files:
                        print(f"{email}: {len(files)} sent messages")
                        results.append((email, len(files)))
        
    print("\nSummary of accounts with sent mail:")
    for email, count in sorted(results, key=lambda x: x[1], reverse=True):
        print(f"  {email}: {count}")

if __name__ == "__main__":
    get_sent_sizes()
