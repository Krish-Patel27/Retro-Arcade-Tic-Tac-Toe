"""
Retro Arcade Tic-Tac-Toe
Built with Streamlit and Python.
Theme: Retro Arcade (game-theme.json)
Modes:
  1) Player vs Player (Offline Local Multiplayer)
  2) Player vs Computer (Recursive Minimax Defense)
"""

import streamlit as st
import json
import os
import copy

# ==============================================================================
# 1. THEME & CONFIGURATION SPECIFICATION
# ==============================================================================
DEFAULT_THEME = {
    "themeName": "Retro Arcade Tic-Tac-Toe",
    "version": "1.1.0",
    "boardLayout": {
        "dimensions": "400px",
        "gridGap": "12px",
        "gridStructure": "repeat(3, 1fr)"
    },
    "colors": {
        "gameplay": {
            "background": "#0B0F19",
            "boardBackground": "#161F30",
            "cellDefault": "#1E293B",
            "cellHover": "#2C3B54"
        },
        "tokens": {
            "playerX": "#38BDF8",
            "playerO": "#FB7185",
            "neutralText": "#F8FAFC",
            "subtleText": "#64748B"
        },
        "states": {
            "winningLine": "#EF4444",
            "drawOverlay": "#475569",
            "winGlowX": "rgba(56, 189, 248, 0.4)",
            "winGlowO": "rgba(251, 113, 133, 0.4)"
        }
    },
    "typography": {
        "gameFonts": "system-ui, -apple-system, sans-serif",
        "tokenSize": "3.5rem",
        "tokenWeight": "800",
        "statusSize": "1.25rem"
    },
    "animations": {
        "duration": "150ms",
        "easing": "ease-in-out"
    },
    "borders": {
        "radius": {
            "cell": "16px",
            "board": "24px",
            "button": "8px"
        }
    }
}


def load_theme():
    theme_file = "game-theme.json"
    if os.path.exists(theme_file):
        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_THEME
    return DEFAULT_THEME


THEME = load_theme()

WIN_COMBINATIONS = [
    # Rows
    (0, 1, 2, "row-0"),
    (3, 4, 5, "row-1"),
    (6, 7, 8, "row-2"),
    # Columns
    (0, 3, 6, "col-0"),
    (1, 4, 7, "col-1"),
    (2, 5, 8, "col-2"),
    # Diagonals
    (0, 4, 8, "diag-main"),
    (2, 4, 6, "diag-anti")
]

# Theme variables
bg_color = THEME["colors"]["gameplay"]["background"]
board_bg = THEME["colors"]["gameplay"]["boardBackground"]
cell_bg = THEME["colors"]["gameplay"]["cellDefault"]
cell_hover = THEME["colors"]["gameplay"]["cellHover"]
color_x = THEME["colors"]["tokens"]["playerX"]
color_o = THEME["colors"]["tokens"]["playerO"]
neutral_text = THEME["colors"]["tokens"]["neutralText"]
subtle_text = THEME["colors"]["tokens"]["subtleText"]
win_line_color = THEME["colors"]["states"].get("winningLine", "#EF4444")
cell_radius = THEME["borders"]["radius"]["cell"]
board_radius = THEME["borders"]["radius"]["board"]
btn_radius = THEME["borders"]["radius"]["button"]
token_size = THEME["typography"]["tokenSize"]
token_weight = THEME["typography"]["tokenWeight"]


# ==============================================================================
# 2. GAME RULES & PURE RECURSIVE MINIMAX LOGIC
# ==============================================================================
def check_win_condition(board, player):
    """
    Checks if a given player has achieved 3-in-a-row on the board.
    Returns (True, combo) or (False, None).
    """
    for a, b, c, combo_type in WIN_COMBINATIONS:
        if board[a] == player and board[b] == player and board[c] == player:
            return True, (a, b, c, combo_type)
    return False, None


