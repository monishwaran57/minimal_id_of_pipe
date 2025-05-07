from gpt_dfs import dfs_df as ordered_df
from constants import IOP, find_closest_iop_index_by_formula, find_velocity_by_formula, \
    find_residual_head_at_end_by_formula, find_friction_head_loss_by_formula, find_needed_rhas_for_getting_expected_rhae, \
    find_needed_rhas_for_getting_rhae_0plus

calculated_dict = {}

i = 0
RHAS = 0
PARENT_IOP = None
MINIMUM_PARENT_RHAE = 0
MINIMUN_VILLAGE_RHAE = 28


reverse_calc_dict = {}

def find_rhas_and_rhae_for_parents(child_node):

    matches = ordered_df.loc[ordered_df['end_node'] == child_node['start_node']]

    if not matches.empty:
        parent_node = matches.iloc[0].to_dict()

        parent_node_index = matches.index[0]

        diff_in_g_level = parent_node['ground_level_start'] - parent_node['ground_level_end']

        closest_iop_index = find_closest_iop_index_by_formula(discharge=parent_node['discharge'])

        closest_iop = IOP[closest_iop_index]

        fhl = find_friction_head_loss_by_formula(length=parent_node['length'], discharge=parent_node['discharge'],
                                                 cr_value=1, iop=closest_iop)

        min_needed_rhae_by_child = child_node['min_needed_rhas']

        min_needed_rhas = find_needed_rhas_for_getting_expected_rhae(difference_in_g_level=diff_in_g_level, fhl=fhl, expected_rhae=min_needed_rhae_by_child)

        parent_node_vals = {
            "min_needed_rhas": min_needed_rhas,
            "min_needed_rhae": min_needed_rhae_by_child,
            "fhl": fhl,
            "velocity": 3,
            "iop": closest_iop,
            "iop_index": closest_iop_index,
            "start_node": parent_node['start_node'],
            "end_node": parent_node['end_node']
        }
        if parent_node_index not in reverse_calc_dict:
            reverse_calc_dict[parent_node_index] = parent_node_vals
        else:
            if reverse_calc_dict[parent_node_index]["min_needed_rhae"] < min_needed_rhae_by_child:
                reverse_calc_dict[parent_node_index] = parent_node_vals
            else:
                pass
        result = find_rhas_and_rhae_for_parents(parent_node_vals)

        return result
    else:
        return None



# find_rhas_and_rhae_for_parents({
# "min_needed_rhas": 30.51438,
#         "min_needed_rhae": 28,
#         "fhl": 1.37438,
#         "velocity": 3,
#         "iop": 96.8,
#         "iop_index": 0,
#         "start_node": "J-383400",
#         "end_node": "V38_C6"
# })

def find_min_rhas_for_child_pipes(c_index):

    child_pipe = ordered_df.loc[c_index]

    closest_iop_index = find_closest_iop_index_by_formula(discharge=child_pipe['discharge'])

    closest_iop = IOP[closest_iop_index]

    fhl = find_friction_head_loss_by_formula(length=child_pipe['length'], discharge=child_pipe['discharge'], cr_value=1, iop=closest_iop)

    diff_in_g_level = child_pipe['ground_level_start'] - child_pipe['ground_level_end']

    min_needed_rhas = find_needed_rhas_for_getting_expected_rhae(difference_in_g_level=diff_in_g_level, fhl=fhl)

    child_node_vals = {
        "min_needed_rhas": min_needed_rhas,
        "min_needed_rhae": 28,
        "fhl": fhl,
        "velocity": 3,
        "iop": closest_iop,
        "iop_index": closest_iop_index,
        "start_node": child_pipe['start_node'],
        "end_node": child_pipe['end_node']
    }

    reverse_calc_dict[c_index] = child_node_vals

    find_rhas_and_rhae_for_parents(child_node_vals)




for idx, row in ordered_df.iterrows():
    if "V" in row['end_node']:
        find_min_rhas_for_child_pipes(idx)

