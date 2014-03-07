from six import add_metaclass

from .utils import DslMeta

class QueryMeta(DslMeta):
    _classes = {}

def Q(name_or_query, **params):
    if isinstance(name_or_query, dict):
        if params:
            raise #XXX
        if len(name_or_query) != 1:
            raise #XXX
        name, params = name_or_query.popitem()
        return Query.get_dsl_class(name)(**params)
    if isinstance(name_or_query, Query):
        if params:
            raise #XXX
        return name_or_query
    return Query.get_dsl_class(name_or_query)(**params)

@add_metaclass(QueryMeta)
class Query(object):
    name = None
    def __init__(self, **params):
        self._params = params

    def __add__(self, other):
        return Bool(must=[self, other])

    def __eq__(self, other):
        return isinstance(other, Query) and other.name == self.name \
            and other._params == self._params

    def to_dict(self):
        return {self.name: self._params}

class MatchAll(Query):
    name = 'match_all'
    def __add__(self, other):
        return other

    def __radd__(self, other):
        return other

EMPTY_QUERY = MatchAll()

class Match(Query):
    name = 'match'

class Bool(Query):
    name = 'bool'
    def __init__(self, **params):
        for n in ('must', 'should', 'must_not'):
            if n in params:
                params[n] = list(map(Q, params[n]))
        super(Bool, self).__init__(**params)

    @property
    def must(self):
        return self._params.setdefault('must', [])

    @property
    def should(self):
        return self._params.setdefault('should', [])

    @property
    def must_not(self):
        return self._params.setdefault('must_not', [])

    def to_dict(self):
        d = {}
        out = {self.name: d}
        for n in ('must', 'should', 'must_not'):
            if n in self._params:
                d[n] = list(map(lambda x: x.to_dict(), self._params[n]))
        return out

