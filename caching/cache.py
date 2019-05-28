"""
Cache Players, Statistics, Achivements, And PlayerAchievements
"""


class Cacher:
    def __init__(self):
        self.data = {}
        self.unique_to_pk = {}

    def get(self, unique=None, pk=None):
        if pk is not None:
            return self.data[pk]

        if unique is not None:
            return self.data[self.unique_to_pk[unique]]

        return None

    def create(self, pk, item, unique=None):
        self.data[pk] = item
        if unique is not None:
            self.unique_to_pk[unique] = pk
