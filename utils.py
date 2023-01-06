import warnings


def lines_from_last_stop(input_filepath: str, output_filepath: str):
    with open(output_filepath) as f:
        output_lines = f.readlines()

    with open(input_filepath) as f:
        input_lines = f.readlines()

    return input_lines[len(output_lines) :]


def last_session_log_not_found(logger):
    logger.warning(
        "Log file for last session not found, "
        "considering free limit as not exceeded. "
        "If this is your first time using this tool, you can ignore this warning. "
        "Otherwise, please make sure you have not exceeded "
        "the limit manually to avoid payments. Guck Foogle."
    )
