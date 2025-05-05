import copy
import json

import pandas as pd

from gpt_dfs import dfs_df
from constants import IOP
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

IOP_INDEX = 0
RHAS = 0
LOOP_COUNT = {}
increased_top = {0:0}


def find_velocity_by_formula(discharge, id_of_pipe):
    velocity = discharge * (4 / (3.14 * (id_of_pipe / 1000) ** 2))
    return round(velocity, 5)


def find_closest_iop_index_by_formula(discharge):
    velocity = 3
    id_of_pipe = (((4 / (velocity / discharge)) / 3.14) ** (1 / 2)) * 1000
    closest_value = min(IOP, key=lambda x: abs(x - id_of_pipe))
    iop_index = IOP.index(closest_value)
    return iop_index


def find_friction_head_loss_by_formula(length, discharge, cr_value, iop):
    fhl = ((length * (discharge / cr_value) ** 1.81) / (994.62 * (iop / 1000) ** 4.81)) * 1.1
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

def find_rhae_until_atmost_bottom(c_r_i, c_fhl, current_row_iop, entire_dict, c_index):
    current_row = entire_dict[c_r_i]
    c_rhas = current_row['rhas']
    c_parent_iop = current_row['parent_iop']
    for row_index in range(c_r_i, len(entire_dict)):
        c_row = entire_dict[row_index]
        diff_in_g_level = c_row['row_vals']['ground_level_start'] - c_row['row_vals']['ground_level_end']
        new_rhae = find_residual_head_at_end_by_formula(diff_in_g_level=diff_in_g_level,
                                             avail_resi_head_at_start=c_rhas,
                                             fhl=c_fhl)

        entire_dict[row_index]['rhas'] = c_rhas
        entire_dict[row_index]['rhae'] = new_rhae
        entire_dict[row_index]['iop'] = current_row_iop
        entire_dict[row_index]['iop_index'] = IOP.index(current_row_iop)
        entire_dict[row_index]['parent_iop'] = c_parent_iop

        c_rhas = new_rhae
        c_parent_iop = current_row_iop
        if row_index+1 in entire_dict:
            c_row = entire_dict[row_index+1]
            c_fhl = find_friction_head_loss_by_formula(length=c_row['row_vals']['length'],
                                                       discharge=c_row['row_vals']['discharge'],
                                                       cr_value=1,
                                                       iop=c_row['iop'])
            current_row_iop = c_row['iop']
        else:
            break

    child_row = ordered_df.loc[c_index]
    parent_pipe_indices_list = ordered_df.index[
        ordered_df['end_node'] == child_row['start_node']].to_list()
    childs_parent_pipe_index = 0 if len(parent_pipe_indices_list) == 0 else parent_pipe_indices_list[0]
    CHILDS_PARENT_RHAS = entire_dict[childs_parent_pipe_index]['rhae'] if c_index != 0 else 0
    nearer_iop_index = find_closest_iop_index_by_formula(discharge=child_row['discharge'])
    parents_iop_index = entire_dict[childs_parent_pipe_index]['iop_index']
    new_c_rhae = None

    while nearer_iop_index <= parents_iop_index:

        new_c_fhl = find_friction_head_loss_by_formula(length=child_row['length'], discharge=child_row['discharge'],
                                                       cr_value=1, iop=IOP[nearer_iop_index])
        diff_in_g_level = child_row['ground_level_start'] - child_row['ground_level_end']
        new_c_rhae = find_residual_head_at_end_by_formula(diff_in_g_level=diff_in_g_level,
                                                          avail_resi_head_at_start=CHILDS_PARENT_RHAS,
                                                          fhl=new_c_fhl)
        nearer_iop_index += 1

    return new_c_rhae