for v_index, village_row in reverse_calc_dict.items():
    ordered_df.loc[v_index, "start_node"] = village_row['start_node']
    ordered_df.loc[v_index, "end_node"] = village_row['end_node']
    ordered_df.loc[v_index, "iop_index"] = village_row['iop_index']
    ordered_df.loc[v_index, "iop"] = village_row['iop']
    ordered_df.loc[v_index, "rhas"] = village_row['min_needed_rhas']
    ordered_df.loc[v_index, "rhae"] = village_row['min_needed_rhae']
    ordered_df.loc[v_index, "fhl"] = village_row['fhl']

ordered_df.to_excel("min_rhas_for_child.xlsx")


def correct_rhas_and_rhae_values(corrected_iop_dict):

    for idx, new_iop in corrected_iop_dict.items():
        parent_indexes_list = ordered_df.index[ordered_df['end_node'] == calculated_dict[idx]['start_node']].to_list()

        parent_index = None if len(parent_indexes_list) == 0 else parent_indexes_list[0]

        rhas = 0 if parent_index is None else calculated_dict[parent_index]['rhae']

        calculated_dict[idx]['rhas'] = rhas

        calculated_dict[idx]['velocity'] = find_velocity_by_formula(discharge=calculated_dict[idx]['discharge'], id_of_pipe=calculated_dict[idx]['iop'])

        diff_in_g_level = calculated_dict[idx]['ground_level_start'] - calculated_dict[idx]['ground_level_end']

        calculated_dict[idx]['rhae'] = find_residual_head_at_end_by_formula(diff_in_g_level=diff_in_g_level, rhas=rhas,
                                                                            fhl=calculated_dict[idx]['fhl'])


def upgrade_parent_iop_of_child_pipes(pipe_index_of_parent, parent_iop):
    parent_pipe = calculated_dict[pipe_index_of_parent]

    child_pipe_indexes = ordered_df.index[ordered_df['start_node'] == parent_pipe['end_node']].to_list()

    for child_idx in child_pipe_indexes:
        if child_idx in calculated_dict:
            calculated_dict[child_idx]['parent_iop'] = parent_iop


def find_correct_indexes_that_gives_needed_rhae(c_index, c_rhae, is_village):
    needed_rhae = MINIMUN_VILLAGE_RHAE if is_village else MINIMUM_PARENT_RHAE
    missing_rhae = needed_rhae - c_rhae
    if c_index == 42:
        print("hi")
    correct_indexes = {index:row_vals['iop'] for index, row_vals in calculated_dict.items()}
    j = 1
    move_forward = False
    while missing_rhae > 0:
        pipe_index = c_index-j
        if pipe_index > 0:
            if pipe_index == c_index:
                move_forward = False
                pipe_index -= 1
            pipe_above = calculated_dict[pipe_index]
            if "V" not in pipe_above['end_node'] and pipe_above['iop'] < pipe_above['parent_iop']:
                current_iop_index = IOP.index(pipe_above['iop'])
                # new_iop = IOP[current_iop_index+1]
                new_iop = IOP[current_iop_index+1] if move_forward else pipe_above['parent_iop']
                new_fhl = find_friction_head_loss_by_formula(length=pipe_above['length'],discharge=pipe_above['discharge'],
                                                             cr_value=1,iop=new_iop)
                reduced_fhl = pipe_above['fhl'] - new_fhl
                missing_rhae = missing_rhae - reduced_fhl
                correct_indexes[pipe_index] = pipe_above['parent_iop']
                calculated_dict[pipe_index]['iop'] = new_iop
                calculated_dict[pipe_index]['fhl'] = new_fhl
                upgrade_parent_iop_of_child_pipes(pipe_index_of_parent=pipe_index, parent_iop=new_iop)
                move_forward=True
                j += 1

        else:
            pipe_above = calculated_dict[pipe_index]
            top_iop_index = IOP.index(pipe_above['iop'])
            if top_iop_index + 1 < len(IOP):
                increased_top_iop = IOP[top_iop_index+1]
                new_fhl = find_friction_head_loss_by_formula(length=pipe_above['length'], discharge=pipe_above['discharge'],
                                                             cr_value=1, iop=increased_top_iop)
                reduced_fhl = pipe_above['fhl'] - new_fhl
                missing_rhae = missing_rhae - reduced_fhl
                correct_indexes[pipe_index] = increased_top_iop
                calculated_dict[pipe_index]['iop'] = increased_top_iop
                calculated_dict[pipe_index]['fhl'] = new_fhl
                upgrade_parent_iop_of_child_pipes(pipe_index_of_parent=pipe_index, parent_iop=increased_top_iop)
            else:
                for h_c_i, h_c_row in calculated_dict.items():
                    if h_c_row['iop'] == IOP[-1]:
                        j += -1
                    else:
                        j += 1
                        break
            move_forward = True

        j += -1 if move_forward else 1

    return correct_indexes



