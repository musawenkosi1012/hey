# Button to Backend Route Mapping Analysis

## Complete UI Button Inventory and Backend Route Mapping

This document provides a comprehensive analysis of all buttons and interactive elements in the ChroniSense application, mapped to their corresponding Flask backend routes.

---

## Summary Table

| Button/Element | Location | Label/Purpose | HTTP Method | Route/Endpoint | Handler Function | Description |
|---|---|---|---|---|---|---|
| 1 | index.html | "Get Started" | GET | `/auth/register` | `auth.register()` | Navigate to registration page |
| 2 | index.html | "Sign In" | GET | `/auth/login` | `auth.login()` | Navigate to login page |
| 3 | index.html | "Go to Dashboard" | GET | `/dashboard` or `/doctor/dashboard` | `main.patient_dashboard()` or `doctor.dashboard()` | Navigate to role-specific dashboard |
| 4 | index.html | "Join as Doctor" | GET | `/auth/register` | `auth.register()` | Navigate to registration with doctor role |
| 5 | index.html | "Start Your Journey" | GET | `/auth/register` | `auth.register()` | Navigate to registration page |
| 6 | login.html | "Sign in" (submit) | POST | `/auth/login` | `auth.login()` | Submit login credentials |
| 7 | login.html | "create a new account" | GET | `/auth/register` | `auth.register()` | Navigate to registration |
| 8 | register.html | "Create Account" (submit) | POST | `/auth/register` | `auth.register()` | Submit registration data |
| 9 | register.html | Role selection (Patient) | - | - | Client-side only | Select patient role |
| 10 | register.html | Role selection (Doctor) | - | - | Client-side only | Select doctor role |
| 11 | register.html | Role selection (Caregiver) | - | - | Client-side only | Select caregiver role |
| 12 | patient.html | "Start Simulation" | POST | `/api/simulator/start` | `api.start_simulator()` | Start vitals simulation |
| 13 | patient.html | "Stop Simulation" | POST | `/api/simulator/stop` | `api.stop_simulator()` | Stop vitals simulation |
| 14 | patient.html | Chart toggle "BP" | - | - | Client-side only | Switch chart to blood pressure view |
| 15 | patient.html | Chart toggle "HR" | - | - | Client-side only | Switch chart to heart rate view |
| 16 | patient.html | Chart toggle "SpO2" | - | - | Client-side only | Switch chart to oxygen saturation view |
| 17 | patient.html | "View All" (insights) | GET | `/electrobook` | `main.electrobook()` | Navigate to insights page |
| 18 | patient.html | "Start Chat" | GET | `/chatbot` | `main.chatbot_page()` | Navigate to chatbot page |
| 19 | patient.html | "View History" | GET | `/vitals` | `main.vitals_history()` | Navigate to vitals history |
| 20 | patient.html | "Call 911" | - | - | Client-side only | Emergency contact (non-functional demo) |
| 21 | patient.html | "Dismiss" (alert) | - | - | Client-side only | Dismiss alert modal |
| 22 | patient.html | "Contact Doctor" | - | - | Client-side only | Contact doctor (non-functional demo) |
| 23 | chat.html | Send message (submit) | POST | `/api/chat` | `api.chat_with_ai()` | Send message to AI chatbot |
| 24 | chat.html | Quick suggestion buttons | POST | `/api/chat` | `api.chat_with_ai()` | Send pre-defined question to AI |
| 25 | chat.html | "Clear History" | - | - | Client-side only | Clear local chat display |
| 26 | chat.html | "View Full Dashboard" | GET | `/dashboard` | `main.patient_dashboard()` | Navigate to dashboard |

---

## Detailed Button Analysis

### 1. Landing Page (index.html)

#### Navigation Buttons
- **"Get Started"** (line 19-22)
  - **Action**: Navigate to registration
  - **Route**: `GET /auth/register`
  - **Function**: `auth.register()`
  - **Logic**: Display registration form for new users

- **"Sign In"** (line 23-26)
  - **Action**: Navigate to login page
  - **Route**: `GET /auth/login`
  - **Function**: `auth.login()`
  - **Logic**: Display login form for existing users

- **"Go to Dashboard"** (line 28-31)
  - **Action**: Navigate to role-specific dashboard
  - **Routes**: `GET /dashboard` (patient) or `GET /doctor/dashboard` (doctor)
  - **Functions**: `main.patient_dashboard()` or `doctor.dashboard()`
  - **Logic**: Redirect authenticated users to their dashboard based on role

