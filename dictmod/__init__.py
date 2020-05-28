"""
Functions for working with nested dictionaries.

e.g.
>>> d = {}
>>> 
>>> dset(d, 'foo.bar.nar', 12)


"""


SEP='.'

def expand_key(d, key, create=False, sep=SEP):
    """
    Expands the parts of a key based on the separator and returns the last dict and final key

    >>> d = {'a': 'one', 'b': {'c': 'two', 'd': 'three'}}
    >>> expand_key(d, 'a')
    ({'a': 'one', 'b': {'c': 'two', 'd': 'three'}}, 'a')
    >>> expand_key(d, 'b.c')
    ({'c': 'two', 'd': 'three'}, 'c')
    >>> expand_key(d, 'b.e.f')
    Traceback (most recent call last):
        ...
    KeyError: "Unable to find component 'e' of 'b.e.f'"
    >>> expand_key(d, 'b.e.f', True)
    ({}, 'f')
    >>> d
    {'a': 'one', 'b': {'c': 'two', 'd': 'three', 'e': {}}}
    """
    parts = key.split(sep)
    for k in parts[:-1]:
        try:
            d = d[k]
        except KeyError:
            if create:
                d[k] = {}
                d = d[k]
            else:
                raise KeyError(f"Unable to find component '{k}' of '{key}'")
    return d, parts[-1]

def flatten_dict(d, prefix="", sep=SEP):
    """
    Flattens a nested dict to a single level iterable with composite keys

    >>> list(flatten_dict({'a': 'one', 'b': {'c': 'two', 'd': 'three'}}))
    [('a', 'one'), ('b.c', 'two'), ('b.d', 'three')]
    >>> list(flatten_dict({'a': 'one', 'b': {'c': 'two', 'd': 'three'}}, sep='->'))
    [('a', 'one'), ('b->c', 'two'), ('b->d', 'three')]
    """
    for k, v in d.items():
        if isinstance(v, dict):
            for r in flatten_dict(v, f"{prefix}{k}{sep}"):
                yield r
        else:
            yield f"{prefix}{k}", v

def dget(d, key, sep=SEP):
    """
    Retreive a value from a nested dict based on a composite key

    >>> d = {'a': 1, 'b': {'c': 2}}
    >>> dget(d, 'b.c')
    2
    """
    d, k = expand_key(d, key, False, sep)
    return d[k]

def dset(d, key ,value, overwrite=True, create=True, sep=SEP):
    """
    Set a nested dict value based on a composite key
    Can control whether to create nested paths and overwrite existing values

    >>> d = {'a': 1}
    >>> dset(d, 'b.c', 2)
    >>> dset(d, 'd.e', 3, create=False)
    Traceback (most recent call last):
    ...
    KeyError: "Unable to find component 'd' of 'd.e'"
    >>> dset(d, 'b.c', 4, overwrite=False)
    Traceback (most recent call last):
    ...
    KeyError: "Cannot overwrite existing value for 'b.c'"
    >>> dset(d, 'b.c', 5)
    >>> d
    {'a': 1, 'b': {'c': 5}}
    """
    d, k = expand_key(d, key, create, sep)
    if not overwrite and k in d:
        raise KeyError(f"Cannot overwrite existing value for '{key}'")
    d[k] = value

def dsetmissing(d, key, value, sep=SEP):
    """
    Set a nested dict value based on a composite key, only if not currently set

    >>> d = {'a': 1, 'b': {'c': 2}}
    >>> dsetmissing(d, 'b.c', 3)
    >>> dsetmissing(d, 'b.d', 4)
    >>> d
    {'a': 1, 'b': {'c': 2, 'd': 4}}
    """
    try:
        dset(d, key, value, overwrite=False, sep=sep)
    except KeyError:
        pass

