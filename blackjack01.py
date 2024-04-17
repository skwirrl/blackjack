from random import randint
from time import sleep
import sys


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

    def hit_loop(self, deck):
        while True:
            self.display_hand()
            if self.hand_value > 21:
                print("Bust!")
                self.is_bust = True
                break
            else:
                print(f"{self.name}, would you like to [h]it or [s]tand?")
                choice = input("").strip().lower()[0]
                if choice != "h" and choice != "s":
                    print("Please choose either [h] or [s]")
                    continue
                elif choice == "s":
                    print("You stand!")
                    break
                elif choice == "h":
                    print("You hit!")
                    deck.deal_card(self)
                    continue

    def place_bets(self):
        print(f"Minimum bet is ${Game.MINIMUM_BET}.")
        while True:
            bet = input(f"{self.name}, how much would you like to bet?")
            if not bet.isdigit():
                print(f"Please enter a number above {Game.MINIMUM_BET}")
                continue
            bet = int(bet)
            if bet < Game.MINIMUM_BET:
                print(f"Please enter a number above {Game.MINIMUM_BET}")
                continue
            self.pot += bet * 2
            self.money -= bet
            print("The Dealer matches your bet.")
            print(f"Your pot is worth ${self.pot}")
            print(f"You have ${self.money} remaining.")
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
                print("Dealer Busts")
                break
            elif self.hand_value > 16:
                print("Dealer Stands")
                break
            else:
                deck.deal_card(self)
                print("Dealer Hits")
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
        self.deck = Deck()
        self.bust_count = 0


    def initialize_players(self):
        while True:
            n_players = input("How many players? (1-4)")
            if not n_players.isdigit():
                print("Please enter a number")
                continue
            n_players = int(n_players)
            if not 1 <= n_players <= 4:
                print("Please choose between 1 and 4!")
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
            print("Dealer loses all hands in play!")
            for player in self.not_bust:
                if player.name == "Dealer":
                    continue
                print(f"Dealer pays out {player.pot} to {player.name}!")
                player.money += player.pot
                player.pot = 0
        else:
            print(f"{player.name} has lost a pot of ${player.pot}")
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
                    print(f"{player.name} beats the dealer!")
                    print(f"Dealer pays out ${player.pot}!")
                    player.money += player.pot
                    player.pot = 0
                case "Lose":
                    print(f"{player.name} loses to the dealer!")
                    print(f"The dealer takes the pot of ${player.pot}!")
                    player.pot = 0
                case "Push":
                    print("Push!")
                    print(f"{player.name}'s bet of ${player.pot / 2}"
                          "was returned.")
                    player.money += player.pot / 2

    def reset(self):
        self.not_bust.clear()
        for player in self.player_list:
            while player.hand:
                returned_card = player.hand.pop(0)
                self.deck.deck.append(returned_card)
            player.is_bust = False
            if not player.name == "Dealer":
                self.not_bust.append(player)
        self.deck.shuffle_deck()


def main():
    game = Game()
    game.initialize_players()
    while True:
        for p in game.not_bust:
            p.place_bets()
        game.deck.deal_hands(game.player_list)
        for p in game.player_list:
            if game.bust_count == len(game.player_list) - 1:
                print("All Players Busted!")
                break
            p.hit_loop(game.deck)
            if p.is_bust:
                game.player_busts(p)
                game.bust_count += 1
        game.end_check()
        while True:
            restart = input("Would you like to play again? (Y/N)\n")
            restart = restart.strip().lower()[0]
            if restart != "y" and restart != "n":
                print("Please choose either 'y' or 'n'!")
                continue
            break
        if restart == "y":
            game.reset()
            for i, v in vars(game).items():
                print(i, ":", v)
            continue
        else:
            print("Thanks for playing!")
            sys.exit()


if __name__ == "__main__":
    main()
