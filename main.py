
import pandas as pd


from constants import IOP

IOP_INDEX = 0
RHAS = 0

def find_velocity_by_formula(discharge, id_of_pipe):
    velocity = discharge * (4/(3.14 * (id_of_pipe/1000)**2))
    return round(velocity, 5)

def find_friction_head_loss_by_formula(length, discharge, cr_value, iop):
    fhl = ((length * (discharge/cr_value)**1.81)/(994.62 * (iop/1000)**4.81)) * 1.1
    return round(fhl, 5)

def find_residual_head_at_end_by_formula(diff_in_g_level, avail_resi_head_at_start, fhl):

    rhae = (diff_in_g_level + avail_resi_head_at_start) - fhl
    return round(rhae, 5)

# print("lenght of iop", len(IOP))
df = pd.read_excel("fha.xlsx", sheet_name="Sheet1")
# print("...main_df\n", df)
df = df.dropna(subset=['start_node'])
# print(".........dropped nulls", df)
all_start_nodes = set(df['start_node'])
all_end_nodes = set(df['end_node'])
starting_node = (all_start_nodes - all_end_nodes).pop()

# Initialize variables
ordered_rows = []
current_node = starting_node
remaining_indices = set(df.index)

for i, row in df.iterrows():
    if i not in ordered_rows:
        ordered_rows.append(i)
    child_indexes_v_nodes = df.index[(df['start_node'] == row['end_node']) & df['end_node'].str.contains('V', na=False)].to_list()
    child_indexes_m_nodes = df.index[(df['start_node'] == row['end_node']) & df['end_node'].str.contains('J', na=False)].to_list()
    ordered_rows += child_indexes_v_nodes
    ordered_rows += child_indexes_m_nodes

print("ordered rows", ordered_rows)

ordered_df = df.loc[ordered_rows].reset_index()
# def build_sequence(df):
#
#     starting_nodes = [df['start_node'].iloc[0]]
#
#
#
#     ordered_rows = []
#     visited = set()
#
#     def dfs(node):
#         nonlocal ordered_rows, visited
#         # Find all rows starting with this node
#         next_rows = df[df['start_node'] == node]
#
#         for _, row in next_rows.iterrows():
#             if row.name not in visited:
#                 visited.add(row.name)
#                 ordered_rows.append(row.name)
#                 dfs(row['end_node'])
#
#     # Start DFS from each starting node
#     for node in starting_nodes:
#         dfs(node)
#
#     # Create ordered DataFrame
#     ordered_df = df.loc[ordered_rows].reset_index()
#     return ordered_df
#
#
# # Usage
# ordered_df = build_sequence(df)
# print(ordered_df)
ordered_df.to_excel("oha.xlsx")





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
    # print("PREVIOUS ROW DICT", previous_values_dict)
    previous_iop = previous_values_dict[parent_pipe_index]['iop'] if wr_index != 0 else None
    print("rhas--->", rhas)
    print("rhae--->", calculated_rhae)
    print("velocity", calculated_velocity)
    print("iop index", iop_index)
    print("current_iop---->", IOP[iop_index])
    print("previous_iop---->", previous_iop)
    print("current_row:::", wr_index)
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
        # print("computed_values dict", computed_values_dict)
        current_pipe_starting_node = working_row['start_node']
        parent_pipe_index_list = ordered_df.index[ordered_df['end_node'] == current_pipe_starting_node].to_list()
        if len(parent_pipe_index_list) == 0:
            parent_pipe_index = 0
        else:
            parent_pipe_index = parent_pipe_index_list[0]
        previous_row = computed_values_dict[parent_pipe_index]
        print("$$$$parent pipe index ---------->>>>",parent_pipe_index)
        # previous_row = computed_values_dict[row_index - 1]
        computed_rows_index = list(computed_values_dict.keys())
        print("...computed rows index", computed_rows_index)
        print("...current row", row_index)
        for computed_row in computed_rows_index:
            if computed_row >= parent_pipe_index:
                del computed_values_dict[computed_row]
        computed_values = start_increasing_iop_values(previous_row['row_vals'], previous_row['iop_index']+1, parent_pipe_index, previous_row['rhas'], computed_values_dict)
        return computed_values
computed_values_dict = {}
i = 0
print("df length", len(ordered_df))
# while i <= len(ordered_df)-1:
#     print("current row>>>", i)
#     row = ordered_df.loc[i]
#     is_village_node = True if "V" in row['end_node'] else False
#     print("IS VILLAGE NODE", is_village_node)
#     comp_values = start_increasing_iop_values(row, IOP_INDEX, i, RHAS, computed_values_dict)
#
#     # RHAS = comp_values['rhae']
#
#     print("COMPUTED VALUES DICT", computed_values_dict)
#     i = list(computed_values_dict)[-1]
#
#
#     print("last element key of computed dict::::", i)
#     i += 1
#     if i > len(ordered_df)-1:
#         break
#     current_row = ordered_df.loc[i]
#     print("......start_node.............>>>", current_row['start_node'])
#     print("df index of end node, parent:::",
#           ordered_df.index[ordered_df['end_node'] == current_row['start_node']].to_list())
#     pipe_indices_list = ordered_df.index[ordered_df['end_node'] == current_row['start_node']].to_list()
#     parent_pipe_index = 0 if len(pipe_indices_list) == 0 else pipe_indices_list[0]
#     print("........parent piep index", parent_pipe_index)
#     RHAS = computed_values_dict[parent_pipe_index]['rhae']
#     print("current pipe rhas is previous rhae?????????????", RHAS)
#     print("next i", i)






for key, value in computed_values_dict.items():
    ordered_df.loc[key, 'new_iop'] = value['iop']
    ordered_df.loc[key, 'new_velocity'] = value['velocity']
    ordered_df.loc[key, 'new_fhl'] = value['fhl']
    ordered_df.loc[key, 'available_residual_head_at_start'] = round(value['rhas'], 2)
    ordered_df.loc[key, 'residual_head_at_end'] = round(value['rhae'], 2)


# sorted_df = ordered_df.sort_values('index').reset_index(drop=True)
# sorted_df.to_excel('mha.xlsx')
