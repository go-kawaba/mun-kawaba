import re


class Word:
    content: str
    non_word: bool

    morphemes: tuple[str, ...] | None

    def __init__(self, content: str, non_word=False):
        self.content = content
        self.non_word = non_word

        if not non_word:
            morpheme_pattern = re.compile(r"[ptkbdgfscljwhmn]?[aiueo]n?", re.IGNORECASE)
            self.morphemes = tuple(morpheme_pattern.findall(content))

    def __str__(self):
        return f"<hun_kawaba.Word object; content='{self.content}', non_word={self.non_word}>"

    def __repr__(self):
        return f"<hun_kawaba.Word object; content='{self.content}', non_word={self.non_word}>"


def parse_sentence(sentence: str):
    # Fix any fancy smart quotes
    fixed_sentence = (
        sentence.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    )

    # Create the regular expression patterns for matching with the text
    word_pattern = re.compile(r"('?[ptkbdgfscljwhmn]?[aiueo]n?'?)+", re.IGNORECASE)
    loan_word_pattern = re.compile(
        r"(?<!\S)'([ptkbdgfscljwhmn]?[aiueo]n?)+'(?=.)?", re.IGNORECASE
    )

    words: list[Word] = []

    for match in word_pattern.finditer(fixed_sentence):
        # Get the string that was found to have matched the regex
        group = match.group()

        words.append(
            Word(group, non_word=True if loan_word_pattern.match(group) else False)
        )

    return words
