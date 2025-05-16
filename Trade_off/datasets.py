

motor_db = [
    {'id': 'MN3110_KV470', 'mass': 98, 'kv': 470, 'voltage': 22.2, 'prop_diameter': 25.4, 'thrust': 890, 'cell_count': '3-6S', 'peak_current': 5.3, 'power': 117.66, 'efficiency': 7.56, 'diameter': 37.7},
    {'id': 'MN3110_KV700', 'mass': 99, 'kv': 700, 'voltage': 14.8, 'prop_diameter': 25.4, 'thrust': 800, 'cell_count': '3-4S', 'peak_current': 8.1, 'power': 119.88, 'efficiency': 14.01, 'diameter': 37.7},
    {'id': 'MN3110_KV780', 'mass': 100, 'kv': 780, 'voltage': 11.1148, 'prop_diameter': 22.86, 'thrust': 680, 'cell_count': '3-4S', 'peak_current': 8, 'power': 118.4, 'efficiency': 5.74, 'diameter': 37.7},
    {'id': 'F1507_KV2700', 'mass': 15.2, 'kv': 2700, 'voltage': 23.28, 'prop_diameter': 7.9756, 'thrust': 838, 'cell_count': '3-6S', 'peak_current': 23.34, 'power': 543.46, 'efficiency': 1.54, 'diameter': 18.9},
    {'id': 'F1507_KV3800', 'mass': 15.2, 'kv': 3800, 'voltage': 15.14, 'prop_diameter': 7.9756, 'thrust': 673, 'cell_count': '3-6S', 'peak_current': 25.87, 'power': 391.57, 'efficiency': 1.72, 'diameter': 18.9},
    {'id': 'XING_2814', 'mass': 88.3, 'kv': 880, 'voltage': 24, 'prop_diameter': 22.86, 'thrust': 2361, 'cell_count': '2-6S', 'peak_current': 33.9, 'power': 813.6, 'efficiency': 2.902, 'diameter': 36},
    {'id': 'MN4112_KV320', 'mass': 172, 'kv': 320, 'voltage': 22.0, 'prop_diameter': 38.1, 'thrust': 2551, 'cell_count': '3-4S', 'peak_current': 16.59, 'power': 385, 'efficiency': 6.63, 'diameter': 47.4},
    {'id': 'MN4112_KV420', 'mass': 172, 'kv': 420, 'voltage': 23.48, 'prop_diameter': 38.1, 'thrust': 3752, 'cell_count': '3-4S', 'peak_current': 54, 'power': 738, 'efficiency': 5.09, 'diameter': 47.4},
    {'id': 'MN501S_KV240', 'mass': 170, 'kv': 240, 'voltage': 48.52, 'prop_diameter': 35.56, 'thrust': 3891, 'cell_count': '6-12S', 'peak_current': 25, 'power': 899, 'efficiency': 4.33, 'diameter': 55.6},
    {'id': 'MN501S_KV300', 'mass': 170, 'kv': 300, 'voltage': 24.24, 'prop_diameter': 50.8, 'thrust': 4284, 'cell_count': '6-8S', 'peak_current': 40, 'power': 673, 'efficiency': 6.37, 'diameter': 55.6},
    {'id': 'MN501S_KV360', 'mass': 175, 'kv': 360, 'voltage': 24.18, 'prop_diameter': 43.18, 'thrust': 3837, 'cell_count': '6S', 'peak_current': 40, 'power': 761, 'efficiency': 5.05, 'diameter': 55.6},
    {'id': 'AT2304_KV1500', 'mass': 20, 'kv': 1500, 'voltage': 11.2, 'prop_diameter': 17.78, 'thrust': 544, 'cell_count': '2-3S', 'peak_current': 10, 'power': 110.13, 'efficiency': 4.94, 'diameter': 28},
    {'id': 'BE1806_KV1800', 'mass': 20, 'kv': 1800, 'voltage': 10.94, 'prop_diameter': 20.32, 'thrust': 510, 'cell_count': '2-3S', 'peak_current': 13, 'power': 98.78, 'efficiency': 5.16, 'diameter': 28},
    {'id': 'BE1806_KV2300', 'mass': 20, 'kv': 2300, 'voltage': 6.99, 'prop_diameter': 20.32, 'thrust': 521, 'cell_count': '2-3S', 'peak_current': 15, 'power': 102.38, 'efficiency': 5.09, 'diameter': 28},
    {'id': 'BE 1806_KV1400', 'mass': 23, 'kv': 1400, 'voltage': 14.8, 'prop_diameter': 12.7, 'thrust': 335, 'cell_count': '2-4S', 'peak_current': 5.4, 'power': 62.2, 'efficiency': 5.4, 'diameter': 23},
    {'id': 'BE 1806_KV2300', 'mass': 23, 'kv': 2300, 'voltage': 11.1, 'prop_diameter': 12.7, 'thrust': 390, 'cell_count': '2-4S', 'peak_current': 7.6, 'power': 72.2, 'efficiency': 5.4, 'diameter': 23},
    {'id': 'BE 1806_KV2700', 'mass': 23, 'kv': 2700, 'voltage': 14.8, 'prop_diameter': 12.7, 'thrust': 690, 'cell_count': '2-4S', 'peak_current': 16.8, 'power': 248.4, 'efficiency': 2.8, 'diameter': 23},
    {'id': 'MEPS SZ2806.6 KV1300', 'mass': 47.5, 'kv': 1300, 'voltage': 24.7, 'prop_diameter': 15.24, 'thrust': 1999.9, 'cell_count': '-', 'peak_current': 36.8, 'power': 867, 'efficiency': 2.33, 'diameter': 34.14},
    {'id': 'MEPS NEON2207 KV1950', 'mass': 36, 'kv': 1950, 'voltage': 25, 'prop_diameter': 12.95, 'thrust': 1720, 'cell_count': '-', 'peak_current': 44.2, 'power': 1087, 'efficiency': 1.6, 'diameter': 29.53},
    {"id": "Racerstar BR2306S 2400KV",  "mass": 33.5,  "kv": 2400,  "voltage": 14.8,  "prop_diameter": 15.24,  "thrust": 980,  "cell_count": "2-4S",  "peak_current": 33,  "power": 488,  "efficiency": 2.01,  "diameter": 28.5},
    { "id": "Emax RSII 2207 2300KV", "mass": 31.2, "kv": 2300, "voltage": 14.8, "prop_diameter": 15.24, "thrust": 1014, "cell_count": "4S", "peak_current": 34.3, "power": 497, "efficiency": 2.04, "diameter": 27.9 },
    {"id": "EMAX ECO Micro Series 1407 4100KV",  "mass": 13.7,  "kv": 4100,  "voltage": 14.8,  "prop_diameter": 7.64,  "thrust": 523.1,  "cell_count": "2-4S",  "peak_current": 21.6,  "power": 340,  "efficiency": 2.882,  "diameter":18.8},
    { "id": "HyperTrain Blaster 2207 2450KV", "mass": 31.3, "kv": 2450, "voltage": 14.8, "prop_diameter": 15.24, "thrust": 1006, "cell_count": "4S", "peak_current": 34.9, "power": 512, "efficiency": 1.96, "diameter": 28.3},
    { "id": "Racerstar BR2306S 2400KV", "mass": 33.5, "kv": 2400, "voltage": 14.8, "prop_diameter": 15.24, "thrust": 1027, "cell_count": "4S", "peak_current": 35.1, "power": 506, "efficiency": 2.03, "diameter": 28.5},
    {"id": "Racerstar BR2306S 2400KV",  "mass": 33.5,  "kv": 2400,  "voltage": 14.8,  "prop_diameter": 15.24,  "thrust": 980,  "cell_count": "2-4S",  "peak_current": 33,  "power": 488,  "efficiency": 2.01,  "diameter":28.5},
    { "id": "Emax RSII 2207 2300KV", "mass": 31.2, "kv": 2300, "voltage": 14.8, "prop_diameter": 15.24, "thrust": 1014, "cell_count": "4S", "peak_current": 34.3, "power": 497, "efficiency": 2.04, "diameter":27.9},
    { "id": "HyperTrain Blaster 2207 2450KV", "mass": 31.3, "kv": 2450, "voltage": 14.8, "prop_diameter": 15.24, "thrust": 1006, "cell_count": "4S", "peak_current": 34.9, "power": 512, "efficiency": 1.96, "diameter":28.3},
    { "id": "Racerstar BR2306S 2400KV", "mass": 33.5, "kv": 2400, "voltage": 14.8, "prop_diameter": 15.24, "thrust": 1027, "cell_count": "4S", "peak_current": 35.1, "power": 506, "efficiency": 2.03, "diameter":28.5},
    { "id": "Multistar Elite 2306 2150KV", "mass": 33.1, "kv": 2150, "voltage": 14.8, "prop_diameter": 15.24, "thrust": 967, "cell_count": "4S", "peak_current": 32.7, "power": 470, "efficiency": 2.06, "diameter": 27.9 },
    { "id": "DYS Samguk Wei 2207 2300KV", "mass": 32.3, "kv": 2300, "voltage": 14.8, "prop_diameter": 12.7, "thrust": 903, "cell_count": "4S", "peak_current": 29.3, "power": 410, "efficiency": 2.20, "diameter": 27.7 },
    { "id": "DYS Samguk Shu 2306 2500KV", "mass": 33.3, "kv": 2500, "voltage": 14.8, "prop_diameter": 12.7, "thrust": 949, "cell_count": "4S", "peak_current": 32.2, "power": 447, "efficiency": 2.12, "diameter":27.7}

]

