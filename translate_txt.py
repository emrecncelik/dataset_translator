import os
from loguru import logger
from dataclasses import dataclass
from simple_parsing import ArgumentParser
from simple_parsing.helpers import Serializable
from translator import Translator

from utils import lines_from_last_stop


@dataclass
class TranslationArguments(Serializable):
    input: str  # input data file path
    output: str  # output data file path
    source: str = "en"  # language of input data
    target: str = "tr"  # language of output data
    credentials: str = "credentials.json"  # google cloud credentials for translate api
    save_every: int = 100  # save batch size
    logfile: str = "translator.log"  # log file path
    loglevel: str = "INFO"  # logging level
    inline_separator: str = None  # separator for dialogue-datasets eg. __eou__


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_arguments(TranslationArguments, dest="translation_args")
    args = parser.parse_args().translation_args
    args.save(args.input.split(".")[0] + "_" + "args.json")

    if ".txt" not in args.input:
        raise ValueError("This script only supports txt files.")

    if not os.path.exists(args.credentials):
        raise FileNotFoundError(f"Credentials file not found in {args.credentials}")

    if os.path.exists(args.output):
        lines = lines_from_last_stop(args.input, args.output)
    else:
        with open(args.input) as f:
            lines = f.readlines()

    if args.inline_separator:
        lines = [l.split(args.inline_separator) for l in lines]

    translator = Translator(
        credentials=args.credentials,
        log_filepath=args.logfile,
        log_level=args.loglevel,
    )

    if not translator.is_api_free():
        logger.info("Exceeded monthly character limit.")
        exit()

    translations = []
    if args.inline_separator:
        for idx, line in enumerate(lines):
            translation = (
                args.inline_separator.join(
                    translator.translate_text(
                        line,
                        target=args.target,
                        source=args.source,
                    )
                )
                if args.inline_separator
                else translator.translate_text(
                    line,
                    target=args.target,
                    source=args.source,
                )
            )
            translations.append(translation + "\n")
            if (idx + 1) % args.save_every == 0:
                logger.info(f"Saving translation batch at {idx + 1}")
                with open(args.output, "a") as f:
                    f.writelines(translations)
                translations = []
        else:
            with open(args.output, "a") as f:
                f.writelines(translations)
