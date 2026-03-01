from src.workflow.langgraph_flow import run_email_assistant

state = run_email_assistant(
    user_prompt="Write a follow-up email to a recruiter after an interview yesterday. Keep it confident and short.",
    tone_mode="assertive",
    user_id="default",
    metadata={"recipient_name": "Sarah", "recipient_org": "Acme"},
    max_retries=1,
)

print("\n--- TRACE ---")
print("\n".join(state.get("trace", [])))

if state.get("router", {}).get("next_step") == "ask_user":
    print("\n--- QUESTION ---")
    print(state.get("clarification_question"))

print("\n--- FINAL OUTPUT ---")
print(state.get("final_output"))