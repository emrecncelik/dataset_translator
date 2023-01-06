from __future__ import annotations

import os
import json
from loguru import logger
from google.oauth2 import service_account
from google.cloud import translate_v2 as translate


class Translator:
    def __init__(
        self,
        credentials: str = "credentials.json",
        log_filepath: str = "translator.log",
        log_level: str | int = "INFO",
    ) -> None:
        self.client = translate.Client(credentials=self._get_credentials(credentials))
        self.log_filepath = log_filepath
        self.log_level = log_level
        self.session_char_count = self._get_last_char_count()

        logger.add(log_filepath, level=log_level)

        logger.info(
            f"Translator initialized with character count: {self.session_char_count}"
        )

    def _get_last_char_count(self):
        if os.path.exists(self.log_filepath):
            with open(self.log_filepath) as f:
                lines = f.readlines()

            return int(lines[-1].split(":")[-1].strip())
        else:
            return 0

    def _get_credentials(self, filepath: str):
        with open(filepath) as f:
            service_account_info = json.load(f)  # Fuck safety
        return service_account.Credentials.from_service_account_info(
            service_account_info
        )

    def translate_text(
        self,
        text: str | list[str],
        target: str = "tr",
        source: str = "en",
    ):
        """Translates text into the target language."""

        if isinstance(text, str):
            self.session_char_count += len(text)
        else:
            self.session_char_count += sum([len(t) for t in text])

        result = self.client.translate(
            text, target_language=target, source_language=source
        )
        logger.info(f"Current character count: {self.session_char_count}")

        if isinstance(text, str):
            return result["translatedText"]
        else:
            return [r["translatedText"] for r in result]
