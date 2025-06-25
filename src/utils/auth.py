import streamlit as st

# Username dan password hardcoded (bisa diubah sesuai kebutuhan)
USERS = {
    "admin": "admin123",
    "user": "user123",
}

def login(username: str, password: str) -> bool:
    """Cek kredensial dan set session jika berhasil."""
    if username in USERS and USERS[username] == password:
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        return True
    else:
        st.session_state["authenticated"] = False
        return False

def logout():
    """Logout user dengan menghapus session autentikasi."""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None

def is_authenticated() -> bool:
    """Cek apakah user sudah login."""
    return st.session_state.get("authenticated", False) 