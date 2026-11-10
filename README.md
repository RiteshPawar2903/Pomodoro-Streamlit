# Zen Flip Focus — Python Streamlit Edition

A faithful, aesthetic Python Streamlit rewrite of the **Zen-Style Pomodoro Clock**, delivering the full Geometric Balance design language, 3D flip card clock aesthetic, multi-phase cognitive learning cycles, and task KPI analytics.

---

## 🌟 Key Features

1. **Zen 3D Flip Clock & Soundscapes**:
   - Split-flap visual layout matching typography from *JetBrains Mono* and *Space Grotesk*.
   - Web Audio API browser sound synthesis for bells, singing bowls, gongs, and warm brown noise.

2. **Dual Cycle Protocol**:
   - **Classic Pomodoro**: 25m Focus &bull; 5m Short Break &bull; 15m Long Break (after 4 cycles).
   - **Cognitive Mastery Protocol (4-Step Learning Cycle)**:
     - *Phase 1*: Mental Visualization & Box Breathing (2 min)
     - *Phase 2*: Deep Focus Execution (20 min)
     - *Phase 3*: Active Recall & Retrieval Flashcards (3 min)
     - *Phase 4*: Diffuse Mode Relaxation & 20-20-20 Rule (5 min)

3. **Task & Performance KPI Dashboard**:
   - Priority and category task allocation.
   - Task velocity tracking and estimation calibration accuracy (Spot-on vs Over/Under-estimates).
   - Session logging with instant CSV export.

4. **Curated Themes**:
   - `Geometric Balance` (Paper light)
   - `Zen Dark`
   - `Obsidian Black`
   - `Minimal Light`
   - `Amber Glow`
   - `Forest Moss`
   - `Midnight Indigo`

---

## 🚀 Quickstart

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run Application
```bash
streamlit run app.py
```

### 3. Run Unit Tests
```bash
python -m unittest tests/test_zen_pomodoro.py
```

## Firebase Google Sign-In

The app uses Firebase Authentication with Google as the provider. Enable Google
under **Firebase Console -> Authentication -> Sign-in method**, and add the
local/deployed hostname under **Authorized domains**.

Create `.streamlit/secrets.toml` locally or add the same values to Streamlit
Cloud Secrets:

```toml
[firebase]
projectId = "your-firebase-project-id"
apiKey = "your-web-api-key"
authDomain = "your-firebase-project-id.firebaseapp.com"
appId = "your-firebase-app-id"

[firebase_service_account]
type = "service_account"
project_id = "your-firebase-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-...@your-firebase-project-id.iam.gserviceaccount.com"
client_id = "..."
```

The browser signs in with Firebase and sends an ID token to the app. The
server verifies that token with the Firebase Admin SDK before creating the
Streamlit user session. Never commit `secrets.toml` or the service-account
private key.
