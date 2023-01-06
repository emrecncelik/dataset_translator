from __future__ import annotations

import os
import json
from loguru import logger
from datetime import datetime
from dateutil.relativedelta import relativedelta
from google.oauth2 import service_account
from google.cloud import translate_v2 as translate

from utils import last_session_log_not_found


class Translator:
    def __init__(
        self,
        credentials: str = "credentials.json",
        log_filepath: str = "translator.log",
        log_level: str | int = "INFO",
        free_limit_char_count: int = 500000,
    ) -> None:
        self.client = translate.Client(credentials=self._get_credentials(credentials))
        self.log_filepath = log_filepath
        self.log_level = log_level
        self.session_char_count = self._get_char_count_at(1)
        self.free_limit_char_count = free_limit_char_count
        self._last_session_log_not_found_warning_raised = False

        logger.add(log_filepath, level=log_level)

        logger.info(
            f"Translator initialized with character count: {self.session_char_count}"
        )

    def is_api_free(self):
        # TODO make this check faster
        today = datetime.today()
        last_session_date = self._get_session_date_at(1)

        if (
            today - relativedelta(months=1) >= last_session_date
            or last_session_date is None
        ):
            return True
        else:
            if not self._is_free_limit_exceeded():
                return True
            else:
                return False

    def _is_free_limit_exceeded(self):
        last_session_date = self._get_session_date_at(1)

        if last_session_date is None:
            self._raise_warning()
            return False
        else:
            t_minus = 1
            last_char_count = self._get_char_count_at(t_minus)

            log_line_count = self._get_log_line_count()
            print(log_line_count)
            while t_minus < log_line_count - 1:
                t_minus += 1
                temp_char_count = self._get_char_count_at(t_minus)

                if abs(
                    last_char_count - temp_char_count
                ) > self.free_limit_char_count and self._get_session_date_at(
                    t_minus
                ) + relativedelta(
                    months=1
                ) >= self._get_session_date_at(
                    1
                ):
                    return True
            else:
                return False

    def _get_log_line_count(self):
        if os.path.exists(self.log_filepath):
            with open(self.log_filepath) as f:
                lines = f.readlines()
            return len(lines)
        else:
            self._raise_warning()
            return 0

    def _get_char_count_at(self, t_minus: int = 1):
        if os.path.exists(self.log_filepath):
            with open(self.log_filepath) as f:
                lines = f.readlines()

            last_line = lines[-t_minus]
            while "character count" not in last_line and t_minus < len(lines):
                t_minus += 1
                last_line = lines[-t_minus]

            return int(last_line.split(":")[-1].strip())
        else:
            self._raise_warning()
            return 0

    def _get_session_date_at(self, t_minus: int = 1):
        if os.path.exists(self.log_filepath):
            with open(self.log_filepath) as f:
                lines = f.readlines()
            return datetime.strptime(lines[-t_minus].split()[0], "%Y-%m-%d")
        else:
            self._raise_warning()
            return None

    def _get_credentials(self, filepath: str):
        with open(filepath) as f:
            service_account_info = json.load(f)  # Fuck safety
        return service_account.Credentials.from_service_account_info(
            service_account_info
        )

    def _raise_warning(self):
        if not self._last_session_log_not_found_warning_raised:
            last_session_log_not_found(logger)
            self._last_session_log_not_found_warning_raised = True

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
