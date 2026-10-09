from maix import camera, image, display, app, time, touchscreen, key
from maix import sys as msys
from maix.ext_dev import pmu
import os, sys, glob, threading, pickle
import cv2
import piexif
import numpy as np
from datetime import datetime

import filters
from ui import *
from utils import *
from defs import *

VERSION = '0.3.0'

### globals
if app.app_id() == 'MaixPy':
    DEBUG = True
else:
    DEBUG = False

date = datetime.today().strftime('%Y-%m-%d')
photo_num = 0
init_dir = False

fps_main = 0

cboxw = 170
cboxh = 170
cboxz = 3

on_key = False
boot_key = True

photo_taken_t = None
palette_cc = None
curr_photo = None

res_w = 0
res_h = 0
resize_preview = True

on = True

battery = pmu.PMU()

cam_conf_file = 'cconf.dat'

app_path = app.get_app_path()
data_path = app.get_app_data_path()
temp_path = app.get_tmp_path()
photo_path = app.get_picture_path()

if DEBUG:
    app_path = '/maixapp/apps/ncam/'
    data_path = '/maixapp/apps/ncam/data/'

cam_conf_file_path = os.path.abspath(os.path.join(data_path, cam_conf_file))
image.load_font('ncb', os.path.join(os.path.join(app_path, 'fonts'), 'NotCourierSans-Bold.ttf'), size = 16)
image.set_default_font('ncb')

palettes_path = os.path.abspath(os.path.join(app_path, 'palettes'))
#palettes_path = '/tmp/maixpy_run/palettes'
os.chdir(palettes_path)
for pal in glob.glob('*.npy'):
    palette_table.append(os.path.splitext(pal)[0])
palette_table.sort()
palette_table_len = len(palette_table)

class CameraSettings:
    def __init__(self):
        self.cformat = image.Format.FMT_YVU420SP # image.Format.FMT_GRAYSCALE, image.Format.FMT_RGB888
        self.aemode = camera.AeMode.Auto
        self.awbmode = camera.AwbMode.Auto
        self.wb = [0.0682, 0, 0, 0.04897] # r, gr, gb, and b
        self.exposure = int((1/1200) * 1000000)
        self.exp_table_item = 0
        # self.gain = -1 # duplicate of iso
        self.iso = 100
        self.iso_table_item = 0
        self.luma = -1
        self.contrast = -1
        self.saturation = -1
        #
        self.menu = 0
        self.fzoom = 0
        self.ai_isp = 0
        self.filter = 0
        self.saturation_adj = 0.0
        self.filter_table_item = 0
        self.ord_m_table_item = 0
        self.ord_m_art_table_item = 0
        self.res_table_item = 4
        self.palette_table_item = 0
        self.cont = 0
        self.w = res_table[self.res_table_item][0]
        self.h = res_table[self.res_table_item][1]

def on_key(key_id, state):
    global on_key
    global boot_key
    global on
    if key_id == key.Keys.KEY_OK:
        if state == key.State.KEY_PRESSED:
            if boot_key:
                boot_key = False
                return
            if not on:
                on = True
                return
            on_key = True
        if state == key.State.KEY_LONG_PRESSED:
            pass
        if state == key.State.KEY_RELEASED:
            #on_key = False
            pass

