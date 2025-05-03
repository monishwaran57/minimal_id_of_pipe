IOP = [96.8, 111.6, 125, 142.8, 160.8, 178.6, 201, 223.4, 250.4, 314.8, 366, 416.4, 466.8, 518, 619.6, 700, 800, 900,
       1000, 1100, 1200, 1300, 1400]

# IOP.sort()
# print("....\n", IOP)

def find_closest_iop_index_by_formula(discharge):
    velocity = 1.5
    id_of_pipe = (((4 / (velocity / discharge)) / 3.14)**(1/2)) * 1000
    print(".....iop index:::", round(id_of_pipe, 2))
    closest_value = min(IOP, key=lambda x: abs(x-id_of_pipe))
    print("closest value:::", closest_value)
    iop_index = IOP.index(closest_value)
    print("iop_index", iop_index)
    return iop_index

find_closest_iop_index_by_formula(2.09757)

def find_friction_head_loss_by_formula(length, discharge, cr_value, iop):
    fhl = ((length * (discharge / cr_value) ** 1.81) / (994.62 * (iop / 1000) ** 4.81)) * 1.1
    return round(fhl, 5)


def find_residual_head_at_end_by_formula(diff_in_g_level, avail_resi_head_at_start, fhl):
    rhae = (diff_in_g_level + avail_resi_head_at_start) - fhl
    return round(rhae, 5)

def find_velocity_by_formula(discharge, id_of_pipe):
    velocity = discharge * (4 / (3.14 * (id_of_pipe / 1000) ** 2))
    return round(velocity, 5)

"""
0 --> 96.8
1 --> 111.6
2 --> 125
3 --> 142.8
4 --> 160.8
5 --> 178.6
6 --> 201
7 --> 223.4
8 --> 250.4
9 --> 314.8
10 --> 366
11 --> 416.4
12 --> 466.8
13 --> 518
14 --> 619.6
15 --> 700
16 --> 800
17 --> 900
18 --> 1000
19 --> 1100
20 --> 1200
21 --> 1300
22 --> 1400
23 --> 1500
24 --> 1600
25 --> 1700
26 --> 1800
27 --> 1900
28 --> 2000
29 --> 2100
30 --> 2200
31 --> 2300
32 --> 2400
33 --> 2500
"""