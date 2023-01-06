import os
from loguru import logger
from dataclasses import dataclass
from simple_parsing import ArgumentParser
from simple_parsing.helpers import Serializable
from translator import Translator

from utils import lines_from_last_stop

translator = Translator()
output_filepath = "dialogues_translated.txt"
input_filepath = "dialogues.txt"


parser = ArgumentParser()


@dataclass
class TranslationArguments(Serializable):
    input_filepath: str
    output_filepath: str = "output.txt"
    source_lang: str = "en"
    target_lang: str = "tr"
    credentials_filepath: str = "credentials.json"
    save_every: int = 100
    log_filepath: str = "translator.log"
    log_level: str = "INFO"
    inline_separator: str = None


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_arguments(TranslationArguments, dest="translation_args")
    args = parser.parse_args().translation_args
    args.save(args.input_filepath.split(".")[0] + "_" + "args.json")

    if ".txt" not in args.input_filepath:
        raise ValueError("This script only supports txt files.")

    if not os.path.exists(args.credentials_filepath):
        raise FileNotFoundError(
            f"Credentials file not found in {args.credentials_filepath}"
        )

    if os.path.exists(args.output_filepath):
        lines = lines_from_last_stop(args.input_filepath, args.output_filepath)
    else:
        with open(args.input_filepath) as f:
            lines = f.readlines()

    if args.inline_separator:
        lines = [l.split(args.inline_separator) for l in lines]

    translator = Translator(
        credentials=args.credentials_filepath,
        log_filepath=args.log_filepath,
        log_level=args.log_level,
    )

    translations = []
    if args.inline_separator:
        for idx, line in enumerate(lines):
            translation = (
                args.inline_separator.join(
                    translator.translate_text(
                        line,
                        target=args.target_lang,
                        source=args.source_lang,
                    )
                )
                if args.inline_separator
                else translator.translate_text(
                    line,
                    target=args.target_lang,
                    source=args.source_lang,
                )
            )
            translations.append(translation + "\n")
            if (idx + 1) % args.save_every == 0:
                logger.info(f"Saving translation batch at {idx + 1}")
                with open(args.output_filepath, "a") as f:
                    f.writelines(translations)
                translations = []
        else:
            with open(args.output_filepath, "a") as f:
                f.writelines(translations)
