import colorsys


def hex_to_hsla(hex_color: str) -> tuple[float, float, float, float]:
    """
    Converts a HEX color string to HSL (Hue, Lightness, Saturation).

    Parameters
    ----------
    hex_color : str
        HEX color string.

    Returns
    -------
    tuple[float, float, float, float]
        Color in HSLA color model (h, l, s, a)
    """
    hex_color = hex_color.lstrip("#")

    if len(hex_color) == 6:
        hex_color += "ff"
    elif len(hex_color) != 8:
        raise ValueError("Invalid HEX format. Must be 6 or 8 characters long.")

    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    a = int(hex_color[6:8], 16) / 255.0

    h, l, s = colorsys.rgb_to_hls(r, g, b)

    return h, s, l, a


def hsla_to_hex(h: float, s: float, l: float, a: float) -> str:
    """
    Converts HSL values back to a HEX color string.

    Parameters
    ----------
    h : float
        Hue value (0.0-1.0).
    l : float
        Lightness value (0.0-1.0).
    s : float
        Saturation value (0.0-1.0).
    a : float
        Alpha value (0.0-1.0)

    Returns
    -------
    str
        Color in HEX format (e.g., "#FF0000").
    """
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    return "#{:02x}{:02x}{:02x}{:02x}".format(
        int(r * 255), int(g * 255), int(b * 255), int(a * 255)
    )


def adjust_lightness(hex_color: str, amount: float) -> str:
    """
    Adjusts the lightness of a given HEX/HEXA color while preserving transparency.

    Parameters
    ----------
    hex_color : str
        The color in hex format (e.g., "#2e88dc").
    amount : float
        Range from -0.5 (darken) to 0.5 (lighten).

    Returns
    -------
    str
        The adjusted HEX color.

    Raises
    ------
    ValueError
        If amount is outside the [-0.5, 0.5] range.
    """
    if not -0.5 <= amount <= 0.5:
        raise ValueError(
            f"Value Error: 'amount' ({amount}) must be between -0.5 and 0.5"
        )

    h, s, l, a = hex_to_hsla(hex_color)

    new_l = max(0.0, min(1.0, l + amount))

    if amount > 0:
        new_s = s * (1 - amount * 0.5)
    else:
        new_s = min(1.0, s * (1 + abs(amount) * 0.5))

    return hsla_to_hex(h, new_s, new_l, a)


def to_hexa(hex_color: str) -> str:
    """
    Converts ARGB hex color to RGBA hex color format.

    Parameters
    ----------
    hex_color : str
        HEX color in ARGB format (e.g., "#FF2E88DC").

    Returns
    -------
    str
        HEX color in RGBA format (e.g., "#2E88DCFF").
    """

    return hex_color[0] + hex_color[3:] + hex_color[1:3]


def to_ahex(hex_color: str) -> str:
    """
    Converts RGBA hex color to ARGB hex color format.

    Parameters
    ----------
    hex_color : str
        HEX color in RGBA format (e.g., "#2E88DCFF").

    Returns
    -------
    str
        HEX color in ARGB format (e.g., "#FF2E88DC").
    """

    return hex_color[0] + hex_color[-2:] + hex_color[1:-2]
