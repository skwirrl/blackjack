from __future__ import annotations

from random import randint
from time import sleep


def print_sleep(string):
    print(string)
    sleep(.5)


class Card:
    INDICES = ("Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J",
               "Q", "K")
    SUITS = ("Clubs", "Hearts", "Spades", "Diamonds")
    FACE_CARDS = ("J", "Q", "K")

    def __init__(self, index: str, suit: str):
        self.index = index
        self.suit = suit
        self.name = f"{index} of {suit}"
        self.is_face_down = False
        if self.index == "Ace":
            self.is_ace = True
            self.value = 11
        elif self.index in Card.FACE_CARDS:
            self.is_ace = False
            self.value = 10
        else:
            self.is_ace = False
            self.value = int(index)

    def flip_card(self) -> None:
        if self.is_face_down:
            self.is_face_down = False
            self.name = f"{self.index} of {self.suit}"
            if self.is_ace:
                self.value = 11
            elif self.index in Card.FACE_CARDS:
                self.is_ace = False
                self.value = 10
            else:
                self.value = 10
        else:
            self.is_face_down = True
            self.name = "Unknown"
            self.value = 0


class CardManager:

    def __init__(self):
        self.deck = self.create_deck()
        self.shuffle_deck()

    @staticmethod
    def create_deck() -> list:
        card_list = []
        for suit in Card.SUITS:
            for index in Card.INDICES:
                new_card = Card(index, suit)
                card_list.append(new_card)
        return card_list

    def shuffle_deck(self) -> None:
        n = len(self.deck)
        for _ in range(300):
            for i in range(n - 1, 0, -1):
                j = randint(0, i)
                self.deck[i], self.deck[j] = self.deck[j], self.deck[i]

    def deal_card(self, player: Player) -> None:
        dealt_card = self.deck.pop(0)
        player.hand.append(dealt_card)
        player.set_hand_value()

    def deal_hands(self, *players):
        print_sleep("Dealing hands...")
        for _ in range(2):
            for p in players:
                self.deal_card(p)
        for p in players:
            if p.name == "Dealer":
                p.hand[0].flip_card()
                p.set_hand_value()
            p.display_hand()


class BetManager:
    def __init__(self):
        self.pot_value = 0
        self.minimum_bet = 25

    def take_bets(self, player):
        bets_taken = False
        while not bets_taken:
            print_sleep("Place your bet\n")
            print_sleep(f"Minimum bet: ${self.minimum_bet}\n")
            print_sleep(f"You have ${player.money}")
            player_bet = input()
            if not player_bet.isdigit():
                print_sleep("Please enter a positive whole number")
                continue
            else:
                player_bet = int(player_bet)
                if player_bet < self.minimum_bet:
                    print_sleep("Please meet or exceed the minimum bet.")
                player.money -= player_bet
                self.pot_value += player_bet * 2
                print_sleep(f"You bet ${player_bet}")
                sleep(.5)
                print_sleep("The Dealer matches your bet")
                print_sleep(f"The pot is currently ${self.pot_value}")
                bets_taken = True


class Player:
    STARTING_CASH = 500
    HAND_SIZE = 2

    def __init__(self):
        self.name = "Player"
        self.money = Player.STARTING_CASH
        self.hand = []
        self.hand_value = 0
        self.is_bust = False

    def set_hand_value(self):
        hand_value = sum(card.value for card in self.hand)
        aces = [card for card in self.hand if card.is_ace]
        for ace in aces:
            if hand_value > 21:
                ace.value = 1
                hand_value -= 10
            else:
                break
        self.hand_value = hand_value

    def get_hand_value(self):
        return self.hand_value

    def display_hand(self):
        hand_value = self.get_hand_value()
        print_sleep("++++++++++++++++++++++++++++++")
        print_sleep(f"{self.name}'s Hand:")
        for i, card in enumerate(self.hand):
            if i == len(self.hand) - 1:
                print_sleep(card.name)
            else:
                print(card.name, end=", ")
        print_sleep(f"Hand value: {hand_value}.")
        print("++++++++++++++++++++++++++++++")

    def hit_loop(self, crd_mngr):
        while True:
            if self.hand_value > 21:
                print_sleep("You bust!")
                self.is_bust = True
                break
            else:
                print_sleep("Would you like to hit or stay? (h/s)")
                hit = input().strip().lower()
                if hit == "s":
                    break
                elif hit == "h":
                    crd_mngr.deal_card(self)
                    self.set_hand_value()
                    self.display_hand()
                    sleep(1)
                    continue
                else:
                    print("Please enter either 'h' or 's'!")

    def reset_hand(self, crd_mngr):
        while self.hand:
            returned_card = self.hand.pop()
            crd_mngr.deck.append(returned_card)