def ui_thread(ui_disp, ts, cam):
    global palette_cc
    global on
    uiw = ui_disp.width()
    uih = ui_disp.height()
    bg_color = image.Color.from_rgba(0, 0, 0, 0)

    while not app.need_exit():
        img = image.Image(uiw, uih, ui_disp.format(), bg=bg_color)

        img.draw_string(600, 3, f'{battery.get_bat_percent()}%', TCOLOR, scale=1)
        # draw photo taken indicator border
        ctime = time.ticks_ms()
        if photo_taken_t and ctime <= photo_taken_t + 1500:
            t = (ctime - photo_taken_t) // 6
            img.draw_rect(0, 0,uiw, uih, color=image.Color.from_rgb(t, t, t), thickness=20)
        # write current palette or dithering pattern
        if curr_photo:
            img.draw_string(180, 50, curr_photo, TCOLOR, scale=2)

        on_btn = {'label' : 'cam', 'scale' : 1.8, 'pos' : [0, 0, 80, 60]}
        draw_onoff_btn(img, on_btn, on, bgcol=MCOLOR_t)
        exit_btn = {'label' : 'exit', 'scale' : 1.5, 'pos' : [uiw - 80, 0, 80, 60]}
        draw_btn(img, exit_btn, bgcol=MCOLOR_t)

        if on:
            menu_btn = {'label' : 'menu', 'scale' : 1.8, 'pos' : [0, uih - 160, 80, 70]}
            draw_onoff_btn(img, menu_btn, cs.menu)

            if cs.menu:
                fzoom_btn = {'label' : 'FZ', 'scale' : 2, 'pos' : [90, uih - 380, 80, 70]}
                draw_onoff_btn(img, fzoom_btn, cs.fzoom)

                isp_btn = {'label' : 'IP', 'scale' : 2, 'pos' : [190, uih - 380, 80, 70]}
                draw_onoff_btn(img, isp_btn, cs.ai_isp)

                res_btn = {'label' : '1200x1200', 'scale' : 1.4, 'pos' : [280, uih - 380, 80, 70]}
                draw_res_btn(img, res_btn, res_table[cs.res_table_item])

                sat_btn = {'label' : 'sat 0%', 'scale' : 1.4, 'pos' : [90, uih - 290, 80, 70]}
                draw_res_btn(img, sat_btn, ('sat', f'{int(cs.saturation_adj * 100)}%'))

            filter_btn = {'label' : 'F', 'scale' : 2, 'pos' : [uiw - 80, uih - 70, 80, 70]}
            draw_onoff_btn(img, filter_btn, cs.filter)

            if cs.filter:
                filter_sel_btn = {'label' : 'F', 'scale' : 2, 'pos' : [uiw - 80, uih - 160, 80, 70]}
                filter_sel_btn['label'] = filter_table[cs.filter_table_item][0]
                draw_btn(img, filter_sel_btn)

                ord_sel_btn = {'label' : 'O', 'scale' : 1.7, 'pos' : [uiw - 80, uih - 250, 80, 70]}
                if filter_table[cs.filter_table_item][0] == 'ord':
                    ord_sel_btn['label'] = ord_m_table[cs.ord_m_table_item][0]
                    draw_btn(img, ord_sel_btn)
                elif filter_table[cs.filter_table_item][0] == 'art':
                    ord_sel_btn['label'] = ord_m_art_table[cs.ord_m_art_table_item][0]
                    draw_btn(img, ord_sel_btn)

                palette_sel_btn = {'label' : '4c_CMYK', 'scale' : 1.4, 'pos' : [uiw - 80, uih - 340, 80, 70]}
                draw_res_btn(img, palette_sel_btn, palette_table[cs.palette_table_item].split('_'))

            aemode_btn = {'label' : 'AE', 'scale' : 4, 'pos' : [0, uih - 70, 80, 70]}
            iso_btn = {'label' : '9999', 'scale' : 1.5, 'pos' : [140, uih - 70, 80, 70]}
            iso_btn2 = {'label' : '9999', 'scale' : 1.5, 'pos' : [220, uih - 70, 80, 70]}
            exp_btn = {'label' : '9999', 'scale' : 1.5, 'pos' : [340, uih - 70, 80, 70]}
            exp_btn2 = {'label' : '9999', 'scale' : 1.5, 'pos' : [420, uih - 70, 80, 70]}
            if cs.aemode == camera.AeMode.Auto:
                aemode_btn['label'] = 'AE'
            elif cs.aemode == camera.AeMode.Manual:
                aemode_btn['label'] = 'M'
                draw_pm_btns(img, iso_btn, iso_btn2, f'{cs.iso}', 1.6, 40)
                draw_pm_btns(img, exp_btn, exp_btn2, f'{exp_table[cs.exp_table_item][0]}', 1.2, 40)
            draw_btn(img, aemode_btn)

        x, y, pressed = ts.read()
        if pressed:
            if on:
                if is_in_button(x, y, exit_btn['pos']):
                    app.set_exit_flag(True)

                if cs.menu:
                    if is_in_button(x, y, fzoom_btn['pos']):
                        cs.fzoom = not cs.fzoom
                        save_settings()
                        time.sleep_ms(100)

                    if is_in_button(x, y, isp_btn['pos']):
                        cs.ai_isp = not cs.ai_isp
                        app.set_sys_config_kv('npu', 'ai_isp', str(int(cs.ai_isp)))
                        save_settings()
                        time.sleep_ms(100)

                    if is_in_button(x, y, res_btn['pos']):
                        cs.res_table_item += 1
                        if cs.res_table_item >= res_table_len:
                            cs.res_table_item = 0
                        save_settings()
                        time.sleep_ms(100)

                    if is_in_button(x, y, sat_btn['pos']):
                        cs.saturation_adj = round(cs.saturation_adj + 0.2, 1)
                        if cs.saturation_adj > 1.0:
                            cs.saturation_adj = 0.0
                        save_settings()
                        time.sleep_ms(100)

                if is_in_button(x, y, aemode_btn['pos']):
                    if cs.aemode == camera.AeMode.Auto:
                        cs.aemode = camera.AeMode.Manual
                        cam.exp_mode(camera.AeMode.Manual)
                        cam.iso(cs.iso)
                        cam.exposure(cs.exposure)
                    elif cs.aemode == camera.AeMode.Manual:
                        cs.aemode = camera.AeMode.Auto
                        cam.exp_mode(camera.AeMode.Auto)
                    save_settings()
                    time.sleep_ms(100)

                if is_in_button(x, y, iso_btn['pos']) and cs.aemode == camera.AeMode.Manual:
                    cs.iso_table_item -= 1
                    if cs.iso_table_item < 0:
                        cs.iso_table_item = iso_table_len - 1
                    cam.iso(iso_table[cs.iso_table_item])
                    cs.iso = iso_table[cs.iso_table_item]
                    save_settings()
                    time.sleep_ms(100)
                
                if is_in_button(x, y, iso_btn2['pos']) and cs.aemode == camera.AeMode.Manual:
                    cs.iso_table_item += 1
                    if cs.iso_table_item >= iso_table_len:
                        cs.iso_table_item = 0
                    cam.iso(iso_table[cs.iso_table_item])
                    cs.iso = iso_table[cs.iso_table_item]
                    save_settings()
                    time.sleep_ms(100)

                if is_in_button(x, y, exp_btn['pos']) and cs.aemode == camera.AeMode.Manual:
                    cs.exp_table_item -= 1
                    if cs.exp_table_item < 0:
                        cs.exp_table_item = exp_table_len - 1
                    exp = int(exp_table[cs.exp_table_item][1] * 1000000)
                    cam.exposure(exp)
                    cs.exposure = exp
                    save_settings()
                    time.sleep_ms(100)

                if is_in_button(x, y, exp_btn2['pos']) and cs.aemode == camera.AeMode.Manual:
                    cs.exp_table_item += 1
                    if cs.exp_table_item >= exp_table_len:
                        cs.exp_table_item = 0
                    exp = int(exp_table[cs.exp_table_item][1] * 1000000)
                    cam.exposure(exp)
                    cs.exposure = exp
                    save_settings()
                    time.sleep_ms(100)

                if cs.filter:
                    if is_in_button(x, y, filter_sel_btn['pos']):
                        cs.filter_table_item += 1
                        if cs.filter_table_item >= filter_table_len:
                            cs.filter_table_item = 0
                        save_settings()
                        time.sleep_ms(100)
                    if filter_table[cs.filter_table_item][0] == 'ord':
                        if is_in_button(x, y, ord_sel_btn['pos']):
                            cs.ord_m_table_item += 1
                            if cs.ord_m_table_item >= ord_m_table_len:
                                cs.ord_m_table_item = 0
                            save_settings()
                            time.sleep_ms(100)
                    elif filter_table[cs.filter_table_item][0] == 'art':
                        if is_in_button(x, y, ord_sel_btn['pos']):
                            cs.ord_m_art_table_item += 1
                            if cs.ord_m_art_table_item >= ord_m_art_table_len:
                                cs.ord_m_art_table_item = 0
                            save_settings()
                            time.sleep_ms(100)
                    if is_in_button(x, y, palette_sel_btn['pos']):
                        cs.palette_table_item += 1
                        if cs.palette_table_item >= palette_table_len:
                            cs.palette_table_item = 0
                        if palette_table[cs.palette_table_item] != '0c_all':
                            palette_cc = load_palette(palette_table[cs.palette_table_item])
                        save_settings()
                        time.sleep_ms(100)

                if is_in_button(x, y, filter_btn['pos']):
                    cs.filter = not cs.filter
                    save_settings()
                    time.sleep_ms(100)

                if is_in_button(x, y, menu_btn['pos']):
                    cs.menu = not cs.menu
                    save_settings()
                    time.sleep_ms(100)

            if is_in_button(x, y, on_btn['pos']):
                on = False
                time.sleep_ms(100)

        time.sleep_ms(10)
        ui_disp.show(img)

