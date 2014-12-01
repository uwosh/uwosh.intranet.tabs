from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility

def generate_unique_id(ids, id):
    origid = id = getUtility(IIDNormalizer).normalize(id)
    count = 1
    while id in ids:
        id = origid + '-' + str(count)
        count += 1
    return id

def list_from_string(s):
    """
    Takes a comma separated string and returns the equivalent list.
    'blah,asdf,word' -> ['blah', 'asdf', 'word']
    """
    return [v.strip() for v in s.split(',') if v.strip()]

def string_from_list(l):
    """
    Turns a list of strings into a comma separated string.
    ['blah', 'asdf', 'word'] -> 'blah,asdf,word'
    """
    return ','.join(l)