import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Data file paths
DATA_FILE = 'data.json'
NOTIFICATIONS_FILE = 'notifications.json'

# Initialize session state
def init_session_state():
    if 'entries' not in st.session_state:
        st.session_state.entries = load_data()
    if 'notifications' not in st.session_state:
        st.session_state.notifications = load_notifications()
    if 'filter' not in st.session_state:
        st.session_state.filter = 'all'
    if 'show_notifications' not in st.session_state:
        st.session_state.show_notifications = False

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    st.session_state.entries = data

def load_notifications():
    if os.path.exists(NOTIFICATIONS_FILE):
        try:
            with open(NOTIFICATIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_notifications(data):
    with open(NOTIFICATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    st.session_state.notifications = data

def get_days_diff(target_date_str):
    try:
        if not target_date_str:
            return 999
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        target = datetime.strptime(target_date_str, "%Y-%m-%d")
        diff = target - today
        return diff.days
    except Exception as e:
        return 999

def get_status_info(days_left):
    if days_left < 0:
        return "Overdue", "🔴", "overdue"
    elif days_left <= 60:
        return f"Expiring ({days_left}d)", "🟡", "warning"
    else:
        return f"Active ({days_left}d)", "🟢", "active"

def check_notifications_manual():
    """Manually check notifications and save them"""
    entries = load_data()
    if not entries:
        st.info("📭 No contracts found. Add some contracts first!")
        return False
    
    notifications = []
    overdue_notifications = []
    upcoming_notifications = []
    
    for entry in entries:
        days_left = get_days_diff(entry.get('nextYear', ''))
        
        if days_left < 0:
            overdue_notifications.append({
                'no': entry.get('no', ''),
                'name': entry.get('name', ''),
                'contract_date': entry.get('contractDate', entry.get('signDate', '')),
                'expiry_date': entry.get('nextYear', ''),
                'days_left': days_left,
                'message': f"CONTRACT OVERDUE by {abs(days_left)} days - PREPARE DOCUMENTATION IMMEDIATELY",
                'type': 'overdue',
                'action': 'IMMEDIATE ACTION REQUIRED'
            })
        elif days_left <= 60:
            upcoming_notifications.append({
                'no': entry.get('no', ''),
                'name': entry.get('name', ''),
                'contract_date': entry.get('contractDate', entry.get('signDate', '')),
                'expiry_date': entry.get('nextYear', ''),
                'days_left': days_left,
                'message': f"CONTRACT EXPIRES in {days_left} days - PREPARE RENEWAL DOCUMENTS",
                'type': 'upcoming',
                'action': 'DOCUMENT PREPARATION REQUIRED'
            })
    
    notifications = overdue_notifications + upcoming_notifications
    
    if notifications:
        notification_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'notifications': notifications,
            'total': len(notifications),
            'overdue_count': len(overdue_notifications),
            'upcoming_count': len(upcoming_notifications)
        }
        
        existing_notifications = load_notifications()
        existing_notifications.append(notification_data)
        save_notifications(existing_notifications)
        
        st.success(f"✅ Found {len(notifications)} notification(s)!")
        return True
    else:
        st.info("✅ No notifications needed - All contracts have more than 60 days remaining")
        return False

# Main UI
def main():
    st.set_page_config(
        page_title="Contract Tracker Pro",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #4F46E5, #7C3AED);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            color: #6B7280;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
            border: 1px solid #E5E7EB;
        }
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #1F2937;
        }
        .stat-label {
            color: #6B7280;
            font-size: 0.875rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    init_session_state()
    
    # Header
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<p class="main-header">📄 Contract Tracker Pro</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Manage and track your contracts with automated expiry notifications</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        col2a, col2b = st.columns(2)
        with col2a:
            if st.button("🔔 Notifications", use_container_width=True):
                st.session_state.show_notifications = not st.session_state.show_notifications
                st.rerun()
        with col2b:
            if st.button("🔄 Check Now", use_container_width=True):
                check_notifications_manual()
                st.rerun()
    
    # Stats
    entries = st.session_state.entries
    total = len(entries)
    active = 0
    warning = 0
    overdue = 0
    
    for entry in entries:
        days_left = get_days_diff(entry.get('nextYear', ''))
        if days_left < 0:
            overdue += 1
        elif days_left <= 60:
            warning += 1
        else:
            active += 1
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{total}</div>
                <div class="stat-label">📋 Total Contracts</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number" style="color: #10B981;">{active}</div>
                <div class="stat-label">✅ Active (60+ days)</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number" style="color: #F59E0B;">{warning}</div>
                <div class="stat-label">⚠️ Expiring Soon (≤60 days)</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number" style="color: #EF4444;">{overdue}</div>
                <div class="stat-label">🚨 Overdue</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Filters
    filter_options = {
        'all': '📋 All Contracts',
        'active': '✅ Active (60+ days)',
        'warning': '⚠️ Expiring Soon (≤60 days)',
        'overdue': '🚨 Overdue'
    }
    selected_filter = st.radio(
        "Filter",
        options=list(filter_options.keys()),
        format_func=lambda x: filter_options[x],
        horizontal=True,
        key="filter_radio"
    )
    st.session_state.filter = selected_filter
    
    # Filter data
    filtered_entries = entries
    if selected_filter == 'active':
        filtered_entries = [e for e in entries if get_days_diff(e.get('nextYear', '')) > 60]
    elif selected_filter == 'warning':
        filtered_entries = [e for e in entries if 0 <= get_days_diff(e.get('nextYear', '')) <= 60]
    elif selected_filter == 'overdue':
        filtered_entries = [e for e in entries if get_days_diff(e.get('nextYear', '')) < 0]
    
    # Add Contract Form
    with st.expander("➕ Add New Contract", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            no = st.text_input("Contract No *", placeholder="e.g. CNT-001", key="new_no")
            name = st.text_input("Name *", placeholder="e.g. Alan", key="new_name")
        with col2:
            contract_date = st.date_input("Contract Date *", key="new_date")
            if contract_date:
                expiry_date = contract_date + timedelta(days=365)
            else:
                expiry_date = None
        with col3:
            remark = st.text_input("Remark", placeholder="Optional notes", key="new_remark")
            st.write(f"**Expiry Date:** {expiry_date.strftime('%Y-%m-%d') if expiry_date else 'Auto-calculated'}")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("💾 Save Contract", use_container_width=True):
                if no and name and contract_date:
                    new_entry = {
                        'no': no,
                        'name': name,
                        'contractDate': contract_date.strftime('%Y-%m-%d'),
                        'nextYear': expiry_date.strftime('%Y-%m-%d') if expiry_date else '',
                        'remark': remark or ""
                    }
                    entries.append(new_entry)
                    save_data(entries)
                    st.success("✅ Contract added successfully!")
                    st.rerun()
                else:
                    st.error("⚠️ Please fill in Contract No, Name, and Contract Date")
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                for key in ['new_no', 'new_name', 'new_date', 'new_remark']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    # Table
    st.subheader("📋 Contract List")
    
    if filtered_entries:
        # Prepare data for display
        table_data = []
        for idx, entry in enumerate(filtered_entries):
            days_left = get_days_diff(entry.get('nextYear', ''))
            status, icon, status_type = get_status_info(days_left)
            
            # Get color for status
            if status_type == 'overdue':
                status_display = f"🔴 {status}"
            elif status_type == 'warning':
                status_display = f"🟡 {status}"
            else:
                status_display = f"🟢 {status}"
            
            table_data.append({
                'Contract No': entry.get('no', ''),
                'Name': entry.get('name', ''),
                'Contract Date': entry.get('contractDate', entry.get('signDate', '')),
                'Expiry Date': entry.get('nextYear', ''),
                'Remark': entry.get('remark', ''),
                'Days Left': days_left if days_left < 999 else 'N/A',
                'Status': status_display,
                '_index': idx,
                '_status_type': status_type
            })
        
        df = pd.DataFrame(table_data)
        
        # Display table
        st.dataframe(
            df.drop(columns=['_index', '_status_type']),
            column_config={
                'Contract No': st.column_config.TextColumn('Contract No', width='small'),
                'Name': st.column_config.TextColumn('Name', width='medium'),
                'Contract Date': st.column_config.TextColumn('Contract Date', width='small'),
                'Expiry Date': st.column_config.TextColumn('Expiry Date', width='small'),
                'Remark': st.column_config.TextColumn('Remark', width='medium'),
                'Days Left': st.column_config.TextColumn('Days Left', width='small'),
                'Status': st.column_config.TextColumn('Status', width='medium'),
            },
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Delete functionality
        st.write("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            delete_options = [f"{e.get('no', '')} - {e.get('name', '')}" for e in filtered_entries]
            if delete_options:
                selected_to_delete = st.selectbox("Select contract to delete", delete_options)
        with col2:
            if st.button("🗑️ Delete Selected", use_container_width=True):
                if selected_to_delete:
                    # Find the entry to delete
                    for idx, entry in enumerate(entries):
                        if f"{entry.get('no', '')} - {entry.get('name', '')}" == selected_to_delete:
                            entries.pop(idx)
                            save_data(entries)
                            st.success("✅ Contract deleted successfully!")
                            st.rerun()
                            break
    else:
        st.info("📭 No contracts match the current filter. Add your first contract above!")
    
    # Notification Display
    if st.session_state.show_notifications:
        st.divider()
        st.subheader("🔔 Notifications")
        
        notifications = load_notifications()
        
        if not notifications:
            st.info("📭 No notifications yet. Notifications are generated when you click 'Check Now'.")
        else:
            # Summary
            total_overdue = sum(n.get('overdue_count', 0) for n in notifications)
            total_upcoming = sum(n.get('upcoming_count', 0) for n in notifications)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                    <div style="background:#FEE2E2; padding:1rem; border-radius:8px; text-align:center; border:1px solid #FCA5A5;">
                        <div style="font-size:2rem; font-weight:700; color:#991B1B;">{total_overdue}</div>
                        <div style="color:#6B7280;">🚨 Overdue</div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div style="background:#FEF3C7; padding:1rem; border-radius:8px; text-align:center; border:1px solid #FCD34D;">
                        <div style="font-size:2rem; font-weight:700; color:#92400E;">{total_upcoming}</div>
                        <div style="color:#6B7280;">📄 Upcoming (≤60 days)</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.write("---")
            
            # Show notifications
            for notification in reversed(notifications[-5:]):  # Show last 5
                with st.expander(f"📅 {notification.get('timestamp', 'Unknown time')} ({len(notification.get('notifications', []))} alerts)"):
                    for item in notification.get('notifications', []):
                        if item.get('type') == 'overdue':
                            st.error(f"🚨 **{item.get('no', '')} - {item.get('name', '')}**  \n{item.get('message', '')}")
                        else:
                            st.warning(f"📄 **{item.get('no', '')} - {item.get('name', '')}**  \n{item.get('message', '')}")
            
            # Clear notifications button
            if st.button("🗑️ Clear All Notifications"):
                save_notifications([])
                st.success("✅ All notifications cleared!")
                st.rerun()
    
    # Dashboard Charts
    st.divider()
    st.subheader("📊 Contract Analytics")
    
    if entries:
        col1, col2 = st.columns(2)
        with col1:
            # Status distribution
            status_counts = {
                'Active (60+ days)': active,
                'Expiring Soon (≤60 days)': warning,
                'Overdue': overdue
            }
            if total > 0:
                fig = px.pie(
                    values=list(status_counts.values()),
                    names=list(status_counts.keys()),
                    title='Contract Status Distribution',
                    color_discrete_sequence=['#10B981', '#F59E0B', '#EF4444']
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Days left distribution
            days_data = []
            for entry in entries:
                days = get_days_diff(entry.get('nextYear', ''))
                if days < 999:
                    days_data.append({
                        'Contract': f"{entry.get('no', '')}",
                        'Name': entry.get('name', ''),
                        'Days Left': days
                    })
            if days_data:
                df_days = pd.DataFrame(days_data)
                # Sort by days left
                df_days = df_days.sort_values('Days Left')
                
                colors = ['#EF4444' if d < 0 else '#F59E0B' if d <= 60 else '#10B981' for d in df_days['Days Left']]
                
                fig = px.bar(
                    df_days,
                    x='Contract',
                    y='Days Left',
                    title='Days Until Expiry',
                    color_discrete_sequence=['#4F46E5']
                )
                fig.update_traces(marker_color=colors)
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No valid expiry dates to display")
    else:
        st.info("Add contracts to see analytics charts")

if __name__ == "__main__":
    main()
