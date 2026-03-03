import requests
import json
from app import ACCESS_TOKEN

def check_perms():
    url = f"https://graph.facebook.com/v24.0/me/permissions"
    try:
        resp = requests.get(url, params={"access_token": ACCESS_TOKEN})
        data = resp.json()
        with open("debug_permissions.json", "w") as f:
            json.dump(data, f, indent=4)
        print("Permissions saved to debug_permissions.json")
        
        if "data" in data:
            granted = [p['permission'] for p in data['data'] if p['status'] == 'granted']
            print("\nGranted:")
            for g in granted:
                print(f"- {g}")
            
            if 'pages_manage_comments' not in granted:
                print("\nWARNING: 'pages_manage_comments' permission is MISSING!")
        else:
            print("Error in response:", data)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_perms()
