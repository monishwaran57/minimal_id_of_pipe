from gpt_dfs import dfs_df as ordered_df
from constants import IOP, find_closest_iop_index_by_formula, find_velocity_by_formula, \
    find_residual_head_at_end_by_formula, find_friction_head_loss_by_formula
import json
import logging
import os

try:
    os.remove('output.log')
except:
    print("no output log to delete")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('output.log'),
        # logging.StreamHandler()  # Also prints to console
    ]
)

calculated_dict = {}

i = 0
RHAS = 0
PARENT_IOP = None
MINIMUM_PARENT_RHAE = 28
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


def give_iop_pipe_indexes_dict(idx_and_iops):
    iop_pipe_indexes_dict = {}

    for idx, iop in idx_and_iops.items():
        iop_pipe_indexes_dict[iop] = [ix for ix, iop2 in idx_and_iops.items() if iop == iop2]


    return iop_pipe_indexes_dict


def give_rhae_with_given_iop_alone(pipe, iop):

    parent_pipe = give_parent_pipe_details(pipe['start_node'])

    ppidx = parent_pipe['index']

    parent_iop = calculated_dict[ppidx]['iop']

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
        "parent_iop": parent_iop,
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


def find_correct_indexes_that_gives_needed_rhae(c_index, c_rhae, is_village):
    needed_rhae = MINIMUN_VILLAGE_RHAE if is_village else MINIMUM_PARENT_RHAE

    child_row = ordered_df.loc[c_index]

    correct_indexes = {index: row_vals['iop'] for index, row_vals in calculated_dict.items()}

    idx_and_iops = create_the_parents_iop_dict(child_row)

    iop_pipe_indexes = give_iop_pipe_indexes_dict(idx_and_iops)

    new_vals = {}

    while c_rhae < needed_rhae:
        formatted_dict = {str(int_idx): str([int(pi) for pi in pi_list]) for int_idx, pi_list in
                          iop_pipe_indexes.items()}
        with open("log.txt", "w") as log_file:
            log_file.write(json.dumps(formatted_dict, indent=4))

        least_iop = min(iop_pipe_indexes)

        top_pipe_index_to_be_increased = min(iop_pipe_indexes[least_iop])

        iop_index = IOP.index(least_iop)

        correct_indexes[top_pipe_index_to_be_increased] = IOP[iop_index+1]

        for idx in range(top_pipe_index_to_be_increased+1, len(correct_indexes)):
            pipe_from_df = ordered_df.loc[idx]
            closest_iop_index = find_closest_iop_index_by_formula(pipe_from_df['discharge'])
            correct_indexes[idx] = IOP[closest_iop_index]


        calculate_rhas_and_rhae_with_new_iop(correct_indexes, start_from=top_pipe_index_to_be_increased)

        parent_pipe = give_parent_pipe_details(child_start_node=child_row['start_node'])

        ppidx = parent_pipe['index']

        parent_iop = 0 if parent_pipe is None else calculated_dict[ppidx]['iop']

        small_iop_index = find_closest_iop_index_by_formula(child_row['discharge'])

        small_iop = IOP[small_iop_index]

        while small_iop <= parent_iop:

            new_vals = give_rhae_with_given_iop_alone(child_row, small_iop)

            c_rhae = new_vals['rhae']

            if c_rhae > needed_rhae:
                break

            small_iop_index += 1

            small_iop = IOP[small_iop_index]

        if c_rhae > needed_rhae:
            break

        idx_and_iops_new = create_the_parents_iop_dict(child_row)
        iop_pipe_indexes = give_iop_pipe_indexes_dict(idx_and_iops_new)

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
        while closest_iop <= parent_iop:
            new_vals = give_rhae_with_given_iop_alone(row_from_df, iop=closest_iop)
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
            current_iop_index = IOP.index(closest_iop)
            closest_iop = IOP[current_iop_index+1]
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
    logging.info(f"-------------------->{i}")
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




