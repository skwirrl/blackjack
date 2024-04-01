import random
from time import sleep


class Card:
    INDICES = ("Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
    SUITS = ("Clubs", "Hearts", "Spades", "Diamonds")
    FACE_CARDS = ("K", "Q", "J")

    def __init__(self, face: str, suit: str, is_ace: bool, is_face_down: bool = False):
        self.face = face
        self.suit = suit
        self.is_ace = is_ace
        self.is_face_down = is_face_down
        self.name = f"{face} of {suit}"
        if self.is_ace:
            self.value = 11
        elif self.face in Card.FACE_CARDS:
            self.value = 10
        else:
            self.value = int(face)

    def flip_card(self):
        if self.is_face_down:
            self.is_face_down = False
            self.name = f"{self.face} of {self.suit}"
            if self.is_ace:
                self.value = 11
            elif self.face in Card.FACE_CARDS:
                self.value = 10
            else:
                self.value = int(self.face)
        else:
            self.is_face_down = True
            self.name = "Unknown"
            self.value = 0


class Player:
    STARTING_CASH = 500
    HAND_SIZE = 2

    def __init__(self):
        self.name = "Player"
        self.money = Player.STARTING_CASH
        self.hand = []
        self.hand_value = 0
        self.set_hand_value()
        self.diff_from_blackjack = 21
        self.bust = False

    def set_hand_value(self):
        card_values = []
        for card in self.hand:
            card_values.append(card.value)
        hand_value = sum(card_values)
        for card in self.hand:
            if hand_value > 21 and card.is_ace:
                card.value = 1
                card_values[self.hand.index(card)] = card.value
                hand_value = sum(card_values)
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


class Dealer(Player):
    def __init__(self):
        super().__init__()
        self.name = "Dealer"
        self.money = 9_999_999


class Game:
    MINIMUM_BET = 25

    def __init__(self):
        self.dealer = Dealer()
        self.d_hand = self.dealer.hand
        self.player = Player()
        self.p_hand = self.player.hand
        self.player_list = [self.dealer, self.player]
        self.deck = self.create_deck()
        self.shuffle_deck()
        self.pot_value = 0
        self.run = True
        self.bets_taken = False
        self.hands_dealt = False
        self.player_done = False
        self.dealer_done = False
        self.round_complete = False
        print("Game Started!\n")

    @staticmethod
    def create_deck():
        card_list = []
        for suit in Card.SUITS:
            for face in Card.INDICES:
                if face == "Ace":
                    new_card = Card(face, suit, True)
                else:
                    new_card = Card(face, suit, False)
                card_list.append(new_card)
        return card_list

    def shuffle_deck(self):
        n = len(self.deck)
        for _ in range(300):
            for i in range(n - 1, 0, -1):
                j = random.randint(0, i)
                self.deck[i], self.deck[j] = self.deck[j], self.deck[i]

    def deal_card(self, player):
        dealt_card = self.deck.pop(0)
        player.hand.append(dealt_card)
        player.set_hand_value()

    def take_bets(self):
        while not self.bets_taken:
            print("Place your bet!\n")
            sleep(.5)
            print(f"Minimum Bet: {Game.MINIMUM_BET}\n")
            sleep(.5)
            print(f"You have ${self.player.money}\n")
            player_bet = input("")
            if player_bet.isdigit():
                player_bet = int(player_bet)
                if player_bet < Game.MINIMUM_BET:
                    print("\nPlease match or exceed the minimum bet.\n")
                    continue
                if player_bet > self.player.money:
                    print("\nYou cannot bet more than you have.\n")
                    continue
                self.player.money -= player_bet
                self.pot_value = player_bet * 2
                print(f"\nYour bet is: ${player_bet}\n")
                sleep(.5)
                print("The dealer matches your bet.\n")
                sleep(.5)
                print(f"The pot is at ${self.pot_value}\n")
                sleep(.5)
                print(f"You have ${self.player.money} remaining.\n")
                self.bets_taken = True
            else:
                print("\nPlease enter a number.\n")

    def deal_hands(self):
        print("Dealing hands...\n")
        sleep(1)
        for _ in range(2):
            for p in self.player_list:
                self.deal_card(p)
        self.dealer.hand[0].flip_card()
        for p in self.player_list:
            p.set_hand_value()
            p.display_hand()

    def player_hit_loop(self):
        while not self.player_done:
            print("Hit or stay? (h/s)")
            hit = input("").strip().lower()
            if hit != "h" and hit != "s":
                print("Please enter either 'h' or 's'")
                continue
            if hit == "s":
                self.player_done = True
                continue
            if hit == "h":
                self.deal_card(self.player)
                self.player.set_hand_value()
                self.player.display_hand()
            if self.player.hand_value > 21:
                print("Oh no! You busted!")
                self.player.bust = True
                self.player_done = True

    def dealer_hit_loop(self):
        self.dealer.hand[0].flip_card()
        self.dealer.set_hand_value()
        self.dealer.display_hand()
        while not self.dealer_done:
            if self.dealer.hand_value > 21:
                print("Dealer Busts")
                self.dealer.bust = True
                self.dealer_done = True
            elif self.dealer.hand_value > 16:
                print("Dealer Stays")
                self.dealer.set_hand_value()
                self.dealer_done = True
            else:
                self.deal_card(self.dealer)
                self.dealer.set_hand_value()
                self.dealer.display_hand()
            sleep(1)

    def round_end_check(self):
        if self.player.bust:
            self.dealer_done = True
            print(f"Pot was ${self.pot_value}!")
            print(f"You lost ${self.pot_value / 2}!")
            self.pot_value = 0
            print("Pot emptied!")
            self.round_complete = True
            return True
        elif self.dealer.bust:
            print(f"Pot was ${self.pot_value}!")
            print(f"You won the pot!")
            self.player.money += self.pot_value
            self.pot_value = 0
            print(f"You have ${self.player.money}")
            self.round_complete = True
            return True
        elif self.dealer_done and self.player_done:
            if self.player.diff_from_blackjack == self.dealer.diff_from_blackjack:
                print("Push!")
                print(f"Pot was ${self.pot_value}")
                self.player.money += self.pot_value / 2
                print(f"Your bet of ${self.pot_value / 2} was returned!")
                print(f"You have ${self.player.money}")
                return True
            elif self.player.diff_from_blackjack < self.dealer.diff_from_blackjack:
                print(f"Pot was ${self.pot_value}!")
                print(f"You won the pot!")
                self.player.money += self.pot_value
                self.pot_value = 0
                print(f"You have ${self.player.money}")
                self.round_complete = True
                return True
            else:
                print(f"Pot was ${self.pot_value}!")
                print(f"You lost ${self.pot_value / 2}!")
                self.pot_value = 0
                print("Pot emptied!")
                self.round_complete = True
                return True

    def reset(self):
        print("Would you like to play another hand? (y/n)")
        while True:
            restart = input().strip().lower()
            if restart != "y" and restart != "n":
                print("Please enter either 'y' or 'n'!")
            elif restart == "n":
                print("Thanks for playing!")
                self.run = False
                break
            else:
                print("Resetting!")
                for p in self.player_list:
                    while p.hand:
                        returned_card = p.hand.pop()
                        self.deck.append(returned_card)
                self.shuffle_deck()
                self.run = True
                self.bets_taken = False
                self.hands_dealt = False
                self.player_done = False
                self.dealer_done = False
                self.round_complete = False
                break


# test
game = Game()
while game.run:
    game.take_bets()
    game.deal_hands()
    game.player_hit_loop()
    end = game.round_end_check()
    if end:
        game.reset()
        continue
    game.dealer_hit_loop()
    game.round_end_check()
    game.reset()