def ddel(d, key, missing_ok=False, sep=SEP):
    """
    Deletes a composite key from a nested dict.

    >>> d = {'a': 1, 'b': {'c': 2}}
    >>> ddel(d, 'd', missing_ok=True)
    >>> ddel(d, 'd')
    Traceback (most recent call last):
    ...
    KeyError: 'd'
    >>> ddel(d, 'b.c')
    >>> ddel(d, 'a')
    >>> d
    {'b': {}}
    """
    try:
        d, k = expand_key(d, key, False, sep)
        del(d[k])
    except KeyError:
        if missing_ok:
            return
        raise

def drename(d, old, new, sep=SEP):
    """
    Moves a value from one composite key to another within a nested dict

    >>> d = {'a': 1, 'b': {'c': 2, 'd': 3}}
    >>> drename(d, 'b.c', 'b.e')
    >>> d
    {'a': 1, 'b': {'d': 3, 'e': 2}}
    >>> drename(d, 'b.d', 'f.g')
    >>> d
    {'a': 1, 'b': {'e': 2}, 'f': {'g': 3}}
    """
    dset(d, new, dget(d, old, sep), sep)
    ddel(d, old, sep)

def dappend(d, key, value, unique=False, create=False, sep=SEP):
    """
    Assumes a composite key refers to a list and appends the value
    Can control whether to allow duplicate values and create the list

    >>> d = {'a': 1, 'b': {'c': 2, 'd': [3]}}
    >>> dappend(d, 'b.d', 4)
    >>> dappend(d, 'b.c', 2, unique=True)
    >>> dappend(d, 'e.f', 5, create=True)
    >>> d
    {'a': 1, 'b': {'c': [2], 'd': [3, 4]}, 'e': {'f': [5]}}
    """
    d, k = expand_key(d, key, create, sep)
    try:
        if not isinstance(d[k], list):
            d[k] = [d[k]]
    except KeyError:
        d[k] = []
    if unique and value in d[k]:
        return
    d[k].append(value)

def dremove(d, key, value, missing_ok=False, sep=SEP):
    """
    Removes a value from a list refered to by a composite key

    >>> d = {'a': 1, 'b': {'c': [1, 2, 3]}}
    >>> dremove(d, 'b.c', 2)
    >>> dremove(d, 'b.c', 2)
    Traceback (most recent call last):
    ...
    ValueError: list.remove(x): x not in list
    >>> dremove(d, 'b.c', 2, missing_ok=True)
    >>> dremove(d, 'b.d', 2, missing_ok=True)
    >>> d
    {'a': 1, 'b': {'c': [1, 3]}}
    """
    try:
        d, k = expand_key(d, key, False, sep)
        d[k].remove(value)
    except:
        if missing_ok:
            return 
        raise

def dprune(d):
    """    
    Removes empty leaves from a nested dict
    """    
    remove = []
    for key, value in d.items():
        if isinstance(value, dict):
            if not value:
                remove.append(key)
            else:
                d[key] = dprune(value)

    for key in remove:
        del(d[key])

    return d


OPS = {
    '=': dset,
    '~=': drename,
    '?=': dsetmissing,
    '+=': dappend,
    '-=': dremove,
}


def dpatch(d, *items):
    """
    >>> d = {'a': 1, 'b': {'c': 2}} 
    >>> dpatch(d, ('b.c', '=', 3), ('b.c', '~=', 'd.c'), ('d.e', '+=', 4))
    {'a': 1, 'd': {'c': 3, 'e': [4]}}
    """ 

    for key, op, value in items:
        OPS[op](d, key, value)

    return dprune(d)

def dargparse(*args):
    """
    >>> list(dargparse('b.d=3', 'a.c+=[1, 2, 3]', 'd.e=foo'))
    [('b.d', '=', 3), ('a.c', '+=', [1, 2, 3]), ('d.e', '=', 'foo')]
    """

    import json
    import re
    RE_OP = re.compile(r'([~\?\+\-]?=)')

    for arg in args:
        key, op, value =  RE_OP.split(arg, 1)
        try:
            value = json.loads(value)
        except:
            pass
        yield key, op, value
            

    