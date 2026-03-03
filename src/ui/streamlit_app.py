import sys
from pathlib import Path

import streamlit as st
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.workflow.langgraph_flow import run_email_assistant
from src.memory.memory_store import update_profile_from_edits

st.set_page_config(page_title="MailForge AI", layout="wide")


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


def render_history(draft_history, review_history):
    if not draft_history:
        return

    st.markdown("### 🧭 Attempts (Draft + Review)")
    # Map attempt -> review
    review_by_attempt = {r.get("attempt"): r for r in (review_history or [])}

    for d in draft_history:
        attempt = d.get("attempt")
        with st.expander(f"Attempt {attempt}", expanded=(attempt == len(draft_history))):
            st.write("**Subject:**", d.get("subject"))
            opts = d.get("subject_options") or []
            if opts:
                st.write("**Subject options:**")
                for o in opts:
                    st.write(f"- {o}")
            st.text_area("Draft body", value=d.get("body", ""), height=220, key=f"hist_body_{attempt}")

            r = review_by_attempt.get(attempt)
            if r:
                st.markdown("---")
                st.write(f"**Review Verdict:** {r.get('verdict')}")
                st.write(f"**Tone Score:** {r.get('tone_alignment_score')}")
                st.write(f"**Structure OK:** {r.get('structure_ok')}")
                issues = r.get("issues", [])
                if issues:
                    st.write("**Issues:**")
                    for issue in issues:
                        st.write(f"- {issue}")


st.title("📧 MailForge AI — Multi-Agent Email Assistant")

# Session state for clarification loop
if "last_prompt" not in st.session_state:
    st.session_state["last_prompt"] = ""
if "last_state" not in st.session_state:
    st.session_state["last_state"] = None

with st.sidebar:
    st.header("⚙️ Controls")

    tone_mode = st.selectbox("Tone", ["formal", "casual", "assertive"], index=0)

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
    st.write("- Include who the recipient is and what you want them to do")
    st.write("- Add deadline if relevant")
    st.write("- For follow-ups: specify what you want them to review/confirm")

# ---------- Execution ----------
def run_workflow(prompt_text: str):
    metadata = {
        "recipient_name": recipient_name,
        "recipient_org": recipient_org,
        "relationship": relationship,
        "deadline": deadline,
    }

    return run_email_assistant(
        user_prompt=prompt_text,
        tone_mode=tone_mode,
        intent_override=intent_override if intent_override else None,
        metadata=metadata,
        user_id="default",
        max_retries=1,
    )

if generate and user_prompt.strip():
    with st.spinner("Running multi-agent workflow..."):
        state = run_workflow(user_prompt.strip())

    st.session_state["last_prompt"] = user_prompt.strip()
    st.session_state["last_state"] = state

# If we have a prior run, show it
state = st.session_state.get("last_state")

if state:
    with st.expander("📚 Retrieved Templates (RAG)", expanded=False):
        templates = state.get("retrieved_templates", [])
        if not templates:
            st.write("No templates retrieved.")
        else:
            for t in templates:
                st.write(f"**{t.get('source')}**")
                st.code((t.get("content", "") or "")[:800])
else:
    with st.expander("📚 Retrieved Templates (RAG)", expanded=False):
        st.write("Run a prompt to retrieve templates.")

if state:
    st.markdown("---")

    # Clarification loop (Option A)
    if state.get("router", {}).get("next_step") == "ask_user":
        st.warning("⚠️ Clarification Needed")
        st.write(state.get("clarification_question"))

        clarification = st.text_input("Your answer (we’ll use it to draft):", key="clarification_answer")
        if st.button("✅ Apply clarification and rerun"):
            combined = st.session_state["last_prompt"] + "\n\nUser clarification: " + clarification.strip()
            with st.spinner("Re-running with clarification..."):
                new_state = run_workflow(combined)
            st.session_state["last_prompt"] = combined
            st.session_state["last_state"] = new_state
            st.rerun()

    else:
        st.subheader("📨 Generated Email")

        draft = state.get("draft") or {}
        subject_options = draft.get("subject_options") or []
        chosen_subject = None

        if subject_options:
            chosen_subject = st.radio("Choose a subject:", subject_options, index=0)
        else:
            chosen_subject = draft.get("subject") or ""

        final_body = (draft.get("body") or "").strip()
        final_output = f"Subject: {chosen_subject}\n\n{final_body}".strip()

        edited_output = st.text_area("Edit before sending:", value=final_output, height=320)

        c1, c2, c3 = st.columns(3)

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

        with c3:
            # Streamlit doesn't provide universal clipboard copy reliably across browsers.
            st.caption("Tip: Select text and Ctrl/Cmd+C to copy.")

        st.markdown("---")

        # Show retry history
        render_history(state.get("draft_history", []), state.get("review_history", []))

        # Show latest review
        render_review(state.get("review") or {})

    st.markdown("---")
    render_trace(state.get("trace", []))