# battery database
battery_db1 = [
    {'id': 'GAONENG GNB 4S 14.8V', 'type': 'Li-ion', 'cells': 4, 'capacity': 4000, 'mass': 434, 'voltage': 14.8, 
     'energy_capacity': 88.8, 'C-rating': 10, 'energy_density': 204.61},
    
    {'id': 'GNB', 'type': 'LiPo 6s', 'cells': 6, 'capacity': 1100, 'mass': 177, 'voltage': 22.8, 
     'energy_capacity': 25.08, 'C-rating': 5, 'energy_density': 141.69},

    {'id': 'DJI 200 TB55 (for Matrice)', 'type': 'Lipo', 'cells': 6, 'capacity': 7660, 'mass': 885, 'voltage': 22.8, 
     'energy_capacity': 174.6, 'C-rating': None, 'energy_density': 197},

    {'id': 'DJI TB51 (for Inspire 3)', 'type': 'LiPo 4s', 'cells': 4, 'capacity': 4280, 'mass': 470, 'voltage': 23.1, 
     'energy_capacity': 98.8, 'C-rating': None, 'energy_density': 210},

    {'id': 'DJI Mavic 3 intelligent battery', 'type': 'LiPo 4s', 'cells': 4, 'capacity': 5000, 'mass': 335.5, 'voltage': 15.4, 
     'energy_capacity': 77, 'C-rating': None, 'energy_density': 230},

    {'id': 'DJI Air 3s intelligent battery', 'type': 'LiHv', 'cells': 4, 'capacity': 4241, 'mass': 267, 'voltage': 14.67, 
     'energy_capacity': 62.6, 'C-rating': None, 'energy_density': 234},

    {'id': 'GRPB042104', 'type': 'LiHv', 'cells': 1, 'capacity': 7100, 'mass': 102, 'voltage': 4.4, 
     'energy_capacity': 31.24, 'C-rating': 5, 'energy_density': 306},

    {'id': 'GRP8674133', 'type': 'Li-Ion 4s', 'cells': 4, 'capacity': 12000, 'mass': 176, 'voltage': 4.4, 
     'energy_capacity': 52.8, 'C-rating': 5, 'energy_density': 300},

    {'id': 'DJI Air 3s', 'type': 'LiPo 4s', 'cells': 4, 'capacity': 4276, 'mass': 247, 'voltage': 14.6, 
     'energy_capacity': 62.5, 'C-rating': None, 'energy_density': 253},

    {'id': 'CNHL LiPo 6s (1300mAh)', 'type': 'LiPo 6s', 'cells': 6, 'capacity': 1300, 'mass': 246, 'voltage': 22.2, 
     'energy_capacity': 28.86, 'C-rating': 70, 'energy_density': 117.32},

    {'id': 'CNHL LiPo 6s (1200mAh)', 'type': 'LiPo 6s', 'cells': 6, 'capacity': 1200, 'mass': 204, 'voltage': 22.2, 
     'energy_capacity': 26.64, 'C-rating': 30, 'energy_density': 130.59},

    {'id': 'Tattu G-Tech 4S 5200mAh', 'type': '4s lipo', 'cells': 4, 'capacity': 5200, 'mass': 436.5, 'voltage': 14.8, 
     'energy_capacity': 76.96, 'C-rating': 35, 'energy_density': 176.31},

    {'id': 'S 6750mAh 14.8V', 'type': '4s lipo', 'cells': 4, 'capacity': 6750, 'mass': 620, 'voltage': 14.8, 
     'energy_capacity': 99.9, 'C-rating': 25, 'energy_density': 161.13},
     
    {'id': 'Turnigy Graphene 4S 6000mAh', 'type': 'LiPo 4s', 'cells': 4, 'capacity': 6000, 'mass': 800, 'voltage': 14.8, 'C-rating': 75},

    {'id': 'Tattu R-Line 6S 1400mAh', 'type': 'LiPo 6s', 'cells': 6, 'capacity': 1400, 'mass': 223, 'voltage': 22.2, 'C-rating': 150},

    {'id': 'BONKA 8000mAh 120C 2S 7.6V HV', 'type': 'LiPo 2s', 'cells': 2, 'capacity': 8000, 'mass': 320, 'voltage': 7.6, 'C-rating': 120},

    {'id': 'HRB Graphene 4S 5000mAh', 'type': 'LiPo 4s', 'cells': 4, 'capacity': 5000, 'mass': 492, 'voltage': 14.8, 'C-rating': 100},
    
    {'id': 'Lectron Pro 4S 7600mAh', 'type': 'LiPo 4s', 'cells': 4, 'capacity': 7600, 'mass': 626, 'voltage': 14.8, 'C-rating': 75},

    {'id': 'Gens Ace 6S 5000mAh', 'type': 'LiPo 6s', 'cells': 6, 'capacity': 5000, 'mass': 695, 'voltage': 22.2, 'C-rating': 45},

    {'id': 'MaxAmps 4S 10900mAh', 'type': 'LiPo 4s', 'cells': 4, 'capacity': 10900, 'mass': 950, 'voltage': 16.8, 'C-rating': 30},

    {'id': 'Ovonic 6S 1300mAh', 'type': 'LiPo 6s', 'cells': 6, 'capacity': 1300, 'mass': 180, 'voltage': 22.2, 'C-rating': 130},
]

