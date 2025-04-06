from utils.db import db

# Parent table: User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    UserBehaviorClass = db.Column(db.String(100), nullable=False)

    # Relationship to the Mobile table (One-to-Many)
    data = db.relationship('Mobile', backref='user', lazy=True)

# Child table: Mobile
class Mobile(db.Model):
    mobile_id = db.Column(db.Integer, primary_key=True)  # Correct column name for primary key
    DeviceModel = db.Column(db.String(100), nullable=False)
    OperatingSystem = db.Column(db.String(100), nullable=False)
    AppusageTime = db.Column(db.Integer, nullable=False)
    BatteryDrain = db.Column(db.Integer, nullable=False)
    ScreenOnTime_hours_per_day = db.Column(db.Integer, nullable=False)  # Column to store screen time in hours per day
    NumberofAppsInstalled = db.Column(db.Integer, nullable=False)
    DataUsage_MB_per_day = db.Column(db.Integer, nullable=False)  # Data usage per day in MB

    # ForeignKey to the User table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