- **"Join as Doctor"** (line 165-168)
  - **Action**: Navigate to registration
  - **Route**: `GET /auth/register`
  - **Function**: `auth.register()`
  - **Logic**: Display registration form (can pre-select doctor role)

- **"Start Your Journey"** (line 183-186)
  - **Action**: Navigate to registration
  - **Route**: `GET /auth/register`
  - **Function**: `auth.register()`
  - **Logic**: Display registration form for new users

### 2. Authentication Pages

#### Login Page (login.html)

- **"Sign in" Submit Button** (line 54-60)
  - **Action**: Submit login credentials
  - **Route**: `POST /auth/login`
  - **Function**: `auth.login()`
  - **Logic**: 
    - Validate username and password
    - Check against database
    - Create user session
    - Redirect to appropriate dashboard

- **"create a new account" Link** (line 14-16)
  - **Action**: Navigate to registration
  - **Route**: `GET /auth/register`
  - **Function**: `auth.register()`
  - **Logic**: Display registration form

#### Registration Page (register.html)

- **"Create Account" Submit Button**
  - **Action**: Submit registration data
  - **Route**: `POST /auth/register`
  - **Function**: `auth.register()`
  - **Logic**:
    - Validate all form fields
    - Check username uniqueness
    - Hash password
    - Create user and patient/doctor profile
    - Redirect to login or dashboard

- **Role Selection Buttons** (Patient/Doctor/Caregiver)
  - **Action**: Select user role
  - **Type**: Client-side only
  - **Logic**: Update form field value for submission

### 3. Patient Dashboard (patient.html)

#### Simulation Controls

- **"Start Simulation" Button** (line 44-46)
  - **Action**: Start vitals simulation
  - **Route**: `POST /api/simulator/start`
  - **Function**: `api.start_simulator()`
  - **Request Body**: `{ patient_id: <id> }`
  - **Logic**:
    - Verify user authorization
    - Start simulator thread for patient
    - Begin generating vitals data
    - Return success response

- **"Stop Simulation" Button** (line 47-49)
  - **Action**: Stop vitals simulation
  - **Route**: `POST /api/simulator/stop`
  - **Function**: `api.stop_simulator()`
  - **Logic**:
    - Stop simulator thread
    - Cease vitals data generation
    - Return success response

#### Chart Controls

- **"BP" Chart Toggle** (line 145)
  - **Action**: Switch chart to blood pressure view
  - **Type**: Client-side only
  - **Logic**: Update chart display to show blood pressure data

- **"HR" Chart Toggle** (line 146)
  - **Action**: Switch chart to heart rate view
  - **Type**: Client-side only
  - **Logic**: Update chart display to show heart rate data

- **"SpO2" Chart Toggle** (line 147)
  - **Action**: Switch chart to oxygen saturation view
  - **Type**: Client-side only
  - **Logic**: Update chart display to show SpO2 data

#### Navigation Buttons

- **"View All" (Insights)** (line 159-161)
  - **Action**: Navigate to insights page
  - **Route**: `GET /electrobook`
  - **Function**: `main.electrobook()`
  - **Logic**: Display AI-generated health insights and reports

- **"Start Chat" Button** (line 192-195)
  - **Action**: Navigate to chatbot page
  - **Route**: `GET /chatbot`
  - **Function**: `main.chatbot_page()`
  - **Logic**: Display AI health coach chat interface

- **"View History" Button** (line 207-210)
  - **Action**: Navigate to vitals history
  - **Route**: `GET /vitals`
  - **Function**: `main.vitals_history()`
  - **Logic**: Display detailed vitals history with filtering options

- **"Call 911" Emergency Button** (line 222-225)
  - **Action**: Emergency contact (demo only)
  - **Type**: Client-side only
  - **Logic**: In production, would initiate emergency contact

#### Alert Modal Buttons

- **"Dismiss" Alert Button** (line 242-244)
  - **Action**: Close alert modal
  - **Type**: Client-side only
  - **Logic**: Hide alert modal from view

- **"Contact Doctor" Button** (line 245-247)
  - **Action**: Contact doctor (demo only)
  - **Type**: Client-side only
  - **Logic**: In production, would notify assigned doctor

