"""
Unit tests for Undo and Move Highlight logic.
"""

import os
import logging
import warnings

# Suppress Streamlit bare-mode context warnings during headless testing
logging.getLogger("streamlit").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")
os.environ["STREAMLIT_LOG_LEVEL"] = "error"

from app import apply_move, evaluate_board, check_win_condition

class DummySessionState:
    def __init__(self):
        self.board = [" "] * 9
        self.history = []
        self.p1_shape = "X"
        self.game_mode = "pvp"
        self.current_player = "X"
        self.winner = None
        self.winning_combo = None
        self.celebrated = False
        self.show_highlights = False
        self.highlight_step = 0
        self.score = {"p1": 0, "p2_or_ai": 0, "draws": 0}

def test_undo_and_highlights():
    import app
    app.st.session_state = DummySessionState()
    state = app.st.session_state

    # 1. Simulate Move 1: Player 1 plays X at (0, 0)
    app.apply_move(0, "X", "Player 1")
    assert state.board[0] == "X"
    assert len(state.history) == 1
    assert state.history[0]["row"] == 1 and state.history[0]["col"] == 1
    assert state.current_player == "O"
    print("[PASS] Move 1 applied and recorded successfully")

    # 2. Simulate Move 2: Player 2 plays O at (1, 1)
    app.apply_move(4, "O", "Player 2")
    assert state.board[4] == "O"
    assert len(state.history) == 2
    assert state.current_player == "X"
    print("[PASS] Move 2 applied and recorded successfully")

    # 3. Test Undo in PvP: should undo Move 2
    app.undo_move()
    assert state.board[4] == " "
    assert len(state.history) == 1
    assert state.current_player == "O"
    print("[PASS] PvP Undo successfully reverted back to Turn 1")

    # 4. Test PvC Undo (two-step undo)
    state.game_mode = "pvc"
    app.apply_move(4, "O", "Computer")
    assert len(state.history) == 2
    app.undo_move()
    assert len(state.history) == 0
    assert state.board[0] == " " and state.board[4] == " "
    assert state.current_player == state.p1_shape
    print("[PASS] PvC Undo successfully reverted both computer and human moves")

    # 5. Play to win and test Highlights recording
    app.apply_move(0, "X", "Player 1")
    app.apply_move(3, "O", "Player 2")
    app.apply_move(1, "X", "Player 1")
    app.apply_move(4, "O", "Player 2")
    app.apply_move(2, "X", "Player 1") # Winning strike on row 0

    assert state.winner == "X"
    assert state.winning_combo[3] == "row-0"
    assert len(state.history) == 5
    print(f"[PASS] Winner recorded ({state.winner}) with strike {state.winning_combo[3]}")
    print(f"[PASS] All {len(state.history)} steps preserved for match highlights replay")

if __name__ == "__main__":
    test_undo_and_highlights()
    print("\n[ALL UNDO & HIGHLIGHT TESTS PASSED]")
