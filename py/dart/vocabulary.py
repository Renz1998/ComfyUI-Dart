"""Pinned, offline tag retrieval. Dataset names are not asserted to be current canonical names."""
from pathlib import Path
import base64
import hashlib
import json
import math
import re
import zlib
from functools import lru_cache

# Retrieval hints only; never rewrite or emit an output tag without candidate selection.
QUERY_FORMS = {'haired':'hair','eyed':'eyes','rainy':'rain','snowy':'snow','smiling':'smile',
               'wildflowers':'flowers','stands':'standing','gazes':'looking','motes':'particles'}

def words(text):
    return re.findall(r"[\w]+", text.casefold().replace('_', ' '))

def normalized(text):
    return ' '.join(words(text))

@lru_cache(maxsize=1)
def vocabulary():
    path = Path(__file__).parents[1] / 'data' / 'tag_vocabulary.json.z85'
    raw = path.read_bytes()
    value = json.loads(zlib.decompress(base64.b85decode(raw)))
    return Vocabulary(value, hashlib.sha256(raw).hexdigest())

class Vocabulary:
    def __init__(self, value, digest='fixture'):
        self.manifest = value['manifest']; self.digest = digest
        self.rows = {}; self.exact = {}; self.terms = {}
        for index, row in enumerate(value['tags']):
            key = f't{index}'
            name, category, slot, count, aliases = row
            self.rows[key] = dict(id=key, tag=name, category=category, slot=slot, count=count)
            for spelling in [name, *aliases]:
                self.exact.setdefault(normalized(spelling), set()).add(key)
                for term in set(words(spelling)):
                    self.terms.setdefault(term, set()).add(key)

    def lookup(self, text):
        return sorted(self.exact.get(normalized(text), ()))

    def search(self, text, limit=12):
        terms = {QUERY_FORMS.get(term,term) for term in words(text)}; scores = {}
        for term in terms:
            for key in self.terms.get(term, ()):
                scores[key] = scores.get(key, 0) + math.log(1 + len(self.rows)/len(self.terms[term]))
        exact = self.lookup(text)
        for key in exact: scores[key] = scores.get(key, 0) + 100
        ranked = sorted(scores, key=lambda key: (-scores[key], -math.log1p(self.rows[key]['count']), self.rows[key]['tag']))
        return [self.rows[key] for key in ranked[:limit]]

    def candidates(self, concepts, limit=180):
        # Round-robin prevents the first facet from monopolizing the context.
        groups = [self.search(text, 12) for text in concepts]
        result = {}; max_depth = max((len(group) for group in groups), default=0)
        for depth in range(max_depth):
            for group in groups:
                if depth < len(group): result.setdefault(group[depth]['id'], group[depth])
                if len(result) >= limit: return list(result.values())
        return list(result.values())

def sort_tags(records):
    def rank(row):
        tag = row['tag']; category = row['category']
        if re.fullmatch(r'\d+(girls?|boys?|others?)', tag) or tag in ('solo','multiple_girls','multiple_boys'): return 0
        return {'character':1,'copyright':2,'general':3,'meta':4}.get(category, 5)
    seen = set(); result = []
    for row in sorted(records, key=rank):
        if row['tag'] not in seen: result.append(row['tag']); seen.add(row['tag'])
    return result
