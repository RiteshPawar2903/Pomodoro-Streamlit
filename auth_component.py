"""
Firebase Authentication Component for Streamlit.
Provides Google OAuth popup login and session management using the official Firebase Web SDK (v10).
Conforms to IEEE Std 730/1016 standards.
"""

from __future__ import annotations

import json
from typing import Optional
from config import CONFIG
from models import UserProfile
from themes import THEMES


def render_firebase_auth_button(
    user: Optional[UserProfile] = None,
    theme_key: str = "geometric-balance",
) -> str:
    """Render client-side Firebase Google Sign-In / User Profile widget."""
    t = THEMES.get(theme_key, THEMES["geometric-balance"])
    fb_config = CONFIG.get_firebase_config()
    fb_config_json = json.dumps(fb_config)

    user_dict = {
        "uid": user.uid,
        "email": user.email,
        "displayName": user.displayName,
        "photoURL": user.photoURL,
    } if user else None
    user_json = json.dumps(user_dict)

    html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    user-select: none;
}}

body {{
    background: transparent;
    font-family: 'Space Grotesk', sans-serif;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    height: 100%;
    overflow: hidden;
}}

.auth-wrapper {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
}}

.google-signin-btn {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: {t["bg_surface"]};
    color: {t["text_primary"]};
    border: 1px solid {t["border_color"]};
    border-radius: 12px;
    padding: 7px 14px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 2px 8px {t["shadow_card"]};
    transition: all 0.2s ease;
}}

.google-signin-btn:hover {{
    transform: translateY(-1px);
    border-color: {t["accent"]};
    box-shadow: 0 4px 12px {t["shadow_card"]};
}}

.user-profile-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: {t["bg_surface"]};
    border: 1px solid {t["border_color"]};
    border-radius: 12px;
    padding: 4px 12px 4px 6px;
    font-size: 12px;
    color: {t["text_primary"]};
    box-shadow: 0 2px 8px {t["shadow_card"]};
}}

.user-avatar {{
    width: 24px;
    height: 24px;
    border-radius: 50%;
    object-fit: cover;
    border: 1px solid {t["border_color"]};
}}

.user-avatar-initials {{
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: {t["accent"]};
    color: {t["bg_surface"]};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 11px;
}}

.signout-btn {{
    background: transparent;
    border: none;
    color: {t["text_muted"]};
    cursor: pointer;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 6px;
    transition: all 0.2s ease;
    margin-left: 4px;
}}

.signout-btn:hover {{
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
}}
</style>
</head>
<body>

<div class="auth-wrapper" id="auth-app">
    <!-- Populated by JavaScript -->
</div>

<script type="module">
import {{ initializeApp, getApps, getApp }} from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js';
import {{ getAuth, GoogleAuthProvider, signInWithPopup, signOut }} from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js';

const firebaseConfig = {fb_config_json};
const currentUser = {user_json};
const container = document.getElementById('auth-app');

if (!firebaseConfig.projectId || !firebaseConfig.apiKey) {{
    container.innerHTML = `
        <div style="font-size: 11px; padding: 4px 10px; border-radius: 9999px; background: rgba(245, 158, 11, 0.12); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.35); font-weight: 600; display: inline-flex; align-items: center; gap: 5px; cursor: help;" title="Add your new Firebase Project configuration in firebase-config.json or secrets.toml to enable Google Sign-In">
            <span>⚙️</span> Connect Firebase
        </div>
    `;
}} else {{
    let app;
    try {{
        app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();
    }} catch (e) {{
        console.error("Firebase init error:", e);
    }}

    const auth = getAuth(app);
    const googleProvider = new GoogleAuthProvider();
    googleProvider.setCustomParameters({{ prompt: 'select_account' }});

    function render() {{
        container.innerHTML = '';

        if (currentUser) {{
            const profileDiv = document.createElement('div');
            profileDiv.className = 'user-profile-badge';

            const nameShort = (currentUser.displayName || currentUser.email || 'User').split(' ')[0];

            if (currentUser.photoURL) {{
                profileDiv.innerHTML = `
                    <img src="${{currentUser.photoURL}}" class="user-avatar" alt="Avatar" referrerpolicy="no-referrer" />
                    <span style="font-weight:600;">${{nameShort}}</span>
                    <button class="signout-btn" id="btn-signout" title="Sign Out">Sign Out</button>
                `;
            }} else {{
                const initial = (currentUser.displayName || currentUser.email || 'U')[0].toUpperCase();
                profileDiv.innerHTML = `
                    <div class="user-avatar-initials">${{initial}}</div>
                    <span style="font-weight:600;">${{nameShort}}</span>
                    <button class="signout-btn" id="btn-signout" title="Sign Out">Sign Out</button>
                `;
            }}

            container.appendChild(profileDiv);

            document.getElementById('btn-signout').onclick = async () => {{
                try {{
                    await signOut(auth);
                }} catch(e) {{}}
                if (window.parent && window.parent.location) {{
                    window.parent.location.search = '?auth_action=logout';
                }}
            }};
        }} else {{
            const loginBtn = document.createElement('button');
            loginBtn.className = 'google-signin-btn';
            loginBtn.innerHTML = `
                <svg viewBox="0 0 24 24" width="16" height="16">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                </svg>
                <span>Sign in with Google</span>
            `;
            loginBtn.onclick = async () => {{
                try {{
                    loginBtn.innerHTML = '<span>Connecting...</span>';
                    const result = await signInWithPopup(auth, googleProvider);
                    const u = result.user;
                    const search = `?auth_action=login&uid=${{encodeURIComponent(u.uid)}}&email=${{encodeURIComponent(u.email || '')}}&name=${{encodeURIComponent(u.displayName || '')}}&photo=${{encodeURIComponent(u.photoURL || '')}}`;
                    if (window.parent && window.parent.location) {{
                        window.parent.location.search = search;
                    }}
                }} catch(err) {{
                    console.error("Sign-in error:", err);
                    const frameHost = window.location.hostname || "unknown";
                    let parentHost = frameHost;
                    try {{
                        if (window.parent && window.parent.location) {{
                            parentHost = window.parent.location.hostname;
                        }}
                    }} catch(e) {{
                        parentHost = "cross-origin-frame";
                    }}

                    if (err.code === 'auth/unauthorized-domain') {{
                        alert(
                            "Firebase Error: auth/unauthorized-domain\\n\\n" +
                            "Firebase rejected the domain from which the popup was opened.\\n\\n" +
                            "• Iframe Hostname: " + frameHost + "\\n" +
                            "• Parent Hostname: " + parentHost + "\\n" +
                            "• Active Project ID: " + (firebaseConfig.projectId || 'EMPTY') + "\\n" +
                            "• Auth Domain: " + (firebaseConfig.authDomain || 'EMPTY') + "\\n\\n" +
                            "How to fix in Firebase Console:\\n" +
                            "1. Open Firebase Console -> Authentication -> Settings -> Authorized domains\\n" +
                            "2. Ensure '" + frameHost + "' is added (bare domain name only: no https:// and no port numbers)\\n" +
                            (parentHost !== frameHost && parentHost !== "cross-origin-frame" ? "3. Also ensure '" + parentHost + "' is added.\\n" : "") +
                            "3. In Streamlit Secrets, verify authDomain is set to '" + (firebaseConfig.projectId || 'project-id') + ".firebaseapp.com'"
                        );
                    }} else {{
                        alert("Google Sign-In note: " + (err.message || err));
                    }}
                    render();
                }}
            }};
            container.appendChild(loginBtn);
        }}
    }}

    render();
}}
</script>
</body>
</html>
    """
    return html_code
