IOP = [250, 300, 350, 400, 450, 500, 600, 696.8, 798.8, 898, 998.4, 1049.4, 1199, 1397, 1597.6,
1800.6, 2000, 2200, 2500, 2800, 3000]

# IOP.sort()
# print("....\n", IOP)

for idx, iop in enumerate(IOP):
    print(idx, "------>", iop)
print(len(IOP))
print(IOP[len(IOP)-1])

def find_closest_iop_index_by_formula(discharge):
    velocity = 3
    id_of_pipe = (((4 / (velocity / discharge)) / 3.14)**(1/2)) * 1000
    closest_value = min(IOP, key=lambda x: abs(x-id_of_pipe))
    iop_index = IOP.index(closest_value)
    # print("*", IOP[iop_index])
    return iop_index


find_closest_iop_index_by_formula(0.00648)


def find_friction_head_loss_by_formula(length, discharge, cr_value, iop):
    fhl = ((length * (discharge / cr_value) ** 1.81) / (994.62 * (iop / 1000) ** 4.81)) * 1.1
    return round(fhl, 5)


def find_residual_head_at_end_by_formula(diff_in_g_level, rhas, fhl):
    rhae = (diff_in_g_level + rhas) - fhl
    return round(rhae, 5)

def find_velocity_by_formula(discharge, id_of_pipe):
    velocity = discharge * (4 / (3.14 * (id_of_pipe / 1000) ** 2))
    return round(velocity, 5)

def find_needed_rhas_for_getting_expected_rhae(difference_in_g_level, fhl, expected_rhae=28):
    rhas = (expected_rhae + fhl) - difference_in_g_level
    return round(rhas, 5)

def find_needed_rhas_for_getting_rhae_0plus(difference_in_g_level, fhl, expected_rhae=0):
    rhas = (expected_rhae + fhl) - difference_in_g_level
    return round(rhas, 5)

def find_fhl_with_rhas_rhae(rhae, rhas, difference_in_g_level):
    fhl = (rhas + difference_in_g_level) - rhae
    return round(fhl, 5)

def find_iop_with_fhl(fhl, length, discharge, cr_value):
    iop = ((((length * (discharge / cr_value) ** 1.81) * fhl/1.1) ** 1/4.81)/994.62) * 1000
    return iop

# find_needed_rhas_for_getting_rhae_0plus(difference_in_g_level=-8, fhl=1.68667, expected_rhae=23)

"""
0 ------> 95.4
1 ------> 96.8
2 ------> 111.6
3 ------> 125
4 ------> 142.8
5 ------> 160.8
6 ------> 178.6
7 ------> 201
8 ------> 223.4
9 ------> 250.4
10 ------> 314.8
11 ------> 366
12 ------> 416.4
13 ------> 466.8
14 ------> 518
15 ------> 619.6
16 ------> 700
17 ------> 800
18 ------> 900
19 ------> 1000
20 ------> 1100
21 ------> 1200
22 ------> 1300
23 ------> 1400
"""