class Dealer(Player):

    def __init__(self):
        super().__init__()
        self.name = "Dealer"
        self.money = 9_999_999

    def hit_loop(self, crd_mngr: CardManager):
        self.hand[0].flip_card()
        self.set_hand_value()
        self.display_hand()
        dealer_done = False
        while not dealer_done:
            if self.hand_value > 21:
                print_sleep("Dealer busts")
                self.is_bust = True
                dealer_done = True
                continue
            elif self.hand_value > 16:
                print_sleep("Dealer stays")
                dealer_done = True
                continue
            else:
                print_sleep("Dealer hits")
                crd_mngr.deal_card(self)
                self.set_hand_value()
                self.display_hand()
                sleep(1)


class GameStateManager:
    def __init__(self):
        self.run = True
        self.players_done = False
        self.state = vars(self)

    def report_state(self):
        for k, v in vars(self).items():
            print_sleep(f"{k}: {v}")

    def update_state(self, last_action: str, state: bool):
        self.state[last_action] = state

    def reset_state(self):
        for k in self.state.keys():
            if k == "Run":
                self.state[k] = True
            else:
                self.state[k] = False


class GameManager:
    def __init__(self):
        self.crd_mngr = CardManager()

        self.bt_mngr = BetManager()

        self.players = []
        self.dealer = Dealer()
        self.d_hand = self.dealer.hand
        self.players.append(self.dealer)
        self.player = Player()
        self.p_hand = self.player.hand
        self.players.append(self.player)

        self.state_mngr = GameStateManager()
        self.state = self.state_mngr.state

    def end_check(self):
        if self.player.is_bust or (self.state_mngr.players_done and
                                   self.dealer.hand_value >
                                   self.player.hand_value):
            self.end_handler("Dealer Wins")
        elif self.dealer.is_bust or (self.state_mngr.players_done and
                                     self.player.hand_value >
                                     self.player.hand_value):
            self.end_handler("Player Wins")
        elif (self.state_mngr.players_done and
              self.player.hand_value
              == self.dealer.hand_value):
            self.end_handler("Push")
        else:
            self.end_handler(False)

    def end_handler(self, end_check):
        if not end_check:
            return False
        elif end_check == "Dealer Wins":
            print_sleep("You Lost!")
            print_sleep(f"Pot of ${self.bt_mngr.pot_value} emptied!")
            print_sleep("Ouch!")
            self.bt_mngr.pot_value = 0
            return True
        elif end_check == "Player Wins":
            self.player.money += self.bt_mngr.pot_value
            print_sleep("You Won!")
            print_sleep(f"Pot of ${self.bt_mngr.pot_value} emptied")
            print_sleep(f"You received ${self.bt_mngr.pot_value}!")
            self.bt_mngr.pot_value = 0
            return True
        elif end_check == "Push":
            self.player.money += self.bt_mngr.pot_value / 2
            print_sleep("Push!")
            print_sleep(f"Pot of ${self.bt_mngr.pot_value} emptied")
            print_sleep(f"Your bet of ${self.bt_mngr.pot_value / 2} was returned.")
            self.bt_mngr.pot_value = 0
            return True

    def reset(self):
        while True:
            print("Would you like to play another hand? (Y/N)")
            restart = input().strip().lower()
            if restart != "y" and restart != "n":
                print("Please enter either 'y' or 'n'")
                continue
            elif restart == "y":
                print_sleep("Resetting...")
                self.dealer.reset_hand(self.crd_mngr)
                self.player.reset_hand(self.crd_mngr)
                self.crd_mngr.shuffle_deck()
                return True
            elif restart == "n":
                print_sleep("Thanks for playing!")
                return False


def main():
    game = GameManager()
    while True:
        game.bt_mngr.take_bets(game.player)
        game.crd_mngr.deal_hands(game.dealer, game.player)
        game.player.hit_loop(game.crd_mngr)
        if not game.end_check():
            game.dealer.hit_loop(game.crd_mngr)
            game.state_mngr.players_done = True
        game.end_check()
        if game.reset():
            continue
        else:
            break


main()
