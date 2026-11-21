"""
PulseShield UI View: Security Notifications & Threat Alerts
"""

import streamlit as st
from database import get_alerts, mark_all_alerts_read, mark_alert_read, add_alert

def render_notifications_view():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2>Security Monitoring & Threat Notifications</h2>
        <p style="color: #94A3B8;">
            Audit real-time incident logs, unauthorized facial scraping attempts,
            and rPPG biometric signal desynchronization alerts.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2, col_filter = st.columns([1, 1, 2])
    with col_btn1:
        if st.button("Mark All as Read"):
            mark_all_alerts_read()
            st.rerun()
    with col_btn2:
        if st.button("Generate Test Alert"):
            add_alert("WARNING", "Synthetic Face Scan Probe", "External IP triggered deepfake scan matching against registered identity.")
            st.rerun()
    with col_filter:
        sev_filter = st.selectbox("Severity Filter", ["All", "CRITICAL", "WARNING", "INFO"])

    unread_only = st.checkbox("Show unread notifications only", value=False)

    alerts = get_alerts(unread_only=unread_only, limit=50)
    if sev_filter != "All":
        alerts = [a for a in alerts if a["severity"] == sev_filter]

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    if alerts:
        for alert in alerts:
            aid = alert["id"]
            sev = alert["severity"]
            badge_class = "badge-red" if sev == "CRITICAL" else ("badge-yellow" if sev == "WARNING" else "badge-cyan")
            border_col = "#EF4444" if sev == "CRITICAL" else ("#F59E0B" if sev == "WARNING" else "#00F0FF")
            is_read = alert["is_read"]

            col_card, col_action = st.columns([6, 1])
            with col_card:
                st.markdown(f"""
                <div style="background: rgba(14, 23, 38, {0.4 if is_read else 0.85}); border-left: 4px solid {border_col}; border: 1px solid rgba(255, 255, 255, {0.05 if is_read else 0.15}); padding: 14px 20px; border-radius: 8px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: 700; color: #F8FAFC; font-size: 0.95rem;">{alert['title']}</span>
                        <div>
                            <span class="{badge_class}">{sev}</span>
                            {'<span style="color: #64748B; font-size: 0.75rem; margin-left: 8px;">READ</span>' if is_read else '<span style="color: #10B981; font-size: 0.75rem; margin-left: 8px; font-weight: 600;">NEW</span>'}
                        </div>
                    </div>
                    <div style="color: #CBD5E1; font-size: 0.88rem; line-height: 1.4;">{alert['message']}</div>
                    <div style="color: #64748B; font-size: 0.75rem; margin-top: 6px; font-family: monospace;">Logged at: {alert['created_at']} (Incident #{aid})</div>
                </div>
                """, unsafe_allow_html=True)
            with col_action:
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                if not is_read:
                    if st.button("Dismiss", key=f"btn_read_{aid}"):
                        mark_alert_read(aid)
                        st.rerun()
    else:
        st.info("No matching security alerts found.")
