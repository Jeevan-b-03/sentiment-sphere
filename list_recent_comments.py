from app import app, db
from models import Comment

def list_comments():
    with app.app_context():
        comments = Comment.query.order_by(Comment.timestamp.desc()).limit(5).all()
        if not comments:
            print("No comments found in DB.")
            return
        
        print(f"{'ID':<25} | {'Username':<15} | {'Sentiment':<10} | {'Replied':<8} | {'Message'}")
        print("-" * 80)
        for c in comments:
            msg = (c.message[:50] + '...') if len(c.message) > 50 else c.message
            print(f"{c.id:<25} | {str(c.username):<15} | {c.sentiment:<10} | {str(c.replied):<8} | {msg}")

if __name__ == "__main__":
    list_comments()
