import streamlit as st
import time
import string
from itertools import product

# --- CONFIGURATION ---
REAL_KEY = "ECON" 
# This is the 'Secret' we want to reveal
SECRET_RIDDLE = "I AM THE HAND THAT YOU CANNOT SEE" 

def vigenere_decrypt(ciphertext, key):
    decrypted = ""
    key = key.upper()
    key_indices = [ord(k) - ord('A') for k in key]
    k_len = len(key_indices)
    
    char_count = 0
    for char in ciphertext:
        if char.isalpha():
            # Standard Vigenère decryption math: (C - K) % 26
            shift = key_indices[char_count % k_len]
            decrypted_char = chr((ord(char.upper()) - ord('A') - shift) % 26 + ord('A'))
            decrypted += decrypted_char
            char_count += 1
        else:
            decrypted += char # Keep spaces/punctuation as-is
    return decrypted

# We pre-encrypt the riddle so the brute force has something to work on
# (This is like the 'intercepted' packet)
def vigenere_encrypt(plaintext, key):
    encrypted = ""
    key = key.upper()
    key_indices = [ord(k) - ord('A') for k in key]
    k_len = len(key_indices)
    
    char_count = 0
    for char in plaintext:
        if char.isalpha():
            shift = key_indices[char_count % k_len]
            encrypted_char = chr((ord(char.upper()) - ord('A') + shift) % 26 + ord('A'))
            encrypted += encrypted_char
            char_count += 1
        else:
            encrypted += char
    return encrypted

ENCRYPTED_MSG = vigenere_encrypt(SECRET_RIDDLE, REAL_KEY)

# --- SESSION STATE ---
if 'attempt_count' not in st.session_state:
    st.session_state.attempt_count = 0
    st.session_state.found_key = False
    st.session_state.final_message = ""

st.title("🕵️ OPERATION: BRUTE FORCE")

if not st.session_state.found_key:
    st.info(f"**Intercepted Cipher:** `{ENCRYPTED_MSG}`")
    placeholder = st.empty()
    
    # --- BRUTE FORCE ENGINE ---
    chars = string.ascii_uppercase
    all_combinations = product(chars, repeat=len(REAL_KEY))
    
    chunk_size = 1 # Adjust for classroom speed
    start_idx = st.session_state.attempt_count
    
    current_key = ""
    for i, combo in enumerate(all_combinations):
        if i < start_idx: continue
        if i >= start_idx + chunk_size: break
            
        current_key = "".join(combo)
        
        if current_key == REAL_KEY:
            st.session_state.found_key = True
            st.session_state.final_message = vigenere_decrypt(ENCRYPTED_MSG, REAL_KEY)
            st.rerun()
            
        st.session_state.attempt_count += 1

    # Show live guessing progress
    with placeholder.container():
        st.warning(f"**CPU ATTACK IN PROGRESS...**")
        st.code(f"Testing Key: {current_key} | Result: {vigenere_decrypt(ENCRYPTED_MSG, current_key)}")
        progress = min(st.session_state.attempt_count / (26**len(REAL_KEY)), 1.0)
        st.progress(progress)
    
    time.sleep(0.01)
    st.rerun()

else:
    # --- SUCCESS STATE ---
    st.balloons()
    st.success(f"### ✅ ACCESS GRANTED: KEY '{REAL_KEY}' DISCOVERED")
    st.markdown(f"""
    > ## "{st.session_state.final_message}"
    
    **Computational Report:** System cracked at attempt **{st.session_state.attempt_count}**.
    """)
    
    if st.button("Reset System"):
        st.session_state.attempt_count = 0
        st.session_state.found_key = False
        st.rerun()