"""
MailForgeAI Streamlit App for Hugging Face Spaces Deployment
Optimized for HF Spaces environment with pathlib.Path usage
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from typing import Dict, Any

from src.workflow.langgraph_flow import run_email_assistant
from src.memory.memory_store import update_profile_from_edits
from src.utils.path_utils import PATHS

st.set_page_config(
    page_title="MailForge AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_trace(trace):
    """Render the agent execution trace."""
    st.markdown("### 🔍 Agent Trace")
    for step in trace:
        st.write(step)


def render_review(review: Dict[str, Any]):
    """Render the review report."""
    if not review:
        return
    st.markdown("### 🧪 Review Report")
    st.write(f"**Verdict:** {review.get('verdict')}")
    st.write(f"**Tone Alignment Score:** {review.get('tone_alignment_score')}")
    st.write(f"**Structure OK:** {review.get('structure_ok')}")
    issues = review.get("issues", [])
    if issues:
        st.markdown("**Issues:**")
        for issue in issues:
            st.write(f"- {issue}")


def render_history(draft_history, review_history):
    """Render the draft and review history."""
    if not draft_history:
        return

    st.markdown("### 🧭 Attempts (Draft + Review)")
    review_by_attempt = {r.get("attempt"): r for r in (review_history or [])}

    for d in draft_history:
        attempt = d.get("attempt")
        with st.expander(f"Attempt {attempt}", expanded=(attempt == len(draft_history))):
            st.write("**Subject:**", d.get("subject"))
            opts = d.get("subject_options") or []
            if opts:
                st.markdown("**Subject options:**")
                for opt in opts:
                    st.write(f"- {opt}")
            st.write("**Body:**")
            st.write(d.get("body", ""))

            r = review_by_attempt.get(attempt)
            if r:
                st.markdown("**Review feedback:**")
                st.write(f"- Verdict: {r.get('verdict')}")
                st.write(f"- Score: {r.get('tone_alignment_score')}")
                if r.get("issues"):
                    st.write(f"- Issues: {', '.join(r['issues'])}")


def main():
    """Main app logic."""
    st.title("✉️ MailForgeAI - AI Email Assistant")
    st.markdown(
        """
        Generate professional, personalized emails using AI-powered agents.
        """
    )

    # Sidebar for configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        user_id = st.text_input("User ID", value="user_001", help="Your unique identifier")
        tone_mode = st.selectbox(
            "Tone Mode",
            ["formal", "casual", "assertive"],
            help="Choose the email tone",
        )
        max_retries = st.slider("Max Retries", 1, 5, 2, help="Maximum revision attempts")

    # Main input area
    st.markdown("### 📝 Email Details")
    col1, col2 = st.columns(2)

    with col1:
        user_prompt = st.text_area(
            "What email do you want to write?",
            placeholder="e.g., Send a meeting request to John about Q1 planning",
            height=100,
        )

    with col2:
        recipient_name = st.text_input("Recipient Name", placeholder="John")
        recipient_company = st.text_input("Recipient Company", placeholder="Acme Corp")
        relationship = st.selectbox(
            "Relationship",
            ["colleague", "manager", "client", "vendor", "friend"],
        )
        deadline = st.text_input("Deadline (optional)", placeholder="Tomorrow, end of day")

    # Generate button
    if st.button("✨ Generate Email", use_container_width=True, type="primary"):
        if not user_prompt:
            st.warning("Please enter what email you want to write")
        else:
            with st.spinner("🔄 Generating your email..."):
                try:
                    metadata = {
                        "recipient_name": recipient_name or "there",
                        "recipient_company": recipient_company or "",
                        "relationship": relationship,
                        "deadline": deadline or "",
                    }

                    result = run_email_assistant(
                        user_prompt=user_prompt,
                        tone_mode=tone_mode,
                        user_id=user_id,
                        metadata=metadata,
                        max_retries=max_retries,
                    )

                    # Display results
                    st.success("✅ Email generated successfully!")

                    # Final email
                    st.markdown("### 📧 Final Email")
                    final_output = result.get("final_output", "")
                    st.markdown(f"```\n{final_output}\n```")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="⬇️ Download as Text",
                            data=final_output,
                            file_name="email.txt",
                            mime="text/plain",
                        )
                    with col2:
                        st.button("📋 Copy to Clipboard")

                    # Additional sections
                    if st.checkbox("🔍 Show Agent Trace", value=False):
                        render_trace(result.get("trace", []))

                    if st.checkbox("🧪 Show Review Details", value=False):
                        render_review(result.get("review", {}))

                    if st.checkbox("📊 Show Generation History", value=False):
                        render_history(
                            result.get("draft_history", []),
                            result.get("review_history", []),
                        )

                except Exception as e:
                    st.error(f"❌ Error generating email: {str(e)}")
                    st.info("Make sure OPENAI_API_KEY is set in your secrets or environment.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        💡 **Tips:**
        - Be specific about what you want the email to convey
        - The AI considers tone, recipient context, and relationship
        - You can regenerate with different settings
        - All data paths are configured for cloud deployment
        """
    )


if __name__ == "__main__":
    main()