def save_settings():
    with open(cam_conf_file_path, 'wb') as f:
        pickle.dump(cs, f)

def setup_camera(cs):
    app.set_sys_config_kv('npu', 'ai_isp', str(int(cs.ai_isp)))
    cs.w = res_table[cs.res_table_item][0]
    cs.h = res_table[cs.res_table_item][1]
    cam = camera.Camera(cs.w, cs.h, cs.cformat)
    cam.skip_frames(10)
    cam.exp_mode(cs.aemode)
    cam.awb_mode(cs.awbmode)
    if cs.aemode == camera.AeMode.Manual:
        cam.exposure(int(exp_table[cs.exp_table_item][1] * 1000000))
        cam.iso(cs.iso)
        cam.luma(cs.luma)
        cam.saturation(cs.saturation)
        cam.constrast(cs.contrast)
    if cs.awbmode == camera.AwbMode.Manual:
        cam.set_wb_gain(cs.awb_gain)
    return cam

def take_photo(img, cam, fimg=None, ftype=None, fpalette=None, fpattern=None):
    global init_dir
    global photo_num
    if not init_dir:
        os.chdir(photo_path)
        if date not in os.listdir():
            os.mkdir(date)
            os.chdir(date)
            photo_num = 0
        else:
            os.chdir(date)
            photos = glob.glob('*.jpg')
            photo_num = len(photos)
        init_dir = True
    if img is not None:
        photo_num += 1
        photo_f = f'P{photo_num:05d}.jpg'
        img.save(photo_f, quality=95)
        if cs.aemode == camera.AeMode.Auto:
            aemode = 'Auto'
            iso = cam.iso(-1)
            exposure = f'1/{int((1 / cam.exposure(-1)) * 100000)}'
        else:
            aemode = 'Manual'
            iso = cs.iso
            exposure = exp_table[cs.exp_table_item][0]

        zeroth_ifd = {
            piexif.ImageIFD.Make: u'MaixCam2',
            piexif.ImageIFD.Software: f'ncam v{VERSION} https://nothing.lt'
        }
        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: datetime.today().strftime('%Y:%m:%d %H:%M:%S'),
            piexif.ExifIFD.UserComment: f'AE mode {aemode}, {iso} ISO, {exposure}s, AI ISP {bool(cs.ai_isp)}'.encode('utf8')
        }
        exif_dict = {'0th': zeroth_ifd, 'Exif': exif_ifd}
        piexif.insert(piexif.dump(exif_dict), photo_f)
    if fimg is not None:
        if ftype == 'ord':
            fimg_f = f'P{photo_num:05d}_ord_{fpattern}_{fpalette}.png'
        else:
            fimg_f = f'P{photo_num:05d}_{ftype}_{fpalette}.png'          
        cv2.imwrite(fimg_f, fimg)

