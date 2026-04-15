# card.py

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    @property
    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

    @property
    def counting_value(self):
        if self.rank in ['2', '3', '4', '5', '6'] :
            return 1
        elif self.rank in ['7', '8', '9'] :
            return 0
        else : 
            return -1

