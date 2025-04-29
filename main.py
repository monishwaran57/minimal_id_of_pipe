
import json

from gpt_dfs import dfs_df
from constants import IOP


IOP_INDEX = 0
RHAS = 0


def find_velocity_by_formula(discharge, id_of_pipe):
    velocity = discharge * (4/(3.14 * (id_of_pipe/1000)**2))
    return round(velocity, 5)

def find_closest_iop_index_by_formula(discharge):
    velocity = 1.5
    id_of_pipe = (((4 / (velocity / discharge)) / 3.14)**(1/2)) * 1000
    closest_value = min(IOP, key=lambda x: abs(x-id_of_pipe))
    iop_index = IOP.index(closest_value)
    return iop_index

def find_friction_head_loss_by_formula(length, discharge, cr_value, iop):
    fhl = ((length * (discharge/cr_value)**1.81)/(994.62 * (iop/1000)**4.81)) * 1.1
    return round(fhl, 5)

def find_residual_head_at_end_by_formula(diff_in_g_level, avail_resi_head_at_start, fhl):

    rhae = (diff_in_g_level + avail_resi_head_at_start) - fhl
    return round(rhae, 5)

# print("lenght of iop", len(IOP))
# df = pd.read_excel("sdc.xlsx", sheet_name="small dc2")
# # print("...main_df\n", df)
# df = df.dropna(subset=['start_node'])
# print(".........dropped nulls", df)


# Initialize variables
# ordered_rows = []
#
#
# for i, row in dfs_df.iterrows():
#
#     if i not in ordered_rows:
#         ordered_rows.append(i)
#     print("row start node", row['start_node'])
#     child_indexes_v_nodes = dfs_df.index[(dfs_df['start_node'] == row['end_node']) & dfs_df['end_node'].str.contains('V', na=False)].to_list()
#     ordered_rows += child_indexes_v_nodes
#
# print("ordered rows", ordered_rows)


# unique_df = df.drop_duplicates(keep="first")

# ordered_df.to_excel("oha.xlsx")



ordered_df = dfs_df

def get_computed_values(working_row, iop_index, wr_index, rhas, previous_values_dict):
    calculated_velocity = find_velocity_by_formula(working_row['discharge'], IOP[iop_index])

    calculated_fhl = find_friction_head_loss_by_formula(length=working_row['length'],
                                                        discharge=working_row['discharge'],
                                                        cr_value=1, iop=IOP[iop_index])
    difference_in_g_level = working_row['ground_level_start'] - working_row['ground_level_end']
    rhas = rhas

    calculated_rhae = find_residual_head_at_end_by_formula(diff_in_g_level=difference_in_g_level,
                                                           avail_resi_head_at_start=rhas,
                                                           fhl=calculated_fhl)

    pipe_indices_list = ordered_df.index[ordered_df['end_node'] == working_row['start_node']].to_list()
    parent_pipe_index = 0 if len(pipe_indices_list) == 0 else pipe_indices_list[0]
    previous_iop = previous_values_dict[parent_pipe_index]['iop'] if wr_index != 0 else None
    print("rhas--->", rhas)
    print("rhae--->", calculated_rhae)
    print("velocity", calculated_velocity)
    print("iop index", iop_index)
    print("current_iop---->", IOP[iop_index])
    print("previous_iop---->", previous_iop)
    print("current_row:::", wr_index, "start_node", working_row['start_node'])
    if previous_iop and IOP[iop_index] > previous_iop:
        return False

    elif 0.6 <= calculated_velocity <= 3:
        is_village_node = "V" in working_row["end_node"]
        print("passed velocity, if its village node", is_village_node)
        if is_village_node:
            if calculated_rhae >= 28:
                 return {
                     "iop": IOP[iop_index],
                     "iop_index": iop_index,
                     "velocity": calculated_velocity,
                     "fhl": calculated_fhl,
                     "rhas": rhas,
                     "rhae": calculated_rhae,
                     "row_vals": dict(working_row)
                 }
            else:
                result = get_computed_values(working_row, iop_index + 1, wr_index, rhas, previous_values_dict)
                return result
        else:
            return {
                "iop": IOP[iop_index],
                "iop_index": iop_index,
                "velocity": calculated_velocity,
                "fhl": calculated_fhl,
                "rhas": rhas,
                "rhae": calculated_rhae,
                "row_vals": dict(working_row)
            }

    else:
        result = get_computed_values(working_row, iop_index + 1, wr_index, rhas, previous_values_dict)
        return result




