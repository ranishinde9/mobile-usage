from flask import Flask, render_template, request, redirect, jsonify

from sqlalchemy.orm import aliased

from flask_sqlalchemy import SQLAlchemy  # Add this import for SQLAlchemy
from utils.db import db
from models.data import Mobile, User

# Initialize Flask app
flask_app = Flask(__name__)

# Set up the database URI and other configurations
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional: Disable modification tracking for performance

# Initialize database
db.init_app(flask_app)

# Home route
@flask_app.route('/')
def index():
    data = Mobile.query.all()
    return render_template('index.html', content=data)

# Help page
@flask_app.route('/help')
def help():
    return render_template('help.html')

# Add data page
@flask_app.route('/add_data')
def add_data():
    return render_template('add_data.html')

# Explore data page with filtering


# Inside your explore route, when applying filters:
@flask_app.route('/explore', methods=['GET', 'POST'])
def explore():
    # Fetch all distinct device models from the Mobile table
    device_models = db.session.query(Mobile.DeviceModel).distinct().all()
    device_models = [device[0] for device in device_models]  # Convert to list of device model names

    age_filter = request.args.get('age')
    gender_filter = request.args.get('gender')
    os_filter = request.args.get('os')
    device_filter = request.args.get('device')

    # Start with all data
    query = Mobile.query.join(User, User.id == Mobile.user_id)

    # Apply filters if selected
    if age_filter:
        age_range = age_filter.split('-')
        if len(age_range) == 2:
            query = query.filter(User.age >= int(age_range[0]), User.age <= int(age_range[1]))
        elif age_filter == '45+':
            query = query.filter(User.age >= 45)

    if gender_filter:
        query = query.filter(User.gender == gender_filter)

    if os_filter:
        query = query.filter(Mobile.OperatingSystem == os_filter)

    if device_filter:
        query = query.filter(Mobile.DeviceModel == device_filter)

    # Execute the query
    data = query.all()

    # Return the filtered data with device models for the filter dropdown
    return render_template('explore.html', content2=data, devices=device_models)

# Update data route
@flask_app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    data = Mobile.query.get_or_404(id)
    if not data:
        return jsonify({'message': 'task not found'}), 404

    if request.method == 'POST':
        data.user.id = request.form['id']
        data.user.age = request.form['age']
        data.user.gender = request.form['gender']
        data.user.UserBehaviorClass = request.form['UserBehaviorClass']
        data.DeviceModel = request.form['DeviceModel']
        data.OperatingSystem = request.form['OperatingSystem']
        data.AppusageTime = request.form['AppusageTime']
        data.BatteryDrain = request.form['BatteryDrain']
        data.ScreenOnTime_hours_per_day = request.form['ScreenOnTime_hours_per_day']
        data.NumberofAppsInstalled = request.form['NumberofAppsInstalled']
        data.DataUsage_MB_per_day = request.form['DataUsage_MB_per_day']

        try:
            db.session.commit()
            return redirect('/explore')
        except Exception as e:
            db.session.rollback()
            return "There is an issue while updating the record"
    return render_template('update.html', data=data)

# Delete data route
@flask_app.route('/delete/<int:id>', methods=['GET', 'DELETE'])
def delete(id):
    data = Mobile.query.get(id)
    if not data:
        return jsonify({'message': 'task not found'}), 404
    try:
        db.session.delete(data)
        db.session.commit()
        return jsonify({'message': 'task deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred while deleting the data: {e}'}), 500

# About Us page
@flask_app.route('/about_us')
def about_us():
    return render_template('about_us.html')

# Submit form data
@flask_app.route('/submit', methods=['POST'])
def submit():
    form_data = request.form.to_dict()

    age = form_data.get('age')
    gender = form_data.get('gender')
    user_behavior_class = form_data.get('UserBehaviorClass')

    device_model = form_data.get('DeviceModel')
    operating_system = form_data.get('OperatingSystem')
    app_usage_time = form_data.get('AppusageTime')
    battery_drain = form_data.get('BatteryDrain')
    screen_on_time = form_data.get('ScreenOnTime_hours_per_day')
    num_apps_installed = form_data.get('NumberofAppsInstalled')
    data_usage = form_data.get('DataUsage_MB_per_day')

    # Check if user exists
    user = User.query.filter_by(age=age).first()
    if not user:
        user = User(age=age, gender=gender, UserBehaviorClass=user_behavior_class)
        db.session.add(user)
        db.session.commit()

    # Add mobile data
    data = Mobile(
        DeviceModel=device_model,
        OperatingSystem=operating_system,
        AppusageTime=app_usage_time,
        BatteryDrain=battery_drain,
        ScreenOnTime_hours_per_day=screen_on_time,
        NumberofAppsInstalled=num_apps_installed,
        DataUsage_MB_per_day=data_usage,
        user_id=user.id
    )
    db.session.add(data)
    db.session.commit()

    return redirect('/')

# Graphs route
@flask_app.route('/graphs')
def graphs():
    # Query the data needed for graphs (Assuming you have models defined for User and Mobile)
    mobile_data = Mobile.query.all()
    user_data = User.query.all()

    # Process the data for visualization
    graph_data = {
        'gender_distribution': {
            'Male': sum(1 for user in user_data if user.gender == 'Male'),
            'Female': sum(1 for user in user_data if user.gender == 'Female')
        },
        'age_groups': {
            '18-24': sum(1 for user in user_data if 18 <= user.age <= 24),
            '25-34': sum(1 for user in user_data if 25 <= user.age <= 34),
            '35-44': sum(1 for user in user_data if 35 <= user.age <= 44),
            '45+': sum(1 for user in user_data if user.age >= 45)
        },
        'app_usage': {
            'App A': 5,
            'App B': 10,
            'App C': 7
        },
        'os_distribution': {
            'Android': sum(1 for mobile in mobile_data if mobile.OperatingSystem == 'Android'),
            'iOS': sum(1 for mobile in mobile_data if mobile.OperatingSystem == 'iOS')
        },
        'social_media_usage': {
            'Facebook': 40,
            'Instagram': 30,
            'Twitter': 20,
            'Snapchat': 10
        },
        'device_usage': {
            'Mobile': 60,
            'Tablet': 20,
            'Desktop': 10,
            'Others': 10
        },
        'app_downloads': {
            'App A': 1500,
            'App B': 2000,
            'App C': 1200
        },
        'user_activity': {
            'Active': 80,
            'Inactive': 20
        },
        'monthly_spending': {
            'Less than $10': 40,
            '$10 - $50': 35,
            '$50 - $100': 15,
            'Above $100': 10
        },
        'education_usage': {
            'E-Learning': 50,
            'Courses': 30,
            'Certification': 20
        },
        'product_satisfaction': {
            'Very Satisfied': 60,
            'Satisfied': 25,
            'Neutral': 10,
            'Dissatisfied': 5
        },
        'device_models': {
            'Model A': 30,
            'Model B': 50,
            'Model C': 20
        }
    }

    # Pass the graph data to the template
    return render_template('graphs.html', graph_data=graph_data)

# Initialize database and create tables
with flask_app.app_context():
    db.create_all()

# Run the Flask app
if __name__ == '__main__':
    flask_app.run( debug=True)
