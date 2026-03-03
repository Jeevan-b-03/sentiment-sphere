from app import app, db
from models import Comment
from datetime import datetime
import random

def refine_jan_2026_data():
    with app.app_context():
        # Clear previous Jan 2026 dummy data
        Comment.query.filter(Comment.id.like('jan2026_%')).delete(synchronize_session=False)
        db.session.commit()
        print("Cleared previous Jan 2026 dummy data.")

        # Specific distribution: 6 negative, 5 positive, 4 neutral
        
        # 6 Negative (3-line statements)
        negative_msgs = [
            "This service is absolutely terrible.\nI have been waiting for hours without help.\nI want an immediate refund now.",
            "The app crashes every time I open it.\nIt is very frustrating to use this device.\nTechnical support has been no help at all.",
            "Highly disappointed with the recent update.\nAll my data seems to have disappeared.\nWhere is the quality control team?",
            "The customer service agent was very rude.\nThey didn't listen to my problem at all.\nI will be switching to a competitor.",
            "I was overcharged on my last statement.\nThis has happened three times in a row.\nYour billing system is completely broken.",
            "The delivery arrived two weeks late.\nAnd the item was broken when I opened it.\nExtremely poor experience overall."
        ]
        
        # 5 Positive
        positive_msgs = [
            "Great experience! The team was very professional.",
            "Wow, I'm impressed with the new features.",
            "Quickest resolution I've ever seen, thanks!",
            "Love the new design of the dashboard.",
            "Best support team in the industry!"
        ]
        
        # 4 Neutral
        neutral_msgs = [
            "Can someone clarify the new policy?",
            "Is the office open on weekends?",
            "Where can I find my account number?",
            "Just checking in on my previous request."
        ]
        
        usernames = ["John Doe", "Jane Smith", "Bob Jones", "Alice Brown", "Charlie White", "Dana Green", "Eli Black"]
        
        total_added = 0
        
        # Helper to add comments
        def add_batch(messages, sentiment):
            nonlocal total_added
            for msg in messages:
                # Random day in Jan 1-6 2026
                day = random.randint(1, 6)
                hour = random.randint(9, 17)
                ts = datetime(2026, 1, day, hour, random.randint(0, 59))
                
                cid = f"jan2026_{sentiment}_{total_added}_{int(ts.timestamp())}"
                
                new_c = Comment(
                    id=cid,
                    message=msg,
                    sentiment=sentiment,
                    username=random.choice(usernames),
                    timestamp=ts,
                    permalink_url=f"https://fb.com/{cid}"
                )
                db.session.add(new_c)
                total_added += 1

        add_batch(negative_msgs, 'negative')
        add_batch(positive_msgs, 'positive')
        add_batch(neutral_msgs, 'neutral')
        
        db.session.commit()
        print(f"Successfully added {total_added} refined comments for Jan 1-6, 2026.")

if __name__ == '__main__':
    refine_jan_2026_data()
