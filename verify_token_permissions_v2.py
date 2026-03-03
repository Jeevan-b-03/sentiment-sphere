import requests
from app import ACCESS_TOKEN

def verify_token():
    print("Checking token permissions and identity...")
    
    url_perms = f"https://graph.facebook.com/v24.0/me/permissions"
    try:
        resp = requests.get(url_perms, params={"access_token": ACCESS_TOKEN})
        data = resp.json()
        if "data" in data:
            print("\nGranted Permissions:")
            for p in data["data"]:
                if p['status'] == 'granted':
                    print(f"- {p['permission']}")
        elif "error" in data:
            print(f"\nError checking permissions: {data['error']['message']}")
    except Exception as e:
        print(f"\nException checking permissions: {e}")

    url_me = f"https://graph.facebook.com/v24.0/me"
    try:
        resp = requests.get(url_me, params={"access_token": ACCESS_TOKEN, "fields": "name,id,category"})
        data = resp.json()
        print("\nToken Identity:")
        if "name" in data:
            print(f"Name: {data['name']}")
            print(f"ID: {data['id']}")
            print(f"Category: {data.get('category', 'N/A')}")
        else:
            print(data)
    except Exception as e:
        print(f"\nException checking identity: {e}")

if __name__ == "__main__":
    verify_token()
