from app import app, db
from models import Comment

def check_recent():
    with app.app_context():
        # Get all comments and filter for real ones
        comments = Comment.query.all()
        print(f"{'ID':<40} | {'Sentiment':<10} | {'Replied':<10} | {'Snippet'}")
        print("-" * 120)
        found = 0
        for c in comments:
            if not str(c.id).startswith('dummy'):
                found += 1
                msg = c.message[:30].replace('\n', ' ')
                print(f"{c.id:<40} | {c.sentiment:<10} | {str(c.replied):<10} | {msg}")
        if found == 0:
            print("No real Facebook comments found in database.")
        else:
            print(f"Total real Facebook comments: {found}")

if __name__ == "__main__":
    check_recent()
