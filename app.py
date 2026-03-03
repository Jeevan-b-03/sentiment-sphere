from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, Comment
from sentiment_engine import fetch_facebook_comments, analyze_sentiment, post_facebook_reply
from datetime import datetime
import os
import csv
import io
from flask import make_response

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'comments.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

db.init_app(app)

# CONFIG (Ideally moves to env var)
ACCESS_TOKEN = "EAAO9rA0AaqIBQVzuzT4SwZCHkRZBB2bQfWgz1xqZAPDNne5f9fCsyQK7unKp1StucZAVHrvZCvZBty6TzhUdbaeU4EkZBl3N53V2zhEkSiSR4eBQl2SgmFpr5OkZBxHt9xFsryKxAmexVLJFQ4TuWJ7rr0nm9m6xCKs09potWKCNRaiBZBjSDEMDp7RhMZA2l18ZCIcrRKcZCo3ZAbRxYZCf2QKszkMh5lAPKHfEYgqfHEokuefBGrPL7wgRqJNsIn7ZCKwqVKyoNoUVYav1jMZD"

# Replace deprecated before_first_request
with app.app_context():
    db.create_all()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    sentiment_filter = request.args.get('sentiment')
    
    # Date Range Filter
    time_range = request.args.get('time_range', '6m')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    # Calculate dates based on time_range only if no custom date provided
    if not from_date and time_range != 'custom':
        now = datetime.utcnow()
        if time_range == 'ytd':
            from_date_obj = datetime(now.year, 1, 1)
        elif time_range == '12m':
            from_date_obj = now.replace(year=now.year - 1) if now.month != 2 or now.day != 29 else now.replace(year=now.year - 1, day=28)
        else: # Default 6m
            # Rough 6 months: current month - 6
            month = now.month - 6
            year = now.year
            if month <= 0:
                month += 12
                year -= 1
            from_date_obj = datetime(year, month, now.day)
        
        from_date = from_date_obj.strftime('%Y-%m-%d')
        to_date = now.strftime('%Y-%m-%d')

    # 1. Base Query
    base_query = Comment.query
    
    if from_date:
        try:
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            base_query = base_query.filter(Comment.timestamp >= start_date)
        except ValueError:
            pass
            
    if to_date:
        try:
            end_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            end_date = end_date_obj.replace(hour=23, minute=59, second=59)
            base_query = base_query.filter(Comment.timestamp <= end_date)
        except ValueError:
            pass

    # Month Filter (Legacy/Alternative - keeping if needed, but Date Range takes precedence usually)
    # If both are present, they stack (AND logic), which might be confusing. 
    # Let's assume Date Range overrides Month filter if present, or just let them coexist.
    month_filter = request.args.get('month') 
    if month_filter and not (from_date or to_date):
        try:
            filter_date = datetime.strptime(month_filter, '%Y-%m')
            start_date = filter_date
            if filter_date.month == 12:
                end_date = datetime(filter_date.year + 1, 1, 1)
            else:
                end_date = datetime(filter_date.year, filter_date.month + 1, 1)
            base_query = base_query.filter(Comment.timestamp >= start_date, Comment.timestamp < end_date)
        except ValueError:
            pass

    # Data for Charts & Metrics
    # Top Row Charts + Metrics (Time Filtered ONLY - Context Preserved)
    global_comments = base_query.order_by(Comment.timestamp.desc()).all()
    
    # Bottom Grid Charts + Cards (Time AND Sentiment Filtered - Drill Down)
    filtered_query = base_query
    if sentiment_filter:
        filtered_query = filtered_query.filter_by(sentiment=sentiment_filter)
    
    filtered_comments = filtered_query.order_by(Comment.timestamp.desc()).all()
    
    # Display cards use the filtered set
    display_comments = filtered_comments
    
    # Apply Status Filter (for Cards View mostly, but affects display_comments)
    status_filter = request.args.get('status')
    if status_filter == 'completed':
        display_comments = [c for c in display_comments if c.status == 'Acknowledged']
    elif status_filter == 'pending':
        display_comments = [c for c in display_comments if (c.status is None or c.status != 'Acknowledged')]

    # Metrics (Based on GLOBAL time context to show total picture)
    total = len(global_comments)
    pos = sum(1 for c in global_comments if c.sentiment == 'positive')
    neg = sum(1 for c in global_comments if c.sentiment == 'negative')
    neu = sum(1 for c in global_comments if c.sentiment == 'neutral')
    
    # Serialize GLOBAL data for Top Row charts (Monthly, Trend, Dist)
    comments_json = [c.to_dict() for c in global_comments]
    
    # Generate Bottom Grid Data using FILTERED data
    # 1. Word Cloud (Filtered)
    word_cloud_data = get_word_cloud_data(filtered_comments)
    
    # 2. User Activity (Filtered)
    user_stats = {}
    for c in filtered_comments: # Use filtered
        if not c.username: continue
        if c.username not in user_stats:
            user_stats[c.username] = {'total': 0, 'pos': 0, 'neg': 0, 'neu': 0}
        
        user_stats[c.username]['total'] += 1
        if c.sentiment == 'positive':
            user_stats[c.username]['pos'] += 1
        elif c.sentiment == 'negative':
            user_stats[c.username]['neg'] += 1
        else:
            user_stats[c.username]['neu'] += 1

    top_users = sorted(user_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
    user_activity_data = {
        'labels': [u[0] for u in top_users],
        'pos': [u[1]['pos'] for u in top_users],
        'neg': [u[1]['neg'] for u in top_users],
        'neu': [u[1]['neu'] for u in top_users]
    }

    # 3. Associate Stats (Filtered)
    associate_stats = {}
    for c in filtered_comments: # Use filtered
        if not c.associate_name: continue
        name = c.associate_name
        if name not in associate_stats:
            associate_stats[name] = {'cases': 0, 'handles': 0}
        
        associate_stats[name]['handles'] += 1
        if c.action_taken == 'Case Logged':
            associate_stats[name]['cases'] += 1
            
    associate_data = []
    for name, stats in associate_stats.items():
        if stats['handles'] > 0:
            associate_data.append({
                'name': name,
                'value': stats['cases'],
                'handles': stats['handles']
            })

    # 4. Repeated Issues (Moved to Top Section -> Global Context)
    # Shows top issues from ALL negative comments in select month, regardless of sentiment filter drill-down.
    def get_repeated_issues_data(comments):
        # Define issue categories
        issue_keywords = {
            'Account Access': ['login', 'signin', 'password', 'access', 'account', 'locked', 'reset'],
            'UI/Navigation': ['design', 'confusing', 'hard to find', 'layout', 'navigation', 'menu', 'button'],
            'Performance/Speed': ['slow', 'lag', 'loading', 'freeze', 'wait', 'timeout', 'spinner'],
            'Mobile App': ['app', 'mobile', 'iphone', 'android', 'tablet', 'ios', 'crash'],
            'Bugs/Errors': ['error', 'bug', 'fail', 'broken', 'glitch', 'wrong', 'issue'],
            'Feature Request': ['feature', 'missing', 'add', 'wish', 'want', 'function'],
            'Customer Support': ['support', 'service', 'reply', 'response', 'rude', 'agent', 'help', 'contact'],
            'Billing/Payment': ['charge', 'money', 'pay', 'cost', 'subscription', 'price', 'card'],
            'Privacy/Security': ['hack', 'stolen', 'safety', 'private', 'data', 'spam', 'scam'],
            'Content/Media': ['photo', 'video', 'upload', 'image', 'post', 'share', 'quality'],
            'Notifications': ['alert', 'email', 'notification', 'remind', 'message', 'text'],
            'Updates/Versions': ['update', 'version', 'new', 'change', 'upgrade', 'install'],
            'Registration': ['sign up', 'register', 'verify', 'code', 'email', 'start']
        }
        
        issue_counts = {k: 0 for k in issue_keywords}
        
        for c in comments:
            if c.sentiment != 'negative': continue
            text = c.message.lower()
            
            for issue, keywords in issue_keywords.items():
                if any(k in text for k in keywords):
                    issue_counts[issue] += 1
                    
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        sorted_issues = [item for item in sorted_issues if item[1] > 0]
        
        return {
            'labels': [i[0] for i in sorted_issues],
            'data': [i[1] for i in sorted_issues]
        }

    repeated_issues_data = get_repeated_issues_data(global_comments) # Use global context

    # View State Support
    active_view = request.args.get('view', 'cards')

    return render_template('dashboard.html', 
                         comments=display_comments, 
                         comments_json=comments_json, # Global data for Top Charts
                         total=total, positive=pos, negative=neg, neutral=neu, # Global Metrics
                         current_month=month_filter,
                         word_cloud_data=word_cloud_data, # Filtered
                         user_activity_data=user_activity_data, # Filtered
                         associate_data=associate_data, # Filtered
                         repeated_issues_data=repeated_issues_data, # Filtered
                         active_view=active_view,
                         time_range=time_range,
                         calculated_from_date=from_date,
                         calculated_to_date=to_date) # Pass view state

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Demo credentials
        users = {
            'admin': 'admin',
            'admin1': 'admin1',
            'admin2': 'admin2',
            'admin3': 'admin3',
            'admin4': 'admin4',
            'manager': 'manager'
        }
        if username in users and password == users[username]:
            session['user'] = username 

            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

def sync_comments():
    """Helper to fetch and save new comments, returning the count of new items."""
    raw_comments = fetch_facebook_comments(ACCESS_TOKEN)
    count = 0
    for c in raw_comments:
        # Crucial: ID must be a string for consistent lookups in SQLite
        cid = str(c.get('id'))
        exists = Comment.query.get(cid)
        if not exists:
            sentiment = analyze_sentiment(c['message'])
            try:
                ts_str = c.get('timestamp')
                if ts_str:
                    # Robust ISO 8601 parsing handles '+0000', 'Z', and decimal seconds
                    try:
                        created_at = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    except ValueError:
                        # Fallback for older Graph API formats
                        created_at = datetime.strptime(ts_str.replace('+0000', ''), '%Y-%m-%dT%H:%M:%S')
                else:
                    created_at = datetime.utcnow()
            except Exception as e:
                # Log error and fallback
                print(f"Error parsing timestamp {ts_str}: {e}")
                created_at = datetime.utcnow()

            new_comment = Comment(
                id=cid,
                message=c['message'],
                sentiment=sentiment,
                username=c.get('username'),
                permalink_url=c.get('permalink_url'),
                timestamp=created_at
            )
            
            # AUTOMATIC REPLY LOGIC
            reply_sent = False
            if sentiment == 'positive':
                reply_sent = post_facebook_reply(cid, "Thank you for feedback", ACCESS_TOKEN)
            elif sentiment == 'negative':
                reply_sent = post_facebook_reply(cid, "sorry,we will see into it", ACCESS_TOKEN)
            
            new_comment.replied = reply_sent
            
            db.session.add(new_comment)
            count += 1
    db.session.commit()
    return count

@app.route('/manual_reply/<comment_id>', methods=['POST'])
@login_required
def manual_reply(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.replied:
        return jsonify({"success": False, "message": "Already replied"})
        
    msg = "Thank you for feedback" if comment.sentiment == 'positive' else "sorry,we will see into it"
    success = post_facebook_reply(comment.id, msg, ACCESS_TOKEN)
    
    if success:
        comment.replied = True
        db.session.commit()
        
    return redirect(request.referrer or url_for('index'))

@app.route('/fetch_comments', methods=['POST'])
@login_required
def fetch_comments_route():
    sync_comments()
    return redirect(url_for('index'))

@app.route('/create_case/<comment_id>', methods=['POST'])
@login_required
def create_case(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    action_taken = request.form.get('action_taken')
    case_number = request.form.get('case_number')
    
    if action_taken:
        comment.status = 'Acknowledged'
        comment.action_taken = action_taken
        # Auto-assign current user as associate
        comment.associate_name = session.get('user', 'Unknown')
        
        if action_taken == 'Case Logged' and case_number:
            comment.case_number = case_number
            comment.is_salesforce_user = True
        else:
            comment.case_number = None # Ensure it's empty if not applicable
            comment.is_salesforce_user = False
            
        comment.action_timestamp = datetime.utcnow()
        db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/graphs')
@login_required
def graphs():
    # 1. Sentiment Trend (Group by Date)
    raw_comments = Comment.query.order_by(Comment.timestamp).all()
    trend_data = {}
    
    for c in raw_comments:
        date_str = c.timestamp.strftime('%Y-%m-%d')
        if date_str not in trend_data:
            trend_data[date_str] = {'positive': 0, 'negative': 0, 'neutral': 0}
        trend_data[date_str][c.sentiment] += 1
        
    dates = list(trend_data.keys())
    pos_trend = [trend_data[d]['positive'] for d in dates]
    neg_trend = [trend_data[d]['negative'] for d in dates]
    neu_trend = [trend_data[d]['neutral'] for d in dates]
    
    # 2. Resolution Timeline (Pending vs Completed over time)
    # We track WHEN the comment came in (Pending start) vs WHEN action was taken (Completed)
    # For simplicity in this graph: "Pending" = count of comments on that day that are NOT acknowledged
    # "Completed" = count of comments on that day that ARE acknowledged
    # OR requesting: "Pending Acknowledgement" vs "Completed"
    # To match user request: "show pending acknowledgement and completed where it needs to show when the comment was posted,within how many days case was filed and when the action was taken."
    
    # Let's map this to a "Daily Resolution Stats" graph
    # X-Axis: Date
    # Series A: New Comments (Potential Pending)
    # Series B: Actions Taken (Completed)
    
    resolution_data = {}
    
    # Count Actions by Action Date
    actions = Comment.query.filter(Comment.action_timestamp != None).order_by(Comment.action_timestamp).all()
    for a in actions:
        date_str = a.action_timestamp.strftime('%Y-%m-%d')
        if date_str not in resolution_data:
            resolution_data[date_str] = {'new_cases': 0, 'resolved': 0}
        resolution_data[date_str]['resolved'] += 1
        
    # Count New Comments by Creation Date (Potential load)
    for c in raw_comments:
        date_str = c.timestamp.strftime('%Y-%m-%d')
        if date_str not in resolution_data:
            resolution_data[date_str] = {'new_cases': 0, 'resolved': 0}
        resolution_data[date_str]['new_cases'] += 1
        
    res_dates = sorted(list(resolution_data.keys()))
    new_cases_trend = [resolution_data[d]['new_cases'] for d in res_dates]
    resolved_trend = [resolution_data[d]['resolved'] for d in res_dates]
    
    # 3. Person Graph (Associate Performance)
    # "which person has logged the case and how many cases were logged"
    associates = db.session.query(Comment.associate_name, db.func.count(Comment.id)).filter(Comment.status == 'Acknowledged').group_by(Comment.associate_name).all()
    
    assoc_names = [a[0] for a in associates if a[0]]
    assoc_counts = [a[1] for a in associates if a[0]]

    return render_template('graphs.html',
                         dates=dates,
                         pos_trend=pos_trend,
                         neg_trend=neg_trend,
                         neu_trend=neu_trend,
                         res_dates=res_dates,
                         new_cases_trend=new_cases_trend,
                         resolved_trend=resolved_trend,
                         assoc_names=assoc_names,
                         assoc_counts=assoc_counts)

# Helper for Word Cloud
def get_word_cloud_data(comments):
    import re
    from collections import Counter
    
    # Basic stop words (Hardcoded to avoid NLTK download issues)
    STOPWORDS = set([
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't", 'feature', 'app', 'please', 'use', 'using', 'would', 'could', 'get', 'got', 'make', 'made', 'like', 'naviance', 'student', 'school'
    ])

    word_stats = {}

    for c in comments:
        # Simple tokenization
        text = c.message.lower()
        # Remove special chars
        text = re.sub(r'[^a-z\s]', '', text)
        words = text.split()
        
        for w in words:
            if w in STOPWORDS or len(w) < 3:
                continue
            
            if w not in word_stats:
                word_stats[w] = {'count': 0, 'pos': 0, 'neg': 0, 'neu': 0}
            
            word_stats[w]['count'] += 1
            if c.sentiment == 'positive':
                word_stats[w]['pos'] += 1
            elif c.sentiment == 'negative':
                word_stats[w]['neg'] += 1
            else:
                word_stats[w]['neu'] += 1

    # Format for WordCloud2.js: [ [word, weight, color], ... ]
    cloud_data = []
    # Take top 50 words
    top_words = sorted(word_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:50]
    
    for word, stats in top_words:
        # Determine Color
        total = stats['count']
        if stats['pos'] > stats['neg'] and stats['pos'] > stats['neu']:
            color = '#16A34A' # Green
        elif stats['neg'] > stats['pos'] and stats['neg'] > stats['neu']:
            color = '#DC2626' # Red
        else:
            color = '#F59E0B' # Amber/Neutral
            
        cloud_data.append([word, total, color])
        
    return cloud_data

@app.route('/download_csv')
@login_required
def download_csv():
    # Fetch all comments
    comments = Comment.query.order_by(Comment.timestamp.desc()).all()

    # Create CSV in memory
    si = io.StringIO()
    cw = csv.writer(si)
    
    # Header
    cw.writerow(['ID', 'Timestamp', 'User', 'Message', 'Sentiment', 'Status', 'Action Taken', 'Case Number', 'Associate', 'Action Timestamp'])
    
    # Rows
    for c in comments:
        cw.writerow([
            c.id,
            c.timestamp,
            c.username,
            c.message,
            c.sentiment,
            c.status,
            c.action_taken,
            c.case_number,
            c.associate_name,
            c.action_timestamp
        ])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=report.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/api/check_updates')
@login_required
def check_updates():
    new_count = sync_comments()
    return jsonify({"new": new_count})


if __name__ == '__main__':
    app.run(debug=True)
