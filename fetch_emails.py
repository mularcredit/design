import requests
import json
import os

# --- CONFIGURATION ---
# Please provide these details or set them as environment variables
CPANEL_HOST = os.environ.get('CPANEL_HOST', 'https://mularcredit.co.ke:2083')
CPANEL_USER = os.environ.get('CPANEL_USER', 'mular')
API_TOKEN = 'M8GJSJK5MRU8EITT8OQ9J5SBU2423V38'

def get_email_accounts():
    """
    Fetches all email accounts (POPs) from cPanel using UAPI.
    """
    if 'YOUR_HOSTNAME' in CPANEL_HOST or 'YOUR_USERNAME' in CPANEL_USER:
        print("Error: Please update the CPANEL_HOST and CPANEL_USER variables.")
        return

    # UAPI Endpoint for listing email accounts
    # Documentation: https://api.docs.cpanel.net/openapi/cpanel/operation/list_pops/
    url = f"{CPANEL_HOST.rstrip('/')}/execute/Email/list_pops"

    headers = {
        "Authorization": f"cpanel {CPANEL_USER}:{API_TOKEN}"
    }

    try:
        print(f"Connecting to {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 1:
            accounts = data.get('data', [])
            print(f"\nSuccessfully retrieved {len(accounts)} email accounts:\n")
            for acc in accounts:
                print(f"- {acc.get('email')} (Disk usage: {acc.get('diskused')} / {acc.get('diskquota')})")
        else:
            print(f"Error from cPanel: {data.get('errors')}")
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except json.JSONDecodeError:
        print("Failed to parse the response from cPanel.")

if __name__ == "__main__":
    get_email_accounts()
