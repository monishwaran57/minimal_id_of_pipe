IOP = [96.8, 111.6, 125, 142.8, 160.8, 178.6, 201, 223.4, 250.4, 314.8, 366, 416.4, 466.8, 518, 619.6, 700, 800, 900,
       1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500]

# IOP.sort()
# print("....\n", IOP)

def find_closest_iop_index_by_formula(discharge):
    velocity = 3
    id_of_pipe = (((4 / (velocity / discharge)) / 3.14)**(1/2)) * 1000
    print(".....iop index:::", round(id_of_pipe, 2))
    closest_value = min(IOP, key=lambda x: abs(x-id_of_pipe))
    print("closest value:::", closest_value)
    iop_index = IOP.index(closest_value)
    print("iop_index", iop_index)
    return iop_index

find_closest_iop_index_by_formula(3.84724)