import streamlit as st
import requests

st.set_page_config(
    page_title="Medical Report Diagnosis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://127.0.0.1:8000"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.password = None
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'doc_id' not in st.session_state:
    st.session_state.doc_id = None
if 'uploaded_files_info' not in st.session_state:
    st.session_state.uploaded_files_info = []

def login(username, password):
    try:
        response = requests.get(
            f"{API_BASE_URL}/auth/login",
            auth=(username, password),
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.logged_in = True
            st.session_state.username = data["username"]
            st.session_state.role = data["role"]
            st.session_state.password = password
            return True, "✅ Login successful!"
        else:
            return False, "❌ Invalid username or password"
    except:
        return False, f"❌ Cannot connect to {API_BASE_URL}"

def signup(username, password, confirm, role):
    if password != confirm:
        return False, "❌ Passwords don't match"
    if len(password) < 6:
        return False, "❌ Password must be 6+ characters"
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json={"username": username, "password": password, "role": role},
            timeout=10
        )
        if response.status_code == 200:
            return True, "✅ Account created! Please login"
        else:
            return False, f"❌ Signup failed"
    except:
        return False, f"❌ Cannot connect to {API_BASE_URL}"

def upload_report(files, username, password):
    """Upload medical report files"""
    if not files:
        return False, "❌ No files selected"
    
    try:
        # Prepare files for multipart upload
        file_list = [("files", (f.name, f)) for f in files]
        
        response = requests.post(
            f"{API_BASE_URL}/reports/upload",
            files=file_list,
            auth=(username, password),
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            doc_id = data.get("doc_id")
            # Store file info in session state
            st.session_state.uploaded_files_info = [{"name": f.name, "size": f.size} for f in files]
            return True, f"✅ Reports uploaded! Document ID: {doc_id}", doc_id
        else:
            return False, f"❌ Upload failed: {response.text}", None
    except Exception as e:
        return False, f"❌ Error: {str(e)}", None

def get_diagnosis(doc_id, question, username, password):
    """Get diagnosis from uploaded report"""
    if not doc_id or not question:
        return False, "❌ Please enter Document ID and question"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/diagnosis/from_report",
            data={"doc_id": doc_id, "question": question},
            auth=(username, password),
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"❌ Diagnosis failed: {response.text}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

# Sidebar Navigation
with st.sidebar:
    st.title("🏥 Medical Report Diagnosis")
    st.markdown("---")
    
    if st.session_state.logged_in:
        st.success(f"✅ {st.session_state.username}\n({st.session_state.role})")
        st.markdown("---")
        
        if st.button("🏠 Home", use_container_width=True, key="btn_home"):
            st.session_state.page = "home"
        if st.button("⚙️ Settings", use_container_width=True, key="btn_settings"):
            st.session_state.page = "settings"
        
        # Show "Patients" button only for doctors
        if st.session_state.role == "doctor":
            if st.button("👥 Patients", use_container_width=True, key="btn_patients"):
                st.session_state.page = "patients"
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="btn_logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.password = None
            st.session_state.page = "home"
            st.session_state.doc_id = None
            st.session_state.uploaded_files_info = []
            st.rerun()
    else:
        st.subheader("Authentication")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown("### Login")
            user = st.text_input("Username", key="login_user")
            pwd = st.text_input("Password", type="password", key="login_pwd")
            if st.button("Login", use_container_width=True, key="login_btn"):
                if user and pwd:
                    success, msg = login(user, pwd)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("❌ Please enter username and password")
        
        with tab2:
            st.markdown("### Create Account")
            user = st.text_input("Username", key="signup_user")
            pwd = st.text_input("Password", type="password", key="signup_pwd")
            pwd_confirm = st.text_input("Confirm", type="password", key="signup_confirm")
            role = st.selectbox("Role", ["patient", "doctor"], key="signup_role")
            if st.button("Sign Up", use_container_width=True, key="signup_btn"):
                if user and pwd and pwd_confirm:
                    success, msg = signup(user, pwd, pwd_confirm, role)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.error("❌ Please fill all fields")

# Main Content
if st.session_state.logged_in:
    if st.session_state.page == "settings":
        st.title("⚙️ Account Settings")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Username:** {st.session_state.username}")
        with col2:
            st.info(f"**Role:** {st.session_state.role.capitalize()}")
    
    elif st.session_state.page == "patients":
        st.title("👥 Patient Management")
        st.markdown("---")
        
        # Doctor view - search for patients and view their diagnoses
        st.subheader("Search Patient Diagnosis")
        patient_name = st.text_input("Enter patient username to view diagnosis", key="patient_search")
        
        if st.button("🔍 Search Patient", key="search_patient_btn"):
            if patient_name:
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/diagnosis/by_patient_name",
                        params={"patient_name": patient_name},
                        auth=(st.session_state.username, st.session_state.password),
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        diagnoses = response.json()
                        st.success(f"✅ Found {len(diagnoses)} diagnosis record(s) for patient '{patient_name}'")
                        
                        for idx, diag in enumerate(diagnoses, 1):
                            with st.expander(f"📋 Diagnosis {idx} - Document ID: {diag.get('doc_id', 'N/A')}", expanded=False):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Requester:** {diag.get('requester', 'N/A')}")
                                    st.write(f"**Document ID:** {diag.get('doc_id', 'N/A')}")
                                with col2:
                                    from datetime import datetime
                                    timestamp = diag.get('timestamp', 0)
                                    if timestamp:
                                        dt = datetime.fromtimestamp(timestamp)
                                        st.write(f"**Date:** {dt.strftime('%B %d, %Y at %I:%M %p')}")
                                    st.write(f"**Sources:** {len(diag.get('sources', []))}")
                                
                                st.markdown("---")
                                st.markdown("### Question Asked")
                                st.info(diag.get('question', 'N/A'))
                                
                                st.markdown("### Diagnosis Answer")
                                st.markdown(f"""
                                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4; color: #000;">
                                    {diag.get('answer', 'No diagnosis available')}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if diag.get('sources'):
                                    st.markdown("### Sources")
                                    for source in diag.get('sources', []):
                                        st.code(source, language="text")
                    
                    elif response.status_code == 404:
                        st.warning(f"⚠️ No diagnosis records found for patient '{patient_name}'")
                    else:
                        st.error(f"❌ Error: {response.text}")
                
                except Exception as e:
                    st.error(f"❌ Error searching patient: {str(e)}")
            else:
                st.error("❌ Please enter a patient username")
    
    else:  # home page - combined upload and diagnosis
        st.title("🏥 Medical Report Diagnosis System")
        st.markdown("---")
        
        # Upload Section
        st.header("📋 Upload Medical Reports")
        st.markdown("Upload your medical report files (PDF, TXT) for AI-powered diagnosis analysis.")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose medical report files",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            key="file_uploader"
        )
        
        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)} file(s) selected")
            for f in uploaded_files:
                st.text(f"  • {f.name} ({f.size/1024:.1f} KB)")
            
            upload_btn = st.button("📤 Upload Reports", key="upload_btn", use_container_width=False)
            
            if upload_btn:
                with st.spinner("Uploading and indexing reports..."):
                    success, msg, doc_id = upload_report(
                        uploaded_files, 
                        st.session_state.username, 
                        st.session_state.password
                    )
                    if success:
                        st.success(msg)
                        st.session_state.doc_id = doc_id
                        st.info(f"**Document ID saved:** `{doc_id}`")
                    else:
                        st.error(msg)
        
        # Show previously uploaded files info
        if st.session_state.uploaded_files_info:
            st.markdown("---")
            st.subheader("📂 Previously Uploaded Files")
            for file_info in st.session_state.uploaded_files_info:
                st.text(f"  • {file_info['name']} ({file_info['size']/1024:.1f} KB)")
            if st.session_state.doc_id:
                st.info(f"**Document ID:** `{st.session_state.doc_id}`")
        
        st.markdown("---")
        st.markdown("---")
        
        # Diagnosis Section
        st.header("🔍 Get AI-Powered Diagnosis")
        
        if st.session_state.doc_id:
            st.markdown("Query the diagnosis system with your uploaded medical reports.")
            st.info(f"📄 Using Document ID: `{st.session_state.doc_id}`")
            
            question = st.text_area(
                "What would you like to know about this report?",
                value="Please provide a diagnosis based on my report.",
                height=120,
                key="diag_question"
            )
            
            diagnosis_btn = st.button("🔍 Get Diagnosis", key="get_diagnosis_btn", type="primary", use_container_width=False)
            
            if diagnosis_btn:
                if not question:
                    st.error("❌ Please enter a question")
                else:
                    with st.spinner("Analyzing report and generating diagnosis..."):
                        success, result = get_diagnosis(
                            st.session_state.doc_id, 
                            question, 
                            st.session_state.username,
                            st.session_state.password
                        )
                
                    if success:
                        from datetime import datetime
                        
                        st.markdown("---")
                        st.markdown("---")
                        
                        # Header with timestamp
                        st.success("✅ Diagnosis Generated Successfully!")
                        st.subheader("📊 Medical Report Analysis")
                        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
                        st.caption(f"🕒 Generated on: {current_time}")
                        
                        st.markdown("---")
                        
                        # Main Diagnosis
                        st.markdown("### 🏥 Diagnosis")
                        if "diagnosis" in result:
                            diagnosis_text = result["diagnosis"]
                            st.markdown(f"""
                            <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4; color: #000;">
                                {diagnosis_text}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Key Findings Section
                        st.markdown("### 🔍 Key Findings")
                        if "diagnosis" in result:
                            # Try to extract key findings from diagnosis text
                            diagnosis_lower = result["diagnosis"].lower()
                            
                            # Display key findings in bullet points
                            st.markdown("""
                            Based on the medical report analysis:
                            """)
                            
                            # Split diagnosis into sentences for better readability
                            sentences = result["diagnosis"].split('.')
                            findings_shown = False
                            for sentence in sentences[:5]:  # Show first 5 key points
                                if sentence.strip():
                                    st.markdown(f"- {sentence.strip()}")
                                    findings_shown = True
                            
                            if not findings_shown:
                                st.info("Key findings are included in the diagnosis above.")
                        
                        st.markdown("---")
                        
                        # Recommendations Section
                        st.markdown("### 💊 Recommendations & Next Steps")
                        st.markdown("""
                        <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 5px solid #ffc107; color: #000;">
                            <strong>⚠️ Important:</strong>
                            <ul>
                                <li>This is an AI-assisted preliminary analysis</li>
                                <li>Consult with a qualified healthcare professional for accurate diagnosis</li>
                                <li>Do not use this as a substitute for professional medical advice</li>
                                <li>Follow up with your doctor for personalized treatment plan</li>
                                <li>Keep all original medical reports for your healthcare provider</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Sources Section
                        st.markdown("### 📚 Source Documents")
                        if "sources" in result and result["sources"]:
                            st.markdown(f"**Document ID:** `{st.session_state.doc_id}`")
                            st.markdown(f"**Total Sources Referenced:** {len(result['sources'])}")
                            
                            with st.expander("📄 View All Source References", expanded=False):
                                for idx, source in enumerate(result["sources"], 1):
                                    st.markdown(f"**Reference {idx}:**")
                                    st.code(source, language="text")
                                    st.markdown("---")
                        else:
                            st.info("No specific source references available.")
                        
                        # Context snippets if available
                        if "context_snippets" in result and result["context_snippets"]:
                            st.markdown("---")
                            st.markdown("### 📋 Relevant Report Excerpts")
                            with st.expander("View excerpts from your report", expanded=False):
                                for idx, snippet in enumerate(result["context_snippets"], 1):
                                    st.markdown(f"**Excerpt {idx}:**")
                                    st.info(snippet)
                        
                        st.markdown("---")
                        st.markdown("---")
                        
                        # Final Disclaimer
                        st.error("""
                        **⚠️ MEDICAL DISCLAIMER**
                        
                        This AI-generated analysis is for informational purposes only and should not be considered as medical advice, 
                        diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any 
                        questions you may have regarding a medical condition. Never disregard professional medical advice or delay in 
                        seeking it because of something you have read in this analysis.
                        """)
                    else:
                        st.error(result)
        else:
            st.warning("⚠️ Please upload medical reports first to get a diagnosis.")

else:
    st.title("🏥 Medical Report Diagnosis System")
    st.markdown("---")
    st.markdown("""
    ## Welcome!
    
    This application uses a **FastAPI backend** with **LangChain/GenAI stack** to help:
    - 👨‍⚕️ **Patients** get AI-powered diagnosis from medical reports
    - 👩‍⚕️ **Doctors** access patient diagnosis history
    
    ### 🔐 Please Login or Sign Up
    
    Use the sidebar on the left to log in with your credentials or create a new account.
    """)
