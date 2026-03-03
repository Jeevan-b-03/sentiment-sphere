from app import app, db
from models import Comment

def list_ids():
    with app.app_context():
        # Print first 20 IDs
        comments = Comment.query.all()
        print(f"Total comments: {len(comments)}")
        for c in sorted([c.id for c in comments])[:50]:
            print(c)

if __name__ == "__main__":
    list_ids()
