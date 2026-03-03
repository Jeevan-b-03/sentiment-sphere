from app import app, db
from models import Comment

def verify_changes():
    with app.app_context():
        # 1. Check if the column exists by attempting to query it
        try:
            test_comment = Comment.query.first()
            if test_comment:
                print(f"Current is_salesforce_user status: {test_comment.is_salesforce_user}")
                
                # 2. Test updating the flag
                original_status = test_comment.is_salesforce_user
                test_comment.is_salesforce_user = not original_status
                db.session.commit()
                
                updated_comment = Comment.query.get(test_comment.id)
                print(f"Updated is_salesforce_user status: {updated_comment.is_salesforce_user}")
                
                # Revert change
                test_comment.is_salesforce_user = original_status
                db.session.commit()
                print("Verification successful: Column exists and is writable.")
            else:
                print("No comments found in DB to test.")
        except Exception as e:
            print(f"Verification failed: {e}")

if __name__ == "__main__":
    verify_changes()
