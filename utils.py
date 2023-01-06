def lines_from_last_stop(input_filepath: str, output_filepath: str):
    with open(output_filepath) as f:
        output_lines = f.readlines()

    with open(input_filepath) as f:
        input_lines = f.readlines()

    return input_lines[len(output_lines) :]
