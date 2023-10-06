def hvr_clr_g(color, mode, gain=20):
    
    hvr_clr = "#"
    if len(color) == 7 and color[0]=="#":
        color = color [1:]

    if mode == "L" or mode == "l" or mode == "Light" or mode == "light":
        for i in range(0, 6, 2): #generate hover color for light mode
            lit_255 = color[i:i+2]    # FF
            if lit_255 == "00":
                hvr_clr += lit_255
                continue
            num_255 = int(lit_255, 16)  # 255
            if num_255-gain < 0 :
                hex_255 = "0x00"
            else:
                hex_255 = hex(num_255-gain)    # 254 -> 0xFE    ,minus 1 to get darker color, then convert it back to hex 
            if len(hex_255[2:]) == 1:
                hex_255 = "0"+hex_255[2:]
                hvr_clr += hex_255
            else:
                hex_255 = hex_255[2:]
                hvr_clr += hex_255
                    
    elif mode == "D" or mode == "d" or mode == "Dark" or mode == "dark":
        for i in range(0, 6, 2): #generate hover color for dark mode
            lit_255 = color[i:i+2]    # 38
            if lit_255 == "FF" or lit_255 == "ff":
                hvr_clr += lit_255
                continue
            num_255 = int(lit_255, 16)  # 56
            if num_255+gain > 255:
                hex_255 = "0xff"
            else:
                hex_255 = hex(num_255+gain)    # 57 -> 0x39    ,plus 1 to get lighter color, then convert it back to hex 
            if len(hex_255[2:]) == 1:
                hex_255 = "0"+hex_255[2:]
                hvr_clr += hex_255
            else:
                hex_255 = hex_255[2:]
                hvr_clr += hex_255    

    return hvr_clr

