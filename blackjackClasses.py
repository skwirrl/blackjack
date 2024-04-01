from random import randint
from time import sleep


class Card:
    INDICES = ("Ace", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J",
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

    def flip_card(self):
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
    def create_deck():
        card_list = []
        for suit in Card.SUITS:
            for index in Card.INDICES:
                new_card = Card(index, suit)
                card_list.append(new_card)
        return card_list

    def shuffle_deck(self):
        n = len(self.deck)
        for _ in range(300):
            for i in range(n - 1, 0, -1):
                j = randint(0, i)
                self.deck[i], self.deck[j] = self.deck[j], self.deck[i]

    def deal_card(self, player):
        dealt_card = self.deck.pop(0)
        player.hand.append(dealt_card)
        player.set_hand_value()

    def deal_hands(self, *players):
        print("Dealing hands...")
        for _ in range(2):
            for p in players:
                self.deal_card(p)
        for p in players:
            if p == Dealer:
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
            print("Place your bet\n")
            sleep(.5)
            print(f"Minimum bet: {self.minimum_bet}\n")
            sleep(.5)
            print(f"You have ${player.money}")
            player_bet = input()
            if not player_bet.isdigit():
                print("Please enter a positive whole number")
                continue
            else:
                player_bet = int(player_bet)
                if player_bet < self.minimum_bet:
                    print("Please meet or exceed the minimum bet.")
                player.money -= player_bet
                self.pot_value += player_bet * 2
                print(f"You bet {player_bet}")
                sleep(.5)
                print("The Dealer matches your bet")
                print(f"The pot is currently ${self.pot_value}")
                bets_taken = True


class Player:
    STARTING_CASH = 500
    HAND_SIZE = 2

    def __init__(self):
        self.name = "Player"
        self.money = Player.STARTING_CASH
        self.hand = []
        self.hand_value = 0
        self.diff_from_blackjack = 21
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
        self.diff_from_blackjack = 21 - self.hand_value

    def get_hand_value(self):
        return self.hand_value

    def display_hand(self):
        hand_value = self.get_hand_value()
        print("++++++++++++++++++++++++++++++")
        for i, card in enumerate(self.hand):
            if i == len(self.hand) - 1:
                print(card.name)
            else:
                print(card.name, end=", ")
        print(f"Hand value: {hand_value}.")
        print("++++++++++++++++++++++++++++++")
        sleep(1)

    def hit_loop(self, crd_mngr):
        player_done = False
        while not player_done:
            if self.hand_value > 21:
                print("You bust!")
                self.is_bust = True
                player_done = True
            else:
                print("Would you like to hit or stay? (h/s)")
                hit = input().strip().lower()
                if hit != "h" and hit != "s":
                    print("Please enter either 'h' or 's'")
                    sleep(1)
                    continue
                elif hit == "h":
                    crd_mngr.deal_card(self)
                    self.set_hand_value()
                    self.display_hand()
                    sleep(1)
                    continue
                else:
                    player_done = True


class Dealer(Player):

    def __init__(self):
        super().__init__()
        self.name = "Dealer"
        self.money = 9_999_999

    def dealer_hit_loop(self, crd_mngr):
        self.hand[0].flip_card()
        self.set_hand_value()
        self.display_hand()
        dealer_done = False
        while not dealer_done:
            if self.hand_value > 21:
                print("Dealer busts")
                self.is_bust = True
                dealer_done = True
                continue
            elif self.hand_value > 16:
                print("Dealer stays")
                dealer_done = True
                continue
            else:
                print("Dealer hits")
                crd_mngr.deal_card(self)
                self.set_hand_value()
                self.display_hand()
                sleep(1)


class GameStateManager:
    def __init__(self):
        self.state = {
            "Run": True,
            "Player Bust": False,
            "Dealer Bust": False
        }


class GameManager:
    def __init__(self):
        crd_mngr = CardManager()
        self.deck = crd_mngr.deck

        bt_mngr = BetManager()
        self.pot = bt_mngr.pot_value

        player_list = []
        self.dealer = Dealer()
        self.d_hand = self.dealer.hand
        player_list.append(self.dealer)
        self.player = Player()
        self.p_hand = self.player.hand
        player_list.append(self.player)

        state_mngr = GameStateManager()
        self.state = state_mngr.state