def evaluate_board(board):
    """
    Checks if there's any winner or draw on the board.
    Returns (winner_symbol, combo_info) or (None, None).
    """
    for p in ["X", "O"]:
        won, combo = check_win_condition(board, p)
        if won:
            return p, combo
    if all(cell != " " for cell in board):
        return "Draw", None
    return None, None


def recursive_minimax(board, depth, is_maximizing, ai_shape, human_shape):
    """
    Pure Recursive Minimax AI:
    Evaluates all possible branches recursively.
    1. Base Cases:
       - If AI wins: returns positive reward (10 - depth).
       - If Human wins: returns severe penalty (depth - 10) to force blocking the player.
       - If Draw: returns 0.
    2. Recursive Steps:
       - Maximizing (AI turn): finds move maximizing score.
       - Minimizing (Human turn): anticipates human maximizing their chance to win.
    This guarantees the AI detects player threats and prioritizes blocking the player from winning.
    """
    # 1. Base Terminal Checks (Evaluated Recursively)
    if check_win_condition(board, ai_shape)[0]:
        return (10 - depth), None
    if check_win_condition(board, human_shape)[0]:
        # Heavy penalty for human victory branch -> AI will prioritize blocking
        return (depth - 10), None
    if all(cell != " " for cell in board):
        return 0, None

    empty_indices = [i for i, val in enumerate(board) if val == " "]

    if is_maximizing:
        max_score = -float("inf")
        best_move = None
        for move in empty_indices:
            board[move] = ai_shape
            score, _ = recursive_minimax(board, depth + 1, False, ai_shape, human_shape)
            board[move] = " "  # backtrack
            if score > max_score:
                max_score = score
                best_move = move
        return max_score, best_move
    else:
        min_score = float("inf")
        best_move = None
        for move in empty_indices:
            board[move] = human_shape
            score, _ = recursive_minimax(board, depth + 1, True, ai_shape, human_shape)
            board[move] = " "  # backtrack
            if score < min_score:
                min_score = score
                best_move = move
        return min_score, best_move


def execute_ai_move():
    """Triggers the computer turn using the pure recursive minimax approach."""
    if st.session_state.winner is not None:
        return

    ai_shape = "O" if st.session_state.p1_shape == "X" else "X"
    human_shape = st.session_state.p1_shape

    # Solve optimal defensive/offensive move via recursive minimax
    _, best_move = recursive_minimax(
        board=st.session_state.board,
        depth=0,
        is_maximizing=True,
        ai_shape=ai_shape,
        human_shape=human_shape
    )

    if best_move is not None:
        apply_move(best_move, ai_shape, player_name="Computer")


def apply_move(cell_idx, shape, player_name):
    """Applies a move to the board, records history, and updates win state."""
    st.session_state.board[cell_idx] = shape

    # Record turn history snapshot for highlight playback
    turn_record = {
        "turn": len(st.session_state.history) + 1,
        "player": player_name,
        "shape": shape,
        "cell_idx": cell_idx,
        "row": cell_idx // 3 + 1,
        "col": cell_idx % 3 + 1,
        "board_state": copy.deepcopy(st.session_state.board)
    }
    st.session_state.history.append(turn_record)

    # Check for game completion
    winner, combo = evaluate_board(st.session_state.board)
    if winner is not None:
        st.session_state.winner = winner
        st.session_state.winning_combo = combo
        # Update score
        if winner == "Draw":
            st.session_state.score["draws"] += 1
        elif winner == st.session_state.p1_shape:
            st.session_state.score["p1"] += 1
        else:
            st.session_state.score["p2_or_ai"] += 1
    else:
        # Switch turn
        st.session_state.current_player = "O" if shape == "X" else "X"


