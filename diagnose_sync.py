from app import app, db, ACCESS_TOKEN, sync_comments
from models import Comment
from sentiment_engine import fetch_facebook_comments
from datetime import datetime, date

def diagnose():
    with app.app_context():
        print(f"Current UTC time: {datetime.utcnow()}")
        
        # 1. Total count
        total = Comment.query.count()
        print(f"Total comments in DB before: {total}")
        
        # 2. Test Sync
        print("\nTesting sync_comments()...")
        try:
            added = sync_comments()
            print(f"sync_comments() reported adding: {added}")
        except Exception as e:
            print(f"sync_comments() FAILED with error: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. Total count after
        total_after = Comment.query.count()
        print(f"Total comments in DB after: {total_after}")
        
        # 4. Check API directly
        print("\nChecking raw API response...")
        raw = fetch_facebook_comments(ACCESS_TOKEN)
        print(f"API returned {len(raw)} items.")
        if len(raw) > 0:
            for i, item in enumerate(raw[:5]):
                ts = item.get('timestamp')
                msg = item.get('message', '')[:50]
                cid = item.get('id')
                exists = Comment.query.get(cid)
                print(f"{i+1}. ID: {cid} | TS: {ts} | Exists: {exists is not None} | {msg}...")

if __name__ == "__main__":
    diagnose()
