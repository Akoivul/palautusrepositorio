class QueryBuilder:
    def __init__(self, matchers=None):
        if matchers is None:
            self._matchers = []
        else:
            self._matchers = matchers
    
    def build(self):
        if not self._matchers:
            return All()
        
        if len(self._matchers) == 1:
            return self._matchers[0]
        
        return And(*self._matchers)
    
    def plays_in(self, team):
        matcher = [PlaysIn(team)]
        return QueryBuilder(self._matchers + matcher)

    def has_at_least(self, value, attr):
        matcher = [HasAtLeast(value, attr)]
        return QueryBuilder(self._matchers + matcher)
    
    def has_fewer_than(self, value, attr):
        matcher = [HasFewerThan(value, attr)]
        return QueryBuilder(self._matchers + matcher)
    
    def one_of(self, *queries):
        or_matchers = []
        for query in queries:
            or_matchers.append(query.build())
        
        return QueryBuilder([Or(*or_matchers)])

class And:
    def __init__(self, *matchers):
        self._matchers = matchers

    def test(self, player):
        for matcher in self._matchers:
            if not matcher.test(player):
                return False

        return True

class All:
    def __init__(self):
        pass
    def test(self, player):
        return True

class Not:
    def __init__(self, matcher):
        self._matcher = matcher
    
    def test(self, player):
        return not self._matcher.test(player)

class HasFewerThan:
    def __init__(self, value, attr):
        self._value = value
        self._attr = attr
    
    def test(self, player):
        player_value = getattr(player, self._attr)
        
        return player_value < self._value

class Or:
    def __init__(self, *matchers):
        self._matchers = matchers
    
    def test(self, player):
        for matcher in self._matchers:
            if matcher.test(player):
                return True
        return False

class PlaysIn:
    def __init__(self, team):
        self._team = team

    def test(self, player):
        return player.team == self._team


class HasAtLeast:
    def __init__(self, value, attr):
        self._value = value
        self._attr = attr

    def test(self, player):
        player_value = getattr(player, self._attr)

        return player_value >= self._value