def start_increasing_iop_values(working_row, iop_index, row_index, rhas, computed_values_dict):

    current_row_computed_values = get_computed_values(working_row, iop_index, row_index, rhas, computed_values_dict)
    if current_row_computed_values:
        computed_values = {
            "velocity": current_row_computed_values['velocity'],
            "iop": current_row_computed_values['iop'],
            "iop_index": current_row_computed_values['iop_index'],
            "fhl": current_row_computed_values['fhl'],
            "rhas": current_row_computed_values['rhas'],
            "rhae": current_row_computed_values['rhae'],
            "row_vals": current_row_computed_values['row_vals']
        }
        computed_values_dict[row_index] = computed_values
        return computed_values
    else:
        """Use high iop for previous pipe"""
        current_pipe_starting_node = working_row['start_node']
        parent_pipe_index_list = ordered_df.index[ordered_df['end_node'] == current_pipe_starting_node].to_list()
        if len(parent_pipe_index_list) == 0:
            parent_pipe_index = 0
        else:
            parent_pipe_index = parent_pipe_index_list[0]
        previous_row = computed_values_dict[parent_pipe_index]
        # previous_row = computed_values_dict[row_index - 1]
        computed_rows_index = list(computed_values_dict.keys())
        for computed_row in computed_rows_index:
            if computed_row >= parent_pipe_index:
                del computed_values_dict[computed_row]
        computed_values = start_increasing_iop_values(previous_row['row_vals'], previous_row['iop_index']+1, parent_pipe_index, previous_row['rhas'], computed_values_dict)
        return computed_values


computed_values_dict = {}
i = 0
print("df length", len(ordered_df))
while i <= len(ordered_df)-1:
    print("current row>>>", i)
    row = ordered_df.loc[i]

    iop_index = find_closest_iop_index_by_formula(row['discharge'])
    comp_values = start_increasing_iop_values(row, iop_index, i, RHAS, computed_values_dict)

    with open("log.json", "w") as log_file:
        json.dump(computed_values_dict, log_file, indent=4)
    i = list(computed_values_dict)[-1]


    print("last element key of computed dict::::", i)
    i += 1
    if i > len(ordered_df)-1:
        break
    current_row = ordered_df.loc[i]
    print("df index of end node, parent:::",
          ordered_df.index[ordered_df['end_node'] == current_row['start_node']].to_list())
    pipe_indices_list = ordered_df.index[ordered_df['end_node'] == current_row['start_node']].to_list()
    parent_pipe_index = 0 if len(pipe_indices_list) == 0 else pipe_indices_list[0]
    print("........parent piep index", parent_pipe_index)
    RHAS = computed_values_dict[parent_pipe_index]['rhae']
    print("current pipe rhas is previous rhae?????????????", RHAS)
    print("next i", i)

for key, value in computed_values_dict.items():
    ordered_df.loc[key, 'new_iop'] = value['iop']
    ordered_df.loc[key, 'new_velocity'] = value['velocity']
    ordered_df.loc[key, 'new_fhl'] = value['fhl']
    ordered_df.loc[key, 'available_residual_head_at_start'] = round(value['rhas'], 2)
    ordered_df.loc[key, 'residual_head_at_end'] = round(value['rhae'], 2)


ordered_df.to_excel('mha6.xlsx')

