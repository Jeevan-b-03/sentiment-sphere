import requests
import json
from app import ACCESS_TOKEN

def debug_token():
    print("Debugging Token Scopes...")
    
    # Needs a way to get an App Access Token or just try checking /me/permissions
    url = "https://graph.facebook.com/v24.0/me/permissions"
    params = {"access_token": ACCESS_TOKEN}
    
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if "data" in data:
            permissions = data["data"]
            granted = [p["permission"] for p in permissions if p["status"] == "granted"]
            print(f"Granted Permissions: {granted}")
            
            required = ["pages_manage_comments", "pages_manage_engagement", "pages_read_engagement"]
            missing = [p for p in required if p not in granted]
            
            if not missing:
                print("SUCCESS: All required permissions are present.")
            else:
                print(f"MISSING Permissions: {missing}")
        else:
            print(f"Error checking permissions: {data.get('error', {}).get('message')}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    debug_token()
