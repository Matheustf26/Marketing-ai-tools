"""Entry point: sets up the shared shell and runs the page picked in the menu."""

import importlib
import sys

# After a push, Streamlit Cloud can rerun pages with older copies of these modules still in memory.
# Reloading them (dependencies first) on every run keeps pages and core code in step. They are small.
for name in ["core.llm", "core.radar", "core.roi", "core.performance", "core.scout", "core.brief", "core.ui"]:
    if name in sys.modules:
        importlib.reload(sys.modules[name])

from core.ui import footer, navigation

page = navigation()
page.run()
footer()
