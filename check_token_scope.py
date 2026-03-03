import requests
import json
from app import ACCESS_TOKEN

def check_token():
    results = {}
    
    # 1. Identity
    url_me = f"https://graph.facebook.com/v24.0/me"
    params = {"access_token": ACCESS_TOKEN, "fields": "name,id"}
    try:
        data_me = requests.get(url_me, params=params).json()
        results["identity"] = data_me
    except Exception as e:
        results["identity_error"] = str(e)
        
    # 2. Accounts
    url_accounts = f"https://graph.facebook.com/v24.0/me/accounts"
    try:
        data_acc = requests.get(url_accounts, params={"access_token": ACCESS_TOKEN}).json()
        results["accounts"] = data_acc
    except Exception as e:
        results["accounts_error"] = str(e)
        
    with open("token_stats.json", "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    check_token()
