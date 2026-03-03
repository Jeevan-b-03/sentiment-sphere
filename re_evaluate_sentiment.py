from app import app, db
from models import Comment
from sentiment_engine import analyze_sentiment
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def re_evaluate():
    with app.app_context():
        # Search for the comment by keyword
        c = Comment.query.filter(Comment.message.like('%copy-pasted%')).first()
        if c:
            print(f"Message: {c.message}")
            sia = SentimentIntensityAnalyzer()
            
            # Full sentence score
            full_score = sia.polarity_scores(c.message)
            print(f"Full Score: {full_score}")
            
            # Word by word score
            words = c.message.split()
            print("\nWord Level Scores:")
            for word in words:
                score = sia.polarity_scores(word)
                if score['compound'] != 0:
                    print(f"  {word}: {score['compound']}")
            
            # Let's see how VADER handles it sentence by sentence
            import nltk
            try:
                sentences = nltk.sent_tokenize(c.message)
            except:
                sentences = [c.message]
            
            print("\nSentence Level Scores:")
            for i, sent in enumerate(sentences):
                s_score = sia.polarity_scores(sent)
                print(f"  S{i+1}: {sent} | {s_score['compound']}")

        else:
            print("Comment not found.")

if __name__ == "__main__":
    re_evaluate()
