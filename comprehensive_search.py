import requests
import json
import os
import time

HOST = 'https://mularcredit.co.ke:2083'
USER = 'mular'
TOKEN = 'M8GJSJK5MRU8EITT8OQ9J5SBU2423V38'
headers = {'Authorization': f'cpanel {USER}:{TOKEN}'}

TARGET_DOMAIN = 'centralbank.go.ke'

def search_account(email_user):
    print(f"\nScanning {email_user}@mularcredit.co.ke ...")
    
    # Check both Inbox and Sent
    folders = ["cur", ".Sent/cur"]
    
    for folder in folders:
        path = f"mail/mularcredit.co.ke/{email_user}/{folder}"
        print(f"  Folder: {folder}")
        
        r = requests.get(f"{HOST}/execute/Fileman/list_files", headers=headers, params={
            "dir": path,
            "showhidden": 1
        }, timeout=30)
        
        if r.status_code != 200 or r.json().get("status") != 1:
            print(f"    ... skipped (not found)")
            continue

        files = r.json().get("data", [])
        if not files:
            continue

        # Sort by mtime (most recent first)
        files.sort(key=lambda x: x.get("mtime", 0), reverse=True)
        
        # Check top 200 files in each folder
        to_check = files[:200]
        for f_info in to_check:
            filename = f_info.get("file")
            try:
                r_file = requests.get(f"{HOST}/execute/Fileman/get_file_content", headers=headers, params={
                    "dir": path,
                    "file": filename
                }, timeout=20)
                
                if r_file.status_code == 200:
                    resp_json = r_file.json() or {}
                    data_dict = resp_json.get("data") or {}
                    content = data_dict.get("content", "")
                    
                    if TARGET_DOMAIN.lower() in content.lower():
                        print(f"\n[MATCH!] Found '{TARGET_DOMAIN}' in {email_user} -> {folder}")
                        print(f"File: {filename}")
                        print(f"Date: {time.ctime(f_info.get('mtime'))}")
                        
                        headers_found = {}
                        for line in content.splitlines():
                            for h in ["Date:", "From:", "To:", "Subject:"]:
                                if line.startswith(h):
                                    headers_found[h] = line
                        for h in ["Date:", "From:", "To:", "Subject:"]:
                            if h in headers_found:
                                print(f"  {headers_found[h]}")
                        return True
                
                # Progress every 50
                if to_check.index(f_info) % 50 == 0 and to_check.index(f_info) > 0:
                    print(f"    ... checked {to_check.index(f_info)} files")
                    
            except Exception:
                pass
    return False

def main():
    # Priority list based on role and high sent counts
    users = ['finance', 'operations', 'hr', 'amasinde', 'aombasa', 'benard.otieno', 'info', 'dkituva', 'masua', 'mosembe']
    for user in users:
        if search_account(user):
            print("\nMatch found. Stopping.")
            return

if __name__ == "__main__":
    main()
