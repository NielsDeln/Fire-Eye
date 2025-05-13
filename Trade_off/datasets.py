

motor_db = [
    {'id': 'MN3110_KV470', 'mass': 98, 'KV': 470, 'voltage_range': '14.8-22.2', 'thrust': 1200, 'cell_count': '3-4S', 'peak_current': 15, 'efficiency': 14.13, 'diameter': 37.7},
    {'id': 'MN3110_KV700', 'mass': 99, 'KV': 700, 'voltage_range': '11.1-14.8', 'thrust': 1200, 'cell_count': '3-4S', 'peak_current': 21, 'efficiency': 14.01, 'diameter': 37.7},
    {'id': 'MN3110_KV780', 'mass': 100, 'KV': 780, 'voltage_range': '11.1-14.8', 'thrust': 1200, 'cell_count': '3-4S', 'peak_current': 26, 'efficiency': 10.68, 'diameter': 37.7},
    {'id': 'F1507_KV2700', 'mass': 15.2, 'KV': 2700, 'voltage_range': '23.28', 'thrust': 838, 'cell_count': '3-6S', 'peak_current': 22, 'efficiency': 2.82, 'diameter': 18.9},
    {'id': 'F1507_KV3800', 'mass': 15.2, 'KV': 3800, 'voltage_range': '15.14', 'thrust': 673, 'cell_count': '3-6S', 'peak_current': 23, 'efficiency': 2.6, 'diameter': 18.9},
    {'id': 'XING2814', 'mass': 88.3, 'KV': 880, 'voltage_range': '24', 'thrust': 2761, 'cell_count': '2-6S', 'peak_current': 50.9, 'efficiency': 6.39, 'diameter': 36},
    {'id': 'N4112_KV320', 'mass': 172, 'KV': 320, 'voltage_range': '22-25', 'thrust': 3179, 'cell_count': '3-4S', 'peak_current': 40, 'efficiency': 12.31, 'diameter': 47.4},
    {'id': 'N4112_KV420', 'mass': 172, 'KV': 420, 'voltage_range': '22-25', 'thrust': 3370, 'cell_count': '3-4S', 'peak_current': 54, 'efficiency': None, 'diameter': 47.4},
    {'id': 'MN501S_KV240', 'mass': 170, 'KV': 240, 'voltage_range': '48.49-48.59', 'thrust': 3957, 'cell_count': '6-12S', 'peak_current': 25, 'efficiency': 13.08, 'diameter': 55.6},
    {'id': 'MN501S_KV300', 'mass': 170, 'KV': 300, 'voltage_range': '24.24-24.33', 'thrust': 5277, 'cell_count': '6-8S', 'peak_current': 40, 'efficiency': 11.89, 'diameter': 55.6},
    {'id': 'MN501S_KV360', 'mass': 175, 'KV': 360, 'voltage_range': '23.94-24.30', 'thrust': 4644, 'cell_count': '6S', 'peak_current': 40, 'efficiency': 9.75, 'diameter': 55.6},
    {'id': 'T-MOTORHOBBY_AT2304', 'mass': 20, 'KV': 1500, 'voltage_range': '7.54-11.73', 'thrust': 544, 'cell_count': '2-3S', 'peak_current': 10, 'efficiency': 10.09, 'diameter': 28},
    {'id': 'BE1806_KV1800', 'mass': 20, 'KV': 1800, 'voltage_range': '6.99-11.42', 'thrust': 510, 'cell_count': '2-3S', 'peak_current': 13, 'efficiency': 8.99, 'diameter': 28},
    {'id': 'BE1806_KV2300', 'mass': 20, 'KV': 2300, 'voltage_range': '6.99-7.64', 'thrust': 521, 'cell_count': '2-3S', 'peak_current': 15, 'efficiency': 7.43, 'diameter': 28},
    {'id': 'BE_UNKNOWN_KV1400', 'mass': 23, 'KV': 1400, 'voltage_range': '7.4-14.8', 'thrust': 440, 'cell_count': '2-4S', 'peak_current': 5.4, 'efficiency': 9.1, 'diameter': 23},
    {'id': 'BE_UNKNOWN_KV2300', 'mass': 23, 'KV': 2300, 'voltage_range': '7.4-11.1', 'thrust': 521, 'cell_count': '2-4S', 'peak_current': 7.6, 'efficiency': 9.3, 'diameter': 23},
    {'id': 'BE_UNKNOWN_KV2700', 'mass': 23, 'KV': 2700, 'voltage_range': '11.1-14.8', 'thrust': 690, 'cell_count': '2-4S', 'peak_current': 16.8, 'efficiency': 6.4, 'diameter': 23},
]


# battery database
battery_db = [
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

    {'id': 'Tattu Low Temp 14500mAh', 'type': 'LiPo 6s', 'cells': 6, 'capacity': 14500, 'mass': 1961, 'voltage': 22.2,
     'energy_capacity': 321.9, 'C-rating': 3, 'energy_density': 164.15},

    {'id': 'Tattu 80.4Ah 4S', 'type': 'LiPo 4s', 'cells': 4, 'capacity': 80400, 'mass': 3500, 'voltage': 11.51,
     'energy_capacity': 1189.92, 'C-rating': 3, 'energy_density': 339},

    {'id': 'Grepow 6S 17000mAh semi-solid', 'type': '6S semi solid', 'cells': 6, 'capacity': 17000, 'mass': 1444, 'voltage': 22.2,
     'energy_capacity': 377.4, 'C-rating': 3, 'energy_density': 300},

    {'id': 'Tattu G-Tech 6S1P', 'type': '6S1P LLiPi', 'cells': 6, 'capacity': 12000, 'mass': 1532, 'voltage': 22.2,
     'energy_capacity': 266.4, 'C-rating': 3, 'energy_density': 173.89},

    {'id': 'Tattu G-Tech 4S 5200mAh', 'type': '4s lipo', 'cells': 4, 'capacity': 5200, 'mass': 436.5, 'voltage': 14.8,
     'energy_capacity': 76.96, 'C-rating': 35, 'energy_density': 176.31},

    {'id': 'S 6750mAh 14.8V', 'type': '4s lipo', 'cells': 4, 'capacity': 6750, 'mass': 620, 'voltage': 14.8,
     'energy_capacity': 99.9, 'C-rating': 25, 'energy_density': 161.13}
]