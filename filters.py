import numpy as np
import numba

BAYER_MATRIX_8X8 = (1 / 64) * np.array([
    [0, 48, 12, 60, 3, 51, 15, 63],
    [32, 16, 44, 28, 35, 19, 47, 31],
    [8, 56, 4, 52, 11, 59, 7, 55],
    [40, 24, 36, 20, 43, 27, 39, 23],
    [2, 50, 14, 62, 1, 49, 13, 61],
    [34, 18, 46, 30, 33, 17, 45, 29],
    [10, 58, 6, 54, 9, 57, 5, 53],
    [42, 26, 38, 22, 41, 25, 37, 21]
]) * 255

BAYER_MATRIX_4X4 = (1 / 16) * np.array([
    [0, 12, 3, 15],
    [8, 4, 11, 7],
    [2, 14, 1, 13],
    [10, 6, 9, 5]
]) * 255

BAYER_MATRIX_4X4_2 = (1 / 16) * np.array([
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5]
]) * 255

BAYER_MATRIX_2X2 = (1 / 4) * np.array([
    [0, 3],
    [2, 1]
]) * 255

HALFTONE_4X4 = (1 / 16) * np.array([
    [15, 11, 7, 13],
    [5, 3, 1, 8],
    [9, 0, 2, 4],
    [12, 6, 10, 14]
]) * 255

DIAGONAL = (1 / 64) * np.array([
    [0, 8, 16, 24, 32, 40, 48, 56],
    [57, 1, 9, 17, 25, 33, 41, 49],
    [50, 58, 2, 10, 18, 26, 34, 42],
    [43, 51, 59, 3, 11, 19, 27, 35],
    [36, 44, 52, 60, 4, 12, 20, 28],
    [29, 37, 45, 53, 61, 5, 13, 21],
    [22, 30, 38, 46, 54, 62, 6, 14],
    [15, 23, 31, 39, 47, 55, 63, 7],
]) * 255

BRICK = (1 / 64) * np.array([
    [0, 16, 28, 38, 41, 33, 22, 8],
    [44, 1, 17, 29, 34, 23, 9, 49],
    [54, 45, 2, 18, 24, 10, 50, 57],
    [60, 42, 35, 3, 11, 30, 39, 62],
    [43, 36, 25, 12, 4, 19, 31, 40],
    [37, 26, 13, 51, 46, 5, 20, 32],
    [27, 14, 52, 58, 55, 47, 6, 21],
    [15, 53, 59, 61, 63, 56, 48, 7],
]) * 255

RHOMBUS = (1 / 64) * np.array([
    [0, 2, 4, 6, 8, 10, 12, 14],
    [22, 24, 26, 28, 30, 32, 16, 43],
    [44, 46, 48, 50, 34, 18, 41, 57],
    [58, 60, 52, 36, 20, 39, 55, 63],
    [62, 54, 38, 21, 37, 53, 61, 9],
    [56, 40, 19, 35, 51, 49, 47, 45],
    [42, 17, 33, 31, 29, 27, 25, 23],
    [15, 13, 11, 9, 7, 5, 3, 1],
]) * 255

HALFTONE = (1 / 64) * np.array([
    [60, 52, 48, 32, 36, 44, 53, 61],
    [56, 40, 28, 16, 20, 24, 41, 57],
    [47, 27, 12,  4,  8, 13, 29, 49],
    [39, 23, 11,  0,  1,  5, 17, 33],
    [35, 19,  7,  2,  3,  9, 21, 37],
    [51, 30, 15, 10,  6, 14, 25, 45],
    [59, 43, 26, 22, 18, 31, 42, 54],
    [63, 55, 46, 38, 34, 50, 58, 62],
]) * 255

HALFTONE_R = 255 - HALFTONE

ZIG_ZAG = (1 / 49) * np.array([
    [26, 22, 17, 15, 12, 30, 45],
    [48, 44, 24, 19,  7, 10, 32],
    [42, 37, 28,  6,  1, 14, 34],
    [39, 35,  4,  0,  3, 36, 40],
    [33, 13,  5,  2, 27, 38, 41],
    [31,  9,  8, 20, 23, 43, 47],
    [46, 29, 11, 16, 18, 21, 25],
]) * 255

