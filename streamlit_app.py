# streamlit_app.py
import streamlit as st
from datetime import datetime
from agents.google_adk_agent import GoogleADKAgent

# Initialize agent
agent = GoogleADKAgent()

st.title("AI Task Manager")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask to create, list, or update tasks..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        response = agent.process_request(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# Auto-update priorities based on due date (Logic: if due < 24h, set high)
all_tasks_check = agent.task_tools.list_tasks()
for t in all_tasks_check:
    if t.get("due_date") and t.get("status") not in ["completed", "canceled"]:
        try:
            due_dt = datetime.strptime(t["due_date"], "%Y-%m-%d")
            if (due_dt - datetime.now()).days < 1 and t.get("priority") != "high":
                agent.task_tools.update_task(t["id"], priority="high")
        except ValueError:
            pass

# Session State for Editing
if "edit_task_id" not in st.session_state:
    st.session_state.edit_task_id = None

# Sidebar Logic (Create or Edit)
if st.session_state.edit_task_id:
    st.sidebar.header(f"Edit Task {st.session_state.edit_task_id}")
    task_to_edit = agent.task_tools.get_task(st.session_state.edit_task_id)
    
    if task_to_edit:
        with st.sidebar.form("edit_task_form"):
            e_title = st.text_input("Task Title", value=task_to_edit['title'])
            
            p_index = ["low", "medium", "high"].index(task_to_edit['priority']) if task_to_edit['priority'] in ["low", "medium", "high"] else 1
            e_priority = st.selectbox("Priority", ["low", "medium", "high"], index=p_index)
            
            # Date handling
            has_date = bool(task_to_edit['due_date'])
            e_has_due_date = st.checkbox("Set Due Date", value=has_date)
            e_due_date_val = None
            if e_has_due_date:
                default_d = datetime.now().date()
                if has_date:
                    try:
                        default_d = datetime.strptime(task_to_edit['due_date'], "%Y-%m-%d").date()
                    except: pass
                e_due_date_val = st.date_input("Due Date", value=default_d)
            
            s_index = ["pending", "in_progress", "completed", "canceled"].index(task_to_edit.get('status', 'pending'))
            e_status = st.selectbox("Status", ["pending", "in_progress", "completed", "canceled"], index=s_index)
            
            if st.form_submit_button("Save Changes"):
                d_str = str(e_due_date_val) if e_has_due_date and e_due_date_val else None
                agent.task_tools.update_task(task_to_edit['id'], title=e_title, priority=e_priority, status=e_status, due_date=d_str)
                st.session_state.edit_task_id = None
                st.rerun()
                
        if st.sidebar.button("Cancel Edit"):
            st.session_state.edit_task_id = None
            st.rerun()
    else:
        st.session_state.edit_task_id = None
        st.rerun()
else:
    st.sidebar.header("Create a Task")
    with st.sidebar.form("create_task_form"):
        title = st.text_input("Task Title")
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
        
        # Due Date Selection
        has_due_date = st.checkbox("Set Due Date", value=True)
        due_date_val = None
        if has_due_date:
            due_date_val = st.date_input("Due Date")
            
        status = st.selectbox("Initial Status", ["pending", "in_progress", "completed"])
        submit = st.form_submit_button("Create Task")
        if submit:
            command = f'Create Task "{title}" with {priority} priority'
            if has_due_date and due_date_val:
                command += f' due {due_date_val}'
            response = agent.process_request(command)
            st.success(response)
            st.rerun()

# Deduplication Button
st.sidebar.markdown("---")
if st.sidebar.button("Remove Duplicates"):
    with st.spinner("Analyzing tasks..."):
        st.sidebar.success(agent.process_request("remove duplicate tasks"))

# List all tasks
st.header("Task Board")

# Filter
filter_option = st.radio("Filter:", ["All Tasks", "Pending", "In Progress", "Completed", "Canceled"], horizontal=True)

# Get tasks directly from tools for custom rendering
tasks = agent.task_tools.list_tasks()

# Apply Filter
if filter_option != "All Tasks":
    status_map = {
        "Pending": "pending",
        "In Progress": "in_progress",
        "Completed": "completed",
        "Canceled": "canceled"
    }
    tasks = [t for t in tasks if t.get("status") == status_map[filter_option]]

# Always Sort by Priority
priority_map = {"high": 3, "medium": 2, "low": 1}
tasks.sort(key=lambda x: priority_map.get(x.get("priority", "medium"), 0), reverse=True)

for task in tasks:
    p = task.get("priority", "medium")
    d = task.get("due_date")
    s = task.get("status", "pending")
    
    # Determine Border Color based on Status
    border_color = "#9e9e9e" # Default Grey (Pending)
    if s == "in_progress":
        border_color = "#2196f3" # Blue
    elif s == "completed":
        border_color = "#4caf50" # Green
    elif s == "canceled":
        border_color = "#ef5350" # Red/Grey mix
        
    # Determine Priority Icon
    p_icon = "🔵" # Low
    if p == "medium": p_icon = "🟢"
    if p == "high": p_icon = "🔴"
        
    # Timer Logic
    timer_html = ""
    if d and s not in ["completed", "canceled"]:
        try:
            due_dt = datetime.strptime(d, "%Y-%m-%d")
            delta = due_dt - datetime.now()
            total_seconds = delta.total_seconds()
            
            if total_seconds > 0:
                days = delta.days
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                t_color = "#ff4b4b" if total_seconds < 3600 else "#666"
                timer_html = f"<div style='color: {t_color}; font-size: 0.9em; margin-top: 5px;'>⏳ Time left: {days}d {hours}h {minutes}m</div>"
            else:
                timer_html = f"<div style='color: #ff4b4b; font-size: 0.9em; margin-top: 5px;'>⚠️ Overdue</div>"
        except:
            pass

    # Render Card
    col_card, col_actions = st.columns([5, 1])
    
    with col_card:
        st.markdown(f"""
    <div style="border: 3px solid {border_color}; border-radius: 10px; padding: 15px; margin-bottom: 15px; background-color: #1e1e1e;">
        <h3 style="margin: 0; color: {border_color};">{task['title']}</h3>
        <div style="display: flex; justify-content: space-between; margin-top: 5px;">
            <span>Priority: {p_icon} <b>{p.upper()}</b></span>
            <span>Status: <b>{task['status']}</b></span>
        </div>
        <div style='margin-top: 5px;{" color: #9c27b0;" if not d else ""}'>📅 {f"Due: {d}" if d else "No Due Date"}</div>
        {timer_html}
        <div style="font-size: 0.8em; color: #888; margin-top: 10px;">ID: {task['id']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    with col_actions:
        st.write("") # Spacer
        st.write("") # Spacer
        if st.button("✏️", key=f"edit_{task['id']}"):
            st.session_state.edit_task_id = task['id']
            st.rerun()
        if st.button("🗑️", key=f"del_{task['id']}"):
            agent.task_tools.update_task(task['id'], status="canceled")
            st.rerun()