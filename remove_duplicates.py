from app import app, db
from models import Comment
from collections import defaultdict

def delete_duplicate_messages():
    """Delete comments with duplicate message content, keeping only the oldest one"""
    
    with app.app_context():
        # Get all comments
        all_comments = Comment.query.order_by(Comment.timestamp).all()
        
        print(f"Total comments before cleanup: {len(all_comments)}")
        
        # Group comments by message content
        message_groups = defaultdict(list)
        for comment in all_comments:
            # Normalize message for comparison
            normalized_message = comment.message.strip().lower()
            message_groups[normalized_message].append(comment)
        
        # Find duplicates
        duplicates_to_delete = []
        unique_messages = 0
        
        for message, comments in message_groups.items():
            if len(comments) > 1:
                # Keep the first (oldest) comment, delete the rest
                print(f"\nMessage: '{message[:60]}...'")
                print(f"  Found {len(comments)} copies")
                print(f"  Keeping: {comments[0].id[:30]}... (timestamp: {comments[0].timestamp})")
                
                for duplicate in comments[1:]:
                    print(f"  Deleting: {duplicate.id[:30]}... (timestamp: {duplicate.timestamp})")
                    duplicates_to_delete.append(duplicate)
            else:
                unique_messages += 1
        
        print(f"\n{'='*60}")
        print(f"Unique messages: {unique_messages}")
        print(f"Duplicate messages found: {len(message_groups) - unique_messages}")
        print(f"Total duplicates to delete: {len(duplicates_to_delete)}")
        
        # Delete duplicates
        if duplicates_to_delete:
            confirm = input(f"\nDelete {len(duplicates_to_delete)} duplicate comments? (yes/no): ")
            if confirm.lower() == 'yes':
                for comment in duplicates_to_delete:
                    db.session.delete(comment)
                
                db.session.commit()
                print(f"\n✓ Successfully deleted {len(duplicates_to_delete)} duplicates!")
            else:
                print("\nCancelled. No comments were deleted.")
        else:
            print("\n✓ No duplicates found!")
        
        # Print final summary
        remaining = Comment.query.count()
        print(f"\nFinal count: {remaining} comments")

if __name__ == '__main__':
    delete_duplicate_messages()
