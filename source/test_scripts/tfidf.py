import math
import nltk
import re

STOPWORDS = nltk.corpus.stopwords.words('english')
STEMMER = nltk.stem.snowball.SnowballStemmer("english")
LEMMATIZER = nltk.stem.wordnet.WordNetLemmatizer()


class Doc(object):
    text = None
    terms = {}
    idf = {}
    tf = {}
    tfidf = {}

    def __str__(self):
        return self.text + " : " + str(self.terms)


def f_tf(docs):
    for doc in docs:
        doc.tf = {}
        num = len(doc.terms)
        for term in doc.terms:
            if term in doc.tf:
                doc.tf[term] += 1
            else:
                doc.tf[term] = 1
        for tf in doc.tf:
            doc.tf[tf] = int(doc.tf[tf] / float(num) * 1000) / 1000.0
    return docs


def f_idf(docs):
    terms = {}
    for doc in docs:
        for term in set(doc.terms):
            if term in terms:
                terms[term] += 1
            else:
                terms[term] = 1
    for doc in docs:
        doc.idf = {}
        for term in set(doc.terms):
            doc.idf[term] = 1 + math.log(len(docs) / float(terms[term]))
    return docs


def f_tfidf(docs):
    for doc in docs:
        doc.tfidf = {}
        for tf in doc.tf:
            doc.tfidf[tf] = doc.tf[tf] * doc.idf[tf]
    return docs

def f_distance(doc1, doc2):
    """
    Cosine Similarity (d1, d2) =  Dot product(d1, d2) / ||d1|| * ||d2||
    Dot product (d1,d2) = d1[0] * d2[0] + d1[1] * d2[1] * ... * d1[n] * d2[n]
    ||d1|| = square root(d1[0]2 + d1[1]2 + ... + d1[n]2)
    ||d2|| = square root(d2[0]2 + d2[1]2 + ... + d2[n]2)
    """
    dot_product = 0
    for term in doc1.tfidf:
        if term in doc2.tfidf:
            dot_product += doc1.tfidf[term] * doc2.tfidf[term]
    d1 = 0
    d2 = 0
    for term in doc1.tfidf:
        d1 += doc1.tfidf[term] * doc1.tfidf[term]
    d1 = math.sqrt(d1)

    for term in doc2.tfidf:
        d2 += doc2.tfidf[term] * doc2.tfidf[term]
    d2 = math.sqrt(d2)

    return int(dot_product / (d1 * d2) * 1000) / 1000.0

documents = [
    "The sky is blue",
    "The sun is bright",
    "The sun in the sky is bright",
    "We can see the shining sun, the bright sun"
]
query = Doc()
query.text = "sun"
query.terms = [LEMMATIZER.lemmatize(word.lower())
               for word in query.text.split()]
query = f_tf([query])[0]
print(query.tf)

print('*'*5 + ' docs ' + '*'*5)
docs = []
for document in documents:
    doc = Doc()
    doc.text = document
    doc.terms = [LEMMATIZER.lemmatize(re.sub(r'\W+', '', word).lower())
                 for word in document.split()
                 if word.lower() not in STOPWORDS]
    docs.append(doc)
    print(doc)


print('*'*5 + ' IDF ' + '*'*5)
docs = f_idf(docs)
for doc in docs:
    print(doc.idf)

query.idf = {'sun': 1.2876820724517808}
query.tfidf = {'sun': query.tf['sun'] * query.idf['sun']}

print('*'*5 + ' TF ' + '*'*5)
docs = f_tf(docs)
for doc in docs:
    print(doc.tf)

print('*'*5 + ' TFIDF ' + '*'*5)
docs = f_tfidf(docs)
for doc in docs:
    print(doc.tfidf)

print('*'*5 + ' DISTANCE ' + '*'*5)
#for doc in docs:
#    print(doc, str(f_distance(doc, query)))
for doc1 in docs:
    print(doc1.terms)
    for doc2 in docs:
        print('\t', f_distance(doc1, doc2), doc2.terms)

