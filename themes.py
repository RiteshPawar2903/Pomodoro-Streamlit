"""
Theme definitions and CSS styling for Zen Pomodoro Streamlit App.
Provides the 7 curated zen themes and flip clock animations.
Built according to IEEE Std 730/1016/12207 standards.
"""

THEMES = {
    "geometric-balance": {
        "name": "Geometric Balance",
        "bg_primary": "#F2F0EB",
        "bg_surface": "#FFFFFF",
        "bg_card_top": "#FAFAFA",
        "bg_card_bottom": "#FFFFFF",
        "text_primary": "#1A1A1A",
        "text_secondary": "#2C2C2C",
        "text_muted": "#6E6B65",
        "accent": "#2C2C2C",
        "border_color": "rgba(0, 0, 0, 0.12)",
        "hinge_color": "rgba(0, 0, 0, 0.08)",
        "shadow_card": "rgba(0, 0, 0, 0.08)",
    },
    "zen-dark": {
        "name": "Zen Dark",
        "bg_primary": "#0d0d0d",
        "bg_surface": "#171717",
        "bg_card_top": "#1e1e1e",
        "bg_card_bottom": "#191919",
        "text_primary": "#f5f5f5",
        "text_secondary": "#8a8a8a",
        "text_muted": "#525252",
        "accent": "#e5e5e5",
        "border_color": "#262626",
        "hinge_color": "#0d0d0d",
        "shadow_card": "rgba(0, 0, 0, 0.6)",
    },
    "obsidian": {
        "name": "Obsidian Black",
        "bg_primary": "#050505",
        "bg_surface": "#101010",
        "bg_card_top": "#141414",
        "bg_card_bottom": "#0f0f0f",
        "text_primary": "#ffffff",
        "text_secondary": "#737373",
        "text_muted": "#404040",
        "accent": "#fafafa",
        "border_color": "#1f1f1f",
        "hinge_color": "#050505",
        "shadow_card": "rgba(0, 0, 0, 0.85)",
    },
    "minimal-light": {
        "name": "Minimal Light",
        "bg_primary": "#f8f9fa",
        "bg_surface": "#ffffff",
        "bg_card_top": "#ffffff",
        "bg_card_bottom": "#f1f3f5",
        "text_primary": "#1a1a1a",
        "text_secondary": "#495057",
        "text_muted": "#6c757d",
        "accent": "#212529",
        "border_color": "#dee2e6",
        "hinge_color": "#ced4da",
        "shadow_card": "rgba(0, 0, 0, 0.08)",
    },
    "amber-glow": {
        "name": "Amber Glow",
        "bg_primary": "#120e0a",
        "bg_surface": "#1c1611",
        "bg_card_top": "#241d16",
        "bg_card_bottom": "#1e1712",
        "text_primary": "#ffeedb",
        "text_secondary": "#b89a80",
        "text_muted": "#755f4c",
        "accent": "#f59e0b",
        "border_color": "#33261b",
        "hinge_color": "#120e0a",
        "shadow_card": "rgba(0, 0, 0, 0.7)",
    },
    "forest-moss": {
        "name": "Forest Moss",
        "bg_primary": "#0a110e",
        "bg_surface": "#121c17",
        "bg_card_top": "#192720",
        "bg_card_bottom": "#14201a",
        "text_primary": "#e6f4ed",
        "text_secondary": "#8da89a",
        "text_muted": "#536e60",
        "accent": "#10b981",
        "border_color": "#20352b",
        "hinge_color": "#0a110e",
        "shadow_card": "rgba(0, 0, 0, 0.7)",
    },
    "midnight-indigo": {
        "name": "Midnight Indigo",
        "bg_primary": "#0b0e17",
        "bg_surface": "#121724",
        "bg_card_top": "#1a2133",
        "bg_card_bottom": "#151b2a",
        "text_primary": "#edf2f7",
        "text_secondary": "#8c9bb3",
        "text_muted": "#505e78",
        "accent": "#6366f1",
        "border_color": "#222b40",
        "hinge_color": "#0b0e17",
        "shadow_card": "rgba(0, 0, 0, 0.75)",
    },
}


