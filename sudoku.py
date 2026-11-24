import streamlit as st
import numpy as np
import random
import copy

# Konfigurasi halaman
st.set_page_config(page_title="Sudoku Streamlit", page_icon="🧩", layout="centered")

# --- LOGIKA GENERATOR & SOLVER SUDOKU ---

def is_valid(board, row, col, num):
    # Cek baris & kolom
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    # Cek kotak 3x3
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve_sudoku(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def generate_sudoku(difficulty):
    board = np.zeros((9, 9), dtype=int)
    solve_sudoku(board)
    solution = copy.deepcopy(board)
    
    # Tentukan jumlah sel yang dihapus berdasarkan tingkat kesulitan
    attempts = {"Mudah": 30, "Sedang": 42, "Sulit": 52}[difficulty]
    
    while attempts > 0:
        row, col = random.randint(0, 8), random.randint(0, 8)
        if board[row][col] != 0:
            board[row][col] = 0
            attempts -= 1
            
    return board, solution

# --- INISIALISASI STATE ---

def init_game(difficulty="Sedang"):
    puzzle, solution = generate_sudoku(difficulty)
    st.session_state.puzzle = puzzle
    st.session_state.solution = solution
    st.session_state.user_board = copy.deepcopy(puzzle)
    st.session_state.difficulty = difficulty
    st.session_state.message = ""

if "puzzle" not in st.session_state:
    init_game()

# --- ANTARMUKA PENGGUNA (UI) ---

st.title("🧩 Game Sudoku")

# Sidebar untuk pengaturan
with st.sidebar:
    st.header("Pengaturan Game")
    diff = st.selectbox("Tingkat Kesulitan", ["Mudah", "Sedang", "Sulit"], index=1)
    if st.button("🔄 Game Baru", use_container_width=True):
        init_game(diff)
        st.rerun()

    st.divider()
    if st.button("💡 Beri Bantuan (Hint)", use_container_width=True):
        empty_cells = [
            (r, c) for r in range(9) for c in range(9)
            if st.session_state.user_board[r][c] != st.session_state.solution[r][c]
        ]
        if empty_cells:
            r, c = random.choice(empty_cells)
            st.session_state.user_board[r][c] = st.session_state.solution[r][c]
            st.session_state.puzzle[r][c] = st.session_state.solution[r][c] # Kunci sel bantuan
            st.rerun()

# Styling CSS agar tampilan grid menyerupai papan Sudoku asli
st.markdown("""
<style>
    div[data-testid="stNumberInput"] input {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        padding: 4px;
    }
    /* Hilangkan tombol + dan - pada number input */
    button[data-testid="stNumberInputStepUp"],
    button[data-testid="stNumberInputStepDown"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Render Papan 9x9
for r in range(9):
    # Tambahkan garis pemisah horizontal setiap 3 baris
    if r > 0 and r % 3 == 0:
        st.markdown("<hr style='margin: 6px 0; border: 1.5px solid #555;'>", unsafe_allow_html=True)
        
    cols = st.columns([1, 1, 1, 0.15, 1, 1, 1, 0.15, 1, 1, 1])
    col_idx = 0
    
    for c in range(9):
        # Tambahkan spasi pemisah vertikal setiap 3 kolom
        if c > 0 and c % 3 == 0:
            col_idx += 1
            
        with cols[col_idx]:
            is_fixed = st.session_state.puzzle[r][c] != 0
            current_val = int(st.session_state.user_board[r][c])
            
            if is_fixed:
                # Angka bawaan soal ditampilkan dalam kotak statis
                st.markdown(
                    f"<div style='text-align:center; background-color:#262730; color:#FAFAFA; "
                    f"padding:7px 0; border-radius:5px; font-weight:bold; font-size:18px; "
                    f"border: 1px solid #444;'>{current_val}</div>",
                    unsafe_allow_html=True
                )
            else:
                # Sel kosong yang bisa diisi pemain (0 dianggap kosong)
                val = st.number_input(
                    label=f"cell_{r}_{c}",
                    min_value=0,
                    max_value=9,
                    value=current_val,
                    step=1,
                    key=f"input_{r}_{c}_{st.session_state.difficulty}",
                    label_visibility="collapsed"
                )
                st.session_state.user_board[r][c] = val
        col_idx += 1

st.write("")

# Tombol Aksi di bagian bawah
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("✅ Periksa Jawaban", type="primary", use_container_width=True):
        if np.array_equal(st.session_state.user_board, st.session_state.solution):
            st.success("🎉 Selamat! Jawaban Anda benar semua!")
            st.balloons()
        elif 0 in st.session_state.user_board:
            st.warning("⚠️ Papan belum terisi penuh. Isi angka 1-9 pada semua kotak kosong (0 = kosong).")
        else:
            st.error("❌ Masih ada angka yang salah. Silakan periksa kembali!")

with col_btn2:
    if st.button("🏳️ Menyerah & Lihat Solusi", use_container_width=True):
        st.session_state.user_board = copy.deepcopy(st.session_state.solution)
        st.rerun()
