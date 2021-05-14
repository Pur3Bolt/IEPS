import ntpath


from nltk.corpus import stopwords
import nltk
from nltk import word_tokenize
from bs4 import BeautifulSoup
import codecs
import sqlite3
import re
import os

file = 'pages/e-prostor.gov.si/e-prostor.gov.si.1.html'
file_name = ntpath.split(file)[1]
print("Working with file: ", file_name)
f = codecs.open(file, 'r', 'utf-8')
#document = BeautifulSoup(f.read(), features="html.parser")

soup = BeautifulSoup(f.read(), features="html.parser")
for script in soup(["script", "style"]):
    script.decompose()

strips = list(soup.stripped_strings)
print(' '.join(strips))

tokens = word_tokenize(' '.join(strips), language='Slovene', preserve_line=False)
# index_words_with_index = []
# new_index_words = set()
# print(document)

print(tokens)
# for i in range(len(tokens)):
#     a1 = tokens[i].lower()
#     if len(a1) == 1 and not re.match("^[A-Za-z0-9]*$", a1):  # Tle odstranim vse znake ki niso besede ali stevilke
#         continue
#     if a1 not in stop_words_slovene:
#         index_words_with_index.append((a1, i))
#         if a1 not in global_index_words:
#             new_index_words.add(a1)
#             global_index_words.add(a1)