def load_palette(name):
    #start = time.time_ms()
    palette_path = os.path.abspath(os.path.join(palettes_path, f'{name}.npy'))
    ccube = np.load(palette_path)
    #ccube = np.load(palette_path)['arr_0']
    #end = time.time_ms()
    #print(f'load palette: {(end - start) / 1000}')
    return ccube

def image_proc(img):
    if cs.saturation_adj != 0.0:
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        sat = cs.saturation_adj + 1
        hsv_img[:, :, 1] = cv2.convertScaleAbs(hsv_img[:, :, 1], alpha=sat)
        img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
    return img

### do stuff
key_obj = key.Key(on_key)

if os.path.exists(cam_conf_file_path):
    with open(cam_conf_file_path, 'rb') as f:
        try:
            cs = pickle.load(f)
        except:
            cs = CameraSettings()
else:
    cs = CameraSettings()

ts = touchscreen.TouchScreen()
disp = display.Display()
ui_disp = disp.add_channel() 
cam = setup_camera(cs)

th = threading.Thread(target=ui_thread, args=(ui_disp, ts, cam))
th.daemon = True
th.start()

asp_ratio = cs.h / cs.w
if cs.w > 640:
    if asp_ratio < 1:
        res_w = 640
        res_h = int(640 * asp_ratio)
    elif asp_ratio == 1.0:
        res_w = 480
        res_h = 480
