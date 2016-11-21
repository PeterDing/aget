# -*- coding: utf-8 -*-

COLOR_TEMPLATE = '\x1b[{}m{}\x1b[0m'

#
# http://misc.flogisoft.com/bash/tip_colors_and_formatting
#
# formatting text
#
# 1    # Bold/Bright
# 2    # Dim
# 4    # Underlined
# 5    # Blink
# 7    # Reverse (invert the foreground and background colors)
# 8    # Hidden (usefull for passwords)
#
#
# 8/16 Colors
#
# Foreground (text)
# 39   # Default foreground color    Default Default
# 30   # Black   Default Black
# 31   # Red Default Red
# 32   # Green   Default Green
# 33   # Yellow  Default Yellow
# 34   # Blue    Default Blue
# 35   # Magenta Default Magenta
# 36   # Cyan    Default Cyan
# 37   # Light gray  Default Light gray
# 90   # Dark gray   Default Dark gray
# 91   # Light red   Default Light red
# 92   # Light green Default Light green
# 93   # Light yellow    Default Light yellow
# 94   # Light blue  Default Light blue
# 95   # Light magenta   Default Light magenta
# 96   # Light cyan  Default Light cyan
# 97   # White   Default White
#
# Background
# 49   # Default background color    Default Default
# 40   # Black   Default Black
# 41   # Red Default Red
# 42   # Green   Default Green
# 43   # Yellow  Default Yellow
# 44   # Blue    Default Blue
# 45   # Magenta Default Magenta
# 46   # Cyan    Default Cyan
# 47   # Light gray  Default Light gray
# 100  # Dark gray   Default Dark gray
# 101  # Light red   Default Light red
# 102  # Light green Default Light green
# 103  # Light yellow    Default Light yellow
# 104  # Light blue  Default Light blue
# 105  # Light magenta   Default Light magenta
# 106  # Light cyan  Default Light cyan107 White


def color_str(msg, codes=None):
    if not msg:
        return msg

    if codes:
        return COLOR_TEMPLATE.format(';'.join([str(e) for e in codes]), msg)
    else:
        return msg


