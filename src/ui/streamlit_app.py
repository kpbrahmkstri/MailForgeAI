import sys
from pathlib import Path

import streamlit as st
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.workflow.langgraph_flow import run_email_assistant
from src.memory.memory_store import update_profile_from_edits


st.set_page_config(page_title="MailForge AI", layout="wide")


# ---------- Helper ----------
def render_trace(trace):
    st.markdown("### 🔍 Agent Trace")
    for step in trace:
        st.write(step)


def render_review(review: Dict[str, Any]):
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


# ---------- UI ----------
st.title("📧 MailForge AI — Multi-Agent Email Assistant")

with st.sidebar:
    st.header("⚙️ Controls")

    tone_mode = st.selectbox(
        "Tone",
        ["formal", "casual", "assertive"],
        index=0,
    )

    intent_override = st.selectbox(
        "Intent Override (optional)",
        ["", "outreach", "follow_up", "apology", "status_update", "meeting_request", "escalation", "thank_you"],
    )

    st.markdown("---")

    st.subheader("Metadata (optional)")
    recipient_name = st.text_input("Recipient Name")
    recipient_org = st.text_input("Recipient Organization")
    relationship = st.text_input("Relationship (e.g., manager, recruiter, client)")
    deadline = st.text_input("Deadline (optional)")


col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("✍️ Your Prompt")
    user_prompt = st.text_area(
        "Describe the email you want to write:",
        height=200,
        placeholder="Example: Write a follow-up email to a recruiter after yesterday’s interview..."
    )

    generate = st.button("🚀 Generate Email")

with col2:
    st.subheader("📌 Quick Tips")
    st.write("- Be specific about your goal")
    st.write("- Mention recipient type (manager, client, recruiter)")
    st.write("- Specify tone preference")
    st.write("- Include deadline if relevant")


# ---------- Execution ----------
if generate and user_prompt.strip():
    metadata = {
        "recipient_name": recipient_name,
        "recipient_org": recipient_org,
        "relationship": relationship,
        "deadline": deadline,
    }

    with st.spinner("Running multi-agent workflow..."):
        state = run_email_assistant(
            user_prompt=user_prompt,
            tone_mode=tone_mode,
            intent_override=intent_override if intent_override else None,
            metadata=metadata,
            user_id="default",
            max_retries=1,
        )
        
    edited_output = ""  # ✅ define default to avoid NameError
    # If router asked for clarification
    if state.get("router", {}).get("next_step") == "ask_user":
        st.warning("⚠️ Clarification Needed")
        st.write(state.get("clarification_question"))
    else:
        st.subheader("📨 Generated Email")

        final_output = state.get("final_output", "")
        edited_output = st.text_area(
    "Edit before sending:",
    value=final_output,
    height=300,
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button("💾 Save my edits (learn my style)"):
            new_profile = update_profile_from_edits(
                user_id="default",
                generated=final_output,
                edited=edited_output,
            )
            st.success("Saved! Next drafts will better match your style.")
            st.caption(f"Learned prefs: {new_profile.get('style_preferences')}")

    with c2:
        st.download_button(
            label="⬇️ Download as .txt",
            data=edited_output,
            file_name="mailforge_email.txt",
            mime="text/plain",
        )

    st.caption("Tip: select text and copy manually, or download as .txt.")

    st.markdown("---")

    render_trace(state.get("trace", []))
    render_review(state.get("review"))