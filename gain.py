from gpt_dfs import dfs_df as ordered_df
from constants import IOP, find_closest_iop_index_by_formula, find_velocity_by_formula, \
    find_residual_head_at_end_by_formula, find_friction_head_loss_by_formula

calculated_dict = {}

i = 0
RHAS = 0
PARENT_IOP = None
MINIMUM_PARENT_RHAE = 0
MINIMUN_VILLAGE_RHAE = 28


reverse_calc_dict = {}

def give_parent_pipe_details(child_start_node):
    matches = ordered_df.loc[ordered_df['end_node'] == child_start_node]

    if not matches.empty:
        parent_pipe = matches.iloc[0].to_dict()

        parent_pipe["index"] = matches.index[0]

        return parent_pipe
    else:

        return None


def create_the_parents_iop_dict(child_pipe):
    pidx_and_piops = {}
    parent_pipe = give_parent_pipe_details(child_start_node=child_pipe['start_node'])
    while parent_pipe is not None:
        pidx = parent_pipe['index']
        pidx_and_piops[pidx] = calculated_dict[pidx]['iop']
        parent_pipe = give_parent_pipe_details(child_start_node=parent_pipe['start_node'])
    else:
        pass
    return pidx_and_piops


def give_rhae_with_parents_iop_alone(pipe):

    parent_pipe = give_parent_pipe_details(pipe['start_node'])

    ppidx = parent_pipe['index']

    iop = calculated_dict[ppidx]['iop']

    fhl = find_friction_head_loss_by_formula(length=pipe['length'],
                                             discharge=pipe['discharge'],
                                             cr_value=1,
                                             iop=iop)

    diff_in_g_level = pipe['ground_level_start'] - pipe['ground_level_end']



    rhas = calculated_dict[ppidx]['rhae']

    rhae = find_residual_head_at_end_by_formula(diff_in_g_level=diff_in_g_level, rhas=rhas,
                                                fhl=fhl)

    velocity = find_velocity_by_formula(pipe['discharge'], id_of_pipe=iop)

    new_vals = {
        "iop": iop,
        "parent_iop": iop,
        "iop_index": IOP.index(iop),
        "fhl": fhl,
        "rhas": rhas,
        "rhae": rhae,
        "velocity": velocity
    }

    return new_vals

def calculate_rhas_and_rhae_with_new_iop(new_iop_dict, start_from):

    recalculate_dict = {idx: new_iop for idx, new_iop in new_iop_dict.items() if idx >= start_from}

    for idx, new_iop in recalculate_dict.items():
        pipe = ordered_df.loc[idx]

        parent_pipe = give_parent_pipe_details(pipe['start_node'])

        pidx = None if parent_pipe is None else parent_pipe['index']

        rhas = 0 if parent_pipe is None else calculated_dict[pidx]['rhae']

        parent_iop = None if parent_pipe is None else calculated_dict[pidx]['iop']

        diff_g_level = pipe['ground_level_start'] - pipe['ground_level_end']

        velocity = find_velocity_by_formula(discharge=pipe['discharge'], id_of_pipe=new_iop)

        fhl = find_friction_head_loss_by_formula(length=pipe['length'], discharge=pipe['discharge'], cr_value=1, iop=new_iop)

        rhae = find_residual_head_at_end_by_formula(diff_in_g_level=diff_g_level,rhas=rhas,fhl=fhl)

        calculated_dict[idx]['rhas'] = rhas
        calculated_dict[idx]['rhae'] = rhae
        calculated_dict[idx]['fhl'] = fhl
        calculated_dict[idx]['velocity'] = velocity
        calculated_dict[idx]['iop'] = new_iop
        calculated_dict[idx]['parent_iop'] = parent_iop
        calculated_dict[idx]['iop_index'] = IOP.index(new_iop)

def get_the_iiplusone_dict(idx_and_iops):
    iop_indexes_dict = {}

    for idx, iop in idx_and_iops.items():
        iop_indexes_dict[iop] = [ix for ix, iop2 in idx_and_iops.items() if iop == iop2]

    ii_pi_dict = {IOP.index(ii): pi_list for ii, pi_list in iop_indexes_dict.items()}

    least_key = min(ii_pi_dict)

    iiplusone_pi_dict = {}

    iiplusone_pi_dict[least_key+1] = ii_pi_dict[least_key]
    # sorted_ii_pi_dict = {i: ii_pi_dict[i] for i in sorted(ii_pi_dict.keys())}
    # for iop_index, pipe_index_list in sorted_ii_pi_dict.items():
    #     if bool(iiplusone_pi_dict):
    #         if iop_index in iiplusone_pi_dict:
    #             if iop_index + 1 >= len(IOP):
    #                 break
    #             iiplusone_pi_dict[iop_index + 1] = pipe_index_list
    #     else:
    #         iiplusone_pi_dict[iop_index + 1] = pipe_index_list

    return iiplusone_pi_dict


