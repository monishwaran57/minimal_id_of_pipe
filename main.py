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
HIGHEST_IOP_EVER_HAD = {}
LOOP_COUNT = {}


def find_velocity_by_formula(discharge, id_of_pipe):
    velocity = discharge * (4 / (3.14 * (id_of_pipe / 1000) ** 2))
    return round(velocity, 5)


def find_closest_iop_index_by_formula(discharge):
    velocity = 1.8
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


def make_some_pressure_for_village_node(v_rhae, v_index, previous_values_dict):
    missing_rhae = 28 - v_rhae
    print("missing rhae", missing_rhae)
    size_increasable_parent_pipes = []
    i = 1
    size_increased_parent_pipes = {}
    while missing_rhae >=0:
        parent_pipe = previous_values_dict[v_index-i]
        if "V" not in parent_pipe['row_vals']['end_node']:
            size_increasable_parent_pipes.append(parent_pipe)
            new_fhl = find_friction_head_loss_by_formula(length=parent_pipe['row_vals']['length'], discharge=parent_pipe['row_vals']['discharge'],
                                               cr_value=1, iop=parent_pipe['parent_iop'])
            parent_pipe['new_fhl'] = new_fhl
            size_increased_parent_pipes[v_index-i] = parent_pipe
            reduced_fhl = parent_pipe['fhl'] - new_fhl
            missing_rhae = missing_rhae - reduced_fhl
        i += 1
    print("size increasable parent pipes", size_increasable_parent_pipes)




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
        "fhl": calculated_fhl
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
        HIGHEST_IOP_EVER_HAD[wr_index] = iop_index
        return False

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
                make_some_pressure_for_village_node(calculated_rhae, wr_index, previous_values_dict)
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


def start_increasing_iop_values(working_row, iop_index, row_index, rhas, computed_values_dict, delete_memory_index,
                                highest_iop_index_of_first_pipe):
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

    logging.info(f"HIOP\n{HIGHEST_IOP_EVER_HAD}")
    current_row_computed_values = get_computed_values(working_row, iop_index, row_index, rhas, computed_values_dict)
    if current_row_computed_values:
        computed_values = {
            "velocity": current_row_computed_values['velocity'],
            "iop": current_row_computed_values['iop'],
            "parent_iop": current_row_computed_values['parent_iop'],
            "iop_index": current_row_computed_values['iop_index'],
            "fhl": current_row_computed_values['fhl'],
            "rhas": current_row_computed_values['rhas'],
            "rhae": current_row_computed_values['rhae'],
            "row_vals": current_row_computed_values['row_vals'],
            'delete_memory_index': delete_memory_index,
        }
        computed_values_dict[row_index] = computed_values
        return computed_values
    else:
        """Use high iop for previous pipe"""
        # logging.info(f"MORATTU LOOPUH\n{LOOP_COUNT}")
        # print(f"MORATTU LOOPUH\n{LOOP_COUNT}")
        current_pipe_starting_node = working_row['start_node']
        parent_pipe_index_list = ordered_df.index[ordered_df['end_node'] == current_pipe_starting_node].to_list()
        if len(parent_pipe_index_list) == 0:
            parent_pipe_index = 0
        else:
            parent_pipe_index = parent_pipe_index_list[0]

        parent_row = computed_values_dict[parent_pipe_index]
        if parent_pipe_index == 0:
            logging.info(f"i became zerooooooo: {parent_pipe_index}, i'm going to reset delete memory index{DELETE_MEMORY_INDEX}")
            delete_memory_index = 0
        logging.info(
            f"ppi---->{parent_pipe_index}==dmi---->{delete_memory_index} &&&& {parent_row['iop_index']} == {highest_iop_index_of_first_pipe} ")
        if parent_pipe_index == 0 or (parent_pipe_index == delete_memory_index and parent_row[
            'iop_index']+1 == highest_iop_index_of_first_pipe):
            logging.info(f".........going to delete the memory---->>>{delete_memory_index}")
            delete_memory_index += 1
            HIGHEST_IOP_EVER_HAD.clear()
            computed_rows_index = list(computed_values_dict.keys())
            for computed_row in computed_rows_index:
                if computed_row >= parent_pipe_index:
                    del computed_values_dict[computed_row]
            # again_row = ordered_df.loc[i]

            if parent_pipe_index != 0:
                computed_values = start_increasing_iop_values(parent_row['row_vals'], highest_iop_index_of_first_pipe,
                                                              parent_pipe_index, parent_row['rhas'], computed_values_dict,
                                                              delete_memory_index, highest_iop_index_of_first_pipe)
            else:
                computed_values = start_increasing_iop_values(parent_row['row_vals'], parent_row['iop_index'] + 1,
                                                              parent_pipe_index, parent_row['rhas'],
                                                              computed_values_dict,
                                                              delete_memory_index, highest_iop_index_of_first_pipe)
        else:
            computed_rows_index = list(computed_values_dict.keys())
            for computed_row in computed_rows_index:
                if computed_row >= parent_pipe_index:
                    del computed_values_dict[computed_row]
            computed_values = start_increasing_iop_values(parent_row['row_vals'], parent_row['iop_index'] + 1,
                                                          parent_pipe_index, parent_row['rhas'], computed_values_dict,
                                                          delete_memory_index, highest_iop_index_of_first_pipe)
        return computed_values


computed_values_dict = {}
i = 0
DELETE_MEMORY_INDEX = 0
HIGHEST_IOP_INDEX_OF_PARENT_PIPE = 0
try:
    while i <= len(ordered_df) - 1:
        logging.info(f"current row>>>{i}")
        print("current row----->", i)

        row = ordered_df.loc[i]
        logging.info(f"high iop ever had::::{HIGHEST_IOP_EVER_HAD}")
        # HIGHEST_IOP_EVER_HAD.clear()
        closest_iop_index = find_closest_iop_index_by_formula(row['discharge'])
        if i in HIGHEST_IOP_EVER_HAD:
            closest_iop_index = HIGHEST_IOP_EVER_HAD[i]
            logging.info(f"n{i}n--->HIGHEST IOP HAD:::{closest_iop_index}")

        comp_values = start_increasing_iop_values(row, closest_iop_index, i, RHAS, computed_values_dict,
                                                  DELETE_MEMORY_INDEX, HIGHEST_IOP_INDEX_OF_PARENT_PIPE)


        if not comp_values:
            print("excepttttttttttttttion thejdfkdjfdkjf")
            log_df = pd.DataFrame(log_rows)
            log_df.to_excel("log.xlsx")
            break
        DELETE_MEMORY_INDEX = int(comp_values['delete_memory_index'])
        with open("log.json", "w") as log_file:
            json.dump(computed_values_dict, log_file, indent=4)
        i = list(computed_values_dict)[-1]

        high_id_pipe = 0 if DELETE_MEMORY_INDEX == 0 else (DELETE_MEMORY_INDEX-1)
        HIGHEST_IOP_INDEX_OF_PARENT_PIPE = computed_values_dict[high_id_pipe]['iop_index']
        HIGHEST_IOP_EVER_HAD.clear()

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
