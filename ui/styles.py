"""
PulseShield Custom Cybersecurity Glassmorphism CSS Stylesheet
Dark navy/black aesthetic, cyan & electric blue accents, neon purple highlights,
glassmorphism cards, glowing status badges, and clean technical typography.
"""

CUSTOM_CSS = """
<style>
/* Import Cyberpunk / Tech Fonts */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-dark: #0A0E17;
    --bg-card: rgba(14, 23, 38, 0.75);
    --border-card: rgba(0, 240, 255, 0.18);
    --border-glow: 0 0 15px rgba(0, 240, 255, 0.25);
    --accent-cyan: #00F0FF;
    --accent-blue: #0066FF;
    --accent-purple: #A855F7;
    --accent-green: #10B981;
    --accent-red: #EF4444;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
}

/* Global Application Background */
.stApp {
    background-color: #0A0E17;
    background-image: 
        radial-gradient(circle at 15% 10%, rgba(0, 102, 255, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 85% 85%, rgba(168, 85, 247, 0.08) 0%, transparent 40%),
        linear-gradient(to bottom, #0A0E17, #070A10);
    color: #F8FAFC;
    font-family: 'Inter', -apple-system, sans-serif;
}

/* Headings & Tech Monospace */
h1, h2, h3, h4, h5, h6 {
    color: #F8FAFC !important;
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.mono-font {
    font-family: 'JetBrains Mono', monospace;
}

/* Glassmorphism Dashboard Cards */
.cyber-card {
    background: rgba(14, 23, 38, 0.65);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 240, 255, 0.16);
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.cyber-card:hover {
    border-color: rgba(0, 240, 255, 0.4);
    box-shadow: 0 8px 32px 0 rgba(0, 240, 255, 0.12);
}

.cyber-card-highlight {
    background: linear-gradient(135deg, rgba(14, 23, 38, 0.8), rgba(20, 35, 60, 0.7));
    border: 1px solid rgba(0, 240, 255, 0.35);
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.15);
}

/* Stat Metrics Card */
.stat-box {
    text-align: center;
    padding: 16px;
    background: rgba(10, 16, 28, 0.6);
    border: 1px solid rgba(0, 102, 255, 0.2);
    border-radius: 10px;
}

.stat-value {
    font-size: 2.2rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(90deg, #00F0FF, #A855F7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 0.82rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}

/* Glowing Status Badges */
.badge-cyan {
    background: rgba(0, 240, 255, 0.12);
    color: #00F0FF;
    border: 1px solid rgba(0, 240, 255, 0.4);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    display: inline-block;
}

.badge-green {
    background: rgba(16, 185, 129, 0.12);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    display: inline-block;
}

.badge-red {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.4);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    display: inline-block;
}

.badge-yellow {
    background: rgba(245, 158, 11, 0.15);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.4);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    display: inline-block;
}

/* PulseShield Navigation / Header Banner */
.ps-header {
    background: linear-gradient(90deg, rgba(0, 102, 255, 0.12), rgba(168, 85, 247, 0.12));
    border-bottom: 1px solid rgba(0, 240, 255, 0.25);
    padding: 24px 30px;
    border-radius: 12px;
    margin-bottom: 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.ps-logo-text {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #00F0FF 0%, #0066FF 50%, #A855F7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #080B12 !important;
    border-right: 1px solid rgba(0, 240, 255, 0.15) !important;
}

/* Streamlit Button Customization */
div.stButton > button {
    background: linear-gradient(135deg, #0066FF 0%, #00D4FF 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 8px 18px !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:hover {
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.5) !important;
    transform: translateY(-1px) !important;
}

/* Streamlit Tabs Customization */
button[data-baseweb="tab"] {
    background-color: transparent !important;
    color: #94A3B8 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid transparent !important;
}

button[aria-selected="true"] {
    color: #00F0FF !important;
    border-bottom: 2px solid #00F0FF !important;
}

/* Alert Boxes */
.stAlert {
    background-color: rgba(14, 23, 38, 0.8) !important;
    border: 1px solid rgba(0, 240, 255, 0.3) !important;
    border-radius: 8px !important;
}
</style>
"""
