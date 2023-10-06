LIGHT_MODE = {
    'text'              : "#030303", 
    'background'        : "#ebebeb", 
    'primary'           : "#9c9c9c", 
    'secondary'         : "#d4d4d4", 
    'accent'            : "#399583", 
    'accent_btn'        : "#61bdab", 
    'accent_S_btn'      : "#4c4c4c",
    'activated_frame'   : "#dfdfdf", 
    'unactivated_frame' : "#e6e6e6"  
}

DARK_MODE = {
    'text'              : "#ebebeb", 
    'background'        : "#030303", 
    'primary'           : "#9c9c9c", 
    'secondary'         : "#080808", 
    'accent'            : "#4dc9b0", 
    'accent_btn'        : "#25a188", 
    'accent_S_btn'      : "#b3b3b3",
    'activated_frame'   : "#1a1a1a", 
    'unactivated_frame' : "#040404"  
}

def hex_to_0x(hexcolor):
    color = '0x00'
    for i in range(7,0,-2):
        h = hexcolor[i:i+2]
        color = color+h
    return int(color, 16)

TITLE_BAR_HEX_COLORS = {
    "light" : hex_to_0x(LIGHT_MODE['background']),
    "dark"  : hex_to_0x(DARK_MODE['background'])
}

FONT    = "Space Mono"
FONT_B  = "Space Mono Bold"
FONT_I  = "Space Mono Italic"
FONT_BI = "Space Mono Bold Italic" 