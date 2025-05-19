from constants import IOP
# from gain import ordered_df as first_opti_df
#
# main_pipe_dict = {}
#
# for pipe_idx, pipe in first_opti_df.iterrows():
#     if "V" not in pipe['end_node']:
#         main_pipe_dict[pipe_idx] = {
#             "start_node": pipe['start_node'],
#             "end_node": pipe['end_node'],
#             "length": pipe['length'],
#             "discharge": pipe['discharge'],
#             "ground_level_start": pipe["ground_level_start"],
#             "ground_level_end": pipe["ground_level_end"],
#             "old_dia": pipe['old_dia'],
#             "new_iop": pipe['new_iop'],
#             "rhas": pipe['available_residual_head_at_start'],
#             "rhae": pipe['residual_head_at_end']
#         }
#     else:
#         main_pipe_dict[pipe_idx] = {
#             "start_node": pipe['start_node'],
#             "end_node": pipe['end_node'],
#             "length": pipe['length'],
#             "discharge": pipe['discharge'],
#             "ground_level_start": pipe["ground_level_start"],
#             "ground_level_end": pipe["ground_level_end"],
#             "old_dia": pipe['old_dia'],
#             "new_iop": pipe['new_iop'],
#             "rhas": pipe['available_residual_head_at_start'],
#             "rhae": pipe['residual_head_at_end']
#         }
#         break
main_pipe_dict = {
    0: {'start_node': 'DC-2', 'end_node': 'J-3700', 'length': 70.4, 'discharge': 3.84724, 'ground_level_start': 265.0,
        'ground_level_end': 206.98, 'old_dia': 1400.0, 'new_iop': 1300.0, 'rhas': 0.0, 'rhae': 57.77},
    1: {'start_node': 'J-3700', 'end_node': 'J-3701', 'length': 331.56, 'discharge': 2.89976,
        'ground_level_start': 206.98, 'ground_level_end': 206.94, 'old_dia': 1400.0, 'new_iop': 1300.0, 'rhas': 57.77,
        'rhae': 57.09}, 2: {'start_node': 'J-3701', 'end_node': 'J-3702', 'length': 1358.88, 'discharge': 2.89338,
                            'ground_level_start': 206.94, 'ground_level_end': 194.71, 'old_dia': 1400.0,
                            'new_iop': 1300.0, 'rhas': 57.09, 'rhae': 66.41},
    3: {'start_node': 'J-3702', 'end_node': 'J-3703', 'length': 447.59, 'discharge': 2.39764,
        'ground_level_start': 194.71, 'ground_level_end': 192.08, 'old_dia': 1400.0, 'new_iop': 1300.0, 'rhas': 66.41,
        'rhae': 68.36}, 4: {'start_node': 'J-3703', 'end_node': 'J-3704', 'length': 1032.23, 'discharge': 2.12818,
                            'ground_level_start': 192.08, 'ground_level_end': 178.5, 'old_dia': 1300.0,
                            'new_iop': 1300.0, 'rhas': 68.36, 'rhae': 80.67},
    5: {'start_node': 'J-3704', 'end_node': 'J-3705', 'length': 175.96, 'discharge': 2.09757,
        'ground_level_start': 178.5, 'ground_level_end': 179.64, 'old_dia': 1200.0, 'new_iop': 1200.0, 'rhas': 80.67,
        'rhae': 79.22}, 6: {'start_node': 'J-3705', 'end_node': 'J-3706', 'length': 260.56, 'discharge': 2.09114,
                            'ground_level_start': 179.64, 'ground_level_end': 177.32, 'old_dia': 1200.0,
                            'new_iop': 1200.0, 'rhas': 79.22, 'rhae': 81.09},
    7: {'start_node': 'J-3706', 'end_node': 'J-3707', 'length': 362.84, 'discharge': 2.08365,
        'ground_level_start': 177.32, 'ground_level_end': 174.43, 'old_dia': 1200.0, 'new_iop': 1200.0, 'rhas': 81.09,
        'rhae': 83.35}, 8: {'start_node': 'J-3707', 'end_node': 'J-3708', 'length': 698.86, 'discharge': 2.04042,
                            'ground_level_start': 174.43, 'ground_level_end': 179.3, 'old_dia': 1200.0,
                            'new_iop': 1200.0, 'rhas': 83.35, 'rhae': 77.31},
    9: {'start_node': 'J-3708', 'end_node': 'J-3709', 'length': 245.72, 'discharge': 2.03412,
        'ground_level_start': 179.3, 'ground_level_end': 177.98, 'old_dia': 1200.0, 'new_iop': 1200.0, 'rhas': 77.31,
        'rhae': 78.22}, 10: {'start_node': 'J-3709', 'end_node': 'J-3710', 'length': 403.35, 'discharge': 2.02746,
                             'ground_level_start': 177.98, 'ground_level_end': 174.96, 'old_dia': 1200.0,
                             'new_iop': 1200.0, 'rhas': 78.22, 'rhae': 80.57},
    11: {'start_node': 'J-3710', 'end_node': 'J-3711', 'length': 244.67, 'discharge': 2.02057,
         'ground_level_start': 174.96, 'ground_level_end': 172.82, 'old_dia': 1200.0, 'new_iop': 1200.0, 'rhas': 80.57,
         'rhae': 82.31}, 12: {'start_node': 'J-3711', 'end_node': 'J-3712', 'length': 395.64, 'discharge': 1.902,
                              'ground_level_start': 172.82, 'ground_level_end': 173.78, 'old_dia': 1200.0,
                              'new_iop': 1200.0, 'rhas': 82.31, 'rhae': 80.77},
    13: {'start_node': 'J-3712', 'end_node': 'J-3713', 'length': 414.14, 'discharge': 1.6535,
         'ground_level_start': 173.78, 'ground_level_end': 174.53, 'old_dia': 1200.0, 'new_iop': 1200.0, 'rhas': 80.77,
         'rhae': 79.54}, 14: {'start_node': 'J-3713', 'end_node': 'J-3714', 'length': 644.63, 'discharge': 1.62637,
                              'ground_level_start': 174.53, 'ground_level_end': 176.46, 'old_dia': 1200.0,
                              'new_iop': 1200.0, 'rhas': 79.54, 'rhae': 76.9},
    15: {'start_node': 'J-3714', 'end_node': 'J-3715', 'length': 670.11, 'discharge': 1.61161,
         'ground_level_start': 176.46, 'ground_level_end': 176.7, 'old_dia': 1200.0, 'new_iop': 1200.0, 'rhas': 76.9,
         'rhae': 75.93}, 16: {'start_node': 'J-3715', 'end_node': 'J-3716', 'length': 324.94, 'discharge': 1.5562,
                              'ground_level_start': 176.7, 'ground_level_end': 178.09, 'old_dia': 1100.0,
                              'new_iop': 1200.0, 'rhas': 75.93, 'rhae': 74.2},
    17: {'start_node': 'J-3716', 'end_node': 'J-3717', 'length': 448.77, 'discharge': 1.27007,
         'ground_level_start': 178.09, 'ground_level_end': 182.15, 'old_dia': 1000.0, 'new_iop': 1200.0, 'rhas': 74.2,
         'rhae': 69.83}, 18: {'start_node': 'J-3717', 'end_node': 'J-3718', 'length': 301.5, 'discharge': 1.2633,
                              'ground_level_start': 182.15, 'ground_level_end': 185.5, 'old_dia': 1000.0,
                              'new_iop': 1200.0, 'rhas': 69.83, 'rhae': 66.26},
    19: {'start_node': 'J-3718', 'end_node': 'J-3719', 'length': 465.7, 'discharge': 1.25676,
         'ground_level_start': 185.5, 'ground_level_end': 188.85, 'old_dia': 1000.0, 'new_iop': 1200.0, 'rhas': 66.26,
         'rhae': 62.59}, 20: {'start_node': 'J-3719', 'end_node': 'J-3720', 'length': 367.81, 'discharge': 1.23548,
                              'ground_level_start': 188.85, 'ground_level_end': 194.28, 'old_dia': 1000.0,
                              'new_iop': 1200.0, 'rhas': 62.59, 'rhae': 56.91},
    21: {'start_node': 'J-3720', 'end_node': 'J-3721', 'length': 550.07, 'discharge': 1.22279,
         'ground_level_start': 194.28, 'ground_level_end': 189.76, 'old_dia': 1000.0, 'new_iop': 1200.0, 'rhas': 56.91,
         'rhae': 61.07}, 22: {'start_node': 'J-3721', 'end_node': 'J-3722', 'length': 226.81, 'discharge': 1.13657,
                              'ground_level_start': 189.76, 'ground_level_end': 190.29, 'old_dia': 1000.0,
                              'new_iop': 1200.0, 'rhas': 61.07, 'rhae': 60.41},
    23: {'start_node': 'J-3722', 'end_node': 'J-3723', 'length': 287.09, 'discharge': 1.11673,
         'ground_level_start': 190.29, 'ground_level_end': 192.18, 'old_dia': 1000.0, 'new_iop': 1200.0, 'rhas': 60.41,
         'rhae': 58.36}, 24: {'start_node': 'J-3723', 'end_node': 'J-3724', 'length': 516.66, 'discharge': 1.11005,
                              'ground_level_start': 192.18, 'ground_level_end': 194.03, 'old_dia': 1000.0,
                              'new_iop': 1200.0, 'rhas': 58.36, 'rhae': 56.22},
    25: {'start_node': 'J-3724', 'end_node': 'J-3725', 'length': 304.84, 'discharge': 1.06915,
         'ground_level_start': 194.03, 'ground_level_end': 195.97, 'old_dia': 900.0, 'new_iop': 1000.0, 'rhas': 56.22,
         'rhae': 53.9}, 26: {'start_node': 'J-3725', 'end_node': 'J-3726', 'length': 322.68, 'discharge': 0.70129,
                             'ground_level_start': 195.97, 'ground_level_end': 195.77, 'old_dia': 900.0,
                             'new_iop': 1000.0, 'rhas': 53.9, 'rhae': 53.91},
    27: {'start_node': 'J-3726', 'end_node': 'J-3727', 'length': 301.97, 'discharge': 0.69337,
         'ground_level_start': 195.77, 'ground_level_end': 197.17, 'old_dia': 800.0, 'new_iop': 1000.0, 'rhas': 53.91,
         'rhae': 52.34}, 28: {'start_node': 'J-3727', 'end_node': 'J-3728', 'length': 459.04, 'discharge': 0.61598,
                              'ground_level_start': 197.17, 'ground_level_end': 199.0, 'old_dia': 800.0,
                              'new_iop': 1000.0, 'rhas': 52.34, 'rhae': 50.3},
    29: {'start_node': 'J-3728', 'end_node': 'J-3729', 'length': 374.99, 'discharge': 0.60836,
         'ground_level_start': 199.0, 'ground_level_end': 207.0, 'old_dia': 800.0, 'new_iop': 1000.0, 'rhas': 50.3,
         'rhae': 42.13}, 30: {'start_node': 'J-3729', 'end_node': 'J-3730', 'length': 569.45, 'discharge': 0.60836,
                              'ground_level_start': 207.0, 'ground_level_end': 210.44, 'old_dia': 800.0,
                              'new_iop': 1000.0, 'rhas': 42.13, 'rhae': 38.43},
    31: {'start_node': 'J-3730', 'end_node': 'J-3731', 'length': 302.9, 'discharge': 0.53494,
         'ground_level_start': 210.44, 'ground_level_end': 208.98, 'old_dia': 700.0, 'new_iop': 900.0, 'rhas': 38.43,
         'rhae': 39.71}, 32: {'start_node': 'J-3731', 'end_node': 'J-3732', 'length': 87.95, 'discharge': 0.22348,
                              'ground_level_start': 208.98, 'ground_level_end': 207.75, 'old_dia': 700.0,
                              'new_iop': 619.6, 'rhas': 39.71, 'rhae': 40.88},
    33: {'start_node': 'J-3732', 'end_node': 'J-3733', 'length': 354.84, 'discharge': 0.21621,
         'ground_level_start': 207.75, 'ground_level_end': 204.96, 'old_dia': 619.6, 'new_iop': 619.6, 'rhas': 40.88,
         'rhae': 43.42}, 34: {'start_node': 'J-3733', 'end_node': 'J-3734', 'length': 274.25, 'discharge': 0.20852,
                              'ground_level_start': 204.96, 'ground_level_end': 200.23, 'old_dia': 518.0,
                              'new_iop': 619.6, 'rhas': 43.42, 'rhae': 47.97},
    35: {'start_node': 'J-3734', 'end_node': 'J-3735', 'length': 171.34, 'discharge': 0.2009,
         'ground_level_start': 200.23, 'ground_level_end': 195.94, 'old_dia': 518.0, 'new_iop': 619.6, 'rhas': 47.97,
         'rhae': 52.16}, 36: {'start_node': 'J-3735', 'end_node': 'J-3736', 'length': 323.46, 'discharge': 0.19332,
                              'ground_level_start': 195.94, 'ground_level_end': 192.46, 'old_dia': 466.8,
                              'new_iop': 619.6, 'rhas': 52.16, 'rhae': 55.46},
    37: {'start_node': 'J-3736', 'end_node': 'J-3737', 'length': 375.24, 'discharge': 0.18672,
         'ground_level_start': 192.46, 'ground_level_end': 188.76, 'old_dia': 416.4, 'new_iop': 619.6, 'rhas': 55.46,
         'rhae': 58.96}, 38: {'start_node': 'J-3737', 'end_node': 'J-3738', 'length': 129.13, 'discharge': 0.18023,
                              'ground_level_start': 188.76, 'ground_level_end': 186.92, 'old_dia': 366.0,
                              'new_iop': 518.0, 'rhas': 58.96, 'rhae': 60.65},
    39: {'start_node': 'J-3738', 'end_node': 'J-3739', 'length': 204.52, 'discharge': 0.16579,
         'ground_level_start': 186.92, 'ground_level_end': 184.23, 'old_dia': 366.0, 'new_iop': 518.0, 'rhas': 60.65,
         'rhae': 63.13}, 40: {'start_node': 'J-3739', 'end_node': 'J-3740', 'length': 264.79, 'discharge': 0.15242,
                              'ground_level_start': 184.23, 'ground_level_end': 183.03, 'old_dia': 366.0,
                              'new_iop': 518.0, 'rhas': 63.13, 'rhae': 64.1},
    41: {'start_node': 'J-3740', 'end_node': 'J-3741', 'length': 316.94, 'discharge': 0.13823,
         'ground_level_start': 183.03, 'ground_level_end': 180.17, 'old_dia': 366.0, 'new_iop': 518.0, 'rhas': 64.1,
         'rhae': 66.73}, 42: {'start_node': 'J-3741', 'end_node': 'J-3742', 'length': 365.84, 'discharge': 0.13102,
                              'ground_level_start': 180.17, 'ground_level_end': 182.95, 'old_dia': 366.0,
                              'new_iop': 518.0, 'rhas': 66.73, 'rhae': 63.71},
    43: {'start_node': 'J-3742', 'end_node': 'J-3743', 'length': 237.23, 'discharge': 0.10839,
         'ground_level_start': 182.95, 'ground_level_end': 183.99, 'old_dia': 314.8, 'new_iop': 466.8, 'rhas': 63.71,
         'rhae': 62.48}, 44: {'start_node': 'J-3743', 'end_node': 'J-3744', 'length': 350.89, 'discharge': 0.09372,
                              'ground_level_start': 183.99, 'ground_level_end': 177.86, 'old_dia': 250.4,
                              'new_iop': 416.4, 'rhas': 62.48, 'rhae': 68.25},
    45: {'start_node': 'J-3744', 'end_node': 'J-3745', 'length': 63.68, 'discharge': 0.07328,
         'ground_level_start': 177.86, 'ground_level_end': 177.48, 'old_dia': 250.4, 'new_iop': 366.0, 'rhas': 68.25,
         'rhae': 68.55}, 46: {'start_node': 'J-3745', 'end_node': 'J-3746', 'length': 366.6, 'discharge': 0.06637,
                              'ground_level_start': 177.48, 'ground_level_end': 177.27, 'old_dia': 250.4,
                              'new_iop': 366.0, 'rhas': 68.55, 'rhae': 68.39},
    47: {'start_node': 'J-3746', 'end_node': 'J-3747', 'length': 151.5, 'discharge': 0.05913,
         'ground_level_start': 177.27, 'ground_level_end': 178.55, 'old_dia': 250.4, 'new_iop': 314.8, 'rhas': 68.39,
         'rhae': 66.85}, 48: {'start_node': 'J-3747', 'end_node': 'J-3748', 'length': 520.55, 'discharge': 0.0446,
                              'ground_level_start': 178.55, 'ground_level_end': 179.38, 'old_dia': 250.4,
                              'new_iop': 250.4, 'rhas': 66.85, 'rhae': 64.4},
    49: {'start_node': 'J-3748', 'end_node': 'J-3749', 'length': 372.68, 'discharge': 0.02857,
         'ground_level_start': 179.38, 'ground_level_end': 180.79, 'old_dia': 250.4, 'new_iop': 223.4, 'rhas': 64.4,
         'rhae': 62.1}, 50: {'start_node': 'J-3749', 'end_node': 'J-3750', 'length': 912.59, 'discharge': 0.02182,
                             'ground_level_start': 180.79, 'ground_level_end': 176.89, 'old_dia': 223.4,
                             'new_iop': 201.0, 'rhas': 62.1, 'rhae': 63.77},
    51: {'start_node': 'J-3750', 'end_node': 'J-3752', 'length': 105.14, 'discharge': 0.01283,
         'ground_level_start': 176.89, 'ground_level_end': 173.86, 'old_dia': 160.8, 'new_iop': 160.8, 'rhas': 63.77,
         'rhae': 66.51}, 52: {'start_node': 'J-3752', 'end_node': 'V33_C13', 'length': 168.61, 'discharge': 0.00648,
                              'ground_level_start': 173.86, 'ground_level_end': 177.16, 'old_dia': 111.6,
                              'new_iop': 111.6, 'rhas': 66.51, 'rhae': 62.43}}
