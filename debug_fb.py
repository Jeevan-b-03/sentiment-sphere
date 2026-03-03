import requests
import json
from app import ACCESS_TOKEN

def debug_fetch():
    print(f"Using Token: {ACCESS_TOKEN[:10]}...")
    
    # Check Accounts (Pages)
    print("\n--- CHECKING ACCOUNTS (PAGES) ---")
    try:
        # Fetch pages this user manages
        url = "https://graph.facebook.com/v24.0/me/accounts"
        params = {"access_token": ACCESS_TOKEN}
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if "data" in data and len(data["data"]) > 0:
            print(f"Found {len(data['data'])} Page(s):")
            for page in data["data"]:
                print(f"- Name: {page.get('name')}")
                print(f"  ID: {page.get('id')}")
                print(f"  Category: {page.get('category')}")
                # print(f"  Page Token: {page.get('access_token')[:10]}...") 
                
                # Check Feed of this Page
                page_token = page.get('access_token')
                page_id = page.get('id')
                print(f"  -> Fetching Feed for Page {page.get('name')}...")
                
                feed_url = f"https://graph.facebook.com/v24.0/{page_id}/feed"
                feed_params = {
                    "fields": "message,created_time,comments{message,from,created_time}",
                    "limit": 3,
                    "access_token": page_token # Use Page Token!
                }
                feed_resp = requests.get(feed_url, params=feed_params)
                feed_data = feed_resp.json()
                # print(json.dumps(feed_data, indent=2))
                
                if "data" in feed_data and len(feed_data["data"]) > 0:
                    print(f"     Found {len(feed_data['data'])} posts.")
                    for p in feed_data["data"]:
                        msg = p.get('message', 'No Message')[:30]
                        print(f"     Post: {msg}...")
                        if "comments" in p:
                            print(f"       {len(p['comments']['data'])} comments found.")
                        else:
                            print("       No comments.")
                else:
                    print("     No posts found on this page.")
                    
        else:
            print("No pages found for this user.")
            print("Raw Response:", json.dumps(data, indent=2))

    except Exception as e:
        print(f"Accounts Check Failed: {e}")

if __name__ == "__main__":
    debug_fetch()
