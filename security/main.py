# main.py

import streamlit as st
import os
import sys

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set Streamlit page config
st.set_page_config(page_title="Legal Intelligence Assistant", layout="wide")

# Import authentication functions
try:
    from security.auth import check_user_login, logout_user, check_permission, get_user_permissions, is_role_authorized
    print("Successfully imported authentication functions")
except ImportError as e:
    print(f"Import error: {e}")
    st.error(f"Failed to import authentication module: {e}")
    st.stop()

# Import MCP modules (with fallback to mock)
try:
    from mcp.context import MCPContext
    from mcp.intent_agent import IntentAgent
    from mcp.retrieval_agent import RetrievalAgent
    from mcp.memo_agent import MemoAgent
    from mcp.orchestrator import Orchestrator
    from utils.logger import log_event
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"MCP import error: {e}")
    MCP_AVAILABLE = False

    class MockContext:
        def __init__(self, user_query):
            self.user_query = user_query
            self.intent = "mock_intent"
            self.retrieved_cases = [
                {
                    "case_id": "MOCK-001",
                    "title": "Mock Case 1",
                    "jurisdiction": "Mock",
                    "category": "Mock Category",
                    "summary": "This is a mock case for testing purposes",
                    "outcome": "Mock Outcome",
                    "key_legal_issues": ["Mock Issue 1", "Mock Issue 2"],
                    "year": 2025
                }
            ]
            self.memo = f"Mock legal memo for: {user_query}"
            self.logs = ["Processing query...", "Intent detected", "Cases retrieved", "Memo generated"]

    def log_event(user, event_type, data):
        print(f"Mock log: {user['name']} - {event_type} - {data}")

# Check user login
try:
    user = check_user_login()
    if not user:
        st.stop()
except Exception as e:
    st.error(f"Authentication error: {e}")
    st.stop()

# ✅ Debug: print full user object and role
# st.sidebar.write(f"🧪 Debug User Info: {user}")
# st.sidebar.write(f"🔍 Debug Role: {user.get('role')}")

# Main app
st.title("LIA: Legal Intelligence Assistant")

# Sidebar: user info
st.sidebar.write(f" **{user['name']}** ({user['role']})")
st.sidebar.write(f" {user['email']}")

# Sidebar: permissions
try:
    user_permissions = get_user_permissions(user['role'])
    with st.sidebar.expander(" Your Permissions"):
        for perm in user_permissions:
            st.write(f" {perm.replace('_', ' ').title()}")
except Exception as e:
    st.sidebar.error(f"Error loading permissions: {e}")

if st.sidebar.button(" Log out"):
    logout_user()

# Role-based UI blocks
if user['role'].lower() == 'admin':
    st.sidebar.markdown("---")
    st.sidebar.subheader(" Admin Controls")
    if st.sidebar.button(" Manage Users"):
        st.info("User management functionality will be displayed here")
    if st.sidebar.button(" View System Logs"):
        st.info("System logs will be displayed here")

elif user['role'].lower() == 'lawyer':
    st.sidebar.markdown("---")
    st.sidebar.subheader(" Lawyer Tools")
    if st.sidebar.button(" Case Templates"):
        st.info("Legal case templates will be displayed here")
    if st.sidebar.button(" Legal Research"):
        st.info("Advanced legal research tools will be displayed here")

elif user['role'].lower() == 'paralegal':
    st.sidebar.markdown("---")
    st.sidebar.subheader(" Paralegal Tools")
    # st.sidebar.write("🧪 Debug: Inside paralegal role block")
    if st.sidebar.button(" Document Review"):
        st.info("Document review tools will be displayed here")
    if st.sidebar.button(" Basic Research"):
        st.info("Basic research tools will be displayed here")

# Main interaction area
st.markdown("---")
st.subheader("Legal Query Analysis")

query = st.text_area(
    "Enter your legal query or case description:",
    height=150,
    placeholder="Describe your legal question, case details, or research needs..."
)

