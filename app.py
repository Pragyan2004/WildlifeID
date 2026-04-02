import os
import numpy as np
import pickle
import tensorflow as tf
from tensorflow.keras.applications.efficientnet_v2 import preprocess_input
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
from PIL import Image
import io
import base64
from datetime import datetime
import json
import uuid
from dotenv import load_dotenv

load_dotenv()


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_PATH, 'static', 'uploads')
HISTORY_FOLDER = os.path.join(BASE_PATH, 'data') 
HISTORY_FILE = os.path.join(HISTORY_FOLDER, 'prediction_history.json')
USERS_FILE = os.path.join(HISTORY_FOLDER, 'users.json')
MODEL_PATH = os.path.join(BASE_PATH, 'saved_models', 'best_model.keras')
PICKLE_PATH = os.path.join(BASE_PATH, 'OpenAnimalTracks', 'pickle_files')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HISTORY_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'wildlife-id-clinical-2026')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['FIREBASE_API_KEY'] = os.getenv('FIREBASE_API_KEY')
app.config['FIREBASE_AUTH_DOMAIN'] = os.getenv('FIREBASE_AUTH_DOMAIN')
app.config['FIREBASE_PROJECT_ID'] = os.getenv('FIREBASE_PROJECT_ID')
app.config['FIREBASE_STORAGE_BUCKET'] = os.getenv('FIREBASE_STORAGE_BUCKET')
app.config['FIREBASE_MESSAGING_SENDER_ID'] = os.getenv('FIREBASE_MESSAGING_SENDER_ID')
app.config['FIREBASE_APP_ID'] = os.getenv('FIREBASE_APP_ID')
app.config['FIREBASE_MEASUREMENT_ID'] = os.getenv('FIREBASE_MEASUREMENT_ID')

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        users = load_data(USERS_FILE)
        
        user = next((u for u in users if u['email'] == email), None)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash('Successfully logged in!', 'success')
            return redirect(url_for('home'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        users = load_data(USERS_FILE)
        if any(u['email'] == email for u in users):
            flash('Email already registered.', 'danger')
        else:
            new_user = {
                'id': str(uuid.uuid4()),
                'name': name,
                'email': email,
                'password': generate_password_hash(password)
            }
            users.append(new_user)
            save_data(USERS_FILE, users)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))



