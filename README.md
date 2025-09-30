# ChroniSense - AI-Powered Health Monitoring System

ChroniSense is an AI-powered health monitoring and coaching system designed for chronic condition patients (hypertension, diabetes, stroke recovery). It combines real-time vitals simulation, AI health coaching, and personalized insights to provide comprehensive health management.

## 🚀 Features

### Core Components

1. **Vitals Simulator**
   - Continuous heart rate, blood pressure, SpO₂, steps, and sleep data generation
   - Realistic circadian rhythm patterns
   - Anomaly injection for testing health alerts

2. **Flask WebApp**
   - RESTful API endpoints for data ingestion and retrieval
   - WebSocket/Socket.IO for real-time updates
   - Responsive, mobile-friendly interface

3. **AI Health Coach Chatbot**
   - English conversation with patients
   - Access to real-time patient vitals
   - Personalized lifestyle tips, diet guidance, and exercise recommendations
   - On-demand health reports generation

4. **Electro-book Insights**
   - AI-generated daily and weekly health summaries
   - Personalized insights for patients
   - Doctor portal for reviewing insights and raw data

5. **Machine Learning Engine**
   - Risk prediction for complications (6h, 24h, 72h)
   - Anomaly detection from vitals trends
   - Explainable insights

6. **Notification & Escalation System**
   - Real-time alerts for patients and caregivers
   - Doctor escalation for critical thresholds

## 🏥 User Roles

### Patient Features
- **AI Chatbot Coach**: Chat interface for health questions and advice
- **Real-time Dashboard**: Live vitals monitoring with interactive charts
- **Electro-book**: Daily and weekly AI-generated health reports
- **Alerts**: Critical warnings with recommendations
- **Vitals History**: Detailed trends and patterns

### Doctor Features
- **Patient Management**: Overview of all patients with health status
- **Real-time Monitoring**: Live patient vitals and alerts
- **AI Insights**: Access to patient electro-book reports
- **Risk Assessment**: ML-powered risk predictions

### Caregiver Features
- **Alert Notifications**: Receive critical patient alerts
- **Summary Reports**: Weekly patient updates

## 🛠 Tech Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **Flask-SocketIO** - Real-time communications
- **Flask-Login** - User authentication
- **OpenAI API** - AI chatbot capabilities

### Frontend
- **Tailwind CSS** - Modern styling
- **Chart.js** - Interactive data visualizations
- **Font Awesome** - Icons
- **Socket.IO Client** - Real-time updates

### Database
- **SQLite** (development) / **PostgreSQL** (production)

### Machine Learning
- **scikit-learn** - Risk prediction models
- **pandas/numpy** - Data processing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Node.js (optional, for additional frontend tools)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/musawenkosi1012/hey.git
   cd hey
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**
   ```bash
   python init_db.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser to `http://localhost:5000`

### Demo Accounts

The system comes with pre-configured demo accounts:

- **Patient**: `username: patient`, `password: password123`
- **Doctor**: `username: doctor`, `password: password123`
- **Caregiver**: `username: caregiver`, `password: password123`

## 📱 Usage

### For Patients

1. **Dashboard**: View real-time vitals, daily stats, and health trends
2. **AI Coach**: Chat with the AI health coach for personalized advice
3. **Insights**: Read daily and weekly AI-generated health reports
4. **Vitals History**: Explore detailed health data over time

### For Doctors

1. **Patient Management**: Monitor multiple patients from a single dashboard
2. **Individual Patient View**: Deep dive into specific patient data
3. **Alert Management**: Respond to critical patient alerts
4. **Reports**: Access comprehensive patient insights

### Starting Vitals Simulation

1. Log in as a patient
2. Go to the dashboard
3. Click "Start Simulation" to begin generating realistic vitals data
4. Watch real-time updates on charts and vitals cards

### Standalone Vitals Demonstration

To showcase the system's monitoring capabilities without running the full web application:

**Production Mode (5-minute intervals):**
```bash
python simulate_vitals.py
```

**Demo Mode (5-second intervals for quick demonstration):**
```bash
python simulate_vitals_demo.py
```

These standalone scripts demonstrate:
- Real-time vitals collection and monitoring
- Intelligent analysis with alert detection
- Continuous display of health metrics
- System intelligence in action

Press `Ctrl+C` to stop the simulation.

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///chronisense.db
OPENAI_API_KEY=your-openai-api-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

### OpenAI API Setup

To enable the AI chatbot:

1. Get an OpenAI API key from https://platform.openai.com/
2. Add it to your `.env` file as `OPENAI_API_KEY`
3. The chatbot will automatically use GPT-3.5-turbo for responses

## 🏗 Architecture

### Data Flow

1. **Simulator → Flask API**: Continuous vitals data generation
2. **Aggregator Worker**: Builds time windows (5-15 min)
3. **ML Service**: Predicts risks and stores in database
4. **AI Coach**: Accesses database for vitals and generates responses
5. **Electro-book Generator**: Creates daily/weekly insights
6. **Frontend**: Real-time dashboard and chatbot interface

### Database Schema

- **Users**: Authentication and role management
- **Patients**: Patient profiles and medical information
- **VitalSigns**: Time-series vitals data
- **PatientInsights**: AI-generated reports and insights
- **ChatMessages**: Conversation history with AI coach
- **RiskPredictions**: ML-generated risk assessments

## 🧪 Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/
flake8 app/
```

### Database Migrations
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🔮 Roadmap

### Phase 1 (Weeks 1-4): Core Setup ✅
- Flask app with vitals simulator
- Basic dashboard and API endpoints

### Phase 2 (Weeks 5-8): Electro-book MVP
- Daily/weekly AI insights
- Doctor dashboard for viewing reports

### Phase 3 (Weeks 9-12): AI Chatbot Coach ✅
- English chatbot with vitals integration
- Lifestyle and diet recommendations

### Phase 4 (Weeks 13-16): Full Integration
- Advanced alerts and escalation
- Mobile-responsive design polish
- Pilot testing

## 📊 Features Implemented

- [x] Real-time vitals simulation
- [x] Patient dashboard with live charts
- [x] AI chatbot health coach
- [x] User authentication (patient/doctor/caregiver)
- [x] WebSocket real-time updates
- [x] Responsive UI with Tailwind CSS
- [x] Database models and relationships
- [x] Basic insights system
- [x] Demo data and user accounts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact: support@chronisense.com

## 🙏 Acknowledgments

- OpenAI for GPT-3.5 API
- Chart.js for beautiful visualizations
- Tailwind CSS for modern styling
- Flask ecosystem for robust backend

---

**ChroniSense** - Empowering patients and healthcare providers with AI-driven health insights.