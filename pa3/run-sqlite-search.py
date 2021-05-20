import re
import sqlite3
import os
import time
import nltk
import sys
from bs4 import BeautifulSoup
from snippet import Snippet


class SQLiteSearch:

    def __init__(self, snippet_limit=3, take_words=3, results_limit=10, db_name='inverted-index.db', data_dir='pages'):
        self.time_needed_to_search = None
        self.db_name = db_name
        self.take_words = take_words
        self.snippet_limit = snippet_limit
        self.results_limit = results_limit
        self.data_dir = os.path.join(os.getcwd(), data_dir)
        self.all_results = None
        self.snip = Snippet(self.take_words, self.results_limit)

        self.stop_words_slovene = set(nltk.corpus.stopwords.words("Slovene")).union(
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
             "katera", "ampak", "lahek", "lahka", "lahko", "morati", "torej"})

        self.conn = sqlite3.connect(self.db_name)

    def build_query(self, words):
        # -3 because we want to remove the last or and space (so 3 chars) from the list
        rm = len('or ') * -1
        if not isinstance(words, list):
            words = [words]
        whr = ' '.join(['word = \'{}\' or'.format(w) for w in words])[:rm]
        qry = "select documentName as file, SUM(frequency) 'freq', GROUP_CONCAT(indexes) as idx " \
              "from posting " \
              "where {} " \
              "group by documentName " \
              "order by freq desc ".format(whr)
        return qry

    @staticmethod
    def process_results(results):
        if len(results):
            return [[result[0], result[1], [int(i) for i in result[2].split(',')]] for result in results]

    def print_results(self, query, frequencies, pages, snippets):
        print(f'Results for query: "{" ".join(query)}"')
        print('{} results found in {:.0f}ms'.format(self.all_results, self.time_needed_to_search))
        print("{:<12} {:<40} {}".format('Frequencies', 'Document', 'Snippets'))
        print("{} {} {}".format('-' * 12, '-' * 40, '-' * 80))
        for i in range(min(self.results_limit, len(pages))):
            print("{:<12} {:<40} {}".format(frequencies[i],
                                            pages[i],
                                            '... ' + ' ... '.join(snippets[i][:self.snippet_limit]) + ' ...'))

    def search_db(self, words):
        cursor = self.conn.cursor()
        query = self.build_query(words)
        cursor.execute(query)
        results = cursor.fetchall()
        return self.process_results(results)

    def get_document(self, page_name):
        map_name = '.'.join(page_name.split('.')[:3])
        return open(os.path.join(self.data_dir, "{}/{}".format(map_name, page_name)), 'r', encoding='utf-8')

    def search(self, words):
        # start the timer and do the search, after that calculate the time needed for search
        start_time = time.time()
        results = self.search_db(words)
        self.all_results = len(results)
        end_time = time.time()
        self.time_needed_to_search = (end_time - start_time) * 1000

        pages, frequencies, snippets = [], [], []
        ctr = 0
        for page_file, frequency, indexes in results:
            if ctr > self.results_limit:
                break
            ctr += 1
            pages.append(page_file)
            frequencies.append(frequency)
            document = self.get_document(page_file)
            soup = BeautifulSoup(document, features="html.parser")
            for script in soup(["script", "style"]):
                script.decompose()

            strips = list(soup.stripped_strings)
            text = ' '.join(strips)
            tokens = nltk.word_tokenize(text, language='Slovene', preserve_line=False)
            word_tokens = []
            for i in range(len(tokens)):
                w = tokens[i].lower()
                if not re.search('[a-žA-ž]', w):
                    continue
                if len(w) == 1 and not re.match("^[A-Ža-ž0-9]*$", w):
                    continue
                if len(w) >= 2 and not re.match("^[A-Ža-ž0-9]*$", w[-1]):
                    w = w[:-1]
                if len(w) >= 2 and not re.match("^[A-Ža-ž0-9]*$", w[0]):
                    w = w[1:]
                if w not in self.stop_words_slovene:
                    word_tokens.append(w)
            # snippets.append(self.get_snip(tokens, indexes))
            snippets.append(self.snip.get_snip(tokens, indexes))
        self.print_results(words, frequencies, pages, snippets)


sqlite_search = SQLiteSearch()
sqlite_search.search([x.lower() for x in sys.argv[1:]])
