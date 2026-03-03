from app import app, db
from models import Comment
from datetime import datetime

def check_comment():
    with app.app_context():
        cid = '122093438499169'
        c = Comment.query.get(cid)
        if c:
            print(f"ID: {c.id}")
            print(f"Timestamp: {c.timestamp}")
            print(f"Sentiment: {c.sentiment}")
            print(f"Status: {c.status}")
            print(f"Message: {c.message[:100]}")
            
            # Check current server time
            print(f"Server Utcnow: {datetime.utcnow()}")
        else:
            print("Comment not found in DB.")

if __name__ == "__main__":
    check_comment()