def find_rhae(row_index, row_from_df, rhas, parent_iop):
    closest_iop_index = find_closest_iop_index_by_formula(row_from_df['discharge'])

    closest_iop = IOP[closest_iop_index]

    velocity = find_velocity_by_formula(discharge=row_from_df['discharge'], id_of_pipe=closest_iop)

    fhl = find_friction_head_loss_by_formula(length=row_from_df['length'],
                                             discharge=row_from_df['discharge'],
                                             cr_value=1,
                                             iop=closest_iop)

    diff_in_g_level = row_from_df['ground_level_start'] - row_from_df['ground_level_end']

    rhae = find_residual_head_at_end_by_formula(diff_in_g_level=diff_in_g_level, rhas=rhas,
                                                fhl=fhl)

    rhae_meets_criteria = check_rhae_meets_criteria(rhae, row_from_df['end_node'])

    if rhae_meets_criteria:
        calculated_dict[row_index] = {
            "start_node": row_from_df['start_node'],
            "end_node": row_from_df['end_node'],
            "length": row_from_df['length'],
            "discharge": row_from_df['discharge'],
            "ground_level_start": row_from_df["ground_level_start"],
            "ground_level_end": row_from_df["ground_level_end"],
            "parent_iop": parent_iop,
            "iop": closest_iop,
            "iop_index": IOP.index(closest_iop),
            "fhl": fhl,
            "velocity": velocity,
            "rhas": rhas,
            "rhae": rhae
        }
        return rhae
    else:
        """find correct indexes that gives needed rhae"""
        correct_indexes = find_correct_indexes_that_gives_needed_rhae(c_index=row_index, c_rhae=rhae, is_village= "V" in row_from_df['end_node'])

        correct_rhas_and_rhae_values(correct_indexes)

        parent_indexes_list = ordered_df.index[ordered_df['end_node'] == current_row_from_df['start_node']].to_list()

        parent_index = None if len(parent_indexes_list) == 0 else parent_indexes_list[0]

        rhas = 0 if parent_index is None else calculated_dict[parent_index]['rhae']

        parent_iop = None if parent_index is None else calculated_dict[parent_index]['iop']

        rhae = find_rhae(row_index=row_index, row_from_df=row_from_df, rhas=rhas, parent_iop=parent_iop)

        return rhae

def check_rhae_meets_criteria(rhae, end_node):
    if "V" in end_node and rhae > MINIMUN_VILLAGE_RHAE:
        return True
    elif "J" in end_node and rhae > MINIMUM_PARENT_RHAE:
        return True
    else:
        return False


# while i < len(ordered_df):
#     print("*********----->", i)
#     current_row_from_df = ordered_df.loc[i]
#
#     parent_pipe_index_list = ordered_df.index[ordered_df['end_node'] == current_row_from_df['start_node']].to_list()
#
#     parent_pipe_index = None if len(parent_pipe_index_list) == 0 else parent_pipe_index_list[0]
#
#     PARENT_IOP = None if parent_pipe_index is None else calculated_dict[parent_pipe_index]['iop']
#
#     RHAS = 0 if parent_pipe_index is None else calculated_dict[parent_pipe_index]['rhae']
#
#     current_row_rhae = find_rhae(i, current_row_from_df, RHAS, PARENT_IOP)
#
#     i += 1
#
#
# print(calculated_dict)
#
# for key, value in calculated_dict.items():
#     ordered_df.loc[key, 'new_iop'] = value['iop']
#     ordered_df.loc[key, 'new_velocity'] = value['velocity']
#     ordered_df.loc[key, 'new_fhl'] = value['fhl']
#     ordered_df.loc[key, 'available_residual_head_at_start'] = round(value['rhas'], 2)
#     ordered_df.loc[key, 'residual_head_at_end'] = round(value['rhae'], 2)
#
# ordered_df.to_excel('mha6.xlsx')