# print("katingksa\n", main_pipe_dict)

# dict_of_main_pipe_ids = {}
# for idx, pipe_vals in main_pipe_dict.items():
#     if pipe_vals['new_iop'] not in dict_of_main_pipe_ids:
#         dict_of_main_pipe_ids[pipe_vals['new_iop']] = 1
#     else:
#         dict_of_main_pipe_ids[pipe_vals['new_iop']] += 1
#
# print("oskaban\n", dict_of_main_pipe_ids)
#
# high_count = 0
# most_repeated_iop = 0
#
# for iop, count in dict_of_main_pipe_ids.items():
#     if count > high_count:
#         high_count = count
#         most_repeated_iop = iop


def give_iop_pipe_indexes_dict(idx_and_iops):
    iop_pipe_indexes_dict = {}

    for idx, iop in idx_and_iops.items():
        iop_pipe_indexes_dict[iop] = [ix for ix, iop2 in idx_and_iops.items() if iop == iop2]


    return iop_pipe_indexes_dict


idx_and_iop_dict = {}
for pipe_index, pipe_vals in main_pipe_dict.items():
    idx_and_iop_dict[pipe_index] = pipe_vals['new_iop']

iop_indexes_dict = give_iop_pipe_indexes_dict(idx_and_iop_dict)
print("taki taki \n", iop_indexes_dict)

for iop, indexes_list in iop_indexes_dict.items():
    same_iop_using_last_pipe_index = max(iop_indexes_dict[iop])

    current_iop_index = IOP.index(iop)

