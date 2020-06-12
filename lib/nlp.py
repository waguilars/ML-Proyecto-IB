
import timeit
import math as ma
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import pandas as pd
import numpy as np
import re
from unidecode import unidecode
import emoji


def get_dictionary(doc):
    f = open(doc, encoding='utf-8')
    dictionary = []
    for i in f:
        dictionary.append(i)
    dictionary = list(map(clean, dictionary))
    dictionary = list(map(lambda x: x.split(), dictionary))
    dictionary = list(map(clean_stemmer, dictionary))
    dictionary = list(map(lambda x: " ".join(x), dictionary))
    return list(set(dictionary))


def get_jaccard(query, document):
    interseccion = len(query.intersection(document))
    union = len(query.union(document))
    return interseccion / union


def clean(a):
    emojis = [c for c in a if c in emoji.UNICODE_EMOJI]
    a = a.split()
    a = [i for i in a if i[0] != '@']
    a = [i for i in a if not re.search('^http', i)]
    a = " ".join(a)
    b = a.lower()
    c = unidecode(b)
    c = re.sub('[^a-zA-Z\u00C0-\u017F]+', ' ', c)
    return c+' '+' '.join(emojis)


def clean_stop_words(titles):
    stop_words = stopwords.words('spanish')
    for word in stop_words:
        if word in titles:
            titles.remove(word)
    return titles


def clean_stemmer(titles):
    stemmer = SnowballStemmer('spanish')
    new_titles = []
    for item in titles:
        new_titles.append(stemmer.stem(item))
    return new_titles

# def clean_stemmer(titles):
#     stemmer = PorterStemmer()
#     new_titles = []
#     for item in titles:
#         new_titles.append(stemmer.stem(item))
#     return new_titles


def to_string(titles):
    document = ""
    for item in titles:
        document += item+" "
    return document.strip()


def do_nlp(lista, stop_words=False):
    new_list = []
    for doc in lista:
        doc = clean(doc).strip().split()
        if stop_words:
            doc = clean_stop_words(doc)
        doc = clean_stemmer(doc)
        new_list.append(doc)
    return new_list


def get_jackar(docs):
    labels = ['doc'+str(x) for x in range(len(docs))]
    jaccard_mtx = pd.DataFrame(float, index=labels, columns=labels)

    for i in range(len(docs)):
        for j in range(i, len(docs)):
            d1 = {i for i in docs[i].split()}
            d2 = {i for i in docs[j].split()}
            intersection = len(d1.intersection(d2))
            union = len(d1.union(d2))
            value = intersection/union

            jaccard_mtx._set_value('doc'+str(i), 'doc'+str(j), value)
            jaccard_mtx._set_value('doc'+str(j), 'doc'+str(i), value)
    return jaccard_mtx


def get_dict(cleaned_docs):
    data = []
    for doc in cleaned_docs:
        data += doc
    return list(set(data))


def get_positions(token, docs):
    all_matches = [token]
    for doc in docs:
        matches = []
        if token in doc:
            indexes = [i for i, x in enumerate(doc) if x == token]
            #matches += [docs.index(doc), len(indexes), indexes]
            matches += [docs.index(doc), len(indexes)]
        if matches:
            all_matches.append(matches)
    return all_matches


def get_fii(docs, diccionary):
    my_dict = diccionary
    fii = map(lambda x: get_positions(x, docs), my_dict)
    return list(fii)


def get_mtx_tf_idf(palabras, abstracts, tb_wtf, idf):
    tb_tf_idf = pd.DataFrame(float(0), index=palabras, columns=[
                             x for x in range(len(abstracts))])
    for index, row in tb_wtf.iterrows():
        for i, ind in row.iteritems():
            # index nombre fila , # i columna nombre, #ind term frecuency
            tb_tf_idf._set_value(
                index, i, (ind*idf._get_value(index, 'frecuency')))
    return tb_tf_idf


def normalize_tf_idf(tf_idf):
    tf = tf_idf
    nom = tf.columns.tolist()
    for i in nom:
        columna = tf[i].tolist()
        res = ma.sqrt(sum(value**2 for value in columna))
        div = [value/res for value in columna]
        tf[i] = div
    return tf


def get_cos_mtx(tf_idf_mtx):
    labels = tf_idf_mtx.columns
    cos_mtx = pd.DataFrame(float, index=labels, columns=labels)

    for i in range(len(labels)):
        for j in range(i, len(labels)):

            doc1 = tf_idf_mtx[i].tolist()
            doc2 = tf_idf_mtx[j].tolist()
            value = sum(val1*val2 for val1, val2 in zip(doc1, doc2))
            cos_mtx[i][j] = value
            cos_mtx[j][i] = value

    return cos_mtx

# text="RT @Lenin: @DrJuanCZevallos confirmó que el 89% de contagiados por #COVID19 se han recuperado. De las 110.812 pruebas realizadas, menos de…"
# text=(clean(text))
# print(text)
# text=clean_stop_words(text.split())
# print(text)
# text=clean_stemmer(text)
# print(text)