class AnimalFootprintPreprocessor:
    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        self.class_names = None

    def transform(self, image):
        if isinstance(image, str):
            img = cv2.imread(image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img = image.copy()
        img = cv2.resize(img, self.target_size)
        img = preprocess_input(img.astype(np.float32))
        return np.expand_dims(img, axis=0)

    def predict(self, model, image):
        processed_img = self.transform(image)
        predictions = model.predict(processed_img, verbose=0)
        top_idx = np.argmax(predictions[0])
        species = self.class_names[top_idx]
        confidence = float(predictions[0][top_idx])

        species_images = {
            "arctic_fox": "https://images.unsplash.com/photo-1506929199175-632057ead603?auto=format&fit=crop&q=80&w=600",
            "beaver": "https://images.unsplash.com/photo-1579169837555-c549646452e4?auto=format&fit=crop&q=80&w=600",
            "black_bear": "https://images.unsplash.com/photo-1530595467537-0b5996c148a0?auto=format&fit=crop&q=80&w=600",
            "bob_cat": "https://images.unsplash.com/photo-1511216335778-7cb8f49fa7a3?auto=format&fit=crop&q=80&w=600",
            "coyote": "https://images.unsplash.com/photo-1549480017-d76466a4b7e8?auto=format&fit=crop&q=80&w=600",
            "elephant": "https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?auto=format&fit=crop&q=80&w=600",
            "goose": "https://images.unsplash.com/photo-1539721972319-f0e80a00d424?auto=format&fit=crop&q=80&w=600",
            "gray_fox": "https://images.unsplash.com/photo-1474511320721-9a6ee39b3531?auto=format&fit=crop&q=80&w=600",
            "horse": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?auto=format&fit=crop&q=80&w=600",
            "lion": "https://images.unsplash.com/photo-1614027126733-75806b64f9ec?auto=format&fit=crop&q=80&w=600",
            "mink": "https://images.unsplash.com/photo-1546182208-99c195ee540a?auto=format&fit=crop&q=80&w=600",
            "mouse": "https://images.unsplash.com/photo-1425082661705-1834bfd09dca?auto=format&fit=crop&q=80&w=600",
            "muledeer": "https://images.unsplash.com/photo-1484406566174-9da000fda645?auto=format&fit=crop&q=80&w=600",
            "otter": "https://images.unsplash.com/photo-1544473244-f689025ec686?auto=format&fit=crop&q=80&w=600",
            "raccoon": "https://images.unsplash.com/photo-1497206339976-f683076cd523?auto=format&fit=crop&q=80&w=600",
            "rat": "https://images.unsplash.com/photo-1554555122-832145326588?auto=format&fit=crop&q=80&w=600",
            "skunk": "https://images.unsplash.com/photo-1535941339361-efd17579e05f?auto=format&fit=crop&q=80&w=600",
            "turkey": "https://images.unsplash.com/photo-1518398046578-8cca57782e17?auto=format&fit=crop&q=80&w=600",
            "western_grey_squirrel": "https://images.unsplash.com/photo-1507333589414-2f228f74b90c?auto=format&fit=crop&q=80&w=600"
        }
        
        species_key = species.lower().replace(" ", "_")
        reference_image = species_images.get(species_key, "https://images.unsplash.com/photo-1546182208-99c195ee540a?auto=format&fit=crop&q=80&w=600")

        return {
            'success': True,
            'prediction': species,
            'confidence': confidence,
            'reference_image': reference_image,
            'top_class': species,
            'top_confidence': confidence,
            'predictions': [{'class': species, 'confidence': confidence}],
            'all_probabilities': {self.class_names[i]: float(predictions[0][i]) for i in range(len(self.class_names))}
        }

model = None
class_names = None
preprocessor = None
model_metadata = None



def load_artifacts():
    """Load model, class names, and preprocessor"""
    global model, class_names, preprocessor, model_metadata
    
    print("🔄 Loading model and artifacts...")
    
    if os.path.exists(MODEL_PATH):
        try:
            model = tf.keras.models.load_model(MODEL_PATH, compile=False)
            print(f"✅ Model loaded from {MODEL_PATH}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    else:
        print(f"❌ Model not found at {MODEL_PATH}")
        return False
    
    class_names_path = os.path.join(PICKLE_PATH, 'class_names.pkl')
    if os.path.exists(class_names_path):
        with open(class_names_path, 'rb') as f:
            class_names = pickle.load(f)
        print(f"✅ Class names loaded: {len(class_names)} classes")
    else:
        print(f"❌ Class names not found")
        return False
    
    preprocessor_path = os.path.join(PICKLE_PATH, 'footprint_preprocessor.pkl')
    if os.path.exists(preprocessor_path):
        with open(preprocessor_path, 'rb') as f:
            preprocessor = pickle.load(f)
        print(f"✅ Preprocessor loaded")
    else:
        print(f"❌ Preprocessor not found")
        return False
    
    metadata_path = os.path.join(PICKLE_PATH, 'model_metadata.pkl')
    if os.path.exists(metadata_path):
        with open(metadata_path, 'rb') as f:
            model_metadata = pickle.load(f)
        print(f"✅ Model metadata loaded")
    
    return True


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_prediction_history(image_path, result, filename):
    """Save prediction history to JSON file"""
    history_entry = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'filename': filename,
        'original_path': image_path,
        'prediction': result['top_class'],
        'confidence': result['top_confidence'],
        'top_3_predictions': result['predictions'],
        'all_probabilities': result['all_probabilities']
    }
    
    history_file = os.path.join(HISTORY_FOLDER, 'prediction_history.json')
    
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    else:
        history = []
    
    history.append(history_entry)
    
    if len(history) > 100:
        history = history[-100:]
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    return history_entry

def get_prediction_history(limit=20):
    """Get prediction history"""
    history_file = os.path.join(HISTORY_FOLDER, 'prediction_history.json')
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
        return history[-limit:]
    return []

def clear_prediction_history():
    """Clear prediction history"""
    history_file = os.path.join(HISTORY_FOLDER, 'prediction_history.json')
    if os.path.exists(history_file):
        os.remove(history_file)
    return True

def delete_prediction_record(prediction_id):
    """Delete a specific prediction record by ID"""
    history_file = os.path.join(HISTORY_FOLDER, 'prediction_history.json')
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        updated_history = [p for p in history if p.get('id') != prediction_id]
        
        if len(updated_history) < len(history):
            with open(history_file, 'w') as f:
                json.dump(updated_history, f, indent=2)
            return True
    return False


@app.route('/')
def home():
    """Home page with upload form"""
    return render_template('home.html', 
                         class_names=class_names,
                         total_classes=len(class_names) if class_names else 0,
                         current_year=datetime.now().year)

@app.route('/about')
def about():
    """About page with project information"""
    return render_template('about.html',
                         current_year=datetime.now().year,
                         model_info=model_metadata)

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html',
                         current_year=datetime.now().year)

@app.route('/history')
def history():
    """History page showing previous predictions"""
    if not session.get('user_id'):
        flash('Please login to access the history vault.', 'info')
        return redirect(url_for('login'))
        
    predictions = get_prediction_history(50)
    return render_template('history.html',
                         predictions=predictions,
                         current_year=datetime.now().year)

@app.route('/dashboard')
def dashboard():
    """Dashboard with model performance metrics"""
    if not session.get('user_id'):
        flash('Please login to access the intelligence dashboard.', 'info')
        return redirect(url_for('login'))
        
    predictions = get_prediction_history(100)
    
    total_predictions = len(predictions)
    
    if total_predictions > 0:
        class_counts = {}
        confidence_sum = 0
        
        for pred in predictions:
            pred_class = pred['prediction']
            class_counts[pred_class] = class_counts.get(pred_class, 0) + 1
            confidence_sum += pred['confidence']
        
        avg_confidence = confidence_sum / total_predictions
        most_common_class = max(class_counts.items(), key=lambda x: x[1]) if class_counts else ('None', 0)
    else:
        class_counts = {}
        avg_confidence = 0
        most_common_class = ('None', 0)
    
    return render_template('dashboard.html',
                         total_predictions=total_predictions,
                         avg_confidence=avg_confidence,
                         most_common_class=most_common_class[0],
                         most_common_count=most_common_class[1],
                         class_counts=class_counts,
                         current_year=datetime.now().year)

