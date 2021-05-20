import re
import os
import sys
import time
from bs4 import BeautifulSoup

import ntpath
from nltk.corpus import stopwords
from nltk import word_tokenize
import codecs
from snippet import Snippet


class BasicSearch:

    def __init__(self, snippet_limit: int = 3, take_words: int = 3, results_limit: int = 10, data_dir: str = 'pages') -> None:
        """
        This class is used for basic, no SQL searching.

        :param take_words: How many words to display is snippets before/after the found word.
        :param results_limit: How many rows to show when displaying top results with snippets.
        :param data_dir: Directory in which the HTML sites are saved relative to the current directory.
        """
        # nltk.download('punkt')
        # nltk.download('stopwords')
        self.time_needed_to_search = None
        self.take_words = take_words
        self.results_limit = results_limit
        self.data_dir = os.path.join(os.getcwd(), data_dir)
        self.path = data_dir
        self.snippet_limit = snippet_limit
        self.snip = Snippet(self.take_words, self.results_limit)

        self.stop_words_slovene = set(stopwords.words("Slovene")).union(
            {"ter", "nov", "novo", "nova", "zato", "še", "zaradi", "a", "ali", "april", "avgust", "b", "bi", "bil",
             "bila", "bile", "bili", "bilo", "biti", "blizu", "bo", "bodo", "bojo", "bolj", "bom", "bomo", "boste",
             "bova", "boš", "brez", "c", "cel", "cela", "celi", "celo", "d", "da", "daleč", "dan", "danes", "datum",
             "december", "deset", "deseta", "deseti", "deseto", "devet", "deveta", "deveti", "deveto", "do", "dober",
             "dobra", "dobri", "dobro", "dokler", "dol", "dolg", "dolga", "dolgi", "dovolj", "drug", "druga", "drugi",
             "drugo", "dva", "dve", "e", "eden", "en", "ena", "ene", "eni", "enkrat", "eno", "etc.", "f", "februar",
             "g", "g.", "ga", "ga.", "gor", "gospa", "gospod", "h", "halo", "i", "idr.", "ii", "iii", "in", "iv", "ix",
             "iz", "j", "januar", "jaz", "je", "ji", "jih", "jim", "jo", "julij", "junij", "jutri", "k", "kadarkoli",
             "kaj", "kajti", "kako", "kakor", "kamor", "kamorkoli", "kar", "karkoli", "katerikoli", "kdaj", "kdo",
             "kdorkoli", "ker", "ki", "kje", "kjer", "kjerkoli", "ko", "koder", "koderkoli", "koga", "komu", "kot",
             "kratek", "kratka", "kratke", "kratki", "l", "lahka", "lahke", "lahki", "lahko", "le", "lep", "lepa",
             "lepe", "lepi", "lepo", "leto", "m", "maj", "majhen", "majhna", "majhni", "malce", "malo", "manj", "marec",
             "me", "med", "medtem", "mene", "mesec", "mi", "midva", "midve", "mnogo", "moj", "moja", "moje", "mora",
             "morajo", "moram", "moramo", "morate", "moraš", "morem", "mu", "n", "na", "nad", "naj", "najina", "najino",
             "najmanj", "naju", "največ", "nam", "narobe", "nas", "nato", "nazaj", "naš", "naša", "naše", "ne",
             "nedavno", "nedelja", "nek", "neka", "nekaj", "nekatere", "nekateri", "nekatero", "nekdo", "neke",
             "nekega", "neki", "nekje", "neko", "nekoga", "nekoč", "ni", "nikamor", "nikdar", "nikjer", "nikoli", "nič",
             "nje", "njega", "njegov", "njegova", "njegovo", "njej", "njemu", "njen", "njena", "njeno", "nji", "njih",
             "njihov", "njihova", "njihovo", "njiju", "njim", "njo", "njun", "njuna", "njuno", "no", "nocoj",
             "november", "npr.", "o", "ob", "oba", "obe", "oboje", "od", "odprt", "odprta", "odprti", "okoli",
             "oktober", "on", "onadva", "one", "oni", "onidve", "osem", "osma", "osmi", "osmo", "oz.", "p", "pa", "pet",
             "peta", "petek", "peti", "peto", "po", "pod", "pogosto", "poleg", "poln", "polna", "polni", "polno",
             "ponavadi", "ponedeljek", "ponovno", "potem", "povsod", "pozdravljen", "pozdravljeni", "prav", "prava",
             "prave", "pravi", "pravo", "prazen", "prazna", "prazno", "prbl.", "precej", "pred", "prej", "preko", "pri",
             "pribl.", "približno", "primer", "pripravljen", "pripravljena", "pripravljeni", "proti", "prva", "prvi",
             "prvo", "r", "ravno", "redko", "res", "reč", "s", "saj", "sam", "sama", "same", "sami", "samo", "se",
             "sebe", "sebi", "sedaj", "sedem", "sedma", "sedmi", "sedmo", "sem", "september", "seveda", "si", "sicer",
             "skoraj", "skozi", "slab", "smo", "so", "sobota", "spet", "sreda", "srednja", "srednji", "sta", "ste",
             "stran", "stvar", "sva", "t", "ta", "tak", "taka", "take", "taki", "tako", "takoj", "tam", "te", "tebe",
             "tebi", "tega", "težak", "težka", "težki", "težko", "ti", "tista", "tiste", "tisti", "tisto", "tj.", "tja",
             "to", "toda", "torek", "tretja", "tretje", "tretji", "tri", "tu", "tudi", "tukaj", "tvoj", "tvoja",
             "tvoje", "u", "v", "vaju", "vam", "vas", "vaš", "vaša", "vaše", "ve", "vedno", "velik", "velika", "veliki",
             "veliko", "vendar", "ves", "več", "vi", "vidva", "vii", "viii", "visok", "visoka", "visoke", "visoki",
             "vsa", "vsaj", "vsak", "vsaka", "vsakdo", "vsake", "vsaki", "vsakomur", "vse", "vsega", "vsi", "vso",
             "včasih", "včeraj", "x", "z", "za", "zadaj", "zadnji", "zakaj", "zaprta", "zaprti", "zaprto", "zdaj",
             "zelo", "zunaj", "č", "če", "često", "četrta", "četrtek", "četrti", "četrto", "čez", "čigav", "š", "šest",
             "šesta", "šesti", "šesto", "štiri", "ž", "že", "svoj", "jesti", "imeti", "\u0161e", "iti", "kak", "www",
             "km", "eur", "pač", "del", "kljub", "šele", "prek", "preko", "znova", "morda", "kateri", "katero",
             "katera", "ampak", "lahek", "lahka", "lahko", "morati", "torej", "gl", "xsd", "ipd", "om", "gt","lt", "d.o.o"})

    def print_results(self, query: list, results: list) -> None:
        """
        Prints the results of the query to the std output

        :param query: The user search query in list format.
        :param results: A list of lists containing the results in format [frequencies, document, snippets].
        The list should be ordered in descending order.
        """
        print(f'Results for query: "{" ".join(query)}"')
        print('{} results found in {:.0f}s'.format(len(results), self.time_needed_to_search))
        print("{:<12} {:<40} {}".format('Frequencies', 'Document', 'Snippets'))
        print("{} {} {}".format('-' * 12, '-' * 40, '-' * 80))
        for i in range(min(self.results_limit, len(results))):
            print("{:<12} {:<40} {}".format(results[i][0],
                                            results[i][1],
                                            '... ' + ' ... '.join(results[i][2][:self.snippet_limit]) + ' ...'))

    def get_files(self) -> list:
        """
        Gets a list of paths to all HTML files which are contained in the self.path folder.

        :return: List of all HTML files.
        """
        files_path = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.path) for f in filenames if
                      os.path.splitext(f)[1].lower() == '.html']
        return files_path

    def get_document(self, page_name: str) -> object:
        """
        Gets and opens the provided document.

        :param page_name: The HTML document that should be opened for reading.
        :return: The opened document.
        """
        map_name = '.'.join(page_name.split('.')[:3])
        return open(os.path.join(self.data_dir, "{}/{}".format(map_name, page_name)), 'r', encoding='utf-8')

    def parse_file(self, file: str, search_words: list) -> tuple:
        """
        Searches the HTML document for the words in the query and returns the frequency and snippets.

        :param file: The HTML file to search.
        :param search_words: The user search query.
        :return: A touple with frequencies and result snippets.
        """
        # open the file
        f = codecs.open(file, 'r', 'utf-8')
        soup = BeautifulSoup(f.read(), features="html.parser")
        for script in soup(["script", "style"]):
            script.decompose()

        # tokenize and clean file
        strips = list(soup.stripped_strings)
        document = ' '.join(strips)
        tokens = word_tokenize(document, language='Slovene', preserve_line=False)
        indexes = list()
        for i in range(len(tokens)):
            token = tokens[i].lower().replace("'", "").replace("'", '').replace('`', '').replace('·', '')
            # skip if token doesn't contain letters
            if not re.search('[a-žA-ž]', token):
                continue
            # skip tokens of length 1, if they're not a word or number
            if len(token) == 1 and not re.match("^[A-Ža-ž0-9]*$", token):
                continue
            # if token ends with a special character, remove it
            if len(token) >= 2 and not re.match("^[A-Ža-ž0-9]*$", token[-1]):
                token = token[:-1]
            # if token starts with a special character, remove it
            if len(token) >= 2 and not re.match("^[A-Ža-ž0-9]*$", token[0]):
                token = token[1:]
            # if token is a stop-word, continue
            if token not in self.stop_words_slovene:
                # if we're searching for this token, add the index to the list
                if token in search_words:
                    indexes.append(i)
        try:
            # snippet = self.get_snip(tokens, indexes)
            snippet = self.snip.get_snip(tokens, indexes)
        except AssertionError:
            snippet = []
        return len(indexes), snippet

    def search(self, words: list) -> None:
        """
        Performs the search in all files for the user query.

        :param words: The user search query.
        """
        results = []
        # start the timer and do the search, after that calculate the time needed for search
        start_time = time.time()
        files = self.get_files()
        for file in files:
            f, s = self.parse_file(file, words)
            if f > 0:
                results.append([f, ntpath.split(file)[1], s])
        end_time = time.time()
        self.time_needed_to_search = end_time - start_time
        results.sort(key=lambda x: x[0], reverse=True)
        self.print_results(words, results)


basic_search = BasicSearch()
basic_search.search([x.lower() for x in sys.argv[1:]])
