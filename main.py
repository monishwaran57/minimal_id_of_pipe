from constants import IOP, find_velocity_by_formula, find_friction_head_loss_by_formula, \
    find_residual_head_at_end_by_formula, find_closest_iop_index_by_formula
import pandas as pd

optimized_df1 = pd.read_excel("mha6.xlsx")

the_dict = optimized_df1.to_dict(orient="index")

deepest_branch_dict = {}

for idx, pipe_row in optimized_df1.iterrows():
    if "V" not in pipe_row['end_node']:
        pipe_dict = dict(pipe_row)
        pipe_dict['difference'] = pipe_dict['new_iop'] - pipe_dict['old_dia']
        deepest_branch_dict[idx] = pipe_dict
    else:
        pipe_dict = dict(pipe_row)
        pipe_dict['difference'] = pipe_dict['new_iop'] - pipe_dict['old_dia']
        deepest_branch_dict[idx] = pipe_dict
        break


# print(deepest_branch_dict)

deep_df = pd.DataFrame(deepest_branch_dict.values())

deep_df.rename(columns={'Unnamed: 0': 'index'}, inplace=True)

deep_df.to_excel("deepest_branch.xlsx", index=False)

def give_child_pipe_details(parent_end_node):
    matches = optimized_df1.loc[optimized_df1['start_node'] == parent_end_node]

    if not matches.empty:
        child_pipes_list = []
        for i, child_pipe in matches.iterrows():
            child_dict = child_pipe.to_dict()
            child_dict['index'] = int(i)
            child_pipes_list.append(child_dict)
        print("....child ppipes list", child_pipes_list)
        return child_pipes_list
    else:
        return None


def create_the_childs_iop_dict(parent_pipe):
    cidx_and_ciops = {}
    child_pipes_list = give_child_pipe_details(parent_end_node=parent_pipe['end_node'])
    if child_pipes_list is not None:
        for pipe in child_pipes_list:
            cidx_and_ciops[pipe['index']] = pipe['new_iop']

        return cidx_and_ciops
    else:
        return None

def give_parent_pipe_details(child_start_node):
    matches = optimized_df1.loc[optimized_df1['end_node'] == child_start_node]

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
        pidx_and_piops[pidx] = the_dict[pidx]['iop']
        parent_pipe = give_parent_pipe_details(child_start_node=parent_pipe['start_node'])
    else:
        pass
    return pidx_and_piops

def give_iop_pipe_indexes_dict(idx_and_iops):
    iop_pipe_indexes_dict = {}

    for idx, iop in idx_and_iops.items():
        iop_pipe_indexes_dict[iop] = [ix for ix, iop2 in idx_and_iops.items() if iop == iop2]


    return iop_pipe_indexes_dict

