from app import app, db
from models import Comment
from sentiment_engine import analyze_sentiment

def update_all_sentiments():
    with app.app_context():
        print("Starting batch sentiment re-classification...")
        comments = Comment.query.all()
        total = len(comments)
        updated_count = 0
        
        for i, c in enumerate(comments):
            new_sentiment = analyze_sentiment(c.message)
            if new_sentiment != c.sentiment:
                print(f"Update [{i+1}/{total}] ID: {c.id} | {c.sentiment} -> {new_sentiment}")
                c.sentiment = new_sentiment
                updated_count += 1
            
        db.session.commit()
        print(f"Finished! Updated {updated_count} comments out of {total}.")

if __name__ == "__main__":
    update_all_sentiments()
