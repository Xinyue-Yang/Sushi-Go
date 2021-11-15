from hashlib import new
from inspect import isgenerator
import math, copy, random
from functools import total_ordering

from cmu_112_graphics import *

#################################################
# Sushi GO!
#################################################

#---------------------- Card Pool ----------------------
class CardPool(object):
    def __init__(self):
        #create the original card pool
        cardPool = dict()
        cardPool['Tempura'] = 14
        cardPool['Sashimi'] = 14
        cardPool['Dumpling'] = 14
        cardPool['1 Maki roll'] = 6
        cardPool['2 Maki roll'] = 12
        cardPool['3 Maki roll'] = 8
        cardPool['Salmon Nigiri'] = 10
        cardPool['Squid Nigiri'] = 5
        cardPool['Egg Nigiri'] = 5
        cardPool['Pudding'] = 10
        cardPool['Wasabi'] = 6
        cardPool['Chopsticks'] = 4
        self.pool = cardPool
        #create a remaining card pool
        self.remainingPool = copy.deepcopy(cardPool)
        self.cardNameList = ['Tempura', 'Sashimi', 'Dumpling', '1 Maki roll',
        '2 Maki roll', '3 Maki roll', 'Salmon Nigiri', 'Egg Nigiri', 'Squid Nigiri',
        'Pudding', 'Wasabi', 'Chopsticks']
   
    #give out cards randomly to each player
    def deal(self,n):
        hand = []
        for i in range(n):
            picked = False
            while not picked:
                index = random.randint(0,len(self.cardNameList)-1)
                card = self.cardNameList[index]
                if  self.pool[card] > 0:
                    hand.append(card)
                    self.pool[card] -= 1
                    picked = True
        return hand


#---------------------- Player ----------------------
class Player(object):
    def __init__(self,serial):
        self.serial = serial
        self.score = 0
        self.cardNameList = ['Tempura', 'Sashimi', 'Dumpling', '1 Maki roll',
            '2 Maki roll', '3 Maki roll', 'Salmon Nigiri', 'Egg Nigiri', 
            'Squid Nigiri', 'Pudding', 'Wasabi', 'Chopsticks']
        cards = dict()
        cards['Tempura'] = 0
        cards['Sashimi'] = 0
        cards['Dumpling'] = 0
        cards['1 Maki roll'] = 0
        cards['2 Maki roll'] = 0
        cards['3 Maki roll'] = 0
        cards['Salmon Nigiri'] = 0
        cards['Squid Nigiri'] = 0
        cards['Egg Nigiri'] = 0
        cards['Pudding'] = 0
        cards['Wasabi'] = 0
        cards['Chopsticks'] = 0
        self.cards = cards
        self.cardSeq = []
        self.wasabiNotUsed = False
        self.chopsticksNotUsed = False

    #add cards to the hand
    def addCards(self,hand):
        self.hand = hand

    #choose one card from the hand
    def chooseCard(self,card):
        self.cards[card] += 1
        self.cardSeq.append(card)
        self.hand.pop(self.hand.index(card))
        #if card is chopsticks, update
        if card == 'Chopsticks':
            self.wasabiNotUsed = True

    #choose two cards from the hand for chopsticks
    def useChopsticks(self,card1,card2):
        self.cards[card1] += 1
        self.cards[card2] += 1
        self.cardSeq.append(card1)
        self.cardSeq.append(card2)
        self.hand.pop(self.hand.index(card1))
        self.hand.pop(self.hand.index(card2))   
        #put chopsticks back when used
        self.cards['Chopsticks'] -= 1
        self.hand.append('Chopsticks')     
        self.chopsticksNotUsed = False

    #choose one card randomly
    def choose1Randomly(self):
        picked = False
        while not picked:
            index = random.randint(0,len(self.cardNameList)-1)
            card = self.cardNameList[index]
            if  card in self.hand:
                picked = True
                return card

    #choose two cards randomly
    def choose2Randomly(self):
        card1,card2 = '',''
        picked = False
        while not picked:
            index = random.randint(0,len(self.cardNameList)-1)
            card1 = self.cardNameList[index]
            if card1 in self.hand:
                picked = True
        while not picked:
            index = random.randint(0,len(self.cardNameList)-1)
            card2 = self.cardNameList[index]
            if card2 in self.hand:
                #if two chosen cards are the same, # of cards in hand must >= 2
                if card2 == card1:
                    if self.hand[card1] >= 2:
                        picked = True
                else:
                    picked = True
        return card1,card2

    #give the current hand to the next player
    def switchHand(self,app):
        newPlayerSerial = self.serial % app.numOfPlayers
        newPlayer = app.players[newPlayerSerial]
        return newPlayer.hand

    #count the score of puddings
    def countPuddingScore(app):
        pass

    #count the bonus of wasabi
    def countWasabiBonus(self):
        WasabiNotUsed = False
        for card in self.cardSeq[-1:]:
            if card == 'Wasabi':
                WasabiNotUsed = True
            if card.endswith('Nigiri') and WasabiNotUsed:
                if card == 'Salmon Nigiri':
                    self.score += 2 * 2
                if card == 'Squid Nigiri':
                    self.score += 2 * 3
                if card == 'Egg Nigiri':
                    self.score += 2 * 1
                self.wasabiNotUsed = False

    #count final
    def countFinalScore(self):
        self.score += self.cards['Tempura'] // 2 * 5
        self.score += self.cards['Sashimi'] // 3 * 10
        dumpScore = {0:0, 1:1, 2:3, 3:6, 4:10, 5:15}
        self.score += dumpScore[self.cards['Dumpling']]
        self.score += self.cards['Salmon Nigiri'] * 2
        self.score += self.cards['Squid Nigiri'] * 3
        self.score += self.cards['Egg Nigiri'] * 1
        self.countWasabiBonus()
        #remain maki roll, pudding
        #wasabi not working, determine if chopstick

    #player1 < player2 calls player1.__lt__(player2)
    def __lt__(self, other):
        return self.score > other.score

    # player1 == player2 calls player1.__eq__(player2)
    def __eq__(self,other):
        return self.score == other.score

