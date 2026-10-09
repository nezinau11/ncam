from maix import image
from defs import *
import filters

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def btext_pos(bpos, label, scale):
    size = image.string_size(label, scale=scale)    
    px = bpos[0] + (bpos[2] - size.width()) // 2
    py = bpos[1] + (bpos[3] - size.height()) // 2
    return (px, py)

def draw_btn(img, btn, col=TCOLOR, bgcol=MCOLOR):
    tpos = btext_pos(btn['pos'], btn['label'], btn['scale'])
    img.draw_rect(btn['pos'][0], btn['pos'][1], btn['pos'][2], btn['pos'][3], bgcol)

    img.draw_string(tpos[0], tpos[1], btn['label'], col, scale=btn['scale'])

def draw_res_btn(img, btn, res, col=TCOLOR, bgcol=MCOLOR):
    w = str(res[0])
    h = str(res[1])
    wtpos = btext_pos(btn['pos'], w, btn['scale'])
    htpos = btext_pos(btn['pos'], h, btn['scale'])
    img.draw_rect(btn['pos'][0], btn['pos'][1], btn['pos'][2], btn['pos'][3], bgcol)

    img.draw_string(wtpos[0], btn['pos'][1] + 10, w, col, scale=btn['scale'])
    img.draw_string(htpos[0], btn['pos'][1] + 45, h, col, scale=btn['scale'])

def draw_pm_btns(img, btn, btn2, text, text_scale, t_pos, col=TCOLOR, bgcol=MCOLOR):
    pl = '+'
    mi = '-'
    plpos = btext_pos(btn2['pos'], pl, btn['scale'])
    mipos = btext_pos(btn['pos'], mi, btn['scale'])
    tpos = btext_pos(btn['pos'], text, text_scale)
    img.draw_rect(btn['pos'][0], btn['pos'][1], btn['pos'][2], btn['pos'][3], bgcol)
    img.draw_rect(btn2['pos'][0], btn2['pos'][1], btn2['pos'][2], btn2['pos'][3], bgcol)
    img.draw_string(mipos[0] - 20, mipos[1], mi, col, scale=btn['scale'])
    img.draw_string(plpos[0] + 20, plpos[1], pl, col, scale=btn2['scale'])
    img.draw_string(tpos[0] + t_pos, mipos[1] - 5, text, col, scale=text_scale)

def draw_onoff_btn(img, btn, state, col=TCOLOR, bgcol=MCOLOR):
    img.draw_rect(btn['pos'][0], btn['pos'][1], btn['pos'][2], btn['pos'][3], bgcol)
    if state:
        label = 'on'
    else:
        label = 'off'
    tpos = btext_pos(btn['pos'], label, btn['scale'])
    img.draw_string(tpos[0], tpos[1] + 10, label, col, scale=btn['scale'])
    img.draw_string(btn['pos'][0] + 4, btn['pos'][1] + 4, btn['label'], col, scale=btn['scale'])