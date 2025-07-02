"""Main Streamlit application entry point for Conduit UI."""

import streamlit as st

from conduit.ui.pages.atlassian import show_atlassian_config

st.set_page_config(
    page_title="Conduit",
    page_icon="🔗",
    layout="wide",
)


def main():
    st.title("Conduit")

    # Sidebar navigation
    page = st.sidebar.selectbox("Navigation", ["Atlassian Configuration"])

    if page == "Atlassian Configuration":
        show_atlassian_config()


if __name__ == "__main__":
    main()