CLUSTERED_DOT_DIAG_8x8 = (1 / 64) * np.array([
    [24, 10, 12, 26, 35, 47, 49, 37],
    [8,  0,  2, 14, 45, 59, 61, 51],
    [22,  6,  4, 16, 43, 57, 63, 53],
    [30, 20, 18, 28, 33, 41, 55, 39],
    [34, 46, 48, 36, 25, 11, 13, 27],
    [44, 58, 60, 50,  9,  1,  3, 15],
    [42, 56, 62, 52, 23,  7,  5, 17],
    [32, 40, 54, 38, 31, 21, 19, 29],
]) * 255

CLUSTERED_DOT_DIAG_6x6 = (1 / 36) * np.array([
    [8,  6,  7,  9, 11, 10],
    [5,  0,  1, 12, 17, 16],
    [4,  3,  2, 13, 14, 15],
    [9, 11, 10,  8,  6,  8],
    [12, 17, 16,  5,  0,  1],
    [13, 14, 15,  4,  3,  2],
]) * 255

CLUSTERED_DOT_DIAG_16x16 = (1 / 256) * np.array([
    [63,  58,  50,  40,  41,  51,  59, 60, 64,  69,  77,  87,  86,  76,  68, 67],
    [57,  33,  27,  18,  19,  28,  34, 52, 70,  94, 100, 109, 108,  99,  93, 75],
    [49,  26,  13,  11,  12,  15,  29, 44, 78, 101, 114, 116, 115, 112,  98, 83],
    [39,  17,   4,   3,   2,   9,  20, 42, 87, 110, 123, 124, 125, 118, 107, 85],
    [38,  16,   5,   0,   1,  10,  21, 43, 89, 111, 122, 127, 126, 117, 106, 84],
    [48,  25,   8,   6,   7,  14,  30, 45, 79, 102, 119, 121, 120, 113,  97, 82],
    [56,  32,  24,  23,  22,  31,  35, 53, 71,  95, 103, 104, 105,  96,  92, 74],
    [62,  55,  47,  37,  36,  46,  54, 61, 65,  72,  80,  90,  91,  81,  73, 66],
    [64,  69,  77,  87,  86,  76,  68, 67, 63,  58,  50,  40,  41,  51,  59, 60],
    [70,  94, 100, 109, 108,  99,  93, 75, 57,  33,  27,  18,  19,  28,  34, 52],
    [78, 101, 114, 116, 115, 112,  98, 83, 49,  26,  13,  11,  12,  15,  29, 44],
    [87, 110, 123, 124, 125, 118, 107, 85, 39,  17,   4,   3,   2,   9,  20, 42],
    [89, 111, 122, 127, 126, 117, 106, 84, 38,  16,   5,   0,   1,  10,  21, 43],
    [79, 102, 119, 121, 120, 113,  97, 82, 48,  25,   8,   6,   7,  14,  30, 45],
    [71,  95, 103, 104, 105,  96,  92, 74, 56,  32,  24,  23,  22,  31,  35, 53],
    [65,  72,  80,  90,  91,  81,  73, 66, 62,  55,  47,  37,  36,  46,  54, 61],
]) * 255

CLUSTERED_DOT_8x8 = (1 / 64) * np.array([
[3,  9, 17, 27, 25, 15,  7,  1],
[11, 29, 38, 46, 44, 36, 23,  5],
[19, 40, 52, 58, 56, 50, 34, 13],
[31, 48, 60, 63, 62, 54, 42, 21],
[30, 47, 59, 63, 61, 53, 41, 20],
[18, 39, 51, 57, 55, 49, 33, 12],
[10, 28, 37, 45, 43, 35, 22,  4],
[2,  8, 16, 26, 24, 14,  6,  0],
]) * 255

@numba.njit(cache=True)
def quantize_ccube(img, ccube):
    h, w, _ = img.shape
    new_image = np.empty((h, w, 3), dtype=np.uint8)
    
    for i in numba.prange(h):
        for j in range(w):
            b = img[i, j, 0]
            g = img[i, j, 1]
            r = img[i, j, 2]
            new_image[i, j, 0] = ccube[b, g , r, 0]
            new_image[i, j, 1] = ccube[b, g, r, 1]
            new_image[i, j, 2] = ccube[b, g, r, 2]
    return new_image

