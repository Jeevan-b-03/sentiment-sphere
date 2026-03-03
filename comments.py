import requests
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os

# -------------------------------------------
# CONFIG
# -------------------------------------------

ACCESS_TOKEN = "EAAO9rA0AaqIBQO3urmVlGsOs9XyrBBKEfD5UEdm8Ri3IpH81eVFP9JJS6FMOhphhdnOCLTmdWwcLoAlGtm3YxRJOeZC5cZBkp55kk8FFlxM5dNmU7mBm7QPc5xD2dWghoS3ao0ZBXypPYfS1RgMZCdvtJRnTlbZBoRKoYzShESQXrX7joJJ8iZCkJw6VP9CYs5SSwvykq9zjBkwFWQbc1GUBGAgo6oZAbCF9rzTt5WnV4YZD"

OUTPUT_DIR = "./sentiment_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

POS_FILE = os.path.join(OUTPUT_DIR, "positive_comments.txt")
NEG_FILE = os.path.join(OUTPUT_DIR, "negative_comments.txt")
NEU_FILE = os.path.join(OUTPUT_DIR, "neutral_comments.txt")

REPLIED_FILE = "replied_ids.txt"


# -------------------------------------------
# LOAD / SAVE REPLIED COMMENT IDS
# -------------------------------------------

def load_replied_ids():
    """Load previously replied comment IDs to avoid duplicate replies."""
    if not os.path.exists(REPLIED_FILE):
        return set()

    with open(REPLIED_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())


def save_replied_id(comment_id):
    """Save a comment ID after replying once."""
    with open(REPLIED_FILE, "a") as f:
        f.write(comment_id + "\n")


replied_ids = load_replied_ids()


# -------------------------------------------
# FETCH COMMENTS + IDs
# -------------------------------------------

def fetch_facebook_comments(token, limit=100):
    base_url = "https://graph.facebook.com/v24.0/me/feed"
    params = {
        "fields": "message,comments{message,id}",
        "limit": limit,
        "access_token": token,
    }

    response = requests.get(base_url, params=params)

    try:
        data = response.json()
    except:
        print("Invalid JSON:", response.text)
        return [], [], []

    comments = []
    comment_ids = []

    if "data" not in data:
        print("No 'data' field found.")
        return comments, comment_ids

    for post in data["data"]:
        if "comments" in post and "data" in post["comments"]:
            for c in post["comments"]["data"]:
                if "message" in c and "id" in c:
                    comments.append(c["message"])
                    comment_ids.append(c["id"])

    return comments, comment_ids


# -------------------------------------------
# SENTIMENT CLASSIFIER
# -------------------------------------------

def classify_sentiments(comments):
    analyzer = SentimentIntensityAnalyzer()

    positive = []
    negative = []
    neutral = []
    labels = []  # store label order for reply

    for text in comments:
        score = analyzer.polarity_scores(text)
        comp = score["compound"]

        if comp >= 0.01:
            positive.append(text)
            labels.append("positive")
        elif comp <= -0.01:
            negative.append(text)
            labels.append("negative")
        else:
            neutral.append(text)
            labels.append("neutral")

    return positive, negative, neutral, labels


# -------------------------------------------
# SAVE TO TEXT FILE
# -------------------------------------------

def save_to_file(filepath, lines):
    with open(filepath, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


# -------------------------------------------
# REPLY TO COMMENT
# -------------------------------------------

def reply_to_comment(comment_id, message, token):
    url = f"https://graph.facebook.com/v24.0/{comment_id}/comments"
    payload = {
        "message": message,
        "access_token": token
    }

    response = requests.post(url, data=payload)

    try:
        return response.json()
    except:
        return {"error": "Could not decode response"}


# -------------------------------------------
# MAIN PIPELINE
# -------------------------------------------

def main():
    print("Fetching Facebook comments…")
    comments, ids = fetch_facebook_comments(ACCESS_TOKEN)

    print(f"Fetched {len(comments)} comments.")

    if not comments:
        print("No comments found.")
        return

    print("Analyzing sentiment…")
    pos, neg, neu, labels = classify_sentiments(comments)

    print("Saving to files…")
    save_to_file(POS_FILE, pos)
    save_to_file(NEG_FILE, neg)
    save_to_file(NEU_FILE, neu)

    print("Replying to comments based on sentiment…")
    for comment_text, label, comment_id in zip(comments, labels, ids):

        # Skip if already replied
        if comment_id in replied_ids:
            continue

        # Choose reply message
        if label == "positive":
            reply_msg = "Thank you for your feedback! 😊"
        elif label == "negative":
            reply_msg = "We're sorry to hear that. We will look into this immediately."
        else:  # neutral
            reply_msg = "Thank you for your comment! Let us know if you need help."

        # Send reply
        resp = reply_to_comment(comment_id, reply_msg, ACCESS_TOKEN)
        print(f"Replied to '{comment_text[:20]}…' -> {label}: {resp}")

        # Save ID to avoid duplicate reply
        replied_ids.add(comment_id)
        save_replied_id(comment_id)

    print("All tasks completed!")


if __name__ == "__main__":
    main()
