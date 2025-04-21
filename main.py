
import pandas as pd


from constants import IOP

IOP_INDEX = 0
PREVIOUS_RHAE = 51

def find_velocity_by_formula(discharge, id_of_pipe):
    velocity = discharge * (4/(3.14 * (id_of_pipe/1000)**2))
    return velocity

def find_friction_head_loss_by_formula(length, discharge, cr_value, iop):
    fhl = ((length * (discharge/cr_value)**1.81)/(994.62 * (iop/1000)**4.81)) * 1.1
    return fhl

def find_residual_head_at_end_by_formula(diff_in_g_level, avail_resi_head_at_start, fhl):

    rhae = (diff_in_g_level + avail_resi_head_at_start) - fhl
    return rhae

print("lenght of iop", len(IOP))
df = pd.read_excel("ha.xlsx", sheet_name="Sheet1")
velocity_condition = (df['velocity'] > 0.6) & (df['velocity'] < 3)
print("...main_df\n", df)
df = df.dropna(subset=['start_node'])
print(".........dropped nulls", df)





def get_iop_with_correct_velocity(working_row, iop_index, wr_index, previous_rhae, is_village_node):
    calculated_velocity = find_velocity_by_formula(working_row['discharge'], IOP[iop_index])
    calculated_fhl = find_friction_head_loss_by_formula(length=working_row['length'],
                                                        discharge=working_row['discharge'],
                                                        cr_value=working_row['cr_value'], iop=IOP[iop_index])
    difference_in_g_level = working_row['ground_level_start'] - working_row['ground_level_end']
    rhas = previous_rhae
    print("start rhas", rhas)
    calculated_rhae = find_residual_head_at_end_by_formula(diff_in_g_level=difference_in_g_level,
                                                           avail_resi_head_at_start=rhas,
                                                           fhl=calculated_fhl)

    print("end rhae", calculated_rhae)
    print("ccc velocity", calculated_velocity)
    print("iop index222222$$$$", iop_index)
    print("actual iop222::$$$$", IOP[iop_index])
    print("current row-222$$$$", wr_index)

    if 0.1 < calculated_velocity < 3 and calculated_rhae >= 28:
        if is_village_node:
            if calculated_rhae >= -100:
                return {"iop": IOP[iop_index],
                        "velocity": calculated_velocity,
                        "fhl": calculated_fhl,
                        "rhas": rhas,
                        "rhae": calculated_rhae}
            else:
                print("iop index222222::::", iop_index)
                print("actual iop222::", IOP[iop_index])
                print("current row-222------>", wr_index)
                result = get_iop_with_correct_velocity(working_row, iop_index + 1, wr_index, previous_rhae,
                                                       is_village_node)
                return result
        else:
            return {"iop": IOP[iop_index],
                    "velocity": calculated_velocity,
                    "fhl": calculated_fhl,
                    "rhas": rhas,
                    "rhae": calculated_rhae}
    else:
        print("iop index11111::::", iop_index)
        print("actual iop111::", IOP[iop_index])
        print("current row------->", wr_index)
        result = get_iop_with_correct_velocity(working_row, iop_index + 1, wr_index, previous_rhae, is_village_node)
        return result

output_dict = {}
for r_index, row in df.iterrows():
    print("current row>>>", r_index)
    print(".......endnode type", type(row['end_node']))
    print(".......endnode---->", row['end_node'])
    if "V" in row['end_node']:
        is_village_node = True
    else:
        is_village_node = False
    print(".......is village node", is_village_node)
    output = get_iop_with_correct_velocity(row, IOP_INDEX, r_index, PREVIOUS_RHAE, is_village_node=is_village_node)
    output_dict[r_index] = {
        "velocity": output['velocity'],
        "iop": output['iop'],
        "fhl": output['fhl'],
        "rhas": output['rhas'],
        "rhae": output['rhae']
        }
    PREVIOUS_RHAE = output['rhae']




for key, value in output_dict.items():
    df.loc[key, 'new_iop'] = value['iop']
    df.loc[key, 'new_velocity'] = value['velocity']
    df.loc[key, 'new_fhl'] = value['fhl']
    df.loc[key, 'available_residual_head_at_start'] = round(value['rhas'], 2)
    df.loc[key, 'residual_head_at_end'] = round(value['rhae'], 2)



df.to_excel('mha.xlsx')