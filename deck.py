# deck.py

import random
from card import Card
import numpy as np 

class Deck:
    def __init__(self, num_decks=1, prop='default'):
        self.num_decks = num_decks

        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.ten_group_ranks = ['10', 'J', 'Q', 'K']
        self.suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

        if prop != 'default':
            ten_group_prop_each = prop['10'] / 4
            final_props = {r: (ten_group_prop_each if r in self.ten_group_ranks else prop.get(r, 0)) for r in self.ranks}
            self.final_props = final_props
            

        else : 
            self.final_props = {c: 4/52 for c in (self.ranks)}

        self.props = list(self.final_props.values())

        if num_decks < np.inf : 
            self.cards = self.create_deck(prop)
            self.shuffle()
        
        self.count = 0



    def create_deck(self, prop = 'default'):
        if prop == 'default' :
            return [Card(suit, rank) for suit in self.suits for rank in self.ranks] * self.num_decks
                
        ## Si proportion custom  (pas ultra opti...): 
        cards_per_rank = {r: round(self.final_props[r] * self.num_decks) for r in self.ranks}
        deck = []

        for rank in self.ranks:
            count = cards_per_rank[rank]
            per_suit = count // 4
            remainder = count % 4

            for i, suit in enumerate(self.suits):
                extra = 1 if i < remainder else 0
                deck.extend([Card(suit, rank)] * (per_suit + extra))
        
        return deck 


    def shuffle(self):
        if self.num_decks < np.inf : 
            random.shuffle(self.cards)
        self.count = 0


    def deal(self):
        if self.num_decks < np.inf : 
            self.count += self.cards[-1].counting_value
            return self.cards.pop()
        
        rank = np.random.choice(self.ranks , p= self.props)
        #suit = np.random.choice(self.suits) 

        return Card('Diamonds', rank)


    def cards_left(self):
        if self.num_decks == np.inf : 
            return np.inf
        return len(self.cards)


    @property
    def true_count(self):
        if self.num_decks == np.inf : 
            return  0
        return self.count / self.num_decks
