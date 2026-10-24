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


class ClaudeError(RuntimeError):
    """An API problem the person running the app can fix, with a plain explanation."""


def _explain(e: anthropic.APIStatusError) -> ClaudeError | None:
    text = str(e).lower()
    if "credit balance" in text:
        return ClaudeError("The Claude account is out of credits. Add credits at console.anthropic.com → Billing.")
    if isinstance(e, anthropic.AuthenticationError):
        return ClaudeError("The Claude API key is invalid or was deleted. Update ANTHROPIC_API_KEY in the app secrets.")
    if isinstance(e, anthropic.RateLimitError):
        return ClaudeError("Too many requests right now. Wait a minute and try again.")
    return None


def _with_fallback(method, **kwargs):
    """Call with server-side fallbacks; retry without them if the account does not support the beta."""
    try:
        try:
            return method(betas=BETAS, fallbacks=FALLBACKS, **kwargs)
        except anthropic.BadRequestError as e:
            if "fallback" not in str(e).lower():
                raise
            return method(**kwargs)
    except anthropic.APIStatusError as e:
        friendly = _explain(e)
        if friendly is None:
            raise
        raise friendly from e


def create(client: anthropic.Anthropic, **kwargs):
    return _with_fallback(client.beta.messages.create, model=MODEL, **kwargs)


def stream(client: anthropic.Anthropic, on_event=None, **kwargs):
    """Stream a request, passing each event to on_event, and return the final message."""

    def run(**kw):
        with client.beta.messages.stream(model=MODEL, **kw) as events:
            for event in events:
                if on_event:
                    on_event(event)
            return events.get_final_message()

    return _with_fallback(run, **kwargs)


def parse(client: anthropic.Anthropic, **kwargs):
    return _with_fallback(client.beta.messages.parse, model=MODEL, **kwargs)


def check_refusal(message) -> None:
    if message.stop_reason == "refusal":
        st.error("Claude declined this request. Try rephrasing the input.")
        st.stop()