### 4. Chatbot Page (chat.html)

#### Message Sending

- **Send Message Button** (line 118-120)
  - **Action**: Send message to AI chatbot
  - **Route**: `POST /api/chat`
  - **Function**: `api.chat_with_ai()`
  - **Request Body**: `{ message: <text>, session_id: <id> }`
  - **Logic**:
    - Validate message content
    - Get patient context (vitals, conditions)
    - Generate AI response using OpenAI or fallback
    - Save chat message to database
    - Return response with timestamp

#### Quick Suggestions

- **Suggestion Buttons** (Dynamic, line 211-214)
  - **Action**: Send pre-defined question
  - **Route**: `POST /api/chat`
  - **Function**: `api.chat_with_ai()`
  - **Logic**: Same as send message, but with pre-filled text

#### History Management

- **"Clear History" Button** (line 171-173)
  - **Action**: Clear chat history display
  - **Type**: Client-side only
  - **Logic**: Remove chat messages from DOM, reset session

- **"View Full Dashboard" Link** (line 158-160)
  - **Action**: Navigate to dashboard
  - **Route**: `GET /dashboard`
  - **Function**: `main.patient_dashboard()`
  - **Logic**: Return to patient dashboard

---

## API Endpoints Summary

### Authentication Routes (`/auth`)

| Endpoint | Method | Function | Purpose |
|---|---|---|---|
| `/auth/login` | GET | `auth.login()` | Display login form |
| `/auth/login` | POST | `auth.login()` | Process login credentials |
| `/auth/register` | GET | `auth.register()` | Display registration form |
| `/auth/register` | POST | `auth.register()` | Process registration data |
| `/auth/logout` | GET | `auth.logout()` | Log out user |

### Main Routes (`/`)

| Endpoint | Method | Function | Purpose |
|---|---|---|---|
| `/` | GET | `main.index()` | Landing page |
| `/dashboard` | GET | `main.patient_dashboard()` | Patient dashboard |
| `/chatbot` | GET | `main.chatbot_page()` | Chatbot interface |
| `/electrobook` | GET | `main.electrobook()` | Health insights |
| `/vitals` | GET | `main.vitals_history()` | Vitals history |

### API Routes (`/api`)

| Endpoint | Method | Function | Purpose |
|---|---|---|---|
| `/api/vitals/<patient_id>` | GET | `api.get_vitals()` | Retrieve vitals data |
| `/api/vitals` | POST | `api.ingest_vitals()` | Ingest vitals from devices |
| `/api/chat` | POST | `api.chat_with_ai()` | Send message to AI chatbot |
| `/api/chat/history` | GET | `api.get_chat_history()` | Get chat history |
| `/api/chat/suggestions` | GET | `api.get_chat_suggestions()` | Get quick response suggestions |
| `/api/simulator/start` | POST | `api.start_simulator()` | Start vitals simulation |
| `/api/simulator/stop` | POST | `api.stop_simulator()` | Stop vitals simulation |
| `/api/simulator/inject-anomaly` | POST | `api.inject_anomaly()` | Inject test anomaly |

---

## WebSocket Events

| Event | Direction | Purpose |
|---|---|---|
| `vitals_update` | Server → Client | Real-time vitals updates |
| `critical_alert` | Server → Client | Critical health alerts |
| `connect` | Client → Server | Establish connection |
| `disconnect` | Client → Server | Close connection |

---

## Implementation Status

✅ **Fully Implemented**
- All authentication routes
- Patient dashboard and navigation
- Vitals API endpoints
- Chatbot API endpoints
- Simulator controls
- Real-time WebSocket updates

🔄 **Partially Implemented**
- Emergency contact functionality (demo only)
- Doctor contact functionality (demo only)
- Password reset functionality (placeholder)

📋 **Recommended Additions**
- Profile update endpoints
- Settings management
- Notification preferences
- Export health data
- Share data with providers

---

## Notes

1. **Security**: All patient-specific routes require `@login_required` decorator
2. **Authorization**: Routes check user roles before allowing access
3. **Real-time**: WebSocket used for live vitals updates
4. **Client-side**: Some buttons are client-side only for UI interactions
5. **Demo Features**: Emergency and doctor contact are placeholders for demo purposes

---

*Last Updated: 2024*
*Document Version: 1.0*
