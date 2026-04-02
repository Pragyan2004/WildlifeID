# 🐾 WildlifeID: AI-Powered Animal Footprint Intelligence

[![Gunicorn](https://img.shields.io/badge/Server-Gunicorn-5851db.svg)](https://gunicorn.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/Engine-TensorFlow_2.x-orange.svg)](https://tensorflow.org/)
[![Clinical UI](https://img.shields.io/badge/Aesthetic-Clinical_Glassmorphism-2ecc71.svg)](#)

WildlifeID is a high-precision neural diagnostic platform designed for conservationists, field researchers, and wildlife biologists. The system utilizes state-of-the-art computer vision to identify animal species non-invasively through footprint pattern analysis.

## 🌟 Key Features

*   **Neural Identification Hub**: Gated access to an EfficientNetV2-L powered classification engine.
*   **19+ Supported Species**: From Arctic Foxes to Lions, covering a wide range of global biodiversity.
*   **Clinical Research Dashboard**: Real-time telemetry, confidence metrics, and species distribution analytics.
*   **Identification Vault**: Secure, persistent storage of historical field captures and diagnostic reports.
*   **Advanced SEO & Social Sharing**: Fully optimized with Open Graph and Twitter metadata for professional visibility.
*   **Secure Authentication**: Role-based access control to maintain project integrity and data security.

## 🔬 Tech Stack

*   **Backend**: Flask (Python), Gunicorn (Production WSGI)
*   **Deep Learning**: TensorFlow, Keras (EfficientNetV2-L)
*   **Image Processing**: OpenCV, Pillow
*   **Frontend**: Vanilla JS, Bootstrap 5, Animate.css
*   **Persistence**: Local JSON-based storage with UUID tracking
*   **Deployment**: Procfile-ready for cloud environments

## 🚀 Quick Start

### 1. Prerequisite Setup
Ensure you have Python 3.9+ installed.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Pragyan2004/WildlifeID.git
cd WildlifeID

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secure-secret-key-2026
FIREBASE_API_KEY=your-api-key
# ... add other Firebase/Environmental variables
```

### 4. Running the Application
**Development:**
```bash
python app.py
```

**Production (Recommended):**
```bash
gunicorn app:app
```

## Dataset

```
https://www.kaggle.com/datasets/antoreepjana/animals-detection-images-dataset
```


## 📂 Project Structure

*   `/static`: Hardware-accelerated CSS, JS, and clinical image assets.
*   `/templates`: High-end Jinja2 templates with optimized SEO hierarchy.
*   `/data`: Secure storage for the Identification Vault and User records.
*   `app.py`: The central intelligence and routing core.
*   `Procfile`: Standarized startup command for production environments.

## 🛡️ Security
The platform implements a gated access model. The **Identification Hub** is protected by a session-based lock, requiring valid researcher credentials to access the neural diagnostic tools and historical archives.

## 📜 License
Professional research edition. Distributed for conservation and educational purposes.

---
*Developed with a focus on clinical precision and wildlife conservation.*
