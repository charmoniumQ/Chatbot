import re
import string
import random
import itertools
from collections import deque, defaultdict, Counter
import nltk
import nltk.data
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import wordnet

def flatten(seq):
    return itertools.chain.from_iterable(seq)

def get_text(filename):
    with open(filename, 'r') as f:
        return ''.join(f.readlines())

def sanitize(word):
    word = word.lower()
    word = re.sub("[^\.,a-z0-9\-']+", ' ', word)
    word = re.sub(" +", '', word)
    return word

def tokenize(text):
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    word_tokenizer = TreebankWordTokenizer()
    for sentence in sent_tokenizer.tokenize(text):
        result = ['.']
        for word in word_tokenizer.tokenize(sentence):
            result.append(sanitize(word))
            # TODO: break on clauses
        if result:
            yield result

def slow_similarity(sentence1, sentence2):
    weights = []
    for word1 in sentence1:
        synsets1 = wordnet.synsets(word1)
        if len(synsets1) < 10:
            for word2 in sentence2:
                synsets2 = wordnet.synsets(word2)
                if len(synsets1) < 10:
                    ms = []
                    for synset1 in synsets1:
                        for synset2 in wordnet.synsets(word2):
                            m = synset1.path_similarity(synset2)
                            if m:
                                ms.append((m, synset1, synset2))
                            else:
                                ms.append((0, synset1, synset2))
                    if ms:
                        m, synset1, synset2 = max(ms)
                        print('{:0.3f} {} {}'.format(m, synset1, synset2))
                        if m > 0.1:
                            weights.append(m)
    if weights:
        return sum(weights) / len(weights)
    else:
        return 0

def similarity(sentence1, sentence2, min_matches=2, min_size=5):
    summary1 = set(word for word in sentence1 if len(word) >= min_size)
    summary2 = set(word for word in sentence2 if len(word) >= min_size)
    if len(summary1 & summary2) >= min_matches:
        return 1
    else:
        return 0

def context(sentences, topic, min_matches, min_size):
    recorded = False
    for sentence in sentences:
        if similarity(sentence, topic, min_matches, min_size) > 0:
            yield sentence

def n_gram(clauses, n):
    '''Returns an n-gram bank from the clauses'''
    bank = defaultdict(list)
    for clause in clauses:
        words = iter(clause)
        prefix = deque(itertools.islice(words, n-1), maxlen=n-1)
        for word in words:
            bank[tuple(prefix)].append(word)
            prefix.append(word)
    return bank

def seed(bank, delim):
    '''Returns an (n-1)-gram prefix from bank to start a sentence'''
    if delim:
        candidates = [prefix for prefix in bank.keys() if prefix[0] == delim]
    else:
        candidates = [prefix for prefix in bank.keys()]
    seed = random.choice(candidates)
    n = len(seed) + 1
    prefix = deque(seed, maxlen=n-1)
    return prefix

def generate_sentence(bank, min_words=10):
    '''Returns one clause'''
    ctr = 0
    prefix = seed(bank, '.')
    yield from itertools.islice(prefix, 1, None)
    while True:
        ctr += 1
        possible_words = list(bank[tuple(prefix)])
        if not possible_words:
            next_word = '.'
        else:
            next_word = random.choice(possible_words)
        if next_word == '.':
            # end a sentence
            if ctr > min_words:
                break
            else:
                for word in seed(bank, '.'):
                    prefix.append(word)
                yield from prefix
        else:
            yield next_word
            prefix.append(next_word)

proper_nouns = {'i'}
def normalize_sentence(words):
    words = list(words)
    sentence = words[0].capitalize()
    capital = False
    for word in words[1:]:
        if word == ',':
            # add comma
            sentence += ','
        elif word == '.':
            sentence += '.'
            capital = True
        else:
            # add word
            if capital:
                capital = False
                sentence += ' ' + word.capitalize()
            else:
                if word in proper_nouns:
                    sentence += ' ' + word.capitalize()
                else:
                    sentence += ' ' + word
    sentence += '.'
    return sentence

def significant_words(sentence):
    return set(word for word in sentence if len(word) > 5)

class Speaker(object):
    def __init__(self, name, fname, n, min_words, min_size, min_matches):
        self.sentences_bank = list(tokenize(get_text(fname)))
        self.name = name
        self.n = n
        self.min_words = min_words
        self.min_size = min_size
        self.min_matches = min_matches
    def speak(self, topic=None):
        # print(len(self.sentences_bank))
        if topic:
            sentences_bank = list(context(self.sentences_bank, topic, self.min_matches, self.min_size))
        else:
            sentences_bank = list(self.sentences_bank)
        if not sentences_bank:
            return self.speak(None)
        n_gram_bank = n_gram(sentences_bank, self.n)
        return topic, len(sentences_bank), generate_sentence(n_gram_bank, self.min_words)

def test4():
    opts = dict(n=3, min_size=6, min_words=15, min_matches=2)
    republican = Speaker('Republican', 'republican.txt', **opts)
    democrat = Speaker('Democrat', 'democratic.txt', **opts)
    seed = None
    while True:
        # speaker = random.choice([trump, clinton])
        for speaker in [republican, democrat]:
            topic, s, response = speaker.speak(seed)
            response = list(response)
            if seed and topic:
                print('{:20} [{} clauses on "{}"]\n'.format('', s, ' '.join(topic)))
            else:
                print('{:20} [new topic]\n'.format(''))
            print('{:<10}: {}'.format(speaker.name.upper(), normalize_sentence(response)))
            seed = significant_words(response)
            input()


if __name__ == '__main__':
    test4()
# Semantic weight, meaining/semantic density, content weight
