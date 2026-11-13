import streamlit as st

st.set_page_config(page_title="Previs Ideora", page_icon="🎨")

st.title("Previs Ideora")
st.write("Hello, studio co-pilot!")
st.markdown(
    '<img src="app/static/strokes/stroke-01.webp" width="300">',
    unsafe_allow_html=True,
)