def find_correct_indexes_that_gives_needed_rhae(c_index, c_rhae, is_village):
    needed_rhae = MINIMUN_VILLAGE_RHAE if is_village else MINIMUM_PARENT_RHAE

    child_row = ordered_df.loc[c_index]

    correct_indexes = {index: row_vals['iop'] for index, row_vals in calculated_dict.items()}

    idx_and_iops = create_the_parents_iop_dict(child_row)

    iiplusone_pi_dict = get_the_iiplusone_dict(idx_and_iops)

    new_vals = {}

    while c_rhae < needed_rhae:

        for iop_index in sorted(iiplusone_pi_dict.keys()):

            current_iop_using_indexes = iiplusone_pi_dict[iop_index]

            for index in current_iop_using_indexes:
                correct_indexes[index] = IOP[iop_index]

        highest_iop = max(iiplusone_pi_dict)

        changed_top_pipe_index = min(iiplusone_pi_dict[highest_iop])

        calculate_rhas_and_rhae_with_new_iop(correct_indexes, start_from=changed_top_pipe_index)

        new_vals = give_rhae_with_parents_iop_alone(child_row)

        c_rhae = new_vals['rhae']

        if c_rhae > needed_rhae:
            break

        idx_and_iops_new = create_the_parents_iop_dict(child_row)
        iiplusone_pi_dict = get_the_iiplusone_dict(idx_and_iops_new)

    print("dangerous, the girl is so dangerous")

    return new_vals



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

        new_vals = give_rhae_with_parents_iop_alone(row_from_df)
        child_rhae_with_parent_iop = new_vals['rhae']
        rhae_meets_criteria = check_rhae_meets_criteria(child_rhae_with_parent_iop, row_from_df['end_node'])

        if rhae_meets_criteria:
            calculated_dict[row_index] = {
                "start_node": row_from_df['start_node'],
                "end_node": row_from_df['end_node'],
                "length": row_from_df['length'],
                "discharge": row_from_df['discharge'],
                "ground_level_start": row_from_df["ground_level_start"],
                "ground_level_end": row_from_df["ground_level_end"],
                "parent_iop": new_vals['parent_iop'],
                "iop": new_vals['iop'],
                "iop_index": IOP.index(new_vals['iop']),
                "fhl": new_vals['fhl'],
                "velocity": new_vals['velocity'],
                "rhas": new_vals['rhas'],
                "rhae": child_rhae_with_parent_iop
            }
            return child_rhae_with_parent_iop
        else:

            new_vals = find_correct_indexes_that_gives_needed_rhae(c_index=row_index, c_rhae=rhae, is_village= "V" in row_from_df['end_node'])

            calculated_dict[row_index] = {
                "start_node": row_from_df['start_node'],
                "end_node": row_from_df['end_node'],
                "length": row_from_df['length'],
                "discharge": row_from_df['discharge'],
                "ground_level_start": row_from_df["ground_level_start"],
                "ground_level_end": row_from_df["ground_level_end"],
                "parent_iop": new_vals['parent_iop'],
                "iop": new_vals['iop'],
                "iop_index": IOP.index(new_vals['iop']),
                "fhl": new_vals['fhl'],
                "velocity": new_vals['velocity'],
                "rhas": new_vals['rhas'],
                "rhae": new_vals['rhae']
            }
            return new_vals['rhae']

def check_rhae_meets_criteria(rhae, end_node):
    if "V" in end_node and rhae > MINIMUN_VILLAGE_RHAE:
        return True
    elif "J" in end_node and rhae > MINIMUM_PARENT_RHAE:
        return True
    else:
        return False


while i < len(ordered_df):
    print("*********----->", i)
    current_row_from_df = ordered_df.loc[i]

    parent_pipe_index_list = ordered_df.index[ordered_df['end_node'] == current_row_from_df['start_node']].to_list()

    parent_pipe_index = None if len(parent_pipe_index_list) == 0 else parent_pipe_index_list[0]

    PARENT_IOP = None if parent_pipe_index is None else calculated_dict[parent_pipe_index]['iop']

    RHAS = 0 if parent_pipe_index is None else calculated_dict[parent_pipe_index]['rhae']

    current_row_rhae = find_rhae(i, current_row_from_df, RHAS, PARENT_IOP)

    i += 1


print(calculated_dict)

for key, value in calculated_dict.items():
    ordered_df.loc[key, 'new_iop'] = value['iop']
    ordered_df.loc[key, 'new_velocity'] = value['velocity']
    ordered_df.loc[key, 'new_fhl'] = value['fhl']
    ordered_df.loc[key, 'available_residual_head_at_start'] = round(value['rhas'], 2)
    ordered_df.loc[key, 'residual_head_at_end'] = round(value['rhae'], 2)

ordered_df.to_excel('mha6.xlsx')




