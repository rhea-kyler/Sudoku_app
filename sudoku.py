import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import random
import copy
import json

st.set_page_config(page_title="Sudoku Pro", page_icon="🧩", layout="centered")

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; max-width: 520px; }
    header, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    sr, sc = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[sr + i][sc + j] == num:
                return False
    return True

def solve_sudoku(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for n in nums:
                    if is_valid(board, r, c, n):
                        board[r][c] = n
                        if solve_sudoku(board):
                            return True
                        board[r][c] = 0
                return False
    return True

def generate_puzzle(difficulty):
    board = np.zeros((9, 9), dtype=int)
    solve_sudoku(board)
    solution = copy.deepcopy(board)
    holes = {"Mudah": 32, "Sedang": 42, "Sulit": 50, "Ahli": 56}[difficulty]
    while holes > 0:
        r, c = random.randint(0, 8), random.randint(0, 8)
        if board[r][c] != 0:
            board[r][c] = 0
            holes -= 1
    return board.tolist(), solution.tolist()

if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Sedang"
    st.session_state.puzzle, st.session_state.solution = generate_puzzle("Sedang")

col_title, col_diff, col_new = st.columns([2, 1.5, 1.2])
with col_title:
    st.markdown("### 🧩 Sudoku")
with col_diff:
    levels = ["Mudah", "Sedang", "Sulit", "Ahli"]
    selected_diff = st.selectbox("Level", levels, index=levels.index(st.session_state.difficulty), label_visibility="collapsed")
with col_new:
    if st.button("Baru", use_container_width=True, type="primary") or selected_diff != st.session_state.difficulty:
        st.session_state.difficulty = selected_diff
        st.session_state.puzzle, st.session_state.solution = generate_puzzle(selected_diff)
        st.rerun()

# Membaca file game.html eksternal
with open("game.html", "r", encoding="utf-8") as f:
    html_template = f.read()

html_code = (
    html_template
    .replace("__DIFFICULTY__", st.session_state.difficulty)
    .replace("__PUZZLE_JSON__", json.dumps(st.session_state.puzzle))
    .replace("__SOLUTION_JSON__", json.dumps(st.session_state.solution))
)

components.html(html_code, height=640)