def make_some_pressure_for_child_node(c_rhae, c_index, previous_values_dict, village_node):
    needed_rhae = 28 if village_node else 21
    missing_rhae = needed_rhae - c_rhae
    print("missing rhae", missing_rhae)
    print("previous dict", previous_values_dict)
    duplicate_dict = copy.deepcopy(previous_values_dict)
    size_increasable_parent_pipes = []
    i = 1
    j = 0
    forward_i = 1
    forward_step = False
    size_increased_parent_pipes = {}
    while missing_rhae >=0:
        parent_pipe = duplicate_dict[c_index - i]
        current_iop_index = IOP.index(parent_pipe['iop'])

        if current_iop_index >= len(IOP) - 1:
            forward_step = True
            for h_c_i, h_c_row in duplicate_dict.items():
                if h_c_row['iop'] == IOP[-1]:
                    j = None
                else:
                    j = h_c_i
                    break
            i = 0
            parent_pipe = duplicate_dict[j]
            current_iop_index = IOP.index(parent_pipe['iop'])
            using_index = j

            previous_values_dict = duplicate_dict
            # previous_values_dict = {**previous_values_dict, **size_increased_parent_pipes}
            new_computed_dict = {}
            sorted_dict = {k: previous_values_dict[k] for k in sorted(previous_values_dict)}
            for f_r_i, f_row in sorted_dict.items():
                if f_r_i <= j:
                    continue
                parent_iop_index = find_closest_iop_index_by_formula(f_row['row_vals']['discharge'])
                pipe_indices_list = ordered_df.index[
                    ordered_df['end_node'] == f_row['row_vals']['start_node']].to_list()
                parent_pipe_index = 0 if len(pipe_indices_list) == 0 else pipe_indices_list[0]
                PARENT_RHAS = previous_values_dict[parent_pipe_index]['rhae'] if f_r_i != 0 else 0

                new_computed_values = start_increasing_iop_values(f_row['row_vals'], parent_iop_index,
                                                                  f_r_i, PARENT_RHAS, previous_values_dict)
                new_computed_dict = new_computed_values
                previous_values_dict = new_computed_values

            child_row = ordered_df.loc[c_index]
            parent_pipe_indices_list = ordered_df.index[
                ordered_df['end_node'] == child_row['start_node']].to_list()
            childs_parent_pipe_index = 0 if len(parent_pipe_indices_list) == 0 else parent_pipe_indices_list[0]
            CHILDS_PARENT_RHAS = previous_values_dict[childs_parent_pipe_index]['rhae'] if c_index != 0 else 0
            nearer_iop_index = find_closest_iop_index_by_formula(discharge=child_row['discharge'])
            parents_iop_index = new_computed_dict[childs_parent_pipe_index]['iop_index']
            new_c_rhae = c_rhae

            while nearer_iop_index <= parents_iop_index:
                new_c_fhl = find_friction_head_loss_by_formula(length=child_row['length'],
                                                               discharge=child_row['discharge'],
                                                               cr_value=1, iop=IOP[nearer_iop_index])
                diff_in_g_level = child_row['ground_level_start'] - child_row['ground_level_end']
                new_c_rhae = find_residual_head_at_end_by_formula(diff_in_g_level=diff_in_g_level,
                                                                  avail_resi_head_at_start=CHILDS_PARENT_RHAS,
                                                                  fhl=new_c_fhl)
                nearer_iop_index += 1

            needed_rhae = 28 if village_node else 21
            missing_rhae = needed_rhae - new_c_rhae
            if missing_rhae <= 0:
                pass
            else:
                result = make_some_pressure_for_child_node(c_rhae=new_c_rhae, c_index=c_index,
                                                           previous_values_dict=previous_values_dict,
                                                           village_node=village_node)
                return result
            return new_computed_dict

        else:
            using_index = c_index - i
            if parent_pipe['parent_iop'] is None or ("V" not in parent_pipe['row_vals']['end_node'] and parent_pipe['iop'] < parent_pipe['parent_iop']):
                size_increasable_parent_pipes.append(parent_pipe)
                print(previous_values_dict)

                    # forward_i += 1

                increased_iop = IOP[current_iop_index + 1]

                new_velocity = find_velocity_by_formula(discharge=parent_pipe['row_vals']['discharge'],
                                                        id_of_pipe=increased_iop)
                new_fhl = find_friction_head_loss_by_formula(length=parent_pipe['row_vals']['length'],
                                                             discharge=parent_pipe['row_vals']['discharge'],
                                                             cr_value=1, iop=increased_iop)


                # new_c_rhae = find_rhae_until_atmost_bottom(c_r_i=using_index,current_row_iop=increased_iop,entire_dict=previous_values_dict,
                #                               c_fhl=new_fhl,c_index=c_index)

                reduced_fhl = parent_pipe['fhl'] - new_fhl
                missing_rhae = missing_rhae - reduced_fhl
                parent_pipe['fhl'] = new_fhl
                parent_pipe['iop'] = increased_iop
                parent_pipe['iop_index'] = IOP.index(increased_iop)

                diff_in_g_level = parent_pipe['row_vals']['ground_level_start'] - parent_pipe['row_vals']['ground_level_end']
                new_rhae = find_residual_head_at_end_by_formula(diff_in_g_level=diff_in_g_level, avail_resi_head_at_start=parent_pipe['rhas'],
                                                     fhl=new_fhl)

                child_pipes_indices_list = ordered_df.index[
                    ordered_df['start_node'] == parent_pipe['row_vals']['end_node']].to_list()
                for child_index in child_pipes_indices_list:
                    if child_index in duplicate_dict:
                        duplicate_dict[child_index]['parent_iop'] = increased_iop
                        duplicate_dict[child_index]['rhas'] = new_rhae


                size_increased_parent_pipes[c_index - i] = parent_pipe
                print(previous_values_dict)

        i += 1
        if i > c_index:
            previous_values_dict = duplicate_dict
            # previous_values_dict = {**previous_values_dict, **size_increased_parent_pipes}
            new_computed_dict = {}
            sorted_dict = {k: previous_values_dict[k] for k in sorted(previous_values_dict)}
            for f_r_i, f_row in sorted_dict.items():
                if f_r_i <= j:
                    continue
                parent_iop_index = find_closest_iop_index_by_formula(f_row['row_vals']['discharge'])
                pipe_indices_list = ordered_df.index[
                    ordered_df['end_node'] == f_row['row_vals']['start_node']].to_list()
                parent_pipe_index = 0 if len(pipe_indices_list) == 0 else pipe_indices_list[0]
                PARENT_RHAS = previous_values_dict[parent_pipe_index]['rhae'] if f_r_i != 0 else 0

                new_computed_values = start_increasing_iop_values(f_row['row_vals'], parent_iop_index,
                                                                  f_r_i, PARENT_RHAS, previous_values_dict)
                new_computed_dict = new_computed_values
                previous_values_dict = new_computed_values

            child_row = ordered_df.loc[c_index]
            parent_pipe_indices_list = ordered_df.index[
                ordered_df['end_node'] == child_row['start_node']].to_list()
            childs_parent_pipe_index = 0 if len(parent_pipe_indices_list) == 0 else parent_pipe_indices_list[0]
            CHILDS_PARENT_RHAS = previous_values_dict[childs_parent_pipe_index]['rhae'] if c_index != 0 else 0
            nearer_iop_index = find_closest_iop_index_by_formula(discharge=child_row['discharge'])
            parents_iop_index = new_computed_dict[childs_parent_pipe_index]['iop_index']
            new_c_rhae = c_rhae

            while nearer_iop_index <= parents_iop_index:
                new_c_fhl = find_friction_head_loss_by_formula(length=child_row['length'],
                                                               discharge=child_row['discharge'],
                                                               cr_value=1, iop=IOP[nearer_iop_index])
                diff_in_g_level = child_row['ground_level_start'] - child_row['ground_level_end']
                new_c_rhae = find_residual_head_at_end_by_formula(diff_in_g_level=diff_in_g_level,
                                                                  avail_resi_head_at_start=CHILDS_PARENT_RHAS,
                                                                  fhl=new_c_fhl)
                nearer_iop_index += 1

            needed_rhae = 28 if village_node else 21
            missing_rhae = needed_rhae - new_c_rhae
            if missing_rhae <= 0:
                pass
            else:
                result = make_some_pressure_for_child_node(c_rhae=new_c_rhae, c_index=c_index,
                                                           previous_values_dict=previous_values_dict,
                                                           village_node=village_node)
                return result
            return new_computed_dict

    # previous_values_dict = {**previous_values_dict, **size_increased_parent_pipes}
    previous_values_dict = duplicate_dict
    sorted_dict = {k: previous_values_dict[k] for k in sorted(previous_values_dict)}
    for f_r_i, f_row in sorted_dict.items():
        parent_iop_index = IOP.index(f_row['iop'])
        pipe_indices_list = ordered_df.index[
            ordered_df['end_node'] == f_row['row_vals']['start_node']].to_list()
        parent_pipe_index = 0 if len(pipe_indices_list) == 0 else pipe_indices_list[0]
        PARENT_RHAS = previous_values_dict[parent_pipe_index]['rhae'] if f_r_i != 0 else 0

        new_computed_values = start_increasing_iop_values(f_row['row_vals'], parent_iop_index,
                                                          f_r_i, PARENT_RHAS, previous_values_dict)
        previous_values_dict = new_computed_values
    print("look inside way the things tonight", size_increasable_parent_pipes)
    return previous_values_dict