def undo_move():
    """
    Undoes player move:
    - In PvP: Undoes the single last turn.
    - In PvC: Undoes the computer's turn and player's turn so player can take back move.
    """
    if not st.session_state.history:
        return

    # If game already ended, reset win state upon undoing
    st.session_state.winner = None
    st.session_state.winning_combo = None
    st.session_state.celebrated = False

    if st.session_state.game_mode == "pvp":
        last_turn = st.session_state.history.pop()
        st.session_state.board[last_turn["cell_idx"]] = " "
        st.session_state.current_player = last_turn["shape"]
    else:
        # Player vs Computer: Undo computer move and player move together if computer just moved
        if len(st.session_state.history) >= 2:
            last = st.session_state.history.pop()
            st.session_state.board[last["cell_idx"]] = " "
            second_last = st.session_state.history.pop()
            st.session_state.board[second_last["cell_idx"]] = " "
            st.session_state.current_player = st.session_state.p1_shape
        elif len(st.session_state.history) == 1:
            last = st.session_state.history.pop()
            st.session_state.board[last["cell_idx"]] = " "
            st.session_state.current_player = st.session_state.p1_shape


def reset_game():
    """Resets board and state for a fresh match."""
    st.session_state.board = [" "] * 9
    st.session_state.history = []
    st.session_state.winner = None
    st.session_state.winning_combo = None
    st.session_state.celebrated = False
    st.session_state.show_highlights = False
    st.session_state.highlight_step = 0
    st.session_state.current_player = "X"


def render_red_strike_svg(combo_info):
    """
    Generates an animated red laser line exactly traversing the winning 3 cells.
    Board size: 100% width/height of the container.
    Coords are mapped percentage-wise for responsive precision.
    """
    if not combo_info:
        return ""

    _, _, _, combo_type = combo_info

    # Responsive coordinates in percentage
    coords = {
        "row-0": ("8%", "18%", "92%", "18%"),
        "row-1": ("8%", "50%", "92%", "50%"),
        "row-2": ("8%", "82%", "92%", "82%"),
        "col-0": ("18%", "8%", "18%", "92%"),
        "col-1": ("50%", "8%", "50%", "92%"),
        "col-2": ("82%", "8%", "82%", "92%"),
        "diag-main": ("10%", "10%", "90%", "90%"),
        "diag-anti": ("90%", "10%", "10%", "90%"),
    }

    x1, y1, x2, y2 = coords.get(combo_type, ("8%", "50%", "92%", "50%"))

    svg_html = f"""
    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 999; overflow: hidden; border-radius: 24px;">
        <svg style="width: 100%; height: 100%;">
            <defs>
                <filter id="neonRedGlow" x="-50%" y="-50%" width="200%" height="200%">
                    <feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="#EF4444" />
                    <feDropShadow dx="0" dy="0" stdDeviation="12" flood-color="#FF0000" />
                </filter>
            </defs>
            <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="winning-laser" filter="url(#neonRedGlow)" />
        </svg>
    </div>
    """
    return svg_html


