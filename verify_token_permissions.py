import requests
from app import ACCESS_TOKEN

def verify_token():
    # 1. Check token debug info
    url = f"https://graph.facebook.com/debug_token"
    params = {
        "input_token": ACCESS_TOKEN,
        "access_token": ACCESS_TOKEN # Using own token works if it's a Page Token or User Token with proper app access
    }
    
    # Actually, debug_token usually needs an App Token or a User Token for the app.
    # Let's try to get permissions directly from /me/permissions
    
    url_perms = f"https://graph.facebook.com/v24.0/me/permissions"
    try:
        resp = requests.get(url_perms, params={"access_token": ACCESS_TOKEN})
        data = resp.json()
        print("Permissions Check:")
        if "data" in data:
            for p in data["data"]:
                print(f"- {p['permission']}: {p['status']}")
        else:
            print(f"Error checking permissions: {data.get('error', {}).get('message')}")
    except Exception as e:
        print(f"Exception checking permissions: {e}")

    # 2. Check identity
    url_me = f"https://graph.facebook.com/v24.0/me"
    try:
        resp = requests.get(url_me, params={"access_token": ACCESS_TOKEN, "fields": "name,id,category"})
        data = resp.json()
        print("\nToken Identity:")
        print(data)
    except Exception as e:
        print(f"Exception checking identity: {e}")

if __name__ == "__main__":
    verify_token()