log_rows = []
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

    log_row = {
        "row_index": wr_index,
        "start_node": working_row['start_node'],
        "end_node": working_row['end_node'],
        "iop_index": iop_index,
        "parent_iop": previous_iop,
        "iop": IOP[iop_index],
        "rhas": rhas,
        "rhae": calculated_rhae,
        "velocity": calculated_velocity,
        "fhl": calculated_fhl,
        "is_village_node": "V" in working_row["end_node"]
    }
    log_rows.append(log_row)
    logging.info(f"rhas--->{rhas}")
    logging.info(f"rhae--->{calculated_rhae}")
    logging.info(f"velocity{calculated_velocity}")
    logging.info(f"fhl--->{calculated_fhl}")
    logging.info(f"iop index{iop_index}")
    logging.info(f"current_iop---->{IOP[iop_index]}")
    logging.info(f"previous_iop---->{previous_iop}")
    logging.info(
        f"current_row:::{wr_index}, start_node::::{working_row['start_node']}, end_node::::{working_row['end_node']}")
    if previous_iop and IOP[iop_index] > previous_iop:
        return [False, log_row]

    elif 0.6 <= calculated_velocity <= 3 and calculated_rhae > 1:
        is_village_node = "V" in working_row["end_node"]
        # print("passed velocity, if its village node", is_village_node)
        if is_village_node:
            if calculated_rhae >= 28:
                # HIGHEST_IOP_EVER_HAD.clear()
                return {
                    "iop": IOP[iop_index],
                    "parent_iop": previous_iop,
                    "iop_index": iop_index,
                    "velocity": calculated_velocity,
                    "fhl": calculated_fhl,
                    "rhas": rhas,
                    "rhae": calculated_rhae,
                    "row_vals": dict(working_row),
                }
            else:
                result = get_computed_values(working_row, iop_index + 1, wr_index, rhas, previous_values_dict)
                return result
        else:
            # HIGHEST_IOP_EVER_HAD.clear()
            return {
                "iop": IOP[iop_index],
                "parent_iop": previous_iop,
                "iop_index": iop_index,
                "velocity": calculated_velocity,
                "fhl": calculated_fhl,
                "rhas": rhas,
                "rhae": calculated_rhae,
                "row_vals": dict(working_row),
            }

    else:
        if iop_index +1 > len(IOP)-1:
            return False
        result = get_computed_values(working_row, iop_index + 1, wr_index, rhas, previous_values_dict)
        return result


