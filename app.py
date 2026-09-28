from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Sample users database
users_db = {
    'admin': {'password': 'admin123', 'role': 'admin', 'name': 'Admin User'},
    'user': {'password': 'user123', 'role': 'user', 'name': 'Regular User'}
}

class User(UserMixin):
    def __init__(self, username, role, name):
        self.id = username
        self.role = role
        self.name = name

@login_manager.user_loader
def load_user(username):
    if username in users_db:
        return User(username, users_db[username]['role'], users_db[username]['name'])
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if username in users_db and users_db[username]['password'] == password:
            user = User(username, users_db[username]['role'], users_db[username]['name'])
            login_user(user)
            return jsonify({'success': True, 'role': user.role})
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/land')
@login_required
def land():
    return render_template('land.html', user=current_user)

@app.route('/house')
@login_required
def house():
    return render_template('house.html', user=current_user)

@app.route('/survey')
@login_required
def survey():
    return render_template('survey.html', user=current_user)

@app.route('/road')
@login_required
def road():
    return render_template('road.html', user=current_user)


@app.route('/weather')
@login_required
def weather():
    return render_template('weather.html', user=current_user)






# API Endpoints
@app.route('/api/wards')
@login_required
def get_wards():
    wards = [{'id': i, 'name': f'Ward {i}'} for i in range(1, 21)]
    return jsonify(wards)

@app.route('/api/parcels')
@login_required
def get_parcels():
    try:
        data_path = os.path.join(app.static_folder, 'data', 'land_parcels.geojson')
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                return jsonify(json.load(f))
    except:
        pass
    return jsonify(generate_sample_parcels())

@app.route('/api/parcel/search')
@login_required
def search_parcel():
    kitta_no = request.args.get('kitta_no')
    parcels = get_parcels().get_json()
    
    if kitta_no:
        filtered = [f for f in parcels['features'] 
                   if f['properties'].get('kitta_no') == kitta_no]
        return jsonify({'type': 'FeatureCollection', 'features': filtered})
    
    return jsonify(parcels)

@app.route('/api/parcel/filter')
@login_required
def filter_parcel():
    ward = request.args.get('ward')
    parcels = get_parcels().get_json()
    
    if ward:
        filtered = [f for f in parcels['features'] 
                   if str(f['properties'].get('ward')) == ward]
        return jsonify({'type': 'FeatureCollection', 'features': filtered})
    
    return jsonify(parcels)

@app.route('/api/houses')
@login_required
def get_houses():
    try:
        data_path = os.path.join(app.static_folder, 'data', 'houses.geojson')
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                return jsonify(json.load(f))
    except:
        pass
    return jsonify(generate_sample_houses())

@app.route('/api/surveys')
@login_required
def get_surveys():
    try:
        data_path = os.path.join(app.static_folder, 'data', 'surveys.geojson')
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                return jsonify(json.load(f))
    except:
        pass
    return jsonify(generate_sample_surveys())

@app.route('/api/roads')
@login_required
def get_roads():
    print("\n" + "="*50)
    print("ROADS API ENDPOINT CALLED")
    print("="*50)
    
    try:
        # Build file path
        data_path = os.path.join(app.static_folder, 'data', 'roads.geojson')
        print(f"Looking for file at: {data_path}")
        print(f"File exists: {os.path.exists(data_path)}")
        
        if os.path.exists(data_path):
            print("✓ File found! Reading...")
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✓ Loaded {len(data.get('features', []))} features")
                print("="*50 + "\n")
                return jsonify(data)
        else:
            print("✗ File NOT found")
            print("  Using sample/fallback data")
            print("="*50 + "\n")
    except Exception as e:
        print(f"✗ ERROR reading file: {str(e)}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("="*50 + "\n")
    
    # Return sample data
    return jsonify(generate_sample_roads())

def generate_sample_parcels():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "kitta_no": "1001",
                    "ward": "1",
                    "land_use": "Residential",
                    "area": "500 sq.m",
                    "owner": "Ram Prasad",
                    "zone": "Residential"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [87.2718, 26.4525],
                        [87.2725, 26.4525],
                        [87.2725, 26.4530],
                        [87.2718, 26.4530],
                        [87.2718, 26.4525]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "kitta_no": "1002",
                    "ward": "1",
                    "land_use": "Commercial",
                    "area": "800 sq.m",
                    "owner": "Shyam Enterprises",
                    "zone": "Commercial"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [87.2725, 26.4525],
                        [87.2732, 26.4525],
                        [87.2732, 26.4532],
                        [87.2725, 26.4532],
                        [87.2725, 26.4525]
                    ]]
                }
            }
        ]
    }

def generate_sample_houses():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "house_no": "H-001",
                    "ward": "1",
                    "street": "Main Road",
                    "owner": "Krishna Sharma",
                    "floors": "2"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [87.2720, 26.4527]
                }
            }
        ]
    }

def generate_sample_surveys():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "survey_id": "S-001",
                    "date": "2025-01-15",
                    "surveyor": "GIS Team",
                    "status": "Completed"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [87.2728, 26.4528]
                }
            }
        ]
    }

def generate_sample_roads():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "road_name": "Main Road",
                    "road_type": "Primary",
                    "width": "12m",
                    "status": "Paved"
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [87.2715, 26.4520],
                        [87.2735, 26.4535]
                    ]
                }
            }
        ]
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)