from app import db
from datetime import datetime

class MonitoringRequest(db.Model):
    __tablename__ = 'monitoring_request'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MonitoringRequest {self.email} for {self.month}>'