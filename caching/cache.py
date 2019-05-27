"""
Cache Players, Statistics, Achivements, And PlayerAchievements
"""


class Cacher:
    def __init__(self):
        self.data = {}
        self.unique_to_pk = {}

    def get(self, item = None, pk = None):
        if pk is not None:
            return self.data[pk]

        if item is not None:
            return self.data[self.unique_to_pk[item]]

        return None

    def create(self, pk, item, unique=None):
        self.data[pk] = item
        if unique is not None:
            self.unique_to_pk[unique] = pk
