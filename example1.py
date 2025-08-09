import streamlit as st

st.title("Nested Buttons Example")

if 'show_second_buttons' not in st.session_state:
    st.session_state.show_second_buttons = False
  
if st.button("First Button"):
    st.session_state.show_second_buttons = True

if st.session_state.show_second_buttons:
     st.write("Revealed")
     if st.button("Second Button"):
        st.write("Second Button Clicked")
        st.session_state.show_second_buttons = False