def calculate_rhas_and_rhae_with_new_iop(new_iop_dict, start_from):

    recalculate_dict = {i: new_iop for i, new_iop in new_iop_dict.items() if i >= start_from}

    for idx, new_iop in recalculate_dict.items():
        pipe = optimized_df1.loc[idx]

        velocity = find_velocity_by_formula(discharge=pipe['discharge'], id_of_pipe=new_iop)
        iop_index = IOP.index(new_iop)

        if iop_index != 0 and velocity < 0.6 or velocity > 3:
            child_pipe = optimized_df1.loc[idx]

            idx_and_iops_new1 = create_the_parents_iop_dict(child_pipe)

            iop_pipe_indexes1 = give_iop_pipe_indexes_dict(idx_and_iops_new1)

            least_iop = min(iop_pipe_indexes1)

            top_pipe_index_to_be_increased = min(iop_pipe_indexes1[least_iop])

            iop_index = IOP.index(least_iop)

            correct_indexes = {index: row_vals['iop'] for index, row_vals in the_dict.items()}
            if iop_index + 1 <= len(IOP)-1:
                correct_indexes[top_pipe_index_to_be_increased] = IOP[iop_index + 1]

                if iop_index + 1 == len(IOP) - 1:
                    for pipe_idx in range(top_pipe_index_to_be_increased + 1, len(correct_indexes)):
                        pipe_from_df = optimized_df1.loc[pipe_idx]
                        closest_iop_index = find_closest_iop_index_by_formula(pipe_from_df['discharge'])
                        correct_indexes[pipe_idx] = IOP[closest_iop_index]
            else:
                correct_indexes[top_pipe_index_to_be_increased + 1] = IOP[iop_index]

                if iop_index == len(IOP) - 1:
                    for pipe_idx in range(top_pipe_index_to_be_increased + 1, len(correct_indexes)):
                        pipe_from_df = optimized_df1.loc[pipe_idx]
                        closest_iop_index = find_closest_iop_index_by_formula(pipe_from_df['discharge'])
                        correct_indexes[pipe_idx] = IOP[closest_iop_index]



            calculate_rhas_and_rhae_with_new_iop(correct_indexes, start_from=top_pipe_index_to_be_increased)

            return False
        else:
            parent_pipe = give_parent_pipe_details(pipe['start_node'])

            pidx = None if parent_pipe is None else parent_pipe['index']

            rhas = 0 if parent_pipe is None else the_dict[pidx]['residual_head_at_end']

            parent_iop = None if parent_pipe is None else the_dict[pidx]['new_iop']

            diff_g_level = pipe['ground_level_start'] - pipe['ground_level_end']

            fhl = find_friction_head_loss_by_formula(length=pipe['length'], discharge=pipe['discharge'], cr_value=1, iop=new_iop)

            rhae = find_residual_head_at_end_by_formula(diff_in_g_level=diff_g_level,rhas=rhas,fhl=fhl)

            pipe_end_node = the_dict[idx]['end_node']

            if "V" in pipe_end_node and rhae < 28:
                return 500


            the_dict[idx]['available_residual_head_at_start'] = rhas
            the_dict[idx]['residual_head_at_end'] = rhae
            the_dict[idx]['new_fhl'] = fhl
            the_dict[idx]['new_velocity'] = velocity
            the_dict[idx]['new_iop'] = new_iop
            the_dict[idx]['parent_iop'] = parent_iop
            the_dict[idx]['iop_index'] = IOP.index(new_iop)

    return True


def reduce_iop(pipe_index, pipe_vals, index_iop_dict):
    if pipe_vals['new_velocity'] < 1.4:
        child_index_and_iops_old = create_the_childs_iop_dict(parent_pipe=pipe_vals)
        if child_index_and_iops_old is None:
            return
        child_index_and_iops = {pipe_idx: index_iop_dict[pipe_idx] for pipe_idx in child_index_and_iops_old}
        print("000000000", child_index_and_iops)

        pipe_iop = pipe_vals['new_iop']
        pipe_iop_index = IOP.index(pipe_iop)

        top_child_index = min(child_index_and_iops)
        top_child_iop = child_index_and_iops[top_child_index]

        if pipe_iop > top_child_iop:
            index_iop_dict[pipe_index] = IOP[pipe_iop_index-1]
            response = calculate_rhas_and_rhae_with_new_iop(index_iop_dict, start_from=pipe_index)
            if response == 500:
                """do something"""
                print("hi")
        else:
            child_pipe_vals = the_dict[top_child_index]
            reduce_iop(top_child_index, child_pipe_vals, index_iop_dict)

for main_idx, pipe in deep_df.iterrows():
    print("************<<<<>>>>>>", main_idx)
    if main_idx == 51:
        print("..hi")
    index_and_iop = {index: pipe_vals['new_iop'] for index, pipe_vals in the_dict.items()}

    reduce_iop(main_idx, pipe, index_and_iop)



optimized_df2 = pd.DataFrame(the_dict.values())

optimized_df2.rename(columns={'Unnamed: 0': 'index'}, inplace=True)

optimized_df2.to_excel("opti2.xlsx", index=False)




