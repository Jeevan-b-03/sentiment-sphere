from app import app, db
from models import Comment
from datetime import datetime, timedelta
import random

# Sample messages from add_dummy_data.py
positive_messages = [
    "Great service! Very helpful and responsive.", "Thank you so much for the quick resolution!",
    "Excellent support team, highly recommend!", "Amazing experience, will definitely use again.",
    "Very satisfied with the service provided.", "Outstanding customer service!",
    "Quick and efficient, thank you!", "Best support I've ever received."
]

negative_messages = [
    "Very disappointed with the service.", "This is unacceptable, needs immediate attention.",
    "Poor customer service, not happy at all.", "Still waiting for a response, very frustrating.",
    "This issue has not been resolved yet.", "Terrible experience, would not recommend.",
    "Not satisfied with the outcome.", "This needs to be fixed urgently."
]

neutral_messages = [
    "I have a question about my account.", "Can someone help me with this?",
    "What are your operating hours?", "I need more information about this.",
    "Is this feature available?", "How do I access my account?",
    "Can you provide an update?", "I would like to know more details."
]

usernames = ["John Smith", "Sarah Johnson", "Mike Davis", "Emily Brown", "David Wilson", "Lisa Anderson"]

def redistribute_data():
    with app.app_context():
        # 1. Clear existing dummy comments
        print("Cleaning up existing dummy data...")
        Comment.query.filter(Comment.id.like('dummy_%')).delete(synchronize_session=False)
        db.session.commit()

        # 2. Define the zig-zag distribution (Year, Month, Total, Pos, Neg, Neu)
        # Sequence: Jul (High), Aug (Low), Sep (High), Oct (Low), Nov (High), Dec (Low), Jan (High)
        distribution = [
            (2025, 7, 42, 20, 12, 10),
            (2025, 8, 14, 5, 4, 5),
            (2025, 9, 48, 25, 13, 10),
            (2025, 10, 10, 3, 4, 3),
            (2025, 11, 55, 30, 15, 10),
            (2025, 12, 16, 5, 6, 5),
            (2026, 1, 45, 25, 10, 10)
        ]

        total_added = 0
        comment_id_counter = 20000

        print("Generating zig-zag dummy data...")
        for year, month, total, pos, neg, neu in distribution:
            sentiments = (['positive'] * pos) + (['negative'] * neg) + (['neutral'] * neu)
            random.shuffle(sentiments)
            
            # If sentiments count < total due to rounding, pad with neutral
            if len(sentiments) < total:
                sentiments += ['neutral'] * (total - len(sentiments))
            
            for sentiment in sentiments:
                day = random.randint(1, 28)
                hour = random.randint(8, 19)
                minute = random.randint(0, 59)
                ts = datetime(year, month, day, hour, minute)
                
                comment_id = f"dummy_{comment_id_counter}_{int(ts.timestamp())}"
                
                if sentiment == 'positive':
                    msg = random.choice(positive_messages)
                elif sentiment == 'negative':
                    msg = random.choice(negative_messages)
                else:
                    msg = random.choice(neutral_messages)
                
                new_comment = Comment(
                    id=comment_id,
                    message=msg,
                    sentiment=sentiment,
                    username=random.choice(usernames),
                    permalink_url=f"https://facebook.com/comments/{comment_id}",
                    timestamp=ts
                )
                
                # Randomly acknowledge some non-positive comments
                if sentiment != 'positive' and random.random() < 0.3:
                    new_comment.status = 'Acknowledged'
                    new_comment.associate_name = 'Admin'
                    new_comment.action_taken = 'Case Logged'
                    new_comment.case_number = f"CS{random.randint(1000, 9999)}"
                    new_comment.action_timestamp = ts + timedelta(hours=random.randint(2, 48))

                db.session.add(new_comment)
                comment_id_counter += 1
                total_added += 1

        db.session.commit()
        print(f"Successfully added {total_added} comments with zig-zag pattern!")

if __name__ == "__main__":
    redistribute_data()
