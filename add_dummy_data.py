from app import app, db
from models import Comment
from datetime import datetime, timedelta
import random

# Expanded sample messages for different sentiments
positive_messages = [
    "Great service! Very helpful and responsive.",
    "Thank you so much for the quick resolution!",
    "Excellent support team, highly recommend!",
    "Amazing experience, will definitely use again.",
    "Very satisfied with the service provided.",
    "Outstanding customer service!",
    "Quick and efficient, thank you!",
    "Best support I've ever received.",
    "Impressed with the professionalism.",
    "Wonderful experience from start to finish!",
    "The team went above and beyond.",
    "Fantastic job, keep it up!",
    "Really appreciate the help!",
    "Top-notch service, thank you!",
    "Exceeded my expectations!",
]

negative_messages = [
    "Very disappointed with the service.",
    "This is unacceptable, needs immediate attention.",
    "Poor customer service, not happy at all.",
    "Still waiting for a response, very frustrating.",
    "This issue has not been resolved yet.",
    "Terrible experience, would not recommend.",
    "Not satisfied with the outcome.",
    "This needs to be fixed urgently.",
    "Extremely unhappy with this situation.",
    "No one has responded to my complaint.",
    "This is taking way too long.",
    "Very poor communication.",
    "I expected better service than this.",
    "Completely unacceptable behavior.",
    "This problem keeps happening.",
]

neutral_messages = [
    "I have a question about my account.",
    "Can someone help me with this?",
    "What are your operating hours?",
    "I need more information about this.",
    "Is this feature available?",
    "How do I access my account?",
    "Can you provide an update?",
    "I would like to know more details.",
    "When will this be available?",
    "Could you clarify this for me?",
    "I'm looking for information on...",
    "What's the process for this?",
    "Can I get some assistance?",
    "Is there a way to do this?",
    "I need help understanding this.",
]

usernames = [
    "John Smith", "Sarah Johnson", "Mike Davis", "Emily Brown",
    "David Wilson", "Lisa Anderson", "James Taylor", "Jennifer Martinez",
    "Robert Garcia", "Mary Rodriguez", "William Lee", "Patricia White",
    "Michael Chen", "Jessica Thompson", "Daniel Kim", "Amanda Clark"
]

def generate_moderate_dummy_data():
    """Generate a moderate amount of dummy comments for the past 4 months"""
    
    with app.app_context():
        # Get the current date
        end_date = datetime.now()
        
        # Start from 4 months ago
        start_date = end_date - timedelta(days=120)
        
        print(f"Generating dummy data from {start_date.date()} to {end_date.date()}")
        
        comment_id_counter = 10000  # Start with high IDs to avoid conflicts
        
        # Target: ~150-200 comments over 120 days = 1-2 comments per day average
        current_date = start_date
        total_added = 0
        
        while current_date <= end_date:
            # Random number of comments per day (0-4, with some days having none)
            num_comments = random.choices([0, 1, 2, 3, 4], weights=[20, 30, 30, 15, 5])[0]
            
            for _ in range(num_comments):
                # Random sentiment distribution: 45% positive, 30% negative, 25% neutral
                rand = random.random()
                if rand < 0.45:
                    sentiment = 'positive'
                    message = random.choice(positive_messages)
                elif rand < 0.75:
                    sentiment = 'negative'
                    message = random.choice(negative_messages)
                else:
                    sentiment = 'neutral'
                    message = random.choice(neutral_messages)
                
                # Random time during business hours (8 AM - 8 PM)
                random_hour = random.randint(8, 20)
                random_minute = random.randint(0, 59)
                timestamp = current_date.replace(hour=random_hour, minute=random_minute)
                
                # Create unique comment ID
                comment_id = f"dummy_{comment_id_counter}_{int(timestamp.timestamp())}"
                
                # Check if comment already exists
                existing = Comment.query.get(comment_id)
                if not existing:
                    new_comment = Comment(
                        id=comment_id,
                        message=message,
                        sentiment=sentiment,
                        username=random.choice(usernames),
                        permalink_url=f"https://facebook.com/comments/{comment_id}",
                        timestamp=timestamp
                    )
                    
                    # Randomly acknowledge some negative/neutral comments (40% chance)
                    if sentiment in ['negative', 'neutral'] and random.random() < 0.4:
                        new_comment.status = 'Acknowledged'
                        new_comment.associate_name = random.choice(['Admin', 'Support Team', 'Manager', 'Customer Service'])
                        new_comment.action_taken = random.choice(['Case Logged', 'User Not Found'])
                        if new_comment.action_taken == 'Case Logged':
                            new_comment.case_number = f"CS{random.randint(1000, 9999)}"
                        # Action taken 1-5 days after comment
                        new_comment.action_timestamp = timestamp + timedelta(days=random.randint(1, 5))
                    
                    db.session.add(new_comment)
                    comment_id_counter += 1
                    total_added += 1
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Commit all changes
        db.session.commit()
        print(f"\n✓ Successfully added {total_added} dummy comments!")
        
        # Print summary
        total = Comment.query.count()
        pos = Comment.query.filter_by(sentiment='positive').count()
        neg = Comment.query.filter_by(sentiment='negative').count()
        neu = Comment.query.filter_by(sentiment='neutral').count()
        ack = Comment.query.filter_by(status='Acknowledged').count()
        
        print(f"\n{'='*50}")
        print(f"DATABASE SUMMARY")
        print(f"{'='*50}")
        print(f"Total Comments: {total}")
        print(f"  Positive: {pos} ({pos/total*100:.1f}%)")
        print(f"  Negative: {neg} ({neg/total*100:.1f}%)")
        print(f"  Neutral: {neu} ({neu/total*100:.1f}%)")
        print(f"  Acknowledged: {ack} ({ack/total*100:.1f}%)")
        print(f"{'='*50}")

if __name__ == '__main__':
    generate_moderate_dummy_data()
