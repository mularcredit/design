import requests
import json
import os
import time

HOST = 'https://mularcredit.co.ke:2083'
USER = 'mular'
TOKEN = 'M8GJSJK5MRU8EITT8OQ9J5SBU2423V38'
headers = {'Authorization': f'cpanel {USER}:{TOKEN}'}

TARGET_EMAIL = 'fin@centralbank.go.ke'
TARGET_DOMAIN = 'centralbank.go.ke'

def search_account(email_user):
    print(f"Scanning {email_user}@mularcredit.co.ke ...")
    sent_path = f"mail/mularcredit.co.ke/{email_user}/.Sent/cur"
    
    # List files in Sent folder
    r = requests.get(f"{HOST}/execute/Fileman/list_files", headers=headers, params={
        "dir": sent_path,
        "showhidden": 1
    }, timeout=30)
    
    if r.status_code != 200:
        print(f"  Error accessing {sent_path}: {r.status_code}")
        return False

    data = r.json()
    if data.get("status") != 1:
        # print(f"  No Sent folder found for {email_user}")
        return False

    files = data.get("data", [])
    if not files:
        # print(f"  Sent folder is empty for {email_user}")
        return False

    # Sort by mtime (most recent first)
    files.sort(key=lambda x: x.get("mtime", 0), reverse=True)
    
    # Check top 50 most recent files
    to_check = files[:100]
    print(f"  Checking {len(to_check)} most recent sent emails...")
    
    for f_info in to_check:
        filename = f_info.get("file")
        try:
            r_file = requests.get(f"{HOST}/execute/Fileman/get_file_content", headers=headers, params={
                "dir": sent_path,
                "file": filename
            }, timeout=20)
            
            if r_file.status_code == 200:
                resp_json = r_file.json()
                if resp_json and isinstance(resp_json, dict):
                    data_dict = resp_json.get("data") or {}
                    content = data_dict.get("content", "")
                    if TARGET_DOMAIN.lower() in content.lower():
                        print(f"\n[POSSIBLE MATCH] Found '{TARGET_DOMAIN}' in {email_user}@mularcredit.co.ke")
                        print(f"File: {filename}")
                        print(f"Date: {time.ctime(f_info.get('mtime'))}")
                        # Extract some headers
                        headers_found = {}
                        for line in content.splitlines():
                            for h in ["Date:", "From:", "To:", "Subject:"]:
                                if line.startswith(h):
                                    headers_found[h] = line
                        for h in ["Date:", "From:", "To:", "Subject:"]:
                            if h in headers_found:
                                print(f"  {headers_found[h]}")
                        
                        if TARGET_EMAIL.lower() in content.lower():
                            print(f"  *** EXACT MATCH: {TARGET_EMAIL} ***")
                            return True
                
                # Print progress every 10 files
                if to_check.index(f_info) % 10 == 0:
                    print(f"    ... checked {to_check.index(f_info)}/100 files")
                else:
                    print(f"  Warning: Unexpected JSON format for {filename}: {resp_json}")
            else:
                print(f"  Error reading {filename}: HTTP {r_file.status_code}")
        except Exception as e:
            print(f"  Error processing {filename}: {e}")
            
    return False

def main():
    top_users = ['amasinde', 'aombasa', 'operations', 'info', 'finance', 'hr', 'dkituva', 'masua', 'branch.pettycash', 'mchebii', 'jlui', 'mosembe']
    for user in top_users:
        if search_account(user):
            print("\nScan completed with a match.")
            # We found it, but let's see if others sent too? 
            # Usually one account does this.
            # return 
        print("-" * 30)

if __name__ == "__main__":
    main()
