import numpy as np
from PIL import Image
import time
import glob
import os
from skimage.color import rgb2lab, deltaE_ciede2000

def calcc_bgr(palette):
    name = palette[0]
    pal_rgb = np.array(palette[1], dtype=np.uint8)
    num_colors = len(pal_rgb)

    pal_bgr = pal_rgb[:, ::-1]
    
    try:
        precalculated = np.load(f'{name}.npy')
    except Exception:
        print(f'Precalculating BGR color cube for {name} using CIELAB...')

        pal_rgb_norm = pal_rgb.reshape(1, -1, 3) / 255.0
        pal_lab = rgb2lab(pal_rgb_norm).reshape(-1, 3)

        b, g, r = np.mgrid[0:256, 0:256, 0:256]
        bgr_cube = np.stack([b, g, r], axis=-1).astype(np.float32) / 255.0

        rgb_cube = bgr_cube[..., ::-1]
        lab_cube = rgb2lab(rgb_cube)

        min_dist = np.full((256, 256, 256), np.inf, dtype=np.float32)
        closest_indices = np.zeros((256, 256, 256), dtype=np.uint8)
        
        for idx in range(num_colors):
            color_lab = pal_lab[idx]
            dist = np.sum((lab_cube - color_lab) ** 2, axis=-1)
            
            mask = dist < min_dist
            min_dist[mask] = dist[mask]
            closest_indices[mask] = idx

        precalculated = pal_bgr[closest_indices]

        np.save(f'{name}.npy', precalculated)
        print('Calculation complete and cached.')
        
    return precalculated

def calcc_bgr_ciede2000(palette):
    name = palette[0]
    pal_rgb = np.array(palette[1], dtype=np.uint8)
    num_colors = len(pal_rgb)
    pal_bgr = pal_rgb[:, ::-1]
    
    try:
        precalculated = np.load(f'{name}.npy')
    except Exception:
        print(f'Precalculating BGR color cube for {name} using CIEDE2000...')

        pal_rgb_norm = pal_rgb.reshape(1, -1, 3) / 255.0
        pal_lab = rgb2lab(pal_rgb_norm).reshape(-1, 3)

        b, g, r = np.mgrid[0:256, 0:256, 0:256]
        bgr_cube = np.stack([b, g, r], axis=-1).astype(np.float32) / 255.0

        rgb_cube = bgr_cube[..., ::-1]
        lab_cube = rgb2lab(rgb_cube)

        min_dist = np.full((256, 256, 256), np.inf, dtype=np.float32)
        closest_indices = np.zeros((256, 256, 256), dtype=np.uint8)
        
        for idx in range(num_colors):
            color_lab = pal_lab[idx].reshape(1, 1, 1, 3)

            dist = deltaE_ciede2000(lab_cube, color_lab)
            
            mask = dist < min_dist
            min_dist[mask] = dist[mask]
            closest_indices[mask] = idx
            
        precalculated = pal_bgr[closest_indices]
        
        np.save(f'{name}.npy', precalculated)
        #np.savez_compressed(f'{name}.npz', precalculated)
        print('Calculation complete and cached.')
        
    return precalculated
    
def quantize_cube_parallel(img, ccube):
    h, w, _ = img.shape
    new_image = np.empty((h, w, 3), dtype=np.uint8)
    
    for i in range(h):
        for j in range(w):
            b = img[i, j, 0]
            g = img[i, j, 1]
            r = img[i, j, 2]
            
            new_image[i, j, 0] = ccube[b, g, r, 0]
            new_image[i, j, 1] = ccube[b, g, r, 1]
            new_image[i, j, 2] = ccube[b, g, r, 2]
            
    return new_image
        
def run(im):
    palette_table = []
    os.chdir('palettes')
    for pal in glob.glob('*.txt'):
        colors = []
        with open(pal, 'r', encoding='utf-8-sig') as pf:
            lines = pf.readlines()
            for l in lines:
                l = l.strip()
                if not l or l.startswith(';'):
                    continue
                col = tuple(int(l[i:i+2], 16) for i in (0, 2, 4, 6))[1:]
                colors.append(col)
        print(f'Loaded {len(col)} colors from {pal}') 
        palette_table.append([os.path.splitext(pal)[0], colors])
    for pal in palette_table:
        ccube_ciede = calcc_bgr_ciede2000(pal)
        if im.any():
            im = im[:, :, ::-1]        
            result_ciede = quantize_cube_parallel(im, ccube_ciede)
            result_ciede = result_ciede[:, :, ::-1]
            print('Applying to test image')
            Image.fromarray(result_ciede).save(f'test_out_{pal[0]}.png')
            
try:
    im = Image.open('test.jpg')
    im = np.asarray(im)
except:
    im = None
        
run(im)
