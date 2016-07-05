import math

def f_tf(doc):
    tf = {}
    total = len(doc.split())
    for word in doc.split():
        if word in tf.keys():
            tf[word] += 1
        else:
            tf[word] = 1
    for word in tf.keys():
        tf[word] /= float(total)
    return tf


def f_idf(docs):
    idf = {}
    for doc in docs:
        for word in set(doc.split()):
            if word in idf.keys():
                idf[word] += 1
            else:
                idf[word] = 1
    for word in idf.keys():
        idf[word] = 1 + math.log(len(docs) / float(idf[word]))
    return idf

def f_distance(doc1, doc2):
    pass

documents = [
    'a species is a kind of organism',
    'a organism is a living thing',
    'bacteria is a living organism',
    'a is the letter'
]

# for doc in documents:
print(f_idf(documents))

