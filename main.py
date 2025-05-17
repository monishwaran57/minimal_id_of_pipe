from gain import ordered_df as first_opti_df

main_pipe_dict = {}

for pipe_idx, pipe in first_opti_df.iterrows():
    if "V" not in pipe['end_node']:
        main_pipe_dict[pipe_idx] = {
            "start_node": pipe['start_node'],
            "end_node": pipe['end_node'],
            "length": pipe['length'],
            "discharge": pipe['discharge'],
            "ground_level_start": pipe["ground_level_start"],
            "ground_level_end": pipe["ground_level_end"],
            "old_dia": pipe['old_dia'],
            "new_iop": pipe['new_iop'],
            "rhas": pipe['available_residual_head_at_start'],
            "rhae": pipe['residual_head_at_end']
        }
    else:
        main_pipe_dict[pipe_idx] = {
            "start_node": pipe['start_node'],
            "end_node": pipe['end_node'],
            "length": pipe['length'],
            "discharge": pipe['discharge'],
            "ground_level_start": pipe["ground_level_start"],
            "ground_level_end": pipe["ground_level_end"],
            "old_dia": pipe['old_dia'],
            "new_iop": pipe['new_iop'],
            "rhas": pipe['available_residual_head_at_start'],
            "rhae": pipe['residual_head_at_end']
        }
        break

print("katingksa\n", main_pipe_dict)
