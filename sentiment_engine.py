import requests
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Ensure VADER lexicon is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

def fetch_facebook_comments(token, limit=100):
    # 1. Determine if this is a User Token or Page Token
    # Try fetching accounts (Pages)
    page_token = token
    target_id = "me"
    
    try:
        accounts_url = "https://graph.facebook.com/v24.0/me/accounts"
        accounts_resp = requests.get(accounts_url, params={"access_token": token})
        accounts_data = accounts_resp.json()
        
        if "data" in accounts_data and len(accounts_data["data"]) > 0:
            # It's a User Token with Pages -> Use the first Page
            first_page = accounts_data["data"][0]
            page_token = first_page.get("access_token")
            target_id = first_page.get("id")
            print(f"Auto-detected Page: {first_page.get('name')} (ID: {target_id})")
        else:
            print("No pages found or Token is already a Page Token. Using 'me'.")
            
    except Exception as e:
        print(f"Error checking accounts: {e}. Proceeding with provided token.")

    # 2. Fetch Feed of the Target (Page or User)
    base_url = f"https://graph.facebook.com/v24.0/{target_id}/feed"
    params = {
        "fields": "comments{message,id,from,permalink_url,created_time}",
        "limit": limit,
        "access_token": page_token,
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if "error" in data:
            print("API Error:", data["error"]["message"])
            return []
    except:
        print("Invalid JSON:", response.text)
        return []

    comments_data = []

    if "data" not in data:
        print("No 'data' field found. Response:", data)
        return comments_data

    for post in data["data"]:
        # Process post (if needed) or just comments
        if "comments" in post and "data" in post["comments"]:
            for c in post["comments"]["data"]:
                if "message" in c and "id" in c:
                    comments_data.append({
                        "id": str(c["id"]),
                        "message": c["message"],
                        "username": c.get("from", {}).get("name", "Unknown User"),
                        "permalink_url": c.get("permalink_url", "#"),
                        "timestamp": c.get("created_time")
                    })

    return comments_data

def analyze_sentiment(text):
    if not text:
        return "neutral"
    
    text_lower = text.lower()
    
    # 1. Keyword Overrides (High Confidence Negative Triggers)
    negative_triggers = [
        "not helpful", "copy-pasted", "copy pasted", "still waiting", 
        "no response", "disappointed", "poor service", "useless",
        "unacceptable", "frustrating", "terrible", "worst",
        "don't appreciate", "unhelpful", "failed to"
    ]
    
    for trigger in negative_triggers:
        if trigger in text_lower:
            return "negative"

    # 2. VADER with Custom Lexicon
    analyzer = SentimentIntensityAnalyzer()
    
    # Adjust weights for specific context words
    custom_lexicon = {
        'solution': 0.5,    # Reduce from default high positive if needed, but here we just ensure it doesn't mask 'not'
        'proper': 0.5,      # Reduce positive weight
        'copy-pasted': -1.5, # Explicit negative
        'helpful': 1.0      # Standard
    }
    analyzer.lexicon.update(custom_lexicon)
    
    score = analyzer.polarity_scores(text)
    comp = score["compound"]

    if comp >= 0.3:
        return "positive"
    elif comp <= -0.05:
        return "negative"
    else:
        return "neutral"

def post_facebook_reply(comment_id, message, token):
    """
    Posts a reply to a specific comment on Facebook.
    Requires 'pages_manage_comments' permission.
    """
    url = f"https://graph.facebook.com/v24.0/{comment_id}/comments"
    payload = {
        "message": message,
        "access_token": token
    }
    try:
        response = requests.post(url, data=payload)
        result = response.json()
        if "id" in result:
            print(f"Successfully posted reply to {comment_id}")
            return True
        else:
            print(f"Failed to post reply: {result.get('error', {}).get('message')}")
            return False
    except Exception as e:
        print(f"Error posting reply: {e}")
        return False
