from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Comment(db.Model):
    id = db.Column(db.String(100), primary_key=True)  # Facebook Comment ID
    message = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="Pending")  # Pending, Acknowledged
    associate_name = db.Column(db.String(100), nullable=True)
    case_number = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(100), nullable=True)
    permalink_url = db.Column(db.String(500), nullable=True)
    action_taken = db.Column(db.String(50), nullable=True)
    action_timestamp = db.Column(db.DateTime, nullable=True)
    replied = db.Column(db.Boolean, default=False)
    is_salesforce_user = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "sentiment": self.sentiment,
            "status": self.status,
            "associate_name": self.associate_name,
            "case_number": self.case_number,
            "timestamp": self.timestamp.isoformat(),
            "username": self.username,
            "permalink_url": self.permalink_url,
            "action_taken": self.action_taken,
            "action_timestamp": self.action_timestamp.isoformat() if self.action_timestamp else None,
            "is_salesforce_user": self.is_salesforce_user
        }