def start_increasing_iop_values(working_row, iop_index, row_index, rhas, computed_values_dict):
    logging.info(f"row index<--{row_index}-->")
    if iop_index > len(IOP)-1:
        return False
    if row_index in LOOP_COUNT:
        if IOP[iop_index] in LOOP_COUNT[row_index]['count']:
            LOOP_COUNT[row_index]['count'][IOP[iop_index]] = LOOP_COUNT[row_index]['count'][IOP[iop_index]] + 1
        else:
            LOOP_COUNT[row_index]['count'][IOP[iop_index]] = 1
    else:
        LOOP_COUNT[row_index] = {'count': {IOP[iop_index]: 1}}

    current_row_computed_values = get_computed_values(working_row, iop_index, row_index, rhas, computed_values_dict)
    if False not in current_row_computed_values:
        computed_values = {
            "velocity": current_row_computed_values['velocity'],
            "iop": current_row_computed_values['iop'],
            "parent_iop": current_row_computed_values['parent_iop'],
            "iop_index": current_row_computed_values['iop_index'],
            "fhl": current_row_computed_values['fhl'],
            "rhas": current_row_computed_values['rhas'],
            "rhae": current_row_computed_values['rhae'],
            "row_vals": current_row_computed_values['row_vals']
        }
        computed_values_dict[row_index] = computed_values
        return computed_values_dict
    else:
        """Need some pressure!!!!!"""
        pressure_needing_pipe_details = current_row_computed_values[1]

        size_increased_parents = make_some_pressure_for_child_node(c_rhae=pressure_needing_pipe_details['rhae'],
                                                                   c_index=pressure_needing_pipe_details[
                                                                       'row_index'],
                                                                   previous_values_dict=computed_values_dict,
                                                                   village_node=pressure_needing_pipe_details['is_village_node'])

        return size_increased_parents

        recomputed_rows = []
        sorted_dict = {k: size_increased_parents[k] for k in sorted(size_increased_parents)}
        for parent_index, parent in sorted_dict.items():
            parent_iop_index = IOP.index(parent['parent_iop'])
            pipe_indices_list = ordered_df.index[ordered_df['end_node'] == parent['row_vals']['start_node']].to_list()
            parent_pipe_index = 0 if len(pipe_indices_list) == 0 else pipe_indices_list[0]
            PARENT_RHAS = computed_values_dict[parent_pipe_index]['rhae']
            computed_values = start_increasing_iop_values(parent['row_vals'], parent_iop_index,
                                                          parent_index, PARENT_RHAS, computed_values_dict)
            recomputed_rows.append(computed_values[0])
        return recomputed_rows