# ==============================================================================
# 3. STREAMLIT APPLICATION ENTRY POINT
# ==============================================================================
def main():
    st.set_page_config(
        page_title="Retro Arcade Tic-Tac-Toe",
        page_icon="🎮",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # Initialize Session State
    if "board" not in st.session_state:
        st.session_state.board = [" "] * 9
    if "history" not in st.session_state:
        st.session_state.history = []
    if "p1_shape" not in st.session_state:
        st.session_state.p1_shape = "X"
    if "game_mode" not in st.session_state:
        st.session_state.game_mode = "pvp"
    if "current_player" not in st.session_state:
        st.session_state.current_player = "X"
    if "winner" not in st.session_state:
        st.session_state.winner = None
    if "winning_combo" not in st.session_state:
        st.session_state.winning_combo = None
    if "celebrated" not in st.session_state:
        st.session_state.celebrated = False
    if "show_highlights" not in st.session_state:
        st.session_state.show_highlights = False
    if "highlight_step" not in st.session_state:
        st.session_state.highlight_step = 0
    if "score" not in st.session_state:
        st.session_state.score = {"p1": 0, "p2_or_ai": 0, "draws": 0}

    # Generate Dynamic Cell Colors & Glow Styles
    dynamic_cell_styles = []
    for idx in range(9):
        r, c = idx // 3, idx % 3
        val = st.session_state.board[idx]
        is_winning = (st.session_state.winning_combo and idx in st.session_state.winning_combo[:3])

        if is_winning:
            dynamic_cell_styles.append(f"""
            div[class*="st-key-cell_{r}_{c}"] button {{
                border: 3px solid #EF4444 !important;
                background: rgba(239, 68, 68, 0.22) !important;
                box-shadow: 0 0 24px rgba(239, 68, 68, 0.8) !important;
                animation: pulseWinningCell 1s infinite alternate !important;
            }}
            """)

        if val == "X":
            dynamic_cell_styles.append(f"""
            div[class*="st-key-cell_{r}_{c}"] button p {{
                color: {color_x} !important;
                text-shadow: 0 0 16px rgba(56, 189, 248, 0.85) !important;
            }}
            """)
        elif val == "O":
            dynamic_cell_styles.append(f"""
            div[class*="st-key-cell_{r}_{c}"] button p {{
                color: {color_o} !important;
                text-shadow: 0 0 16px rgba(251, 113, 133, 0.85) !important;
            }}
            """)

    extra_cell_css = "\n".join(dynamic_cell_styles)

    # Master CSS Injection
    master_css = f"""
    <style>
    /* Global Background & Typography */
    .stApp {{
        background-color: {bg_color};
        color: {neutral_text};
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }}

    /* Main Container Padding */
    .block-container {{
        padding-top: 1.8rem !important;
        padding-bottom: 3rem !important;
        max-width: 680px !important;
    }}

    /* Header Styling */
    .arcade-header {{
        text-align: center;
        margin-bottom: 12px;
    }}
    .arcade-title {{
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: 2.5px;
        background: linear-gradient(135deg, {color_x} 0%, {color_o} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        text-transform: uppercase;
        filter: drop-shadow(0 0 18px rgba(56, 189, 248, 0.35));
    }}
    .arcade-subtitle {{
        color: {subtle_text};
        font-size: 0.88rem;
        font-weight: 600;
        letter-spacing: 1.5px;
    }}

    /* Quick Setup Bar (Mode & Shape Tabs) */
    .setup-bar {{
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-bottom: 14px;
    }}

    /* Scoreboard Dashboard */
    .score-board {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 16px;
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 8px 18px;
        margin: 0 auto 16px auto;
        max-width: 380px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
    }}
    .score-item {{
        text-align: center;
        flex: 1;
    }}
    .score-label {{
        font-size: 0.75rem;
        color: {subtle_text};
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .score-value {{
        font-size: 1.25rem;
        font-weight: 800;
        color: {neutral_text};
    }}

    /* Current Turn Pill */
    .status-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 14px;
    }}
    .status-pill {{
        background: {board_bg};
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 999px;
        padding: 8px 22px;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45);
    }}
    .status-token {{
        font-size: 1.3rem;
        font-weight: 800;
    }}

    /* Board Container Wrapper */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {board_bg} !important;
        border-radius: {board_radius} !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.65), 0 0 30px rgba(56, 189, 248, 0.06) !important;
        padding: 14px !important;
        position: relative !important;
        max-width: 390px !important;
        margin: 0 auto !important;
    }}

    /* Cell Buttons (Only 3x3 Grid Buttons) */
    div[class*="st-key-cell_"] button {{
        height: 104px !important;
        min-height: 104px !important;
        max-height: 104px !important;
        width: 100% !important;
        border-radius: {cell_radius} !important;
        background-color: {cell_bg} !important;
        border: 2px solid #283548 !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.35) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 150ms ease-in-out !important;
        padding: 0 !important;
    }}
    div[class*="st-key-cell_"] button:hover {{
        background-color: {cell_hover} !important;
        border-color: {color_x} !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(56, 189, 248, 0.3) !important;
    }}
    div[class*="st-key-cell_"] button:active {{
        transform: translateY(1px);
    }}
    div[class*="st-key-cell_"] button p {{
        font-size: 3.4rem !important;
        font-weight: {token_weight} !important;
        line-height: 1 !important;
        margin: 0 !important;
    }}

    /* Laser Strike Line Animation */
    @keyframes strikeLaser {{
        0% {{
            stroke-dashoffset: 500;
            opacity: 0.2;
        }}
        100% {{
            stroke-dashoffset: 0;
            opacity: 1;
        }}
    }}
    .winning-laser {{
        stroke: {win_line_color};
        stroke-width: 9;
        stroke-linecap: round;
        stroke-dasharray: 500;
        animation: strikeLaser 400ms cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }}

    @keyframes pulseWinningCell {{
        from {{ box-shadow: 0 0 10px rgba(239, 68, 68, 0.6); }}
        to {{ box-shadow: 0 0 28px rgba(239, 68, 68, 0.95); }}
    }}

    /* Winning Pop Up Cards */
    .winner-card {{
        background: linear-gradient(145deg, #1A2438, #111827);
        border: 2px solid rgba(239, 68, 68, 0.55);
        border-radius: 16px;
        padding: 16px 20px;
        text-align: center;
        margin: 16px auto;
        max-width: 390px;
        box-shadow: 0 12px 30px rgba(239, 68, 68, 0.25);
    }}
    .winner-card-ai {{
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 2px solid rgba(148, 163, 184, 0.35);
        border-radius: 16px;
        padding: 16px 20px;
        text-align: center;
        margin: 16px auto;
        max-width: 390px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
    }}
    .winner-title {{
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 4px;
    }}
    .winner-desc {{
        font-size: 0.88rem;
        color: {subtle_text};
    }}

    /* Action Control Bar */
    .action-row {{
        max-width: 390px;
        margin: 14px auto 0 auto;
    }}

    /* Mini Replay Board */
    .mini-board {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        width: 220px;
        margin: 14px auto;
        padding: 10px;
        background: #111827;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .mini-cell {{
        height: 58px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #1E293B;
        border-radius: 8px;
        font-size: 1.7rem;
        font-weight: 800;
    }}
    .mini-cell-highlight {{
        background: rgba(56, 189, 248, 0.25) !important;
        border: 2px solid {color_x} !important;
    }}

    /* Dynamic Cell Specific Overrides */
    {extra_cell_css}
    </style>
    """
    st.markdown(master_css, unsafe_allow_html=True)

    # Main Header
    st.markdown(
        """
        <div class="arcade-header">
            <div class="arcade-title">RETRO ARCADE TIC-TAC-TOE</div>
            <div class="arcade-subtitle">OFFLINE MULTIPLAYER &bull; RECURSIVE AI DEFENSE</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Mode and Shape Selector Row (Center-Aligned)
    _, opt_col, _ = st.columns([1, 4, 1])
    with opt_col:
        sel_c1, sel_c2 = st.columns(2)
        with sel_c1:
            mode_opts = ["👥 2 Players (PvP)", "🤖 vs Computer (PvC)"]
            curr_mode_idx = 0 if st.session_state.game_mode == "pvp" else 1
            selected_mode_str = st.selectbox(
                "Mode",
                mode_opts,
                index=curr_mode_idx,
                label_visibility="collapsed"
            )
            selected_mode = "pvp" if "2 Players" in selected_mode_str else "pvc"
            if selected_mode != st.session_state.game_mode:
                st.session_state.game_mode = selected_mode
                reset_game()
                st.rerun()

        with sel_c2:
            shape_opts = ["❌ Play as X", "⭕ Play as O"]
            curr_shape_idx = 0 if st.session_state.p1_shape == "X" else 1
            selected_shape_str = st.selectbox(
                "Shape",
                shape_opts,
                index=curr_shape_idx,
                label_visibility="collapsed"
            )
            selected_shape = "X" if "Play as X" in selected_shape_str else "O"
            if selected_shape != st.session_state.p1_shape:
                st.session_state.p1_shape = selected_shape
                reset_game()
                st.rerun()

    opponent_name = "Player 2" if st.session_state.game_mode == "pvp" else "Computer"
    p2_shape = "O" if st.session_state.p1_shape == "X" else "X"

    # Scoreboard
    st.markdown(
        f"""
        <div class="score-board">
            <div class="score-item">
                <div class="score-label">Player 1 ({st.session_state.p1_shape})</div>
                <div class="score-value" style="color: {color_x if st.session_state.p1_shape == 'X' else color_o};">{st.session_state.score['p1']}</div>
            </div>
            <div class="score-item" style="border-left: 1px solid rgba(255,255,255,0.08); border-right: 1px solid rgba(255,255,255,0.08);">
                <div class="score-label">Draws</div>
                <div class="score-value" style="color: #94A3B8;">{st.session_state.score['draws']}</div>
            </div>
            <div class="score-item">
                <div class="score-label">{opponent_name} ({p2_shape})</div>
                <div class="score-value" style="color: {color_o if p2_shape == 'O' else color_x};">{st.session_state.score['p2_or_ai']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Current Turn Indicator
    if st.session_state.winner is None:
        current_p_name = "Player 1" if st.session_state.current_player == st.session_state.p1_shape else opponent_name
        token_color = color_x if st.session_state.current_player == "X" else color_o

        st.markdown(
            f"""
            <div class="status-container">
                <div class="status-pill">
                    <span style="color: {subtle_text}; font-size: 0.85rem; font-weight: 700;">CURRENT TURN:</span>
                    <span class="status-token" style="color: {token_color};">{st.session_state.current_player}</span>
                    <span style="color: {neutral_text}; font-weight: 700; font-size: 0.92rem;">({current_p_name})</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Centered 3x3 Board
    _, board_col, _ = st.columns([1, 2.2, 1])
    with board_col:
        with st.container(border=True):
            # Render Red Laser Strike Line if someone won
            if st.session_state.winning_combo:
                st.markdown(render_red_strike_svg(st.session_state.winning_combo), unsafe_allow_html=True)

            # 3x3 Buttons with strict container width
            for row in range(3):
                cols = st.columns(3, gap="small")
                for col in range(3):
                    idx = row * 3 + col
                    val = st.session_state.board[idx]
                    label = " " if val == " " else val

                    with cols[col]:
                        btn_clicked = st.button(
                            label,
                            key=f"cell_{row}_{col}",
                            disabled=(val != " " or st.session_state.winner is not None),
                            use_container_width=True
                        )
                        if btn_clicked and val == " " and st.session_state.winner is None:
                            p_name = "Player 1" if st.session_state.current_player == st.session_state.p1_shape else opponent_name
                            apply_move(idx, st.session_state.current_player, p_name)

                            # If PvC mode and next turn is Computer's, execute recursive minimax move
                            if (st.session_state.game_mode == "pvc" and
                                    st.session_state.winner is None and
                                    st.session_state.current_player != st.session_state.p1_shape):
                                execute_ai_move()

                            st.rerun()

    # Action Controls Below Board
    _, act_col, _ = st.columns([1, 2.2, 1])
    with act_col:
        b1, b2 = st.columns(2)
        with b1:
            undo_disabled = len(st.session_state.history) == 0
            if st.button("↩️ Undo Move", disabled=undo_disabled, use_container_width=True):
                undo_move()
                st.rerun()
        with b2:
            if st.button("🔄 Restart Game", use_container_width=True):
                reset_game()
                st.rerun()

    # Winning Pop Up Banner & Celebrations
    if st.session_state.winner is not None:
        winner = st.session_state.winner

        if winner == "Draw":
            st.markdown(
                """
                <div class="winner-card-ai">
                    <div class="winner-title" style="color: #94A3B8;">🤝 IT'S A DRAW!</div>
                    <div class="winner-desc">Both sides played with flawless strategy. No winner this round!</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif st.session_state.game_mode == "pvp":
            winner_name = "Player 1" if winner == st.session_state.p1_shape else "Player 2"
            w_color = color_x if winner == "X" else color_o

            st.markdown(
                f"""
                <div class="winner-card">
                    <div class="winner-title" style="color: {w_color};">🎉 {winner_name} ({winner}) WINS! 🎉</div>
                    <div class="winner-desc">Tremendous victory! Red strike line locked across the winning strike.</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if not st.session_state.celebrated:
                st.balloons()
                st.session_state.celebrated = True
        else:
            if winner == st.session_state.p1_shape:
                st.markdown(
                    f"""
                    <div class="winner-card">
                        <div class="winner-title" style="color: {color_x if winner == 'X' else color_o};">🏆 PLAYER 1 WINS! 🏆</div>
                        <div class="winner-desc">You outsmarted the recursive defense algorithm! Exceptional play!</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if not st.session_state.celebrated:
                    st.balloons()
                    st.session_state.celebrated = True
            else:
                # Mode 2 Computer Wins: NO celebration as requested
                st.markdown(
                    """
                    <div class="winner-card-ai">
                        <div class="winner-title" style="color: #FB7185;">🤖 COMPUTER WINS!</div>
                        <div class="winner-desc">The recursive minimax defense blocked and took the match. Better luck next time!</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Highlight Toggle Button below winning pop up
        _, h_col, _ = st.columns([1, 2.2, 1])
        with h_col:
            highlight_label = "🎬 Hide Highlights" if st.session_state.show_highlights else "🎬 View Move Highlights"
            if st.button(highlight_label, use_container_width=True, type="primary"):
                st.session_state.show_highlights = not st.session_state.show_highlights
                st.session_state.highlight_step = len(st.session_state.history) - 1
                st.rerun()

    # Move Highlights Panel
    if st.session_state.show_highlights and st.session_state.history:
        st.markdown("---")
        st.markdown("### 🎬 Match Turn Highlights & Replay")

        max_steps = len(st.session_state.history) - 1
        selected_step = st.slider(
            "Highlight Step",
            min_value=0,
            max_value=max_steps,
            value=min(st.session_state.highlight_step, max_steps),
            format="Turn %d"
        )
        st.session_state.highlight_step = selected_step

        current_snapshot = st.session_state.history[selected_step]
        active_cell = current_snapshot["cell_idx"]

        nav_c1, nav_c2, nav_c3 = st.columns([1, 2, 1])
        with nav_c1:
            if st.button("◀ Previous", disabled=(selected_step == 0), use_container_width=True):
                st.session_state.highlight_step = max(0, selected_step - 1)
                st.rerun()
        with nav_c2:
            st.markdown(
                f"<div style='text-align: center; font-weight: 700; color: #38BDF8; padding-top: 6px; font-size: 0.9rem;'>"
                f"Turn {selected_step + 1} of {len(st.session_state.history)}: {current_snapshot['player']} marked ({current_snapshot['shape']}) at Row {current_snapshot['row']}, Col {current_snapshot['col']}"
                f"</div>",
                unsafe_allow_html=True
            )
        with nav_c3:
            if st.button("Next ▶", disabled=(selected_step == max_steps), use_container_width=True):
                st.session_state.highlight_step = min(max_steps, selected_step + 1)
                st.rerun()

        mini_cells_html = ""
        for idx, c_val in enumerate(current_snapshot["board_state"]):
            highlight_class = " mini-cell-highlight" if idx == active_cell else ""
            c_color = color_x if c_val == "X" else (color_o if c_val == "O" else subtle_text)
            mini_cells_html += f'<div class="mini-cell{highlight_class}" style="color: {c_color};">{c_val}</div>'

        st.markdown(f'<div class="mini-board">{mini_cells_html}</div>', unsafe_allow_html=True)

        with st.expander("📋 Full Sequence of Turns Log", expanded=False):
            log_rows = []
            for h in st.session_state.history:
                log_rows.append({
                    "Turn #": h["turn"],
                    "Player": h["player"],
                    "Shape": h["shape"],
                    "Board Position": f"Row {h['row']}, Col {h['col']}"
                })
            st.table(log_rows)


if __name__ == "__main__":
    main()