def get_theme_css(theme_key: str = "geometric-balance") -> str:
    """Generate scoped CSS variables and styles based on active theme."""
    t = THEMES.get(theme_key, THEMES["geometric-balance"])

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Outfit:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {{
        --bg-primary: {t["bg_primary"]};
        --bg-surface: {t["bg_surface"]};
        --bg-card-top: {t["bg_card_top"]};
        --bg-card-bottom: {t["bg_card_bottom"]};
        --text-primary: {t["text_primary"]};
        --text-secondary: {t["text_secondary"]};
        --text-muted: {t["text_muted"]};
        --accent: {t["accent"]};
        --border-color: {t["border_color"]};
        --hinge-color: {t["hinge_color"]};
        --shadow-card: {t["shadow_card"]};
    }}

    .stApp {{
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Outfit', sans-serif !important;
    }}

    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* Global Typography Overrides - Ensures High Contrast & Visibility */
    .stApp,
    .stApp p,
    .stApp span:not(.zen-badge):not(.badge-urgent):not(.badge-high):not(.badge-medium):not(.badge-low),
    .stApp label,
    .stApp li,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMarkdownContainer"] em,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {{
        color: var(--text-primary) !important;
    }}

    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {{
        color: var(--text-primary) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }}

    /* Checkbox & Interactive Form Overrides (Fixes light theme invisibility) */
    [data-testid="stCheckbox"],
    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] p,
    [data-testid="stCheckbox"] span,
    [data-testid="stCheckbox"] div,
    [data-testid="stCheckbox"] [data-testid="stMarkdownContainer"] p,
    .stCheckbox,
    .stCheckbox label,
    .stCheckbox p,
    .stCheckbox span,
    label[data-baseweb="checkbox"],
    label[data-baseweb="checkbox"] p,
    label[data-baseweb="checkbox"] span {{
        color: var(--text-primary) !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
    }}

    /* Checkbox box aesthetics */
    [data-testid="stCheckbox"] [data-baseweb="checkbox"] [aria-checked="true"] {{
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
    }}

    [data-testid="stCheckbox"] [data-baseweb="checkbox"] [aria-checked="false"] {{
        background-color: var(--bg-surface) !important;
        border: 2px solid var(--border-color) !important;
    }}

    /* Global card containers */
    .zen-container {{
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 30px var(--shadow-card);
        margin-bottom: 20px;
        transition: all 0.2s ease;
    }}

    .zen-subcard {{
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }}

    /* Streamlit Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: var(--bg-surface);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid var(--border-color);
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 12px !important;
        padding: 8px 18px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.2s ease !important;
    }}

    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] div {{
        color: var(--text-muted) !important;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        box-shadow: 0 2px 8px var(--shadow-card) !important;
    }}

    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] div {{
        color: var(--text-primary) !important;
    }}

    /* Buttons Override */
    .stButton>button {{
        border-radius: 14px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: 0 2px 8px var(--shadow-card) !important;
        transition: all 0.2s ease !important;
    }}

    .stButton>button p,
    .stButton>button span {{
        color: var(--text-primary) !important;
    }}

    .stButton>button:hover {{
        border-color: var(--accent) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px var(--shadow-card) !important;
    }}

    .stButton>button[kind="primary"] {{
        background-color: var(--accent) !important;
        color: var(--bg-surface) !important;
        border-color: var(--accent) !important;
    }}

    .stButton>button[kind="primary"] p,
    .stButton>button[kind="primary"] span {{
        color: var(--bg-surface) !important;
    }}

    /* Form Inputs */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stNumberInput>div>div>input {{
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        font-family: 'Outfit', sans-serif !important;
    }}

    .stSelectbox>div>div {{
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
    }}

    .stSelectbox div[data-baseweb="select"] span,
    .stSelectbox div[data-baseweb="select"] div {{
        color: var(--text-primary) !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 14px !important;
    }}

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"],
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] p,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] span {{
        color: var(--text-primary) !important;
    }}

    /* Metrics */
    div[data-testid="stMetric"] {{
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 4px 16px var(--shadow-card);
    }}

    div[data-testid="stMetricLabel"] {{
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 13px !important;
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    div[data-testid="stMetricValue"] {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 28px !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }}

    /* Progress bar */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, var(--text-muted), var(--accent)) !important;
        border-radius: 9999px !important;
    }}

    /* Dataframe & Tables */
    [data-testid="stDataFrame"] {{
        color: var(--text-primary) !important;
    }}

    /* Badge styles */
    .zen-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.03em;
    }}

    .badge-urgent {{ background: rgba(239, 68, 68, 0.14); color: #ef4444 !important; border: 1px solid rgba(239, 68, 68, 0.3); }}
    .badge-high {{ background: rgba(245, 158, 11, 0.14); color: #f59e0b !important; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .badge-medium {{ background: rgba(59, 130, 246, 0.14); color: #3b82f6 !important; border: 1px solid rgba(59, 130, 246, 0.3); }}
    .badge-low {{ background: rgba(107, 114, 128, 0.14); color: #6b7280 !important; border: 1px solid rgba(107, 114, 128, 0.3); }}

    /* Animations */
    @keyframes pulse-gentle {{
        0% {{ transform: scale(0.98); opacity: 0.85; }}
        50% {{ transform: scale(1.03); opacity: 1; }}
        100% {{ transform: scale(0.98); opacity: 0.85; }}
    }}

    .breathe-sphere {{
        width: 140px;
        height: 140px;
        border-radius: 50%;
        margin: 20px auto;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        animation: pulse-gentle 4s infinite ease-in-out;
        box-shadow: 0 0 35px rgba(139, 92, 246, 0.25);
    }}
    </style>
    """
