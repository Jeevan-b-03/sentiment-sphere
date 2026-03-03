import requests
import json
from app import ACCESS_TOKEN

def test_reply():
    # Example comment ID found in previous logs
    comment_id = "122093438499169394_1412438880242440"
    
    print(f"Attempting to reply to comment: {comment_id}")
    
    url = f"https://graph.facebook.com/v24.0/{comment_id}/comments"
    payload = {
        "message": "Testing automatic reply system...",
        "access_token": ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, data=payload)
        status_code = response.status_code
        result = response.json()
        
        print(f"Status Code: {status_code}")
        print("Response JSON:")
        print(json.dumps(result, indent=2))
        
        if "id" in result:
            print("SUCCESS: Reply posted!")
        else:
            print("FAILURE: Could not post reply.")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_reply()