#---------------------- Game ----------------------
class Game(object):
    def __init__(self):
        self.gameOver = False

    #deal to each player
    def dealAll(self,app):
        for player in app.players:
            hand = app.cardPool.deal(app.numOfCardsInHand)
            player.addCards(hand)

    #switch all hands
    def switchAll(self,app):
        newHands = []
        for player in app.players:
            newHand = player.switchHand(app)
            newHands.append(newHand)
        for player in app.players:
            player.hand = newHands[player.serial - 1]

    #every player choose a card manually
    def chooseAll(self,app):
        for player in app.players:
            #if last chosen card is chopsticks, choose 2 this turn
            if player.chopsticksNotUsed:
                card1 = input(f"Please choose one card for player {player.serial}: ")
                card2 = input(f"Please choose another card for player {player.serial}: ")
                player.useChopsticks(card1,card2)
            #else, choose 1
            else:
                card = input(f"Please choose a card for player {player.serial}: ")
                player.chooseCard(card)

    #count the scores for every player
    def countScoreAll(self,app):
        for player in app.players:
            player.countFinalScore()

    def chooseAllRandom(self,app):
        for player in app.players:
            if player.chopsticksNotUsed:
                card1,card2 = player.choose2Randomly()
                player.useChopsticks(card1,card2)
            else:
                card = player.choose1Randomly()
                player.chooseCard(card)

    #rank players when the game finishes
    def rank(self,app):
        playerList = app.players
        return sorted(playerList)

    #------------------- print functions ----------------------

    #print the current cards in hand
    def printCardsToChoose(self,app):
        for player in app.players:
            print(f"Player {player.serial}:", player.hand)

    #print all chosen cards
    def printCardsChosen(self,app):
        for player in app.players:
            print(f"Player {player.serial} has chosen: {player.cards}")

    #print the finals after a round ends
    def printScores(self,app):
        for player in app.players:
            print(f"Player {player.serial}:", player.score)

    #play a round
    def playRound(self,app):
        self.dealAll(app)
        remainingTurns = app.numOfCardsInHand
        while (remainingTurns > 0):
            self.printCardsToChoose(app)
            self.chooseAll(app)
            self.switchAll(app)
            remainingTurns -= 1
        self.countScoreAll(app)
        self.printCardsChosen(app)
        self.printScores(app)

#################################################
# Setting
#################################################

def appStarted(app):
    app.game = Game()
    app.numOfPlayers = int(input("Please choose the number of players (2 ~ 5)"))
    #2 players-10 cards; 3 players-9 cards; 4 players-8 cards; 5 players-7 cards
    app.numOfCardsInHand = 12 - app.numOfPlayers
    app.cardPool = CardPool()
    app.players = initializePlayers(app.numOfPlayers)
    app.game.playRound(app)
    
#add players to the list
def initializePlayers(n):
    players = []
    for i in range(n):
        players.append(Player(i+1))
    return players

#start the app
def playSushiGO():
    runApp(width = 400, height = 600)

#################################################
# main
#################################################

def main():
    playSushiGO()

if __name__ == '__main__':
    main()
