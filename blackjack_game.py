# blackjack_game.py

import numpy as np 
import random

from deck import Deck
from hand import Hand

import list_strategies


class BlackjackGame:
    def __init__(self, num_decks, reshuffle_pct, rules, prop= 'default'):
        self.num_decks = num_decks
        self.reshuffle_pct = reshuffle_pct
        self.rules = rules


        basic_strategy_name = list_strategies.strategy_by_rules[frozenset(rules.items())]
        self.basic_strategy_dic = getattr(list_strategies, basic_strategy_name)

        self.prop = prop
        self.deck = Deck(num_decks, prop)
        self.player_hands = [Hand()]
        self.dealer_hand = Hand()
        self.split_ace = False  ## Est qu'un ace a été split


    def reshuffle_needed(self):
        return (self.deck.cards_left() / (52 * self.num_decks)) < (self.reshuffle_pct / 100)


    def initial_deal(self):
        #Tirage de la 1ere carte pour chaque main
        for hand in self.player_hands:
            hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        #Tirage seconde carte pour chaque main
        for hand in self.player_hands:
            hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())

    def dealer_action(self):
        while self.dealer_hand.value < 17:
            self.dealer_hand.add_card(self.deck.deal())


    def can_surrender(self, hand, dealer_card): 
        if self.rules['surrender'] == False :
            return False 
        if len(hand.cards) > 2 : 
            return False
        if len(self.player_hands) > 1 : 
            return False
        if self.rules['surr_to_ace'] == False and dealer_card.value == 11: 
            return False
        return True

    def can_double(self, hand):
        if len(hand.cards) > 2 : 
            return False
        if self.rules['double_any_hands'] == False and hand.value not in [9, 10, 11]:
            return False
        if self.rules['double_after_split'] == False and len(self.player_hands) > 1: 
            return False
        return True
    
    def can_split(self):
        if len(self.player_hands) > self.rules['max_split'] : 
            return False
        if self.rules['resplit_after_ace_split'] == False and self.split_ace:
            return False
        return True 
    
    def can_hit(self): 
        if self.rules['hit_after_ace_split'] == False and self.split_ace: 
            return False
        return True
    
    def true_move(self, move, hand, dealer_card= None): 
        if len(move) == 1: 
            return move
        if move[0] == 'D' and self.can_double(hand):
            return move[0]
        if move[0] == 'R' and self.can_surrender(hand, dealer_card):
            return move[0]
        return move[-1]


    ### Utilisation de la strategie
    def use_strategy(self, hand, dealer_card, strategy_dic):
        if hand.value > 21 :
            return 'B'
        
        if strategy_dic == 'random' : 
            return random.choice(['S', 'H'])

        dealer_value = dealer_card.value
        dealer_value = dealer_value if dealer_value <11 else 'A'
        move = None

        ## On lit la table PAIR que si on a une pair et que les conditions de splits sont respectées
        if hand.is_pair() and self.can_split():  
            move = strategy_dic['PAIR'][(hand.cards[0].value, dealer_value)]
            move = self.true_move(move, hand, dealer_card)

            if move == 'P' and hand.has_ace(): # Split avec un AS
                self.split_ace = True

        ## On lit la table SOFT seulement si on a un AS et au moins 2 valeurs possibles de main (A, 7 --> 8 ou 18)
        elif hand.has_ace() and len(hand.values_possible) > 1 and self.can_hit(): 
            move = strategy_dic['SOFT'][(hand.value, dealer_value)]
            move = self.true_move(move, hand, dealer_card)

        elif self.can_hit() : 
            move = strategy_dic['HARD'][(hand.value, dealer_value)]
            move = self.true_move(move, hand, dealer_card)

        else : 
            move = 'S'

        return move



    def play_round(self, strategy_dic, bet, return_info=True):

        info_round = ""
        if self.reshuffle_needed():
            self.deck = Deck(self.num_decks, self.prop)
            info_round += "Reshuffling the deck...\n"
            
        true_count_start = self.deck.true_count
        self.player_hands = [Hand()]
        self.dealer_hand = Hand()
        self.initial_deal()

        nb_hands = 1
        index_hands = 0
        list_bets = [bet]

        while nb_hands > 0:
            hand = self.player_hands[index_hands]
            list_bets[index_hands] = list_bets[index_hands]

            info_round += f"Player's hand: {hand}\n"
            info_round += f"Dealer's hand: {self.dealer_hand.cards[0]} and [Hidden]\n"

            move = self.use_strategy(hand, self.dealer_hand.cards[0], strategy_dic)

            while move == 'H':
                hand.add_card(self.deck.deal())
                move = self.use_strategy(hand, self.dealer_hand.cards[0], strategy_dic)
                info_round += f"Player hits: {hand}\n"

            if move == 'D':
                list_bets[index_hands] = list_bets[index_hands] * 2
                hand.add_card(self.deck.deal())
                info_round += f"Player doubles: {hand}\n"


            if move =='R':
                info_round += f"Player surrender : {hand}\n"

            if move == 'P':

                nb_hands += 2
                list_bets.append(bet)

                new_hand = Hand()
                new_hand.add_card(hand.cards.pop())
                hand.add_card(self.deck.deal())
                new_hand.add_card(self.deck.deal())

                self.player_hands.pop(index_hands)
                index_hands -= 1
                self.player_hands.append(hand)
                self.player_hands.append(new_hand)

                info_round += f"Player splits: {hand} and {new_hand}\n"

            info_round += '\n'

            nb_hands -= 1
            index_hands += 1
            
        self.dealer_action()
        info_round += f"Dealer's final hand: {self.dealer_hand}\n\n"
        final_bet = 0


        ## A Noter que le true blackjack se fait lorsque hand.blackjack()==TRUE et len(self.player_hands) ==1 == True (BJ sans splits)
        for i, hand in enumerate(self.player_hands):
            if move == 'R':
                info_round += f"Player surrendered with {hand.value}\n"
                final_bet -= 0.5 * list_bets[i]

            elif hand.value > 21:
                info_round += f"Player busts with {hand.value}\n"
                final_bet -= list_bets[i]

            elif len(self.player_hands) == 1 and hand.is_blackjack() and not self.dealer_hand.is_blackjack():
                final_bet += 1.5 * list_bets[i]
                info_round += f"BLACKJACK! Player wins with {hand.value} against dealer's {self.dealer_hand.value}\n"
            
            elif self.dealer_hand.is_blackjack() and not (hand.is_blackjack() and len(self.player_hands) == 1):
                final_bet -= list_bets[i]
                info_round += f"Dealer made a BLACKJACK with {self.dealer_hand.value} against player's {hand.value}\n"

            elif self.dealer_hand.value > 21 or hand.value > self.dealer_hand.value:
                final_bet += list_bets[i]
                info_round += f"Player wins with {hand.value} against dealer's {self.dealer_hand.value}\n"

            elif hand.value == self.dealer_hand.value:
                info_round += f"Push with {hand.value}\n"

            else:
                info_round += f"Dealer wins with {self.dealer_hand.value} against player's {hand.value}\n"
                final_bet -= list_bets[i]

        #if hand.value == 21 and len(hand.cards)==2 and self.dealer_hand.is_blackjack() and hand.has_ace() and len(self.player_hands)>1:
         #   print(info_round)
         #   print(final_bet) #On affiche le cas ou le joueur a split et a un faux BJ apres split contre un BJ du croupier ->> OK

        #if self.dealer_hand.is_blackjack() and hand.is_blackjack():  -->> OK
           #print(info_round)
           #print(final_bet)

        #if len(self.player_hands) >1 : 
            #print(info_round)
            #print(final_bet)

        self.split_ace = False # Reinitialisation du split_ace une fois le round terminé
        

        if return_info == False : 
            return final_bet, true_count_start

        return final_bet, true_count_start, info_round



