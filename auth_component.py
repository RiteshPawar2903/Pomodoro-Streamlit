"""Firebase Authentication UI for Streamlit."""

from __future__ import annotations

import json
from typing import Optional

from config import CONFIG
from models import UserProfile
from themes import THEMES


def _safe_json(value: object) -> str:
    """Keep JSON embedded in a script tag from terminating that script."""
    return json.dumps(value).replace("<", "\\u003c").replace(">", "\\u003e")


def render_firebase_auth_button(
    user: Optional[UserProfile] = None,
    theme_key: str = "geometric-balance",
) -> str:
    """Render Firebase Google and email/password authentication controls."""
    theme = THEMES.get(theme_key, THEMES["geometric-balance"])
    firebase_config = _safe_json(CONFIG.get_firebase_config())
    current_user = _safe_json(
        {
            "uid": user.uid,
            "email": user.email,
            "displayName": user.displayName,
            "photoURL": user.photoURL,
        }
        if user
        else None
    )

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: transparent; font-family: 'Space Grotesk', sans-serif; display: flex; justify-content: flex-end; align-items: center; height: 100%; overflow: hidden; }}
.auth-wrapper {{ display: flex; align-items: center; gap: 8px; }}
button, input {{ font: inherit; }}
button {{ cursor: pointer; }}
.auth-btn {{ display: inline-flex; align-items: center; justify-content: center; gap: 7px; background: {theme["bg_surface"]}; color: {theme["text_primary"]}; border: 1px solid {theme["border_color"]}; border-radius: 10px; padding: 8px 12px; font-size: 12px; font-weight: 600; box-shadow: 0 2px 8px {theme["shadow_card"]}; }}
.auth-btn:hover {{ border-color: {theme["accent"]}; transform: translateY(-1px); }}
.email-panel {{ display: flex; align-items: center; gap: 6px; }}
.email-panel input {{ width: 145px; padding: 8px 9px; border: 1px solid {theme["border_color"]}; border-radius: 8px; background: {theme["bg_surface"]}; color: {theme["text_primary"]}; outline: none; font-size: 11px; }}
.email-panel input:focus {{ border-color: {theme["accent"]}; }}
.status {{ color: {theme["text_muted"]}; font-size: 11px; max-width: 180px; }}
.error {{ color: #dc2626; }}
.profile {{ display: inline-flex; align-items: center; gap: 8px; padding: 5px 10px 5px 6px; border: 1px solid {theme["border_color"]}; border-radius: 10px; background: {theme["bg_surface"]}; color: {theme["text_primary"]}; font-size: 12px; }}
.avatar {{ width: 24px; height: 24px; border-radius: 50%; object-fit: cover; background: {theme["accent"]}; color: {theme["bg_surface"]}; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; }}
.signout {{ border: 0; background: transparent; color: {theme["text_muted"]}; font-size: 11px; }}
</style>
</head>
<body>
<div class="auth-wrapper" id="auth-app"></div>
<script type="module">
import {{ initializeApp, getApps, getApp }} from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js';
import {{ getAuth, GoogleAuthProvider, signInWithPopup, signInWithEmailAndPassword, signOut }} from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js';

const firebaseConfig = {firebase_config};
const currentUser = {current_user};
const container = document.getElementById('auth-app');

function redirectWithToken(token) {{
    const url = new URL(window.parent.location.href);
    url.search = '';
    url.searchParams.set('auth_action', 'login');
    url.searchParams.set('auth_token', token);
    window.parent.location.href = url.toString();
}}

function showError(error) {{
    const message = {{
        'auth/invalid-credential': 'Email or password is incorrect.',
        'auth/invalid-email': 'Enter a valid email address.',
        'auth/user-not-found': 'No account exists for this email.',
        'auth/wrong-password': 'Email or password is incorrect.',
        'auth/email-already-in-use': 'An account already exists for this email.',
        'auth/unauthorized-domain': 'This app domain is not authorized in Firebase.',
    }}[error.code] || 'Unable to sign in. Please try again.';
    let status = container.querySelector('.status');
    if (!status) {{
        status = document.createElement('span');
        container.appendChild(status);
    }}
    status.textContent = message;
    status.className = 'status error';
}}

if (!firebaseConfig.projectId || !firebaseConfig.apiKey) {{
    container.innerHTML = '<span class="status">Sign-in is currently unavailable.</span>';
}} else {{
    let app;
    try {{
        app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();
    }} catch (error) {{
        container.innerHTML = '<span class="status error">Unable to initialize sign-in.</span>';
        console.error(error);
    }}

    if (app) {{
        const auth = getAuth(app);
        const googleProvider = new GoogleAuthProvider();
        googleProvider.setCustomParameters({{ prompt: 'select_account' }});

        function render() {{
            container.innerHTML = '';
            if (currentUser) {{
                const profile = document.createElement('div');
                profile.className = 'profile';
                const avatar = document.createElement(currentUser.photoURL ? 'img' : 'span');
                avatar.className = 'avatar';
                if (currentUser.photoURL) {{
                    avatar.src = currentUser.photoURL;
                    avatar.alt = 'Profile';
                }} else {{
                    avatar.textContent = (currentUser.displayName || currentUser.email || 'U')[0].toUpperCase();
                }}
                const name = document.createElement('strong');
                name.textContent = (currentUser.displayName || currentUser.email || 'User').split(' ')[0];
                const logout = document.createElement('button');
                logout.className = 'signout';
                logout.textContent = 'Sign out';
                logout.onclick = async () => {{
                    await signOut(auth);
                    const url = new URL(window.parent.location.href);
                    url.search = '?auth_action=logout';
                    window.parent.location.href = url.toString();
                }};
                profile.append(avatar, name, logout);
                container.appendChild(profile);
                return;
            }}

            const google = document.createElement('button');
            google.className = 'auth-btn';
            google.textContent = 'Continue with Google';
            google.onclick = async () => {{
                google.disabled = true;
                google.textContent = 'Connecting...';
                try {{
                    const result = await signInWithPopup(auth, googleProvider);
                    redirectWithToken(await result.user.getIdToken());
                }} catch (error) {{
                    google.disabled = false;
                    google.textContent = 'Continue with Google';
                    showError(error);
                }}
            }};

            const email = document.createElement('button');
            email.className = 'auth-btn';
            email.textContent = 'Use email';
            email.onclick = () => renderEmailForm();
            container.append(google, email);
        }}

        function renderEmailForm() {{
            container.innerHTML = `
                <div class="email-panel">
                    <input id="email" type="email" placeholder="Email" autocomplete="email">
                    <input id="password" type="password" placeholder="Password" autocomplete="current-password">
                    <button class="auth-btn" id="submit">Sign in</button>
                    <button class="auth-btn" id="back">Back</button>
                </div>
                <span class="status"></span>
            `;
            const submit = document.getElementById('submit');
            submit.onclick = async () => {{
                const emailValue = document.getElementById('email').value.trim();
                const passwordValue = document.getElementById('password').value;
                submit.disabled = true;
                try {{
                    const result = await signInWithEmailAndPassword(auth, emailValue, passwordValue);
                    redirectWithToken(await result.user.getIdToken());
                }} catch (error) {{
                    submit.disabled = false;
                    showError(error);
                }}
            }};
            document.getElementById('back').onclick = render;
        }}

        render();
    }}
}}
</script>
</body>
</html>
"""