@numba.njit(cache=True)
def _dither_diffusion(img_float, ccube, dmethod):
    h, w, _ = img_float.shape
    new_image = np.empty((h, w, 3), dtype=np.uint8)
    
    if dmethod == 'floyd-steinberg':  # Floyd-Steinberg
        offsets = np.array([[0, 1], [1, -1], [1, 0], [1, 1]], dtype=np.int32)
        weights = np.array([7/16, 3/16, 5/16, 1/16], dtype=np.float32)
    elif dmethod == 'atkinson':  # Atkinson
        offsets = np.array([[0, 1], [0, 2], [1, -1], [1, 0], [1, 1], [2, 0]], dtype=np.int32)
        weights = np.array([1/8, 1/8, 1/8, 1/8, 1/8, 1/8], dtype=np.float32)
    elif dmethod == 'stucki':  # Stucki
        offsets = np.array([[0, 1], [0, 2], [1, -2], [1, -1], [1, 0], [1, 1], [1, 2], [2, -2], [2, -1], [2, 0], [2, 1], [2, 2]], dtype=np.int32)
        weights = np.array([8/42, 4/42, 2/42, 4/42, 8/42, 4/42, 2/42, 1/42, 2/42, 4/42, 2/42, 1/42], dtype=np.float32)              

    num_offsets = len(weights)

    for i in range(h):
        if i % 2 == 0:
            dir_x = 1
        else:
            dir_x = -1
            
        for step in range(w):
            j = step if dir_x == 1 else (w - 1 - step)

            val_b = min(max(img_float[i, j, 0], 0.0), 255.0)
            val_g = min(max(img_float[i, j, 1], 0.0), 255.0)
            val_r = min(max(img_float[i, j, 2], 0.0), 255.0)

            b = int(val_b)
            g = int(val_g)
            r = int(val_r)

            out_b = ccube[b, g, r, 0]
            out_g = ccube[b, g, r, 1]
            out_r = ccube[b, g, r, 2]
            
            new_image[i, j, 0] = out_b
            new_image[i, j, 1] = out_g
            new_image[i, j, 2] = out_r

            err_b = val_b - out_b
            err_g = val_g - out_g
            err_r = val_r - out_r

            for k in range(num_offsets):
                dy = offsets[k, 0]
                dx = offsets[k, 1] * dir_x
                
                ny = i + dy
                nx = j + dx

                if 0 <= ny < h and 0 <= nx < w:
                    w_val = weights[k]
                    img_float[ny, nx, 0] += err_b * w_val
                    img_float[ny, nx, 1] += err_g * w_val
                    img_float[ny, nx, 2] += err_r * w_val
                    
    return new_image

@numba.njit(parallel=True, cache=True)
def _ordered_dither(img, ccube, bayer_matrix, midpoint, spread):
    h, w, _ = img.shape
    bh, bw = bayer_matrix.shape
    new_image = np.empty((h, w, 3), dtype=np.uint8)
    
    for i in numba.prange(h):
        for j in range(w):
            bayer_val = bayer_matrix[i % bh, j % bw]
            
            offset = (bayer_val - midpoint) * spread
            
            val_b = np.float32(img[i, j, 0]) + offset
            val_g = np.float32(img[i, j, 1]) + offset
            val_r = np.float32(img[i, j, 2]) + offset
            
            b = int(min(max(val_b, 0.0), 255.0))
            g = int(min(max(val_g, 0.0), 255.0))
            r = int(min(max(val_r, 0.0), 255.0))
            
            new_image[i, j, 0] = ccube[b, g, r, 0]
            new_image[i, j, 1] = ccube[b, g, r, 1]
            new_image[i, j, 2] = ccube[b, g, r, 2]
            
    return new_image

