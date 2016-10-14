import sys
import re
import string
import random
import itertools
from collections import deque, defaultdict, Counter

weird_words = [('i\. e\. ', 'ie '), ('e\. g\. ', 'eg '), ('etc\.', 'etc'),
               ('l\. c\. ', ''), (' p\. ', ''), (' ch\. ', '')]

def sanitize(line):
    line = line.lower()
    for pre, post in weird_words:
        line = re.sub(pre, post, line)
    line = re.sub('[^\.a-z]+', ' ', line)
    line = re.sub(r'\.', ' . ', line)
    line = re.sub(' +', ' ', line)
    return filter(bool, line.split(' '))

def get_words(filename, firstline=None, lastline=None):
    with open(filename, 'r') as fobj:
        i = 0
        for line in fobj:
            i += 1
            if firstline and i < firstline:
                continue
            if lastline and i > lastline:
                break
            yield from sanitize(line)

def n_gram(words, n):
    words = iter(words)
    bank = defaultdict(Counter)
    prefix = deque(itertools.islice(words, n-1), maxlen=n-1)
    for word in words:
        bank[tuple(prefix)].update([word])
        prefix.append(word)
    return bank

def seed(bank):
    seed = random.choice([prefix for prefix in bank.keys() if prefix[0] == '.'])
    n = len(seed) + 1
    prefix = deque(seed, maxlen=n-1)
    return prefix

def generate(bank):
    prefix = []
    while True:
        if tuple(prefix) in bank:
            words = list(bank[tuple(prefix)].elements())
            word = random.choice(words)
            yield word
            prefix.append(word)
        else:
            prefix = seed(bank)
            
            yield from prefix

proper_nouns = set('aristotle plato i m c greek bourgeois bourgoisie'.split(' '))
def normalize(words):
    words = list(words)
    sentence = ''
    for i in range(len(words)):
        if words[i - 1] == '.':
            sentence += words[i].capitalize()
        elif words[i] == '.':
            if i != 0:
                sentence += '. '
        else:
            if words[i] in proper_nouns:
                words[i] = words[i].capitalize()
            sentence += ' ' + words[i]
    return sentence


if __name__ == '__main__':
    fname = sys.argv[1]
    corpus = get_words(fname)
    print('Reading', fname)
    print('Press enter for another sentence')
    bank = n_gram(corpus, 3)
    while True:
        words = itertools.islice(generate(bank), 15)
        print(normalize(words))
        input()
