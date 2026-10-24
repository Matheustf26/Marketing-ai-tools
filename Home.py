"""Entry point: sets up the shared shell and runs the page picked in the menu."""

from core.ui import footer, navigation

page = navigation()
page.run()
footer()
