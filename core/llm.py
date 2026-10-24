"""Shared Claude client and helpers."""

import os

import anthropic
import streamlit as st

MODEL = "claude-opus-5-5"
# Server-side fallback: if a request is declined, the API retries it on another model.
BETAS = ["server-side-fallback-2026-07-01"]
FALLBACKS = "default"


def _configured_key() -> str | None:
    """Key from Streamlit secrets or the environment, if the deployer set one."""
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY")
    except FileNotFoundError:  # no secrets.toml
        key = None
    return key or os.environ.get("ANTHROPIC_API_KEY")


def get_api_key() -> str | None:
    """Use the configured key, or the one typed in the sidebar."""
    return _configured_key() or st.session_state.get("api_key") or None


def api_key_sidebar() -> None:
    """Show a key field in the sidebar only when no key is configured."""
    if _configured_key():
        st.sidebar.success("Claude API key configured")
        return
    st.sidebar.text_input(
        "Anthropic API key",
        type="password",
        key="api_key",
        help="Used only for this browser session. Get one at console.anthropic.com.",
    )


def get_client() -> anthropic.Anthropic:
    key = get_api_key()
    if not key:
        st.error("Add your Anthropic API key in the sidebar to run this tool.")
        st.stop()
    return anthropic.Anthropic(api_key=key)


def text_of(message) -> str:
    """Join the text blocks of a response."""
    return "\n".join(b.text for b in message.content if b.type == "text").strip()


def _with_fallback(method, **kwargs):
    """Call with server-side fallbacks; retry without them if the account does not support the beta."""
    try:
        return method(betas=BETAS, fallbacks=FALLBACKS, **kwargs)
    except anthropic.BadRequestError as e:
        if "fallback" not in str(e).lower():
            raise
        return method(**kwargs)


def create(client: anthropic.Anthropic, **kwargs):
    return _with_fallback(client.beta.messages.create, model=MODEL, **kwargs)


def parse(client: anthropic.Anthropic, **kwargs):
    return _with_fallback(client.beta.messages.parse, model=MODEL, **kwargs)


def check_refusal(message) -> None:
    if message.stop_reason == "refusal":
        st.error("Claude declined this request. Try rephrasing the input.")
        st.stop()
