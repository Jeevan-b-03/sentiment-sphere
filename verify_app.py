from app import app, db, Comment
from flask import session

def test_app():
    # Setup
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # 1. Test Database Creation
        print("Database initialized.")
        
        # 2. Test Adding Comment
        c = Comment(id="123", message="I love this product!", sentiment="positive")
        db.session.add(c)
        db.session.commit()
        print("Test comment added.")
        assert Comment.query.count() == 1
        
        # 3. Test Dashboard Route (Login Required Check)
        with app.test_client() as client:
            resp = client.get('/')
            assert resp.status_code == 302 # Redirect to login
            print("Access control working (redirected to login).")
            
        # 4. Test Login
        with app.test_client() as client:
            resp = client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
            assert resp.status_code == 200
            assert b"SentimentDash" in resp.data
            print("Login successful and Dashboard loaded.")
            
            # 5. Test Case Creation logic
            # Use app context again or continue with client?
            # Let's use the DB directly to check logic for simplicity if client is complex with sessions
            c_neg = Comment(id="999", message="Bad service", sentiment="negative", status="Pending")
            db.session.add(c_neg)
            db.session.commit()
            
            # Simulate case creation POST
            resp = client.post('/create_case/999', data={'associate_name': 'Test User', 'case_number': 'CASE-TEST'}, follow_redirects=True)
            assert resp.status_code == 200
            
            updated_c = Comment.query.get("999")
            assert updated_c.status == 'Acknowledged'
            assert updated_c.associate_name == 'Test User'
            print("Case creation flow verified.")

if __name__ == "__main__":
    try:
        test_app()
        print("ALL TESTS PASSED")
    except Exception as e:
        print(f"TEST FAILED: {e}")
