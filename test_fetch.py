import requests
import json

# Token from app.py
ACCESS_TOKEN = "EAAO9rA0AaqIBQA4EkZCbid2k5QED1KlYwB5ID1OwTMWtDZBAUM0sFPM4mQmHhPENO4BJpWnZA8zg87IpOpXIZByZBcsHqzLn4WdDi7e40djA8sSoavxroqFG2kIKc9r36IZCX2YeSy5SgnpjRW8DFa25VmeSumOMjFhWPRC9e1YUCNIXmcwB2vUHoLh78d7ZC5xcJUPCk4SZBBr51jJuDiTEOZC32MFwp08nkrZAbJKfDLDjgZD"

def fetch_facebook_comments(token, limit=10):
    print(f"Testing token: {token[:10]}...")
    base_url = "https://graph.facebook.com/v24.0/me/feed"
    params = {
        "fields": "comments{message,id,from,permalink_url,created_time}",
        "limit": limit,
        "access_token": token,
    }

    try:
        print(f"Requesting {base_url}...")
        response = requests.get(base_url, params=params)
        print(f"Response status: {response.status_code}")
        
        data = response.json()
        if "error" in data:
            print("API Error:", data["error"]["message"])
            return []
        
        if "data" not in data:
            print("No 'data' field found. Response keys:", data.keys())
            return []

        print(f"Found {len(data['data'])} posts.")
        
        comments_count = 0
        for post in data["data"]:
            if "comments" in post and "data" in post["comments"]:
                for c in post["comments"]["data"]:
                    comments_count += 1
                    print(f"- Comment: {c.get('message', '')} (ID: {c.get('id')})")
        
        print(f"Total comments found: {comments_count}")
        return data

    except Exception as e:
        print("Exception:", str(e))
        return []

if __name__ == "__main__":
    fetch_facebook_comments(ACCESS_TOKEN)
