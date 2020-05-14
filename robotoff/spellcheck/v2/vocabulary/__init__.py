import re
from typing import Optional, List

from robotoff.utils.text import FR_NLP_CACHE
from robotoff.spellcheck.v2.vocabulary.utils import Vocabulary
from robotoff.spellcheck.v2.base_spellchecker import BaseSpellchecker

TOKENS = List[str]
ADDITIVES_REGEX = re.compile("(?:E ?\d{3,5}[a-z]*)", re.IGNORECASE)


class VocabularySpellchecker(BaseSpellchecker):
    def __init__(self):
        self.wikipedia_voc = Vocabulary("wikipedia_lower")
        self.ingredients_voc = Vocabulary("ingredients_fr_tokens") | Vocabulary(
            "ingredients_fr"
        )

    def correct(self, text: str) -> str:
        for token in self.tokenize(text, remove_additives=True):
            if all(c.isalpha() for c in token):
                if not token in self.wikipedia_voc:
                    suggestion: Optional[str] = self.ingredients_voc.suggest(token)
                    if suggestion is not None:
                        text = text.replace(token, suggestion)
        return text

    @staticmethod
    def tokenize(text: str, remove_additives: bool = False) -> TOKENS:
        tokens: TOKENS = []

        nlp = FR_NLP_CACHE.get()
        for token in nlp(text):
            tokens.append(token.orth_)
        tokens = [token for token in tokens if any(c.isalnum() for c in token)]
        if remove_additives:
            tokens = [token for token in tokens if ADDITIVES_REGEX.match(token) is None]
        return tokens