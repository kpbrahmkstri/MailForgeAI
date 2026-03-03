from src.utils.email_postprocess import enforce_single_signoff


def test_does_not_append_second_signoff_if_one_exists():
    body = "Hello\n\nThanks for your time.\n\nSincerely,\nJohn Doe"
    out = enforce_single_signoff(body, {"signoff_style": "Sincerely,"}, {"signature": "Best,\nJohn"})
    # should not add "Best,\nJohn" or another closing
    assert out.count("Sincerely") == 1
    assert "Best," not in out


def test_removes_placeholder_then_appends_signature():
    body = "Hello\n\nPlease see attached.\n\nSincerely, [Your Name]"
    out = enforce_single_signoff(body, {"signoff_style": "Sincerely,"}, {"signature": "Best,\nJohn"})
    assert "[Your Name]" not in out
    # since signature exists, it should be used
    assert "Best," in out
    assert "John" in out


def test_appends_contract_signoff_when_no_signature_and_no_existing_signoff():
    body = "Hello\n\nJust checking in."
    out = enforce_single_signoff(body, {"signoff_style": "Sincerely,"}, {"name": "John Doe"})
    assert "Sincerely," in out
    assert "John Doe" in out