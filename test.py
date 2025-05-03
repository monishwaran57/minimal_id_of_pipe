from gpt_dfs import dfs_df as ordered_df
import math


# ordered_rows = []
# for i, row in ordered_df.iterrows():
#
#     if i not in ordered_rows:
#         ordered_rows.append(i)
#     print("row start node", row['start_node'])
#     child_indexes_v_nodes = ordered_df.index[(ordered_df['start_node'] == row['end_node']) & ordered_df['end_node'].str.contains('V', na=False)].to_list()
#     ordered_rows += child_indexes_v_nodes
#
# print("ordered rows", ordered_rows)
#
# ordered_df = ordered_df.loc[ordered_rows]

# unique_df = df.drop_duplicates(keep="first")

ordered_df.to_excel("oha.xlsx")

def find_velocity_by_formula(discharge, id_of_pipe):
    velocity = discharge * (4 / (math.pi * (id_of_pipe / 1000) ** 2))
    return round(velocity, 5)


def find_friction_head_loss_by_formula(length, discharge, cr_value, iop):
    fhl = ((length * (discharge / cr_value) ** 1.81) / (994.62 * (iop / 1000) ** 4.81)) * 1.1
    return round(fhl, 5)


def find_residual_head_at_end_by_formula(diff_in_g_level, avail_resi_head_at_start, fhl):
    rhae = (diff_in_g_level + avail_resi_head_at_start) - fhl
    return round(rhae, 5)

def get_computed_values(working_row, iop, rhas):
    calculated_velocity = find_velocity_by_formula(working_row['discharge'], iop)

    calculated_fhl = find_friction_head_loss_by_formula(length=working_row['length'],
                                                        discharge=working_row['discharge'],
                                                        cr_value=1, iop=iop)
    difference_in_g_level = working_row['ground_level_start'] - working_row['ground_level_end']
    rhas = rhas

    calculated_rhae = find_residual_head_at_end_by_formula(diff_in_g_level=difference_in_g_level,
                                                           avail_resi_head_at_start=rhas,
                                                           fhl=calculated_fhl)
    rhas_dict[i] = calculated_rhae
    return {
        "velocity": calculated_velocity,
        "fhl": calculated_fhl,
        "rhas": rhas,
        "rhae": calculated_rhae
    }

rhas_dict = {}
initial_rhas = 0
for i, row in ordered_df.iterrows():
    pipe_indices_list = ordered_df.index[ordered_df['end_node'] == row['start_node']].to_list()
    parent_pipe_index = 0 if len(pipe_indices_list)==0 else pipe_indices_list[0]
    current_rhas = 0 if i-1 not in rhas_dict else rhas_dict[parent_pipe_index]
    result = get_computed_values(row, row['Diameter (mm)'],current_rhas)
    ordered_df.loc[i, 'velocity'] = result['velocity']
    ordered_df.loc[i, 'rhas'] = result['rhas']
    ordered_df.loc[i, 'rhae'] = result['rhae']
    ordered_df.loc[i, 'fhl'] = result['fhl']

ordered_df.to_excel('test.xlsx')