@app.route('/model-info')
def model_info():
    """Model information page"""
    return render_template('model_info.html',
                         model_info=model_metadata,
                         class_names=class_names,
                         total_classes=len(class_names) if class_names else 0,
                         current_year=datetime.now().year)

@app.route('/faq')
def faq():
    """FAQ page"""
    return render_template('faq.html',
                         current_year=datetime.now().year)


@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for prediction"""
    if not session.get('user_id'):
        return jsonify({'error': 'Authentication required for diagnostic access.'}), 401

    if 'file' not in request.files:
        flash('No file provided', 'error')
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        flash('File type not allowed', 'error')
        return jsonify({'error': f'File type not allowed. Allowed: {ALLOWED_EXTENSIONS}'}), 400
    
    try:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        result = preprocessor.predict(model, filepath)
        
        result['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result['filename'] = filename
        
        save_prediction_history(filepath, result, filename)
        
        os.remove(filepath)
        
        flash('Prediction successful!', 'success')
        return jsonify(result)
        
    except Exception as e:
        flash(f'Error during prediction: {str(e)}', 'error')
        return jsonify({'error': str(e)}), 500

@app.route('/predict-base64', methods=['POST'])
def predict_base64():
    """API endpoint for base64 encoded images"""
    data = request.get_json()
    
    if 'image' not in data:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        image_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
        image = Image.open(io.BytesIO(image_data))
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_{timestamp}.jpg')
        image.save(temp_path)
        
        result = preprocessor.predict(model, temp_path)
        
        os.remove(temp_path)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def api_history():
    """API endpoint to get prediction history"""
    limit = request.args.get('limit', default=20, type=int)
    history = get_prediction_history(limit)
    return jsonify({
        'success': True,
        'total': len(history),
        'history': history
    })

@app.route('/api/history/delete/<prediction_id>', methods=['DELETE'])
def api_history_delete(prediction_id):
    """API endpoint to delete a specific prediction record"""
    try:
        if delete_prediction_record(prediction_id):
            return jsonify({'success': True, 'message': 'Record deleted successfully'})
        return jsonify({'success': False, 'message': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history/clear', methods=['POST'])
def api_history_clear():
    """API endpoint to clear prediction history"""
    try:
        clear_prediction_history()
        return jsonify({'success': True, 'message': 'History cleared successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None,
        'classes': len(class_names) if class_names else 0,
        'preprocessor_loaded': preprocessor is not None
    })

@app.route('/api/model-info')
def api_model_info():
    """API endpoint for model information"""
    return jsonify({
        'success': True,
        'model_info': model_metadata,
        'class_names': class_names,
        'total_classes': len(class_names) if class_names else 0
    })


@app.errorhandler(404)
def page_not_found(e):
    """404 error handler"""
    return render_template('404.html',
                         current_year=datetime.now().year), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500 error handler"""
    return render_template('500.html',
                         current_year=datetime.now().year), 500

@app.errorhandler(413)
def too_large(e):
    """413 error handler - file too large"""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413


if __name__ == '__main__':
    if load_artifacts():
        print("\n" + "="*60)
        print("🚀 ANIMAL FOOTPRINT CLASSIFIER - FLASK APP")
        print("="*60)
        print(f"📍 Model: {MODEL_PATH}")
        print(f"📍 Classes: {len(class_names)} animal species")
        print(f"📍 Upload folder: {UPLOAD_FOLDER}")
        print(f"📍 History folder: {HISTORY_FOLDER}")
        print("\n📌 Available Pages:")
        print("   - GET  /              : Home page")
        print("   - GET  /about         : About page")
        print("   - GET  /contact       : Contact page")
        print("   - GET  /history       : Prediction history")
        print("   - GET  /dashboard     : Analytics dashboard")
        print("   - GET  /model-info    : Model information")
        print("   - GET  /faq           : FAQ page")
        print("\n📌 API Endpoints:")
        print("   - POST /predict       : Image file prediction")
        print("   - POST /predict-base64 : Base64 image prediction")
        print("   - GET  /api/history   : Get prediction history")
        print("   - POST /api/history/clear : Clear history")
        print("   - GET  /api/health    : Health check")
        print("   - GET  /api/model-info : Model information")
        print("\n" + "="*60)
        print("✅ Server starting on http://localhost:5000")
        print("="*60)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("\n❌ Failed to load model. Please check:")
        print(f"   - Model path: {MODEL_PATH}")
        print(f"   - Pickle path: {PICKLE_PATH}")
        print("\n💡 Run the training notebook first to generate model files!")