@numba.njit(parallel=True, cache=True)
def _lum_dither(img, ccube, mat_dark, mat_light, midpoint, spread, lum=170.0):
    h, w, _ = img.shape

    dh, dw = mat_dark.shape
    lh, lw = mat_light.shape
    
    new_image = np.empty((h, w, 3), dtype=np.uint8)
    
    for i in numba.prange(h):
        row_d = i % dh
        row_l = i % lh
        
        col_d = 0
        col_l = 0
        
        for j in range(w):
            b_pixel = np.float32(img[i, j, 0])
            g_pixel = np.float32(img[i, j, 1])
            r_pixel = np.float32(img[i, j, 2])

            luminance = 0.299 * r_pixel + 0.587 * g_pixel + 0.114 * b_pixel

            if luminance < lum:
                bayer_val = mat_dark[row_d, col_d]
            else:
                bayer_val = mat_light[row_l, col_l]

            col_d += 1
            if col_d == dw:
                col_d = 0
                
            col_l += 1
            if col_l == lw:
                col_l = 0

            offset = (bayer_val - midpoint) * spread
            
            val_b = b_pixel + offset
            val_g = g_pixel + offset
            val_r = r_pixel + offset
            
            b = int(min(max(val_b, 0.0), 255.0))
            g = int(min(max(val_g, 0.0), 255.0))
            r = int(min(max(val_r, 0.0), 255.0))
            
            new_image[i, j, 0] = ccube[b, g, r, 0]
            new_image[i, j, 1] = ccube[b, g, r, 1]
            new_image[i, j, 2] = ccube[b, g, r, 2]
            
    return new_image

@numba.njit(parallel=True, cache=True)
def _sat_dither(img, ccube, mat_neutral, mat_vibrant, midpoint, spread, sat=0.15):
    h, w, _ = img.shape

    nh, nw = mat_neutral.shape
    vh, vw = mat_vibrant.shape
    
    new_image = np.empty((h, w, 3), dtype=np.uint8)
    
    for i in numba.prange(h):
        row_n = i % nh
        row_v = i % vh

        col_n = 0
        col_v = 0
        
        for j in range(w):
            b_pixel = np.float32(img[i, j, 0])
            g_pixel = np.float32(img[i, j, 1])
            r_pixel = np.float32(img[i, j, 2])

            max_val = max(r_pixel, g_pixel, b_pixel)
            min_val = min(r_pixel, g_pixel, b_pixel)

            saturation = (max_val - min_val) / max_val if max_val > 0.0 else 0.0
            #saturation = (max_val - min_val) / 255.0 if max_val > 0.0 else 0.0

            if saturation < sat:
                bayer_val = mat_neutral[row_n, col_n]
            else:
                bayer_val = mat_vibrant[row_v, col_v]

            col_n += 1
            if col_n == nw:
                col_n = 0
                
            col_v += 1
            if col_v == vw:
                col_v = 0

            offset = (bayer_val - midpoint) * spread
            
            val_b = b_pixel + offset
            val_g = g_pixel + offset
            val_r = r_pixel + offset
            
            b = int(min(max(val_b, 0.0), 255.0))
            g = int(min(max(val_g, 0.0), 255.0))
            r = int(min(max(val_r, 0.0), 255.0))

            new_image[i, j, 0] = ccube[b, g, r, 0]
            new_image[i, j, 1] = ccube[b, g, r, 1]
            new_image[i, j, 2] = ccube[b, g, r, 2]
            
    return new_image

def ordered_dither(img, ccube, bayer_matrix, spread=1.0):
    bayer_f32 = bayer_matrix.astype(np.float32)

    midpoint = np.mean(bayer_f32)
    
    return _ordered_dither(img, ccube, bayer_f32, midpoint, np.float32(spread))

def make_diagonal_line_matrix(size=16, angle_deg=45, frequency=2.0):
    y, x = np.meshgrid(np.arange(size), np.arange(size))
    angle_rad = np.radians(angle_deg)
    
    projected = x * np.cos(angle_rad) + y * np.sin(angle_rad)
    
    wave = np.sin(projected * (2 * np.pi * frequency / size))
    
    matrix = (wave - wave.min()) / (wave.max() - wave.min()) * 255
    return matrix.astype(np.float32)

def make_hexagonal_matrix(size=16, frequency=1.5):
    y, x = np.meshgrid(np.arange(size), np.arange(size))

    scale = (2 * np.pi * frequency) / size
    x_scaled = x * scale
    y_scaled = y * scale

    val = (np.cos(x_scaled) + 
           np.cos(0.5 * x_scaled + np.sqrt(3)/2 * y_scaled) + 
           np.cos(-0.5 * x_scaled + np.sqrt(3)/2 * y_scaled))
    
    matrix = (val - val.min()) / (val.max() - val.min()) * 255
    return matrix.astype(np.float32)