computed_values_dict = {}
i = 0
DELETE_MEMORY_INDEX = 0
HIGHEST_IOP_INDEX_OF_PARENT_PIPE = 0
try:
    while i <= len(ordered_df) - 1:
        logging.info(f"current row>>>{i}")
        print("current row----->", i)

        row = ordered_df.loc[i]
        # HIGHEST_IOP_EVER_HAD.clear()
        closest_iop_index = find_closest_iop_index_by_formula(row['discharge'])
        if i in increased_top:
            closest_iop_index += increased_top[i]

        comp_values = start_increasing_iop_values(row, closest_iop_index, i, RHAS, computed_values_dict)


        if comp_values:
            computed_values_dict = comp_values
            i = list(computed_values_dict)[-1]
            i += 1
            current_row = ordered_df.loc[i]

            pipe_indices_list = ordered_df.index[ordered_df['end_node'] == current_row['start_node']].to_list()
            parent_pipe_index = 0 if len(pipe_indices_list) == 0 else pipe_indices_list[0]
            RHAS = computed_values_dict[parent_pipe_index]['rhae']
        elif not comp_values:
            print("excepttttttttttttttion thejdfkdjfdkjf")
            log_df = pd.DataFrame(log_rows)
            log_df.to_excel("log.xlsx")
            break
        else:
            with open("log.json", "w") as log_file:
                json.dump(computed_values_dict, log_file, indent=4)
            i = list(computed_values_dict)[-1]

            i += 1

            if i > len(ordered_df) - 1:
                log_df = pd.DataFrame(log_rows)
                log_df.to_excel('log.xlsx')
                break

            current_row = ordered_df.loc[i]

            pipe_indices_list = ordered_df.index[ordered_df['end_node'] == current_row['start_node']].to_list()
            parent_pipe_index = 0 if len(pipe_indices_list) == 0 else pipe_indices_list[0]
            RHAS = computed_values_dict[parent_pipe_index]['rhae']

    for key, value in computed_values_dict.items():
        ordered_df.loc[key, 'new_iop'] = value['iop']
        ordered_df.loc[key, 'new_velocity'] = value['velocity']
        ordered_df.loc[key, 'new_fhl'] = value['fhl']
        ordered_df.loc[key, 'available_residual_head_at_start'] = round(value['rhas'], 2)
        ordered_df.loc[key, 'residual_head_at_end'] = round(value['rhae'], 2)

    ordered_df.to_excel('mha6.xlsx')
except KeyboardInterrupt:
    log_df = pd.DataFrame(log_rows)
    log_df.to_excel("log.xlsx")
