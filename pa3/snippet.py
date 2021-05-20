class Snippet:

    def __init__(self, take_words: int = 3, results_limit: int = 10) -> None:
        """
        This class is used for basic, no SQL searching.

        :param take_words: How many words to display is snippets before/after the found word.
        :param results_limit: How many rows to show when displaying top results with snippets.
        :param data_dir: Directory in which the HTML sites are saved relative to the current directory.
        """
        # nltk.download('stopwords')
        self.take_words = take_words
        self.results_limit = results_limit

    def get_snip(self, tokens: list, indices: list) -> list:
        """
        Creates results snippets using the token and index lists.

        :param tokens: A list containing all tokens (words) from the HTML website.
        :param indices: A list containing indices of words that are being searched for.
        :return: A list of snippets
        """
        assert len(indices) >= 1
        snippets = []
        i = 0
        if len(indices) > 1:
            while i < len(indices)-1:
                index = indices[i]
                start = index - self.take_words if index - self.take_words >= 0 else 0
                # if the next found token is less than take_words indexes away, we extend the length of this snippet
                while i+1 < len(indices) and indices[i+1] <= index + self.take_words * 2:
                    i += 1
                    index = indices[i]
                end = index + self.take_words + 1 if index + self.take_words + 1 < len(tokens) else len(tokens) - 1
                snippets.append(' '.join(tokens[start:end]))
                i += 1
            if indices[-1] > indices[-2] + self.take_words:
                index = indices[-1]
                start = index - self.take_words if index - self.take_words >= 0 else 0
                end = index + self.take_words + 1 if index + self.take_words + 1 < len(tokens) else len(tokens) - 1
                snippets.append(' '.join(tokens[start:end]))
        else:
            index = indices[0]
            start = index - self.take_words if index - self.take_words >= 0 else 0
            end = index + self.take_words + 1 if index + self.take_words + 1 < len(tokens) else len(tokens) - 1
            snippets.append(' '.join(tokens[start:end]))
        return snippets
