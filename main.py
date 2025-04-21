
import pandas as pd


from constants import IOP

IOP_INDEX = 0
PREVIOUS_RHAE = 51

def find_velocity_by_formula(discharge, id_of_pipe):
    velocity = discharge * (4/(3.14 * (id_of_pipe/1000)**2))
    return round(velocity, 2)

def find_friction_head_loss_by_formula(length, discharge, cr_value, iop):
    fhl = ((length * (discharge/cr_value)**1.81)/(994.62 * (iop/1000)**4.81)) * 1.1
    return round(fhl, 2)

def find_residual_head_at_end_by_formula(diff_in_g_level, avail_resi_head_at_start, fhl):

    rhae = (diff_in_g_level + avail_resi_head_at_start) - fhl
    return round(rhae, 2)

# print("lenght of iop", len(IOP))
df = pd.read_excel("ha.xlsx", sheet_name="Sheet1")
velocity_condition = (df['velocity'] > 0.6) & (df['velocity'] < 3)
# print("...main_df\n", df)
df = df.dropna(subset=['start_node'])
# print(".........dropped nulls", df)





def get_computed_values(working_row, iop_index, wr_index, previous_rhae, previous_values_dict):
    calculated_velocity = find_velocity_by_formula(working_row['discharge'], IOP[iop_index])
    calculated_fhl = find_friction_head_loss_by_formula(length=working_row['length'],
                                                        discharge=working_row['discharge'],
                                                        cr_value=working_row['cr_value'], iop=IOP[iop_index])
    difference_in_g_level = working_row['ground_level_start'] - working_row['ground_level_end']
    rhas = previous_rhae

    calculated_rhae = find_residual_head_at_end_by_formula(diff_in_g_level=difference_in_g_level,
                                                           avail_resi_head_at_start=rhas,
                                                           fhl=calculated_fhl)



    print("PREVIOUS ROW DICT", previous_values_dict)
    previous_iop = previous_values_dict[wr_index-1]['iop'] if wr_index != 0 else None
    print("rhas--->", rhas)
    print("rhae--->", calculated_rhae)
    print("velocity", calculated_velocity)
    print("iop index", iop_index)
    print("current_iop---->", IOP[iop_index])
    print("previous_iop---->", previous_iop)
    print("current_row:::", wr_index)
    if previous_iop and IOP[iop_index] > previous_iop:
        return False

    if 0.1 < calculated_velocity < 3 and calculated_rhae >= 28:
         return {
             "iop": IOP[iop_index],
             "iop_index": iop_index,
             "velocity": calculated_velocity,
             "fhl": calculated_fhl,
             "rhas": rhas,
             "rhae": calculated_rhae,
         }

    else:
        result = get_computed_values(working_row, iop_index + 1, wr_index, previous_rhae, previous_values_dict)
        return result

def start_increasing_iop_values(working_row, iop_index, row_index, previous_rhae, computed_values_dict):
    current_row_computed_values = get_computed_values(working_row, iop_index, row_index, previous_rhae, computed_values_dict)
    if current_row_computed_values:
        computed_values = {
            "velocity": current_row_computed_values['velocity'],
            "iop": current_row_computed_values['iop'],
            "iop_index": current_row_computed_values['iop_index'],
            "fhl": current_row_computed_values['fhl'],
            "rhas": current_row_computed_values['rhas'],
            "rhae": current_row_computed_values['rhae'],
            "row_vals": dict(row)
        }
        computed_values_dict[row_index] = computed_values
        return computed_values
    else:
        """Use high iop for previous pipe"""
        print("computed_values dict", computed_values_dict)
        previous_row = computed_values_dict[row_index - 1]
        computed_values = start_increasing_iop_values(previous_row['row_vals'], previous_row['iop_index']+1, row_index-1, previous_row['rhas'], computed_values_dict)
        return computed_values
computed_values_dict = {}
i = 0
# print("df length", len(df))
while i <= len(df)-1:
    print("current row>>>", i)
    row = df.loc[i]
    comp_values = start_increasing_iop_values(row, IOP_INDEX, i, PREVIOUS_RHAE, computed_values_dict)
    PREVIOUS_RHAE = comp_values['rhae']
    print("COMPUTED VALUES DICT", computed_values_dict)
    i = list(computed_values_dict)[-1]
    print("last element key of computed dict::::", i)
    i += 1
    print("next i", i)



# for r_index, row in df.iterrows():
#     print("current row>>>", r_index)
#     comp_values = start_increasing_iop_values(row, IOP_INDEX, r_index,PREVIOUS_RHAE, computed_values_dict)
#
#     PREVIOUS_RHAE = comp_values['rhae']
#     print("COMPUTED VALUES DICT", computed_values_dict)


for key, value in computed_values_dict.items():
    df.loc[key, 'new_iop'] = value['iop']
    df.loc[key, 'new_velocity'] = value['velocity']
    df.loc[key, 'new_fhl'] = value['fhl']
    df.loc[key, 'available_residual_head_at_start'] = round(value['rhas'], 2)
    df.loc[key, 'residual_head_at_end'] = round(value['rhae'], 2)



df.to_excel('mha.xlsx')