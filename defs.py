from maix import image
import filters

MCOLOR =  image.Color.from_rgba(100, 100, 100, 0.8)
MCOLOR_t =  image.Color.from_rgba(100, 100, 100, 0.2)
TCOLOR = image.Color.from_rgb(255, 255, 255)

#########
#iso_table = [100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400]
iso_table = [
    100, 200, 320, 640, 1250, 2500, 3200, 5000
]
iso_table_len = len(iso_table)

#exp_table = [ 
#    ('1/1200',1/1200), ('1/960',1/960), ('1/720',1/720), ('1/480',1/480),
#    ('1/360',1/360), ('1/240',1/240), ('1/180',1/180), ('1/120',1/120),
#    ('1/90',1/90), ('1/60',1/60), ('1/40',1/40), ('1/30',1/30),
#    ('1/20',1/20), ('1/15',1/15), ('1/10',1/10), ('1/8',1/8),
#    ('1/5',1/5), ('1/3',1/3), ('1/2',1/2), ('2/3',2/3), ('1',1)
#]

exp_table = [
    ('1/30000',1/30000), ('1/20000',1/20000),
    ('1/10000',1/10000), ('1/5000',1/5000),
    ('1/3200',1/3200), ('1/2500',1/2500),
    ('1/1800',1/1800), ('1/1500',1/1500),
    ('1/1200',1/1200), ('1/960',1/960),
    ('1/480',1/480), ('1/240',1/240),
    ('1/60',1/60), ('1/30',1/30),
    ('1/10',1/10), ('1/2',1/2),
    ('1',1)
]
exp_table_len = len(exp_table)

res_table = [
    (480, 480), # 1:1
    (640, 480), # 4:3
    (800, 600), # 4:3
    (1280, 720), # 16:9
    (1200, 1200), # 1:1
    (1600, 1200), # 4:3
    (1600, 1600), # 1:1
    (1920, 1080), # 16:9
    (1920, 1440), # 4:3
    (2560, 1440), # 16:9
    (2560, 1920), # 4:3
    (3840, 2160), # 16:9
]
res_table_len = len(res_table)

filter_table = [
    ('qo', filters.qo), ('fs', filters.fs_d), ('atk', filters.atk_d), ('stk', filters.stk_d), ('ord', filters.ord_d), ('art', filters.exp1_d)
]
filter_table_len = len(filter_table)

ord_m_art_table = [
    ('exp1', filters.exp1_d),
    ('exp2', filters.exp2_d),
    ('exp3', filters.exp3_d),
    ('exp4', filters.exp4_d),
    ('exp5', filters.exp5_d),
    ('exp6', filters.exp6_d),
    ('exp7', filters.exp7_d),
    ('exp8', filters.exp8_d),
    ('exp9', filters.exp9_d),
    ('exp10', filters.exp10_d)
]
ord_m_art_table_len = len(ord_m_art_table)

ord_m_table = [
    ('all', filters.HALFTONE_4X4),
    ('B2x2', filters.BAYER_MATRIX_2X2), 
    #('B4x4', filters.BAYER_MATRIX_4X4),
    ('B8x8', filters.BAYER_MATRIX_8X8),
    ('H4x4', filters.HALFTONE_4X4),

   # ('DIAG', filters.DIAGONAL), ('BRCK', filters.BRICK), 
   # ('RMB', filters.RHOMBUS), ('ZZ', filters.ZIG_ZAG),

    ('HLF', filters.HALFTONE),
    #('HLFR', filters.HALFTONE_R),

    ('CDD6', filters.CLUSTERED_DOT_DIAG_6x6),
    ('CDD8', filters.CLUSTERED_DOT_DIAG_8x8),
    ('CDD16', filters.CLUSTERED_DOT_DIAG_16x16)
]
ord_m_table_len = len(ord_m_table)

palette_table = [
    '0c_all'
]
palette_table_len = len(palette_table)