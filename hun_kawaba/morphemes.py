import re


class Word:
    content: str
    loan_word: bool
    invalid_word: bool

    morphemes: tuple[str, ...] | None

    def __init__(self, content: str, loan_word=False, invalid_word=False):
        """A container for words in kawaba. Primarily used by the parse_sentence function.

        Parameters
        ----------
        content : str
            The full word.
        loan_word : bool, optional
            If this word should be ignored from morpheme splitting.
        invalid_word : bool, optional
            If this word does not follow the phonotactics and/or orthography of kawaba.
        """
        self.content = content
        self.loan_word = loan_word
        self.invalid_word = invalid_word

        if not loan_word and not invalid_word:
            morpheme_pattern = re.compile(r"[ptkbdgfscljwhmn]?[aiueo]n?", re.IGNORECASE)
            self.morphemes = tuple(morpheme_pattern.findall(content))

    def __str__(self):
        return f"<hun_kawaba.Word object; content='{self.content}', loan_word={self.loan_word}, invalid_word={self.invalid_word}>"

    def __repr__(self):
        return f"<hun_kawaba.Word object; content='{self.content}', loan_word={self.loan_word}, invalid_word={self.invalid_word}>"


def parse_sentence(sentence: str):
    # Fix any fancy smart quotes
    fixed_sentence = (
        sentence.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    )

    split_sentence = fixed_sentence.split(" ")

    # Create the regular expression patterns for matching with the text
    kawaba_word_pattern = re.compile(
        r"('?[ptkbdgfscljwhmn]?[aiueo]n?'?)+", re.IGNORECASE
    )
    loan_word_pattern = re.compile(r"(?<!\S)'(\S?)+'(?=.)?", re.IGNORECASE)

    words: list[Word] = []

    for word in split_sentence:
        words.append(
            Word(
                word,
                loan_word=False if loan_word_pattern.fullmatch(word) is None else True,
                invalid_word=False
                if kawaba_word_pattern.fullmatch(word) is not None
                else True,
            )
        )

    return words
