import requests
import os
import re
import json

# --- CONFIGURATION ---
CPANEL_HOST = os.environ.get('CPANEL_HOST', 'https://mularcredit.co.ke:2083')
CPANEL_USER = os.environ.get('CPANEL_USER', 'mular')
API_TOKEN = 'M8GJSJK5MRU8EITT8OQ9J5SBU2423V38'

TARGET_EMAIL = 'fin@centralbank.go.ke'

def fetch_mail_logs():
    headers = {
        "Authorization": f"cpanel {CPANEL_USER}:{API_TOKEN}"
    }

    print(f"Searching for emails sent TO: {TARGET_EMAIL}\n")
    print("=" * 60)

    found_senders = set()

    # -------------------------------------------------------
    # Method 1: Email::DeliveryReporter / track delivery log
    # This is the correct cPanel API for sent mail history
    # -------------------------------------------------------
    print("Method 1: Checking cPanel Email Delivery Track log...")
    endpoints_to_try = [
        ("Email/get_sent_stats",        {"account": "allstaff"}),
        ("Email/list_mail_domains",     {}),
        ("Email/get_identityverification", {}),
    ]

    # The real endpoint for delivery logs
    delivery_url = f"{CPANEL_HOST.rstrip('/')}/execute/Email/list_pops_with_disk"
    r = requests.get(delivery_url, headers=headers, timeout=20)
    print(f"  list_pops_with_disk status: {r.status_code}")

    # -------------------------------------------------------
    # Method 2: WHM API (if token works at WHM level :2087)
    # -------------------------------------------------------
    print("\nMethod 2: Trying WHM API for mail log search...")
    whm_host = CPANEL_HOST.replace(':2083', ':2087')
    whm_headers = {
        "Authorization": f"whm {CPANEL_USER}:{API_TOKEN}"
    }

    # WHM: search exim mail log
    whm_url = f"{whm_host.rstrip('/')}/json-api/emailtrack_search"
    params = {
        "api.version": 1,
        "query": TARGET_EMAIL,
        "searchtype": "to",
    }
    try:
        r2 = requests.get(whm_url, headers=whm_headers, params=params, timeout=30)
        print(f"  WHM emailtrack_search status: {r2.status_code}")
        if r2.status_code == 200:
            data2 = r2.json()
            print(f"  Response: {json.dumps(data2, indent=2)[:2000]}")
            records = data2.get("data", {}).get("records", [])
            for rec in records:
                sender = rec.get("sender", "")
                recipient = rec.get("recipient", "")
                ts = rec.get("datetime", "")
                status = rec.get("deliverystatus", "")
                print(f"  [{ts}] {sender} -> {recipient} | {status}")
                if "@mularcredit.co.ke" in sender.lower():
                    found_senders.add(sender.lower())
        else:
            print(f"  Response: {r2.text[:500]}")
    except Exception as e:
        print(f"  Error: {e}")

    # -------------------------------------------------------
    # Method 3: cPanel Track Delivery (correct endpoint)
    # -------------------------------------------------------
    print("\nMethod 3: cPanel Track Delivery API...")
    track_url = f"{CPANEL_HOST.rstrip('/')}/execute/EmailTrack/search"
    params3 = {
        "query": TARGET_EMAIL,
        "searchtype": "to",
    }
    try:
        r3 = requests.get(track_url, headers=headers, params=params3, timeout=30)
        print(f"  EmailTrack/search status: {r3.status_code}")
        if r3.status_code == 200:
            data3 = r3.json()
            print(f"  Response: {json.dumps(data3, indent=2)[:3000]}")
            records = data3.get("data", {}).get("records", data3.get("data", []))
            if isinstance(records, list):
                for rec in records:
                    if isinstance(rec, dict):
                        sender = rec.get("sender", rec.get("from", ""))
                        recipient = rec.get("recipient", rec.get("to", ""))
                        ts = rec.get("datetime", rec.get("time", ""))
                        status = rec.get("deliverystatus", rec.get("status", ""))
                        print(f"  [{ts}] {sender} -> {recipient} | {status}")
                        if "@mularcredit.co.ke" in sender.lower():
                            found_senders.add(sender.lower())
        else:
            print(f"  Response: {r3.text[:500]}")
    except Exception as e:
        print(f"  Error: {e}")

    # -------------------------------------------------------
    # Method 4: Try reading exim log via cPanel log viewer
    # -------------------------------------------------------
    print("\nMethod 4: cPanel Log viewer API...")
    log_view_url = f"{CPANEL_HOST.rstrip('/')}/execute/LogManager/retrieve_log"
    params4 = {"log": "exim_mainlog", "search": TARGET_EMAIL}
    try:
        r4 = requests.get(log_view_url, headers=headers, params=params4, timeout=30)
        print(f"  LogManager/retrieve_log status: {r4.status_code}")
        print(f"  Response: {r4.text[:1000]}")
    except Exception as e:
        print(f"  Error: {e}")

    # -------------------------------------------------------
    # Summary
    # -------------------------------------------------------
    print("\n" + "=" * 60)
    if found_senders:
        print(f"✅ Found {len(found_senders)} sender(s) that emailed {TARGET_EMAIL}:\n")
        for sender in sorted(found_senders):
            print(f"  → {sender}")
    else:
        print(f"❌ Could not find senders via API.")
        print()
        print("To get accurate results, you need either:")
        print("  1. SSH access to run:")
        print(f"     grep -i '{TARGET_EMAIL}' /var/log/exim_mainlog | grep 'from='")
        print("  2. cPanel >> Track Delivery >> search by recipient in your browser")
        print("     URL: https://mularcredit.co.ke:2083/cpanel/unprotected/run?module=EmailTrack")


if __name__ == "__main__":
    fetch_mail_logs()
