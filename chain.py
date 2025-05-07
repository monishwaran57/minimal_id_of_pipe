import pandas as pd

from constants import find_friction_head_loss_by_formula, find_residual_head_at_end_by_formula

min_df = pd.read_excel("min_rhas_for_child.xlsx")

min_dict = {}

for idx, row in min_df.iterrows():

    matches = min_df.loc[min_df['end_node'] == row['start_node']]

    if not matches.empty:
        parent_node = matches.iloc[0].to_dict()
        parent_index = matches.index[0]
    else:
        parent_node = None
        parent_index = None

    rhas = 0 if parent_node is None else min_dict[parent_index]['new_rhae']

    fhl = find_friction_head_loss_by_formula(length=row['length'], discharge=row['discharge'],
                                       cr_value=1, iop=row['iop'])

    diff_in_g_level = row['ground_level_start'] - row['ground_level_end']

    rhae = find_residual_head_at_end_by_formula(diff_in_g_level=diff_in_g_level, rhas=rhas, fhl=fhl)

    min_dict[idx] = {
        "new_rhas": rhas,
        "new_rhae": rhae
    }

for v_index, village_row in min_dict.items():
    min_df.loc[v_index, "new_rhas"] = village_row['new_rhas']
    min_df.loc[v_index, "new_rhae"] = village_row['new_rhae']

min_df.to_excel("min2.xlsx")