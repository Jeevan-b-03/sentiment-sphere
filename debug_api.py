import requests
from app import ACCESS_TOKEN

def debug_api():
    print(f"Using Token: {ACCESS_TOKEN[:10]}...{ACCESS_TOKEN[-10:]}")
    
    # 1. Check Identity
    r = requests.get("https://graph.facebook.com/v24.0/me", params={"access_token": ACCESS_TOKEN})
    print("\n--- Identity Check ---")
    print(r.text)
    
    if r.status_code != 200:
        print("Token Invalid!")
        return

    # 2. Check Permissions / Feed Existence
    r = requests.get("https://graph.facebook.com/v24.0/me/feed", params={"access_token": ACCESS_TOKEN, "limit": 1})
    print("\n--- Feed Check (Simple) ---")
    print(r.text)

    # 3. Check Exact Query using strict syntax
    # Trying the simplified syntax first: comments{...}
    params = {
        "fields": "comments{message,id,from,permalink_url,created_time}",
        "limit": 5,
        "access_token": ACCESS_TOKEN
    }
    r = requests.get("https://graph.facebook.com/v24.0/me/feed", params=params)
    print("\n--- Full Query Check ---")
    print(r.text)

if __name__ == "__main__":
    debug_api()
