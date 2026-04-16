"""Ghost Browser MCP — ASCII banner and color utilities."""

# Ghost art
_GHOST_LINES = [
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⣾⣿⣿⣿⣿⣿⣿⣶⣄⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⠿⢿⣿⣿⣿⣿⣆⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⠁⠀⠿⢿⣿⡿⣿⣿⡆⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣦⣤⣴⣿⠃⠀⠿⣿⡇⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⡿⠋⠁⣿⠟⣿⣿⢿⣧⣤⣴⣿⡇⠀",
    "⠀⠀⠀⠀⢀⣠⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠘⠁⢸⠟⢻⣿⡿⠀⠀",
    "⠀⠀⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣴⣇⢀⣤⠀⠀⠀⠀⠘⣿⠃⠀⠀",
    "⠀⠀⠀⠀⠀⢈⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣴⣿⢀⣴⣾⠇⠀⠀⠀",
    "⠀⠀⣀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀⠀",
    "⠀⠀⠉⠉⠉⠉⣡⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⡿⠟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀",
    "⠀⠀⣴⡾⠿⠿⠿⠛⠋⠉⠀⢸⣿⣿⣿⣿⠿⠋⢸⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⡿⠟⠋⠁⠀⠀⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
]

# Right-side content: logo lines + subtitle
# Vertically centered against the 15-line ghost art:
# ghost=15 lines, right=9 lines → top_pad = (15-9)//2 = 3
_RIGHT_LINES = [
    "",
    "",
    "",
    "  ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗",
    " ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝",
    " ██║  ███╗███████║██║   ██║███████╗   ██║",
    " ██║   ██║██╔══██║██║   ██║╚════██║   ██║",
    " ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║",
    "  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝",
    "",
    "  B R O W S E R   M C P   v0.5.0  —  Test Runner",
    "",
    "",
    "",
    "",
]

DIVIDER = "═" * 60
THIN_DIV = "─" * 60


def _visual_width(s: str) -> int:
    """
    Approximate terminal visual width of a string.
    Braille block chars (U+2800–U+28FF) and box-drawing chars are 1 cell wide.
    Block elements like █ ╗ ╔ etc. are also 1 cell wide in most terminals.
    We just use len() since all chars here are single-width.
    """
    return len(s)


def print_banner() -> None:
    """Print ghost art on the left and logo/subtitle on the right, side by side."""
    gap = 4  # spaces between art and logo

    # Pad ghost lines to equal width
    ghost_width = max(_visual_width(line) for line in _GHOST_LINES)

    total = max(len(_GHOST_LINES), len(_RIGHT_LINES))

    print()
    for i in range(total):
        left = _GHOST_LINES[i] if i < len(_GHOST_LINES) else ""
        right = _RIGHT_LINES[i] if i < len(_RIGHT_LINES) else ""

        padding = ghost_width - _visual_width(left)
        print(left + " " * (padding + gap) + right)
    print()
