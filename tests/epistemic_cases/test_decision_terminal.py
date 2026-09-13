from backend.app.core.decision.decision_terminal import TerminalDisposition, validate_terminal


def test_terminal_paths_are_explicit():
    assert validate_terminal(TerminalDisposition.DECISION) is TerminalDisposition.DECISION
    assert validate_terminal(TerminalDisposition.HUMAN_REVIEW) is TerminalDisposition.HUMAN_REVIEW
    assert validate_terminal(TerminalDisposition.ABSTENTION) is TerminalDisposition.ABSTENTION
