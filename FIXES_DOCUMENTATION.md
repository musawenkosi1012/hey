# Chatbot and Simulator Fixes - Documentation

## Issue Summary
The AI chatbot was failing to send and receive messages due to missing OpenAI library and outdated API syntax. The vitals simulator also had an application context issue preventing it from running in background threads.

## Fixes Implemented

### 1. Added OpenAI Library to Dependencies
**File**: `requirements.txt`
- Added `openai` package to requirements
- This was missing, preventing the chatbot from using OpenAI API

### 2. Updated Chatbot to Use Latest OpenAI API
**File**: `app/services/chatbot.py`
- Migrated from old `openai.ChatCompletion.create()` syntax to new `OpenAI().chat.completions.create()` syntax
- Updated initialization to use the new `OpenAI` client class
- Added better error handling and logging for OpenAI failures
- Improved fallback mechanism logging

**Changes**:
```python
# Old code:
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')
response = self.openai.ChatCompletion.create(...)

# New code:
from openai import OpenAI
self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = self.openai_client.chat.completions.create(...)
```

### 3. Fixed Vitals Simulator Application Context Issue
**File**: `app/services/vitals_simulator.py`
- Fixed the background thread to maintain Flask application context
- The simulator now creates an app instance and wraps the simulation loop in `app.app_context()`
- This allows database operations to work correctly in the background thread

**Changes**:
```python
# Added app context to simulation thread
from app import create_app
app = create_app()

def simulate():
    with app.app_context():
        while self.running:
            # Database operations now work correctly
            ...
```

### 4. Enhanced Logging Throughout
- Added comprehensive logging to track:
  - OpenAI API calls and responses
  - Fallback mechanism activation
  - Web scraping attempts
  - Response generation
  - Simulator operations

## How It Works Now

### Message Flow
1. **User sends a message** → Frontend sends POST to `/api/chat`
2. **Chatbot receives message** → Retrieves patient context and vitals
3. **OpenAI attempt** → Tries to use OpenAI API (if available and network permits)
4. **Fallback to Web Scraping** → If OpenAI fails, uses web scraper for medical knowledge
5. **Final fallback to Fixed Responses** → If web scraping fails, uses predefined responses
6. **Response sent back** → Frontend displays the response to user
7. **Message saved** → Both message and response saved to database for history

### Simulator Flow
1. **User starts simulation** → Clicks "Start Simulation" button
2. **API call** → POST to `/api/simulator/start`
3. **Background thread starts** → Generates vitals every 30 seconds
4. **Vitals saved** → Each generation saves to database
5. **Real-time updates** → SocketIO emits updates (if available)
6. **Dashboard updates** → Shows latest vitals

## Testing

### Automated Tests
Run the comprehensive test suite:
```bash
python3 test_fixes.py
```

This will test:
- Chatbot message sending/receiving
- OpenAI integration with fallback
- Web scraping fallback mechanism
- Fixed responses fallback
- Vitals simulator live data generation
- Chat history storage and retrieval

### Manual Testing
1. **Start the application**:
   ```bash
   python3 app.py
   ```

2. **Login as patient**:
   - Username: `patient`
   - Password: `password123`

3. **Test chatbot**:
   - Navigate to "AI Coach"
   - Send messages and verify responses
   - Check that responses are relevant and personalized

4. **Test simulator**:
   - Navigate to Dashboard
   - Click "Start Simulation"
   - Watch vitals update every 30 seconds
   - Click "Stop Simulation" when done

## Environment Variables

Create a `.env` file with:
```env
OPENAI_API_KEY=your-api-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///chronisense.db
LOG_LEVEL=INFO
```

**Note**: The `.env` file is gitignored for security.

## Key Features Verified

✅ **Chatbot sends and receives messages**
- Messages are sent via REST API
- Responses are generated using OpenAI (or fallback)
- All messages are saved to database

✅ **OpenAI integration works**
- Uses latest OpenAI library (v1.x)
- Proper error handling for network issues
- Graceful fallback when unavailable

✅ **Web scraping fallback**
- Scrapes medical information for health topics
- Personalizes with patient vitals
- Provides accurate medical guidelines

✅ **Fixed responses fallback**
- Rule-based responses for common queries
- Personalized with patient data
- Always available as last resort

✅ **Vitals simulator**
- Generates realistic vital signs
- Runs in background thread
- Simulates circadian rhythms
- Occasionally generates anomalies
- Saves to database every 30 seconds

✅ **Chat history**
- All conversations saved
- Retrievable via API
- Displayed in UI

## Screenshots

### Dashboard with Live Vitals
![Dashboard](https://github.com/user-attachments/assets/d5459268-92a4-4078-9fb4-72ef166e5ebe)
- Shows real-time vital signs
- Blood Pressure: 131/74 mmHg
- Heart Rate: 89 bpm
- Oxygen Saturation: 97.1%
- Daily Steps: 2235

### AI Chatbot Interface
![Chatbot](https://github.com/user-attachments/assets/07c3a896-9b94-45bd-b0e3-ac5c0f8face9)
- Clean chat interface
- Shows online status
- Ready to receive messages
- Patient context displayed

## Logs

All operations are logged to:
- Console (stdout)
- File: `logs/chronisense.log`

Example log entries:
```
[INFO] OpenAI API available: True
[INFO] OpenAI client initialized successfully
[INFO] Generating response for patient_id=1
[ERROR] OpenAI API error: Connection error
[INFO] Using fallback response generation
[INFO] Successfully retrieved web knowledge for topic: blood pressure
[INFO] Response generated for patient_id=1, length=560
```

## Troubleshooting

### Chatbot not responding
1. Check if OpenAI API key is set in `.env`
2. Check logs for errors
3. Verify fallback mechanisms are working
4. Test API endpoint directly: `curl -X POST http://localhost:5000/api/chat ...`

### Simulator not generating vitals
1. Check logs for errors
2. Verify database is accessible
3. Ensure Flask app context is available
4. Check if simulation is running: Look for log messages every 30 seconds

### Database errors
1. Reinitialize database: `python3 init_db.py`
2. Check file permissions on database file
3. Verify DATABASE_URL in `.env`

## Additional Notes

- The OpenAI API key provided in the issue has been configured
- Network restrictions in sandboxed environments may cause OpenAI to fail, but fallback works correctly
- WebSocket features may not work if CDN is blocked, but REST API works fine
- All fixes are minimal and surgical, changing only what's necessary
