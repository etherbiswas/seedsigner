"""Factory for selecting the appropriate display backend."""

DISPLAY_TYPE__ST7789 = "st7789"
DISPLAY_TYPE__ST7735 = "st7735"
DISPLAY_TYPE__ILI9341 = "ili9341"
DISPLAY_TYPE__ILI9486 = "ili9486"
DISPLAY_TYPE__DESKTOP = "desktop"

ALL_DISPLAY_TYPES = [
    DISPLAY_TYPE__ST7789,
    DISPLAY_TYPE__ST7735,
    DISPLAY_TYPE__ILI9341,
    DISPLAY_TYPE__ILI9486,
    DISPLAY_TYPE__DESKTOP,
]


class DisplayDriver:
    """Wrapper that abstracts away specific display implementations."""

    def __init__(self, display_type: str = DISPLAY_TYPE__ST7789, width: int = None, height: int = None):
        if display_type not in ALL_DISPLAY_TYPES:
            raise ValueError(f"Invalid display type: {display_type}")
        self.display_type = display_type

        if self.display_type == DISPLAY_TYPE__ST7789:
            if width not in [240, 320] or height != 240:
                raise ValueError("ST7789 display only supports 240x240 or 320x240 resolutions")

            if width == 240:
                # TODO: For now the original ST7789 driver has to be used for 240x240.
                # The mpy version below renders incorrectly (almost like each row of pixels
                # is one pixel short, so the entire screen exhibits a diagonal skew).
                from seedsigner.hardware.displays.ST7789 import ST7789
                self.display = ST7789()

            elif width == 320:
                from seedsigner.hardware.displays.st7789_mpy import ST7789, RGB
                # Have to swap width and height; screen is natively 240x320.
                # Use the same Waveshare-style color/gamma tuning as the
                # original 240x240 ST7789 driver while keeping 320x240 geometry.
                waveshare_color_init = (
                    (b"\x11", b"\x00", 150),
                    (b"\x13", b"\x00", 0),
                    (b"\xb6", b"\x0a\x82", 0),
                    (b"\x3a", b"\x55", 10),
                    (b"\xb2", b"\x0c\x0c\x00\x33\x33", 0),
                    (b"\xb7", b"\x35", 0),
                    (b"\xbb", b"\x19", 0),
                    (b"\xc0", b"\x2c", 0),
                    (b"\xc2", b"\x01", 0),
                    (b"\xc3", b"\x12", 0),
                    (b"\xc4", b"\x20", 0),
                    (b"\xc6", b"\x0f", 0),
                    (b"\xd0", b"\xa4\xa1", 0),
                    (b"\xe0", b"\xd0\x04\x0d\x11\x13\x2b\x3f\x54\x4c\x18\x0d\x0b\x1f\x23", 0),
                    (b"\xe1", b"\xd0\x04\x0c\x11\x13\x2c\x3f\x44\x51\x2f\x1f\x1f\x20\x23", 0),
                    (b"\x21", b"\x00", 0),
                    (b"\x29", b"\x00", 120),
                )
                self.display = ST7789(width=height, height=width, color_order=RGB, custom_init=waveshare_color_init)

        elif self.display_type == DISPLAY_TYPE__ST7735:
            if width != 128 or height != 128:
                raise ValueError("ST7735 display only supports 128x128 resolution")
            from seedsigner.hardware.displays.ST7735 import ST7735
            self.display = ST7735()

        elif self.display_type == DISPLAY_TYPE__ILI9341:
            from seedsigner.hardware.displays.ili9341 import ILI9341
            self.display = ILI9341()
            self.display.begin()

        elif self.display_type == DISPLAY_TYPE__ILI9486:
            # TODO: improve performance of ili9486 driver
            raise Exception("ILI9486 display not implemented yet")

        elif self.display_type == DISPLAY_TYPE__DESKTOP:
            try:
                from seedsigner.hardware.displays.desktop_display import DesktopDisplay
            except ModuleNotFoundError as e:
                raise ModuleNotFoundError(
                    "Desktop display requires pygame; install requirements-desktop.txt"
                ) from e

            # Desktop display can support arbitrary sizes; defaults are handled by caller
            self.display = DesktopDisplay(width=width, height=height)


    def __str__(self):
        return f"DisplayDriver(display_type={self.display_type}, width={self.width}, height={self.height})"


    @property
    def width(self):
        return self.display.width


    @property
    def height(self):
        return self.display.height


    def invert(self, enabled: bool = True):
        """Invert how the display interprets colors"""
        self.display.invert(enabled)


    def show_image(self, image, x_start: int = 0, y_start: int = 0):
        self.display.show_image(image, x_start, y_start)


    def close(self):
        close_fn = getattr(self.display, "close", None)
        if callable(close_fn):
            close_fn()