else:
    res_w = cs.w
    res_h = cs.h

while not app.need_exit():
    img_f = None
    bgr_img = None
    ftype = [None]
    fpattern = None
    if on:
        img = cam.read(block=False)
        if img is not None:
            if cs.filter:
                bgr_img = nv21_to_bgr(np.frombuffer(img.to_bytes(copy=True), dtype=np.uint8), cs.w, cs.h)
                bgr_img = image_proc(bgr_img)
                #start = time.time_ms()
                fpalette = palette_table[cs.palette_table_item]
                ftype = filter_table[cs.filter_table_item]

                if ftype[0] == 'art':
                    ftype = ord_m_art_table[cs.ord_m_art_table_item]
                    fpattern = ord_m_art_table[cs.ord_m_art_table_item]
                else:
                    fpattern = ord_m_table[cs.ord_m_table_item]

                if palette_cc is None:
                    if fpalette == '0c_all':
                        fpalette = palette_table[1]
                    palette_cc = load_palette(fpalette)

                if resize_preview and ftype[0].find('exp') == -1:
                        res_img = cv2.resize(bgr_img, (res_w, res_h), cv2.INTER_AREA)
                        fimg = ftype[1](res_img, pattern=fpattern[1], palette=palette_cc)
                else:
                    fimg = ftype[1](bgr_img, pattern=fpattern[1], palette=palette_cc)
                #end = time.time_ms()
                #print(f'apply filter ms: {(end - start) / 1000}')
                img_f = image.cv2image(fimg, bgr=True, copy=True)
                disp.show(img_f)

            elif not cs.filter and cs.fzoom:
                bgr_img = nv21_to_bgr(np.frombuffer(img.to_bytes(copy=True), dtype=np.uint8), cs.w, cs.h)
                bgr_img = image_proc(bgr_img)
                width = int(cs.w // 2 - cboxw // 2)
                height = int(cs.h // 2 - cboxh // 2)
                crop_img = bgr_img[width : width + cboxw, height : height + cboxh]
                crop_img = focus_peaking(crop_img)
                crop_img = cv2.resize(crop_img, (cboxw * cboxz, cboxh * cboxz), cv2.INTER_NEAREST)
                img_f = image.cv2image(crop_img, bgr=True, copy=False)
                img = image.cv2image(bgr_img, bgr=True, copy=False)
                img.draw_rect(width, height, cboxw, cboxh, color=TCOLOR, thickness=2)
                img.draw_image(0, 0, img_f)
                disp.show(img)

            else:
                bgr_img = nv21_to_bgr(np.frombuffer(img.to_bytes(copy=True), dtype=np.uint8), cs.w, cs.h)
                bgr_img = image_proc(bgr_img)
                img = image.cv2image(bgr_img, bgr=True, copy=False)
                disp.show(img)

            if on_key and not boot_key:
                photo_taken_t = time.ticks_ms()
                take_photo(img, cam)
                if ftype[0] == 'ord' and fpattern[0] == 'all':
                    for ord_i in ord_m_table:
                        if ord_i[0] == 'all' or fpalette == '0c_all':
                            continue
                        fimg = filters.ord_d(bgr_img, pattern=ord_i[1], palette=palette_cc)
                        curr_photo = f'{ftype[0]} {ord_i[0]} {fpalette}'
                        take_photo(None, cam, fimg, ftype[0], fpalette, ord_i[0])
                    curr_photo = None
                elif cs.filter and fpalette == '0c_all':
                    for pal in palette_table:
                        if pal == '0c_all':
                            continue
                        if ftype == 'ord' and fpattern[0] == 'all':
                            continue
                        palette = load_palette(pal)
                        fimg = ftype[1](bgr_img, pattern=fpattern[1], palette=palette)
                        curr_photo = f'{ftype[0]} {pal}'
                        take_photo(None, cam, fimg, ftype[0], pal, fpattern[0])
                    curr_photo = None
                elif cs.filter:
                    fimg = ftype[1](bgr_img, pattern=fpattern[1], palette=palette_cc)
                    take_photo(None, cam, fimg, ftype[0], fpalette, fpattern[0])
                on_key = False

    time.sleep_ms(10)
