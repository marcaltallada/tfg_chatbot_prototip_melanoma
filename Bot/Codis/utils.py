from rake_nltk import Rake
import json
import spacy
from scipy import stats

r = Rake() # Used to extract keywords
nlp = spacy.load("en_core_web_lg") # Word embedding dictionary

# Given a sentence, extracts keywords using rake
def get_keywords(sentence):
    r.extract_keywords_from_text(sentence)
    keywords = r.get_ranked_phrases()
    return keywords

# Compares question to dictionary (previously read with read_book)
def compute_scores_from_index(question, data):
    keywords = get_keywords(question)

    analyzed = analyze(question)
    for d in analyzed:
        keywords.extend(d['Subjects'])
        keywords.extend(d['Verbs'])
        keywords.extend(d['Complements'])
    keywords = list(set(keywords))
    #keywords = [nlp(k) for k in keywords]
    scores = []
    for index in data:
        score = get_score(keywords, (index['title']))
        scores.append(score)
    return scores

# Given two lists of keywords, extracts mean distance between their words
def get_score(keywords, title):
    title = nlp(title)
    if len(keywords) == 0 or len(title) == 0:
        return 0
    scores = []
    for word1 in keywords:
        indexes = []
        for word2 in title:
            indexes.append(nlp(word1).similarity(word2))
        scores.append(max(indexes))

    finallist = []
    for max_score in scores:
        if max_score <= 0:
            finallist.append(0.01)
        else:
            finallist.append(max_score)
    mean = stats.gmean(finallist)
    return mean


# Reads a .json file
def read_book(file):
    data = json.load(open("./ProcessedData/" + file, 'r'))
    return data



# Relates pronoun with morphological meaning
def inter_association(noun):
    cosa = {
        'what':'information',
        'who':'person',
        'why':'reason',
        'where' : 'place',
        'when' : 'time',

    }
    return cosa[noun]

# Extracts main features from question sentences (verbs, subjects, etc). Also reads if sentence is negated
def analyze(question):
    doc = nlp(question)
    negative = False
    j = 0
    phrases = []
    how = False
    for sent in doc.sents:
        if sent.text[-1]=="?":
            phrase = {'Subjects':[], 'Verbs':[], 'Negative':[], 'Complements':[]}
            phrase['Negative'].append(False)
            for word in sent:
                if word.dep_ == "nsubj":
                    phrase['Subjects'].append(word.text.lower())
                elif word.dep_ == "ROOT":
                    phrase['Verbs'].append(word.text.lower())
                elif word.dep_ == "neg":
                    phrase['Negative'] = True
                elif word.text.lower() in ['what','where','when','who','why']:
                    phrase['Complements'].append(word.text.lower())
                elif word.dep_ == "acom" or word.dep == "dobj":
                    phrase['Complements'].append(word.text.lower())
                if how:
                    phrase['Complements'].append("how")
                    if word.text.lower() in {'much','many'}:
                        phrase['Complements'].append(word.text.lower())
                how = (word.text.lower()=='how')
            phrases.append(phrase)
    return(phrases)


# Given a question, answers using read data
def process_message(question, data):
    scores = compute_scores_from_index(question, data)
    if max(scores) > 0.6:
        best_match = scores.index(max(scores))
        return data[best_match]
