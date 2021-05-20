import ntpath
from nltk.corpus import stopwords
import nltk
from nltk import word_tokenize
from bs4 import BeautifulSoup
import codecs
import sqlite3
import re
import os


class DataProcessing:
    def __init__(self, path):
        nltk.download('punkt')  # neded for stopwords
        nltk.download('stopwords')
        self.path = path
        self.DB_NAME = "inverted-index.db"
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
             "katera", "ampak", "lahek", "lahka", "lahko", "morati", "torej", "gl", "xsd", "ipd", "om", "gt", "lt", "d.o.o" })

    def get_files(self):
        files_path = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.path) for f in filenames if
                      os.path.splitext(f)[1].lower() == '.html']
        return files_path

    def process(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()
        files = self.get_files()
        global_index_words = set()
        sucpos = 0
        failpos = 0
        sucword = 0
        failword = 0
        for file in files:
            file_name = ntpath.split(file)[1]
            print("Working with file: ", file_name)
            f = codecs.open(file, 'r', 'utf-8')
            soup = BeautifulSoup(f.read(), features="html.parser")
            for script in soup(["script", "style"]):
                script.decompose()

            strips = list(soup.stripped_strings)
            document = ' '.join(strips)
            tokens = word_tokenize(document, language='Slovene', preserve_line=False)
            index_words_with_index = []
            new_index_words = set()
            for i in range(len(tokens)):
                a1 = tokens[i].lower().replace("'", "").replace("'", '').replace('`', '').replace('·', '')
                if not re.search('[a-žA-ž]', a1):
                    continue
                if len(a1) == 1 and not re.match("^[A-Ža-ž0-9]*$", a1):
                    continue
                if len(a1) >= 2 and not re.match("^[A-Ža-ž0-9]*$", a1[-1]):
                    a1 = a1[:-1]
                if len(a1) >= 2 and not re.match("^[A-Ža-ž0-9]*$", a1[0]):
                    a1 = a1[1:]
                if a1 not in self.stop_words_slovene:
                    index_words_with_index.append((a1, i))
                    if a1 not in global_index_words:
                        new_index_words.add(a1)
                        global_index_words.add(a1)

            index_words_dict = dict()
            for element, index in index_words_with_index:
                if element not in index_words_dict.keys():
                    index_words_dict[element] = []
                index_words_dict[element].append(index)

            # First we insert new index_words
            if len(new_index_words) > 0:
                insert_word_string = """INSERT INTO IndexWord VALUES """
                for word in new_index_words:
                    insert_word_string += "('" + word + "'),"
                insert_word_string = insert_word_string[:-1] + ";"
                try:
                    c.execute(insert_word_string)
                    # print("New index words insert success")
                    sucword += 1
                    conn.commit()
                except:
                    failword += 1
                    print(new_index_words)
                    print(insert_word_string)
                    print("New index words insert failed")

            # Inserting postings
            insert_posting_string = """INSERT INTO Posting VALUES """
            for key in index_words_dict.keys():
                positions = index_words_dict[key]
                pos = ",".join([str(item) for item in positions])
                count = len(positions)
                insert_posting_string += "('" + key.replace("'", "").replace("'", '') + "', '" + file_name + "'," + str(
                    count) + ", '" + pos + "'),"

            insert_posting_string = insert_posting_string[:-1] + ";"
            try:
                c.execute(insert_posting_string)
                # print("New Posting insert success")
                sucpos += 1
                conn.commit()
            except:
                failpos += 1
                print(insert_posting_string)
                print("New Posting insert failed")

        print("Succ inserts words: ", sucword, " Succ insert post: ", sucpos)
        print("Fails insert words: ", failword, " Fail insert post: ", failpos)
        conn.close()


processing = DataProcessing("pages")
processing.process()
