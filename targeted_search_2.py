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
    sent_path = f"mail/mularcredit.co.ke/{email_user}/.Sent/cur"
    
    r = requests.get(f"{HOST}/execute/Fileman/list_files", headers=headers, params={
        "dir": sent_path,
        "showhidden": 1
    }, timeout=30)
    
    if r.status_code != 200 or r.json().get("status") != 1:
        return False

    files = r.json().get("data", [])
    files.sort(key=lambda x: x.get("mtime", 0), reverse=True)
    
    for idx, f_info in enumerate(files):
        filename = f_info.get("file")
        try:
            r_file = requests.get(f"{HOST}/execute/Fileman/get_file_content", headers=headers, params={
                "dir": sent_path,
                "file": filename
            }, timeout=20)
            
            if r_file.status_code == 200:
                content = r_file.json().get("data", {}).get("content", "")
                if TARGET_DOMAIN.lower() in content.lower():
                    print(f"\n[FOUND MATCH!] In {email_user} Sent")
                    print(f"File: {filename}")
                    print(f"Date: {time.ctime(f_info.get('mtime'))}")
                    for line in content.splitlines():
                        if any(h in line for h in ["Date:", "From:", "To:", "Subject:"]):
                            print(f"  {line}")
                    return True
            
            if (idx + 1) % 50 == 0:
                print(f"    ... {idx + 1}/{len(files)} checked")
        except Exception:
            pass
    return False

def main():
    users = ['kmutugi', 'konyancha', 'pbundi', 'performance', 'okiro']
    for user in users:
        if search_account(user):
            return

if __name__ == "__main__":
    main()