battery_db = [
    {'id': 'GAONENG GNB 4S 14.8V',     'type': 'Li-ion', 'cells': 4, 'capacity': 4000,  'mass': 292,   'voltage': 14.8, 'energy_capacity': 59.2,    'C-rating': 10,  'energy_density': 202.74},
    {'id': 'GAONENG LiHV 6S 22.8V',     'type': 'LiPo',   'cells': 6, 'capacity': 1100,  'mass': 177,   'voltage': 22.8, 'energy_capacity': 25.08,   'C-rating': 160, 'energy_density': 141.69},
    {'id': 'DJI TB55 (Matrice)',        'type': 'LiPo',   'cells': 6, 'capacity': 7660,  'mass': 885,   'voltage': 22.8, 'energy_capacity': 174.65,  'C-rating': None,'energy_density': 197.00},
    {'id': 'DJI TB51 (Inspire 3)',      'type': 'LiPo',   'cells': 4, 'capacity': 4280,  'mass': 470,   'voltage': 23.1, 'energy_capacity': 98.87,   'C-rating': None,'energy_density': 210.00},
    {'id': 'DJI Mavic 3',               'type': 'LiPo',   'cells': 4, 'capacity': 5000,  'mass': 335.5, 'voltage': 15.4, 'energy_capacity': 77.0,    'C-rating': None,'energy_density': 230.00},
    {'id': 'DJI Air 3',                 'type': 'LiHV',   'cells': 4, 'capacity': 4241,  'mass': 267,   'voltage': 14.76,'energy_capacity': 62.60,   'C-rating': None,'energy_density': 234.00},
    {'id': 'GRPB042104',                'type': 'LiHV',   'cells': 1, 'capacity': 7100,  'mass': 102,   'voltage': 4.4,  'energy_capacity': 31.24,   'C-rating': 5,   'energy_density': 306.00},
    {'id': 'GRP8674133',                'type': 'Li-ion', 'cells': 1, 'capacity': 12000, 'mass': 176,   'voltage': 4.4,  'energy_capacity': 52.8,    'C-rating': 5,   'energy_density': 300.00},
    {'id': 'DJI Air 3S',                'type': 'LiPo',   'cells': 4, 'capacity': 4276,  'mass': 247,   'voltage': 14.6, 'energy_capacity': 62.43,   'C-rating': None,'energy_density': 253.00},
    {'id': 'CNHL LiPo 6S 1300mAh',      'type': 'LiPo',   'cells': 6, 'capacity': 1300,  'mass': 230,   'voltage': 22.2, 'energy_capacity': 28.86,   'C-rating': 100, 'energy_density': 125.48},
    {'id': 'CNHL LiPo 6S 1200mAh',      'type': 'LiPo',   'cells': 6, 'capacity': 1200,  'mass': 216,   'voltage': 22.2, 'energy_capacity': 26.64,   'C-rating': 100, 'energy_density': 123.33},
    # {'id': 'Tattu 6S 14500mAh',         'type': 'LiPo',   'cells': 6, 'capacity': 14500, 'mass': 1961,  'voltage': 22.2, 'energy_capacity': 321.9,   'C-rating': 30,  'energy_density': 164.15},
    # {'id': 'Tattu 4S 80.4Ah',           'type': 'LiPo',   'cells': 4, 'capacity': 80400, 'mass': 3500,  'voltage': 14.8, 'energy_capacity': 1189.92,'C-rating': 5,   'energy_density': 339.98},
    # {'id': 'Grepow 6S 17000mAh',        'type': 'LiPo',   'cells': 6, 'capacity': 17000, 'mass': 1432,  'voltage': 22.2, 'energy_capacity': 377.4,   'C-rating': 3,   'energy_density': 263.55},
    # {'id': 'Tattu G-Tech 6S 12000mAh',  'type': 'LiPo',   'cells': 6, 'capacity': 12000, 'mass': 1532,  'voltage': 22.2, 'energy_capacity': 266.4,   'C-rating': 3,   'energy_density': 173.89},
    {'id': 'Tattu G-Tech 4S 5200mAh',   'type': 'LiPo',   'cells': 4, 'capacity': 5200,  'mass': 436.5, 'voltage': 14.8, 'energy_capacity': 76.96,   'C-rating': 35,  'energy_density': 176.31},
    {'id': 'Tattu 4S 6750mAh 25C',      'type': 'LiPo',   'cells': 4, 'capacity': 6750,  'mass': 620,   'voltage': 14.8, 'energy_capacity': 99.9,    'C-rating': 25,  'energy_density': 161.13}
]


