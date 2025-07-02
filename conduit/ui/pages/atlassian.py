"""Atlassian configuration display page."""

import streamlit as st

from conduit.core.config import load_config


def mask_api_token(token: str) -> str:
    """Mask API token showing only first and last 4 characters."""
    if len(token) <= 8:
        return "*" * len(token)
    return f"{token[:4]}{'*' * (len(token)-8)}{token[-4:]}"


def show_site_config(title: str, config_section, default_alias: str):
    """Display configuration for either Jira or Confluence section."""
    st.subheader(title)

    for alias, site in config_section.sites.items():
        with st.expander(
            f"{alias} {'(Default)' if alias == default_alias else ''}", expanded=True
        ):
            cols = st.columns(2)

            # Column 1: Basic info
            with cols[0]:
                st.text("Site URL")
                st.code(site.url, language=None)
                st.text("Email")
                st.code(site.email, language=None)

            # Column 2: API Token (masked)
            with cols[1]:
                st.text("API Token")
                st.code(mask_api_token(site.api_token), language=None)

            # Add copy button for URL
            st.button(
                "Copy URL",
                key=f"copy_{alias}_{title.lower()}_url",
                on_click=lambda: st.write(site.url),
            )


def show_atlassian_config():
    """Display Atlassian configuration page."""
    st.header("Atlassian Configuration")

    try:
        # Use existing config loading mechanism
        config = load_config()

        # Display Jira configuration
        show_site_config("Jira Sites", config.jira, config.jira.default_site_alias)

        st.markdown("---")

        # Display Confluence configuration
        show_site_config(
            "Confluence Sites", config.confluence, config.confluence.default_site_alias
        )

    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        st.info("Please ensure your configuration file is properly set up.")
