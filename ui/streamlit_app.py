"""
Streamlit UI for MongoDB CRUD with AI Assistant

This provides a user-friendly web interface for:
1. Natural language queries
2. Direct database operations
3. Real-time results visualization

Interview Highlight: Modern UI/UX with Streamlit
- Rapid prototyping
- Python-native
- Interactive data apps
- Perfect for AI demonstrations
"""

import streamlit as st
import httpx
import asyncio
import json
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MongoDB AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# API Configuration
API_BASE_URL = f"http://localhost:{os.getenv('API_PORT', '8000')}/api"

# Initialize Groq client
@st.cache_resource
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found in environment variables!")
        return None
    return Groq(api_key=api_key)

groq_client = get_groq_client()


# Helper functions
async def make_api_call(method: str, endpoint: str, data: dict = None):
    """Make async API call"""
    url = f"{API_BASE_URL}/{endpoint}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json=data)
        elif method == "PUT":
            response = await client.put(url, json=data)
        elif method == "DELETE":
            response = await client.delete(url)
        
        return response


def process_with_groq(query: str):
    """Process natural language with Groq"""
    if not groq_client:
        return None
    
    system_prompt = """You are a database assistant. Convert natural language to JSON API commands.

Available operations:
1. GET /api/users - Get all users
2. GET /api/users/{id} - Get user by ID
3. POST /api/users - Create user
4. GET /api/roles - Get all roles
5. POST /api/roles - Create role

Respond ONLY with valid JSON:
{
  "action": "get_users|create_user|get_roles|create_role",
  "data": {...},
  "explanation": "what you're doing"
}"""

    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.1,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Extract JSON
        json_start = ai_response.find('{')
        json_end = ai_response.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = ai_response[json_start:json_end]
            return json.loads(json_str)
        
        return None
    
    except Exception as e:
        st.error(f"Groq error: {str(e)}")
        return None