if st.button(" Analyze & Generate Memo", type="primary") and query:
    with st.spinner("Processing your query..."):
        try:
            if MCP_AVAILABLE:
                context = MCPContext(user_query=query)
                agents = [IntentAgent(), RetrievalAgent(), MemoAgent()]
                orchestrator = Orchestrator(agents)
                context = orchestrator.run(context)
            else:
                context = MockContext(user_query=query)
                st.info(" Using mock MCP implementation (MCP modules not available)")

            log_event(user, "intent_detected", {"intent": context.intent})
            log_event(user, "cases_retrieved", {"count": len(context.retrieved_cases)})
            log_event(user, "memo_generated", {})

            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader("Processing Logs")
                for log in context.logs:
                    st.text(log)

            with col2:
                # Check if we have retrieved cases for precedent lookup
                if context.intent == "precedent_lookup" and context.retrieved_cases:
                    st.subheader(" Retrieved Cases")
                    for i, case in enumerate(context.retrieved_cases, 1):
                        with st.expander(f" Case {i}: {case.get('title', 'Unknown Title')}"):
                            st.write(f"**Case ID:** {case.get('case_id', 'N/A')}")
                            st.write(f"**Jurisdiction:** {case.get('jurisdiction', 'N/A')}")
                            st.write(f"**Category:** {case.get('category', 'N/A')}")
                            st.write(f"**Year:** {case.get('year', 'N/A')}")
                            st.write(f"**Outcome:** {case.get('outcome', 'N/A')}")
                            st.write(f"**Summary:** {case.get('summary', 'N/A')}")
                            if case.get('key_legal_issues'):
                                st.write(f"**Key Legal Issues:** {', '.join(case['key_legal_issues'])}")

                    st.download_button(
                        label="⬇️ Download Precedent Cases",
                        data=context.retrieved_cases,
                        file_name=f"retrieved_precedent_cases_{user['name'].replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                
                # Check if we have a generated memo (and it's not the default "no memo" message)
                elif context.memo and context.memo != "No memo generated for this intent.":
                    st.subheader("Generated Legal Memo")
                    st.markdown(context.memo)
                    
                    # Show reference cases if available
                    if context.retrieved_cases:
                        with st.expander("Reference Cases Used"):
                            for i, case in enumerate(context.retrieved_cases, 1):
                                st.write(f"**{i}. {case.get('title', 'Unknown Title')}** ({case.get('case_id', 'N/A')})")
                                st.write(f"   {case.get('summary', 'N/A')}")
                    
                    st.download_button(
                        label="⬇️ Download Memo",
                        data=context.memo,
                        file_name=f"legal_memo_{user['name'].replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                
                # Handle FAQ or other intents
                elif context.intent == "faq" and context.memo and context.memo != "No memo generated for this intent.":
                    st.subheader("FAQ Response")
                    st.markdown(context.memo)
                    
                    st.download_button(
                        label="⬇️ Download Response",
                        data=context.memo,
                        file_name=f"faq_response_{user['name'].replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                
                # Handle cases where we have both cases and memo for memo_generation
                elif context.intent == "memo_generation" and context.retrieved_cases and context.memo and context.memo != "No memo generated for this intent.":
                    st.subheader("Generated Legal Memo")
                    st.markdown(context.memo)
                    
                    with st.expander("Reference Cases Used"):
                        for i, case in enumerate(context.retrieved_cases, 1):
                            st.write(f"**{i}. {case.get('title', 'Unknown Title')}** ({case.get('case_id', 'N/A')})")
                            st.write(f"   {case.get('summary', 'N/A')}")
                    
                    st.download_button(
                        label="⬇️ Download Memo",
                        data=context.memo,
                        file_name=f"legal_memo_{user['name'].replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                
                else:
                    st.info("No results to display. Try a different query or check the processing logs for details.")

        except Exception as e:
            st.error(f"Error processing query: {e}")
            print(f"Processing error: {e}")
            if user.get('role') == 'admin':
                with st.expander(" Error Details (Admin Only)"):
                    st.code(str(e))

# Footer
st.markdown("---")
st.markdown("*LIA Legal Intelligence Assistant*")