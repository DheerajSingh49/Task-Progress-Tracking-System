import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Progress Tracker Portal", layout="wide")

# --- 2. MONGODB INTEGRATION ---
@st.cache_resource
def init_connection():
    uri = "mongodb+srv://STREAMLIT:MONGODB000@cluster0.hw49pfr.mongodb.net/?appName=Cluster0"
    return MongoClient(uri)

client = init_connection()
db = client.Company_MIS
auth_col = db.User_Auth
data_col = db.Employee_Data

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_id = None

# --- 4. LOGIN UI ---
if not st.session_state.logged_in:
    st.title("Progress Tracking and Management Portal")
    role_choice = st.selectbox("Select Access Level", ["Employee", "Management", "Admin"])
    u_id = st.text_input("User ID")
    u_pw = st.text_input("Password", type="password")
    if st.button("Login"):
        user = auth_col.find_one({"user_id": u_id, "password": u_pw, "role": role_choice})
        if user:
            st.session_state.logged_in = True
            st.session_state.role = role_choice
            st.session_state.user_id = u_id
            st.rerun()
        else:
            st.error("Invalid Credentials")

# --- 5. DASHBOARD LOGIC ---
else:
    st.sidebar.title(f"{st.session_state.role} Menu")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title(f"{st.session_state.role} Dashboard")
    st.write("---")

    # --- DATA RETRIEVAL ---
    all_records = list(data_col.find({})) 
    query = {"emp_id": st.session_state.user_id} if st.session_state.role == "Employee" else {}
    table_records = list(data_col.find(query))

    # --- PART A: DATA TABLE ---
    st.subheader("Detailed Task Records")
    if table_records:
        df_show = pd.DataFrame(table_records).drop(columns=['_id'])
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("No records found.")

    st.write("---")

    # --- PART B: THE UNIFIED CONTROL CENTER ---
    
    if st.session_state.role == "Admin":
        with st.expander("ADMIN CONTROL CENTER"):
            tab1, tab2, tab3 = st.tabs(["Assign Task", "Update Task", "Delete Task"])
            
            with tab1:
                aid = st.selectbox("Select Employee ID", [r['emp_id'] for r in all_records], key="aid")
                aname = next((r['name'] for r in all_records if r['emp_id'] == aid), "Unknown")
                st.info(f"Assigning to: {aname}")
                
                with st.form("assign_form", clear_on_submit=True):
                    tk = st.text_area("Task Description")
                    if st.form_submit_button("Assign"):
                        data_col.update_one(
                            {"emp_id": aid},
                            {"$set": {
                                "assigned_task": tk,
                                "task_issue_date": datetime.now().strftime("%d/%m/%Y"),
                                "task_submission_date": "Pending",
                                "remarks": "New Assignment"
                            }}
                        )
                        st.rerun()
            
            with tab2:
                uid = st.selectbox("Employee ID", [r['emp_id'] for r in all_records], key="uid")
                uname = next((r['name'] for r in all_records if r['emp_id'] == uid), "Unknown")
                st.info(f"Updating: {uname}")
                
                with st.form("update_form"):
                    new_date = st.text_input("New Submission Date (DD/MM/YYYY)")
                    new_rem = st.text_area("Admin Remarks")
                    if st.form_submit_button("Update"):
                        data_col.update_one({"emp_id": uid}, {"$set": {"task_submission_date": new_date, "remarks": new_rem}})
                        st.rerun()

            with tab3:
                did = st.selectbox("Select ID to Delete Task", [r['emp_id'] for r in all_records], key="did")
                dname = next((r['name'] for r in all_records if r['emp_id'] == did), "Unknown")
                st.info(f"Targeting: {dname}")
                
                if st.button("Delete Task Details"):
                    # CRITICAL FIX: Wiping ALL date and task fields simultaneously
                    data_col.update_one(
                        {"emp_id": did},
                        {"$set": {
                            "assigned_task": "None",
                            "task_issue_date": "N/A",
                            "task_submission_date": "N/A",
                            "remarks": "Task Deleted"
                        }}
                    )
                    st.success(f"All task records for {dname} have been wiped.")
                    st.rerun()

    elif st.session_state.role == "Management":
        with st.expander("MANAGEMENT CONTROL CENTER"):
            mid = st.selectbox("Employee ID", [r['emp_id'] for r in all_records], key="mid")
            mname = next((r['name'] for r in all_records if r['emp_id'] == mid), "Unknown")
            st.info(f"Managing: {mname}")
            
            with st.form("mgt_form"):
                new_date = st.text_input("Submission Date (DD/MM/YYYY)")
                new_rem = st.text_area("Managerial Feedback")
                if st.form_submit_button("Save Update"):
                    data_col.update_one({"emp_id": mid}, {"$set": {"task_submission_date": new_date, "remarks": new_rem}})
                    st.rerun()

    elif st.session_state.role == "Employee":
        with st.expander("SUBMIT PROGRESS UPDATE"):
            st.write(f"Updating for ID: {st.session_state.user_id}")
            with st.form("emp_form"):
                my_rem = st.text_area("Status update")
                if st.form_submit_button("Submit"):
                    data_col.update_one({"emp_id": st.session_state.user_id}, {"$set": {"remarks": my_rem}})
                    st.rerun()

    # --- PART C: ANALYTICS ---
    st.write("---")
    if all_records:
        df_all = pd.DataFrame(all_records)
        today = datetime.now()

        def calculate_status(row):
            sub_date_str = str(row.get('task_submission_date', 'Pending'))
            remark = str(row.get('remarks', '')).lower()
            if sub_date_str not in ["Pending", "N/A"]:
                try:
                    sub_date_obj = datetime.strptime(sub_date_str, "%d/%m/%Y")
                    if "done" in remark or "complete" in remark: return "Completed"
                    if sub_date_obj < today: return "Past Due"
                except: pass
            return "In Progress"

        df_all['Computed_Status'] = df_all.apply(calculate_status, axis=1)
        df_all['date_obj'] = pd.to_datetime(df_all['task_issue_date'], format='%d/%m/%Y', errors='coerce')
        df_all['time_label'] = df_all['date_obj'].dt.strftime('%b %Y')

        st.subheader("Performance Analytics")
        
        if st.session_state.role == "Admin":
            col1, col2 = st.columns(2, gap="large")
            with col1:
                pie_data = df_all['Computed_Status'].value_counts().reset_index()
                pie_data.columns = ['Status', 'Count']
                fig_pie = px.pie(pie_data, values='Count', names='Status', height=350, title="Global Task Status",
                                 color_discrete_map={'Completed':'#2ecc71', 'In Progress':'#3498db', 'Past Due':'#e74c3c'})
                st.plotly_chart(fig_pie, use_container_width=True)
            with col2:
                bar_data = df_all.groupby(['time_label', 'Computed_Status']).size().unstack(fill_value=0).reset_index()
                fig_bar = go.Figure()
                status_colors = {'Completed':'#2ecc71', 'In Progress':'#3498db', 'Past Due':'#e74c3c'}
                for s in ['Completed', 'In Progress', 'Past Due']:
                    if s in bar_data.columns:
                        fig_bar.add_trace(go.Bar(name=s, x=bar_data['time_label'], y=bar_data[s], marker_color=status_colors[s]))
                fig_bar.update_layout(barmode='group', height=350, title="Timeline Summary", xaxis_title="Timeline", yaxis_title="Tasks")
                st.plotly_chart(fig_bar, use_container_width=True)

        elif st.session_state.role == "Management":
            _, col_mid, _ = st.columns([1, 2, 1])
            with col_mid:
                pie_data = df_all['Computed_Status'].value_counts().reset_index()
                fig_pie = px.pie(pie_data, values='count', names='Computed_Status', height=350, title="Overall Team Progress",
                                 color_discrete_map={'Completed':'#2ecc71', 'In Progress':'#3498db', 'Past Due':'#e74c3c'})
                st.plotly_chart(fig_pie, use_container_width=True)

        elif st.session_state.role == "Employee":
            _, col_mid, _ = st.columns([1, 2, 1])
            with col_mid:
                personal_df = df_all[df_all['emp_id'] == st.session_state.user_id]
                fig_pie = px.pie(personal_df, names='Computed_Status', height=350, title="My Personal Status",
                                 color_discrete_map={'Completed':'#2ecc71', 'In Progress':'#3498db', 'Past Due':'#e74c3c'})
                st.plotly_chart(fig_pie, use_container_width=True)