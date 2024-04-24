from random import randint
import sys
from blackjackFunctions import *


class Card:
    INDICES = ("Ace", 2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King")
    SUITS = ("Clubs", "Hearts", "Spades", "Diamonds")
    FACE_CARDS = ("Jack", "Queen", "King")

    def __init__(self, index, suit):
        self.index = index
        self.suit = suit
        self.is_ace = False
        self.is_face_up = True
        self.value = self.set_value()
        self.name = self.__str__()

    def __str__(self):
        return f"{self.index} of {self.suit}"

    def set_value(self) -> int:
        if self.index == "Ace":
            self.is_ace = True
            value = 11
        elif self.index in Card.FACE_CARDS:
            value = 10
        else:
            value = self.index
        return value

    def flip_card(self) -> None:
        if self.is_face_up:
            self.is_face_up = False
            self.name = "Unknown"
            self.value = 0
        else:
            self.is_face_up = True
            self.name = self.__str__()
            self.value = self.set_value()


class Player:
    STARTING_CASH = 500

    def __init__(self, name):
        self.name = name
        self.money = Player.STARTING_CASH
        self.pot = 0
        self.hand = []
        self.hand_value = 0
        self.is_bust = False
        self.blackjack_margin = 21

    def __str__(self):
        return self.name

    def set_hand_value(self) -> None:
        value = sum([card.value for card in self.hand])
        if value <= 21:
            self.hand_value = value
        else:
            aces = [card for card in self.hand if card.is_ace]
            for ace in aces:
                if value > 21:
                    ace.value = 1
                    value = sum([card.value for card in self.hand])
                else:
                    break
        self.blackjack_margin = 21 - value
        self.hand_value = value

    def get_hand_value(self):
        return self.hand_value

    def display_hand(self):
        hand_value = self.get_hand_value()
        print("++++++++++++++++++++++++++++++")
        print(f"{self.name}'s Hand:")
        for i, card in enumerate(self.hand):
            if i == len(self.hand) - 1:
                print(card.name)
            else:
                print(card.name, end=", ")
        print(f"Hand value: {hand_value}.")
        print("++++++++++++++++++++++++++++++")
        sleep(.5)

    def hit_loop(self, deck):
        while True:
            self.display_hand()
            if self.hand_value > 21:
                custom_print("Bust!")
                self.is_bust = True
                break
            else:
                custom_print(
                    f"{self.name}, would you like to [h]it or [s]tand?")
                choice = input("").strip().lower()[0]
                if choice != "h" and choice != "s":
                    custom_print("Please choose either [h] or [s]")
                    continue
                elif choice == "s":
                    custom_print("You stand!")
                    break
                elif choice == "h":
                    custom_print("You hit!")
                    deck.deal_card(self)
                    continue

    def place_bets(self):
        custom_print("=====================")
        custom_print(f"Minimum bet is ${Game.MINIMUM_BET}.")
        custom_print("=====================")
        while True:
            custom_print(f"{self.name}, you have ${self.money}")
            bet = input("How much would you like to bet?")
            if not bet.isdigit():
                custom_print(f"Please enter a number above {Game.MINIMUM_BET}")
                continue
            bet = int(bet)
            if bet < Game.MINIMUM_BET:
                custom_print(f"Please enter a number above {Game.MINIMUM_BET}")
                continue
            elif bet > self.money:
                custom_print("You cannot bet more than you have.")
                continue
            self.pot += bet * 2
            self.money -= bet
            custom_print("The Dealer matches your bet.")
            custom_print(f"Your pot is worth ${self.pot}")
            custom_print(f"You have ${self.money} remaining.")
            break


class Dealer(Player):
    def __init__(self):
        super().__init__(self)
        self.name = "Dealer"

    def hit_loop(self, deck):
        while True:
            self.display_hand()
            if self.hand_value > 21:
                self.is_bust = True
                custom_print("Dealer Busts")
                sleep(.5)
                break
            elif self.hand_value > 16:
                custom_print("Dealer Stands")
                sleep(.5)
                break
            else:
                deck.deal_card(self)
                custom_print("Dealer Hits")
                sleep(.5)
                continue

    def place_bets(self):
        ...


class Deck:
    def __init__(self):
        self.deck = self.create_deck()

    @staticmethod
    def create_deck() -> list:
        deck_list = []
        for suit in Card.SUITS:
            for index in Card.INDICES:
                new_card = Card(index, suit)
                deck_list.append(new_card)
        return deck_list

    def shuffle_deck(self) -> None:
        n = len(self.deck)
        for _ in range(300):
            for i in range(n - 1, 0, -1):
                j = randint(0, i)
                self.deck[i], self.deck[j] = self.deck[j], self.deck[i]

    def deal_card(self, player) -> None:
        dealt_card = self.deck.pop(0)
        player.hand.append(dealt_card)
        player.set_hand_value()

    def deal_hands(self, players: list) -> None:
        for _ in range(2):
            for player in players:
                self.deal_card(player)
        for player in players:
            if player.name == "Dealer":
                player.hand[0].flip_card()
                player.set_hand_value()
            player.display_hand()


class Game:
    MINIMUM_BET = 50

    def __init__(self):
        self.dealer = Dealer()
        self.player_list = []
        self.not_bust = []
        self.end_early = False
        self.deck = Deck()
        self.bust_count = 0

    def initialize_players(self):
        while True:
            n_players = input("How many players? (1-4)")
            if not n_players.isdigit():
                custom_print("Please enter a number")
                continue
            n_players = int(n_players)
            if not 1 <= n_players <= 4:
                custom_print("Please choose between 1 and 4!")
                continue
            for _ in range(n_players):
                name = input("Please enter a name: ")
                new_player = Player(name)
                self.player_list.append(new_player)
                self.not_bust.append(new_player)
            self.player_list.append(self.dealer)
            break

    def player_busts(self, player):
        if player.name == "Dealer":
            custom_print("Dealer loses all hands in play!")
            for player in self.not_bust:
                if player.name == "Dealer":
                    continue
                custom_print(f"Dealer pays out {player.pot} to {player.name}!")
                player.money += player.pot
                player.pot = 0
        else:
            custom_print(f"{player.name} has lost a pot of ${player.pot}")
            player.pot = 0
            self.not_bust.remove(player)

    def result_check(self, player):
        if player.blackjack_margin < self.dealer.blackjack_margin:
            result = "Win"
        elif player.blackjack_margin > self.dealer.blackjack_margin:
            result = "Lose"
        else:
            result = "Push"
        return result

    def end_check(self):
        for player in self.not_bust:
            match self.result_check(player):
                case "Win":
                    custom_print(f"{player.name} beats the dealer!")
                    custom_print(f"Dealer pays out ${player.pot}!")
                    player.money += player.pot
                    player.pot = 0
                case "Lose":
                    custom_print(f"{player.name} loses to the dealer!")
                    custom_print(f"The dealer takes the pot of ${player.pot}!")
                    player.pot = 0
                case "Push":
                    custom_print("Push!")
                    custom_print(
                        f"{player.name}'s bet of ${int(player.pot / 2)}"
                        " was returned.")
                    player.money += player.pot / 2
                    player.pot = 0

    def reset(self):
        self.not_bust.clear()
        self.bust_count = 0
        self.end_early = False
        for player in self.player_list:
            while player.hand:
                returned_card = player.hand.pop(0)
                self.deck.deck.append(returned_card)
            player.is_bust = False
            if not player.name == "Dealer":
                self.not_bust.append(player)
        self.deck.shuffle_deck()

    @staticmethod
    def restart_check():
        while True:
            restart = input("Would you like to play another hand? (Y/N)\n")
            restart = restart.strip().lower()[0]
            if restart != "y" and restart != "n":
                custom_print("Please choose either 'y' or 'n'!")
                continue
            if restart == "n":
                return False
            else:
                return True


def main():
    game = Game()
    game.initialize_players()
    while True:
        for p in game.not_bust:
            if p.money < game.MINIMUM_BET:
                clear_screen()
                custom_print("You are out of money!")
                custom_print("Better luck next time.")
                game.player_list.remove(p)
                game.not_bust.remove(p)
                clear_screen()
                if not game.not_bust:
                    custom_print("Thanks for playing!")
                    sys.exit()
                continue
            p.place_bets()
        game.deck.deal_hands(game.player_list)
        clear_screen()
        for p in game.player_list:
            if game.bust_count == len(game.player_list) - 1:
                custom_print("All Players Busted!")
                game.end_early = True
                break
            p.hit_loop(game.deck)
            clear_screen()
            if p.is_bust:
                game.player_busts(p)
                game.bust_count += 1
                if p.name == "Dealer":
                    game.end_early = True
        if game.end_early:
            if game.restart_check():
                game.reset()
                continue
            else:
                custom_print("Thanks for playing!")
                sys.exit()
        game.end_check()
        if game.restart_check():
            game.reset()
            continue


if __name__ == "__main__":
    main()