# Header
st.markdown('<div class="main-header">🤖 MongoDB AI Assistant</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Check API connection
    if st.button("🔍 Check API Connection"):
        with st.spinner("Checking..."):
            try:
                response = asyncio.run(make_api_call("GET", "roles"))
                if response.status_code == 200:
                    st.success("✅ API Server Connected!")
                else:
                    st.error(f"❌ API Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
    
    st.divider()
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    if st.button("📊 View All Users"):
        try:
            response = asyncio.run(make_api_call("GET", "users"))
            if response.status_code == 200:
                users = response.json()
                st.session_state.last_result = {
                    'type': 'users',
                    'data': users
                }
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    if st.button("🔧 View All Roles"):
        try:
            response = asyncio.run(make_api_call("GET", "roles"))
            if response.status_code == 200:
                roles = response.json()
                st.session_state.last_result = {
                    'type': 'roles',
                    'data': roles
                }
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    if st.button("🌱 Seed Database"):
        try:
            response = asyncio.run(make_api_call("POST", "seed"))
            if response.status_code == 200:
                st.success("✅ Database seeded!")
                result = response.json()
                st.json(result)
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Main content
tab1, tab2, tab3 = st.tabs(["💬 AI Chat", "👥 Users", "🔧 Roles"])

# Tab 1: AI Chat Interface
with tab1:
    st.header("Chat with AI Assistant")
    st.markdown("Ask questions in natural language!")
    
    # Example queries
    with st.expander("📝 Example Queries"):
        st.markdown("""
        - "Show me all users"
        - "Get all roles"
        - "Create a new user named John Doe with email john@example.com as admin"
        - "Create a manager role with read and write permissions"
        - "List users with admin role"
        """)
    
    # Chat input
    user_query = st.text_input(
        "Your question:",
        placeholder="e.g., Show me all users in the system",
        key="chat_input"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button("🚀 Send", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    if send_button and user_query:
        # Add to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_query
        })
        
        # Process with Groq
        with st.spinner("🧠 AI is thinking..."):
            command = process_with_groq(user_query)
            
            if command:
                st.info(f"💭 AI Plan: {command.get('explanation', 'Processing...')}")
                
                # Execute command
                action = command.get("action")
                data = command.get("data", {})
                
                try:
                    if action == "get_users":
                        response = asyncio.run(make_api_call("GET", "users"))
                    elif action == "create_user":
                        response = asyncio.run(make_api_call("POST", "users", data))
                    elif action == "get_roles":
                        response = asyncio.run(make_api_call("GET", "roles"))
                    elif action == "create_role":
                        response = asyncio.run(make_api_call("POST", "roles", data))
                    else:
                        st.error(f"Unknown action: {action}")
                        response = None
                    
                    if response and response.status_code in [200, 201]:
                        result_data = response.json()
                        
                        # Format response
                        if isinstance(result_data, list):
                            response_text = f"✅ Found {len(result_data)} items"
                        else:
                            response_text = "✅ Operation successful"
                        
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response_text,
                            "data": result_data
                        })
                    
                    elif response:
                        error_detail = response.json().get('detail', 'Unknown error')
                        st.error(f"❌ API Error: {error_detail}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.error("❌ Could not understand the query")
    
    # Display chat history
    st.divider()
    st.subheader("💬 Conversation History")
    
    for idx, message in enumerate(reversed(st.session_state.chat_history[-10:])):
        if message["role"] == "user":
            st.markdown(f"**🧑 You:** {message['content']}")
        else:
            st.markdown(f"**🤖 AI:** {message['content']}")
            if "data" in message:
                with st.expander("📊 View Data"):
                    st.json(message["data"])

# Tab 2: Users Management
with tab2:
    st.header("👥 User Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create New User")
        
        with st.form("create_user_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            # Get roles for dropdown
            try:
                roles_response = asyncio.run(make_api_call("GET", "roles"))
                if roles_response.status_code == 200:
                    roles = roles_response.json()
                    role_options = {role['name']: role['_id'] for role in roles}
                    selected_role = st.selectbox("Role", list(role_options.keys()))
                else:
                    st.warning("Could not load roles")
                    role_options = {}
                    selected_role = None
            except:
                role_options = {}
                selected_role = None
            
            phone = st.text_input("Phone (optional)")
            
            submitted = st.form_submit_button("➕ Create User")
            
            if submitted:
                if not all([first_name, last_name, email, password, selected_role]):
                    st.error("Please fill in all required fields")
                else:
                    user_data = {
                        "firstName": first_name,
                        "lastName": last_name,
                        "email": email,
                        "password": password,
                        "role": selected_role,  # Use role name, API will resolve
                        "phone": phone if phone else None
                    }
                    
                    try:
                        response = asyncio.run(make_api_call("POST", "users", user_data))
                        if response.status_code == 201:
                            st.success("✅ User created successfully!")
                            st.json(response.json())
                        else:
                            error = response.json().get('detail', 'Unknown error')
                            st.error(f"❌ Error: {error}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.subheader("All Users")
        
        if st.button("🔄 Refresh Users"):
            try:
                response = asyncio.run(make_api_call("GET", "users"))
                if response.status_code == 200:
                    st.session_state.users = response.json()
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        if 'users' in st.session_state:
            for user in st.session_state.users:
                with st.container():
                    st.markdown(f"""
                    **{user['firstName']} {user['lastName']}**
                    - 📧 {user['email']}
                    - 🔧 Role: {user.get('role', {}).get('name', 'N/A')}
                    - 📊 Status: {'Active' if user.get('isActive') else 'Inactive'}
                    """)
                    st.divider()

# Tab 3: Roles Management
with tab3:
    st.header("🔧 Role Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create New Role")
        
        with st.form("create_role_form"):
            role_name = st.text_input("Role Name")
            role_description = st.text_area("Description")
            
            st.write("Permissions:")
            perm_read = st.checkbox("Read", value=True)
            perm_write = st.checkbox("Write")
            perm_delete = st.checkbox("Delete")
            perm_admin = st.checkbox("Admin")
            
            is_active = st.checkbox("Active", value=True)
            
            submitted = st.form_submit_button("➕ Create Role")
            
            if submitted:
                if not all([role_name, role_description]):
                    st.error("Please fill in all required fields")
                else:
                    permissions = []
                    if perm_read: permissions.append("read")
                    if perm_write: permissions.append("write")
                    if perm_delete: permissions.append("delete")
                    if perm_admin: permissions.append("admin")
                    
                    role_data = {
                        "name": role_name,
                        "description": role_description,
                        "permissions": permissions,
                        "is_active": is_active
                    }
                    
                    try:
                        response = asyncio.run(make_api_call("POST", "roles", role_data))
                        if response.status_code == 201:
                            st.success("✅ Role created successfully!")
                            st.json(response.json())
                        else:
                            error = response.json().get('detail', 'Unknown error')
                            st.error(f"❌ Error: {error}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.subheader("All Roles")
        
        if st.button("🔄 Refresh Roles"):
            try:
                response = asyncio.run(make_api_call("GET", "roles"))
                if response.status_code == 200:
                    st.session_state.roles = response.json()
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        if 'roles' in st.session_state:
            for role in st.session_state.roles:
                with st.container():
                    perms = ', '.join(role.get('permissions', []))
                    st.markdown(f"""
                    **{role['name']}**
                    - 📝 {role['description']}
                    - 🔑 Permissions: {perms}
                    - 📊 Status: {'Active' if role.get('is_active') else 'Inactive'}
                    """)
                    st.divider()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 MongoDB AI Assistant | Built with FastAPI + Groq + Streamlit</p>
    <p>💡 Perfect for demonstrating AI-powered database operations</p>
</div>
""", unsafe_allow_html=True)