def make_halftone_matrix(size=32, dot_grid=1, p_norm=2.0, aspect_ratio=1.0, angle_deg=0.0):
    cell_size = size / dot_grid
    y, x = np.meshgrid(np.arange(size), np.arange(size))

    local_y = ((y + 0.5) % cell_size) / cell_size - 0.5
    local_x = ((x + 0.5) % cell_size) / cell_size - 0.5

    local_x = local_x * aspect_ratio
    
    if angle_deg != 0.0:
        rad = np.radians(angle_deg)
        cos_a, sin_a = np.cos(rad), np.sin(rad)
        rot_x = local_x * cos_a - local_y * sin_a
        rot_y = local_x * sin_a + local_y * cos_a
        local_x, local_y = rot_x, rot_y
        
    if p_norm == np.inf:
        dist = np.maximum(np.abs(local_x), np.abs(local_y))
    else:
        dist = (np.abs(local_x)**p_norm + np.abs(local_y)**p_norm)**(1.0 / p_norm)
        
    flat_dist = dist.flatten()
    sorted_indices = np.argsort(flat_dist)
    
    num_pixels = size * size
    thresholds = np.empty(num_pixels, dtype=np.float32)
    
    for rank, idx in enumerate(sorted_indices):
        thresholds[idx] = (rank / (num_pixels - 1)) * 255.0
        
    return thresholds.reshape((size, size))

def ord_d(image, pattern=None, palette=None):
    return ordered_dither(image, palette, pattern, spread=1.0)

def exp1_d(image, pattern=None, palette=None):
    return _lum_dither(image, palette, CLUSTERED_DOT_DIAG_16x16, HALFTONE_4X4, 127.5, 0.5, 40)

def exp2_d(image, pattern=None, palette=None):
    return _sat_dither(image, palette, CLUSTERED_DOT_DIAG_16x16, HALFTONE_4X4, 127.5, 1.0, 0.3)

def exp3_d(image, pattern=None, palette=None):
    diag = make_diagonal_line_matrix(8, 0, 0.5)
    return _lum_dither(image, palette, HALFTONE_4X4, diag, 127.5, 0.5, 170)

def exp4_d(image, pattern=None, palette=None):
    diag = make_diagonal_line_matrix(8, 0, 0.5)
    return _sat_dither(image, palette, diag, HALFTONE_4X4, 127.5, 1.0, 0.1)

def exp5_d(image, pattern=None, palette=None):
    diag = make_diagonal_line_matrix(4, 0, 4.0)
    return _lum_dither(image, palette, HALFTONE_4X4, diag, 127.5, 0.5, 120)

def exp6_d(image, pattern=None, palette=None):
    dith = make_halftone_matrix(32, 1, 2.0)
    return ordered_dither(image, palette, dith, spread=0.5)

def exp7_d(image, pattern=None, palette=None):
    dith = make_halftone_matrix(96, 1, 2.0)
    return ordered_dither(image, palette, dith, spread=1.0)

def exp8_d(image, pattern=None, palette=None):
    hexagon = make_hexagonal_matrix(16, 1.0) 
    return _sat_dither(image, palette, hexagon, HALFTONE_4X4, 127.5, 1.0, 0.3)

def exp9_d(image, pattern=None, palette=None):
    dith = make_halftone_matrix(96, 1, 2.0)
    return _sat_dither(image, palette, dith, HALFTONE_4X4, 127.5, 1.5, 0.1)

def exp10_d(image, pattern=None, palette=None):
    dith = make_halftone_matrix(96, 1, 2.0)
    return _sat_dither(image, palette, HALFTONE_4X4, dith, 127.5, 1.5, 0.1)

def atk_d(image, pattern=None, palette=None):
    return _dither_diffusion(image.astype(np.float32), palette, 'atkinson')

def fs_d(image, pattern=None, palette=None):
    return _dither_diffusion(image.astype(np.float32), palette, 'floyd-steinberg')

def stk_d(image, pattern=None, palette=None):
    return _dither_diffusion(image.astype(np.float32), palette, 'stucki')

def qo(image, pattern=None, palette=None):
    return quantize_ccube(image, palette)