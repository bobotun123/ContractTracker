from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
DATA_FILE = 'data.json'
NOTIFICATIONS_FILE = 'notifications.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_notifications():
    if os.path.exists(NOTIFICATIONS_FILE):
        try:
            with open(NOTIFICATIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_notifications(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Route to serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# API to get records
@app.route('/api/records', methods=['GET'])
def get_records():
    data = load_data()
    return jsonify(data)

# API to add a record
@app.route('/api/records', methods=['POST'])
def add_record():
    new_record = request.json
    data = load_data()
    data.append(new_record)
    save_data(data)
    return jsonify({"status": "success"}), 201

# API to delete a record
@app.route('/api/records/<int:index>', methods=['DELETE'])
def delete_record(index):
    data = load_data()
    if 0 <= index < len(data):
        data.pop(index)
        save_data(data)
        return jsonify({"status": "deleted"})
    return jsonify({"status": "error"}), 404

# API to get notifications
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    notifications = load_notifications()
    return jsonify(notifications)

# API to clear notifications
@app.route('/api/notifications/clear', methods=['DELETE'])
def clear_notifications():
    save_notifications([])
    return jsonify({"status": "cleared"}), 200

# Background notification checker - runs daily at 9:30 and 16:30
def check_daily_notifications():
    print("⏰ Daily notification checker started...")
    print("📅 Will check at 09:30 and 16:30 daily")
    print("📋 Will alert for contracts expiring within 60 days")
    
    while True:
        try:
            current_time = datetime.now()
            current_time_str = current_time.strftime("%H:%M")
            
            # Check for 9:30 and 16:30 notifications
            if current_time_str in ["09:30", "16:30"]:
                print(f"🔔 Running daily check at {current_time_str}")
                data = load_data()
                
                if not data:
                    print("📭 No records found in database")
                    time.sleep(60)
                    continue
                
                notifications = []
                overdue_notifications = []
                upcoming_notifications = []
                
                for entry in data:
                    days_left = get_days_diff(entry.get('nextYear', ''))
                    
                    # Alert for contracts within 60 days (2 months)
                    if days_left < 0:
                        overdue_notifications.append({
                            'no': entry.get('no', ''),
                            'name': entry.get('name', ''),
                            'contract_date': entry.get('contractDate', entry.get('signDate', '')),
                            'expiry_date': entry.get('nextYear', ''),
                            'days_left': days_left,
                            'message': f"CONTRACT OVERDUE by {abs(days_left)} days - PREPARE DOCUMENTATION IMMEDIATELY",
                            'type': 'overdue',
                            'action': 'IMMEDIATE ACTION REQUIRED'
                        })
                    elif days_left <= 60:
                        upcoming_notifications.append({
                            'no': entry.get('no', ''),
                            'name': entry.get('name', ''),
                            'contract_date': entry.get('contractDate', entry.get('signDate', '')),
                            'expiry_date': entry.get('nextYear', ''),
                            'days_left': days_left,
                            'message': f"CONTRACT EXPIRES in {days_left} days - PREPARE RENEWAL DOCUMENTS",
                            'type': 'upcoming',
                            'action': 'DOCUMENT PREPARATION REQUIRED'
                        })
                
                # Combine all notifications
                notifications = overdue_notifications + upcoming_notifications
                
                if notifications:
                    notification_data = {
                        'timestamp': current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        'notifications': notifications,
                        'total': len(notifications),
                        'overdue_count': len(overdue_notifications),
                        'upcoming_count': len(upcoming_notifications)
                    }
                    
                    existing_notifications = load_notifications()
                    existing_notifications.append(notification_data)
                    save_notifications(existing_notifications)
                    
                    print(f"✅ Daily notification saved at {current_time_str}")
                    print(f"📋 Found {len(notifications)} notifications:")
                    print(f"  ⚠️ Overdue: {len(overdue_notifications)}")
                    print(f"  ⏰ Upcoming (within 60 days): {len(upcoming_notifications)}")
                    
                    for notif in notifications:
                        print(f"  - [{notif['no']}] {notif['name']}: {notif['message']}")
                else:
                    print(f"✅ No notifications needed at {current_time_str} - All contracts have more than 60 days remaining")
                
                # Wait for 2 minutes to avoid duplicate checks
                time.sleep(120)
            
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            print(f"❌ Error in notification checker: {e}")
            time.sleep(60)

def get_days_diff(target_date_str):
    try:
        if not target_date_str:
            return 999
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        target = datetime.strptime(target_date_str, "%Y-%m-%d")
        diff = target - today
        return diff.days
    except Exception as e:
        print(f"⚠️ Date parsing error for '{target_date_str}': {e}")
        return 999

if __name__ == '__main__':
    # Start background thread for daily notifications
    notification_thread = threading.Thread(target=check_daily_notifications, daemon=True)
    notification_thread.start()
    
    print("🚀 Server running... Access via your PC IP address on port 5000")
    print("⏰ Daily notifications will be sent at 9:30 and 16:30")
    print("📋 Alerting for contracts expiring within 60 days (2 months)")
    print("📄 Focus: Document preparation and renewal reminders")
    print("📊 Check console for notification logs")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)