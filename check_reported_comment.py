from app import app, db
from models import Comment

def check_comment():
    with app.app_context():
        # Search for the comment by keyword
        comment = Comment.query.filter(Comment.message.like('%copy-pasted%')).first()
        if comment:
            print(f"Comment Found!")
            print(f"ID: {comment.id}")
            print(f"Sentiment: {comment.sentiment}")
            print(f"Message: {comment.message}")
        else:
            print("Comment not found in database.")

if __name__ == "__main__":
    check_comment()
