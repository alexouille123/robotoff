import re
from typing import List

from robotoff.spellcheck import BaseSpellchecker

PERCENTAGE_REGEX = re.compile(
    r"(\A|.)([0-9]{0,2})([ ]{0,1}?[,|.|;|/]{0,1}[ ]{0,1})([0-9]{0,2})[ ]?(?:%|(?:[\?|/|\\](?:\D|\Z)))"
)
ADDITIVES_REGEX = re.compile(r"(?:E ?\d{3,5}[a-z]*)", re.IGNORECASE)


class PercentagesSpellchecker(BaseSpellchecker):
    def correct(self, txt: str) -> str:
        return self.format_percentages(txt)

    @staticmethod
    def format_percentages(txt: str) -> str:
        formatted_txt_list: List[str] = []
        last_index: int = 0
        for match in PERCENTAGE_REGEX.finditer(txt):
            first_char, first_digits, sep, last_digits = match.groups()

            start = match.start() + len(first_char)
            end = match.end()  # - len(to_drop)
            nb_first_digits = len(first_digits)
            nb_last_digits = len(last_digits)

            valid_match = False
            pad_before = False
            pad_after = False

            if ADDITIVES_REGEX.match(txt[match.start() : match.end()]):
                # Very conservative rule
                formatted_match = txt[start:end]

            elif nb_first_digits == 0 and nb_last_digits == 0:
                # Not a good match
                formatted_match = txt[start:end]

            elif nb_first_digits == 0:
                formatted_match = f"{sep}{last_digits}%"
                pad_before = False
                pad_after = True

            elif nb_last_digits == 0:
                formatted_match = f"{first_digits}%"
                pad_before = True
                pad_after = True

            elif len(sep) > 0 and (nb_first_digits == 2 or nb_last_digits == 2):
                formatted_match = f"{first_digits},{last_digits}%"
                pad_before = True
                pad_after = True

            elif sep.strip() == "":
                if float(f"{first_digits}{last_digits}") <= 100.0:
                    formatted_match = f"{first_digits}{last_digits}%"
                    pad_before = True
                    pad_after = True
                else:
                    formatted_match = f"{first_digits},{last_digits}%"
                    pad_before = True
                    pad_after = True
            else:
                formatted_match = f"{first_digits},{last_digits}%"
                pad_before = True
                pad_after = True

            if pad_before:
                if start > 0:
                    previous_char = txt[start - 1]
                    if previous_char.isalnum() or previous_char in ["*", ")", "]", "}"]:
                        formatted_match = " " + formatted_match.lstrip(" ")

            if pad_after:
                if end < len(txt):
                    next_char = txt[end]
                    if next_char.isalnum() or next_char in ["*", "(", "[", "{"]:
                        formatted_match = formatted_match.rstrip(" ") + " "

            formatted_txt_list.append(txt[last_index:start])
            formatted_txt_list.append(formatted_match)
            last_index = end
        formatted_txt_list.append(txt[last_index:])

        return "".join(formatted_txt_list)
