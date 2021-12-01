import math, copy, random

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
    
    #give out cards randomly to each player without replacement
    def deal(self,n):
        hand = []
        for i in range(n):
            picked = False
            while not picked:
                index = random.randint(0,len(self.cardNameList)-1)
                card = self.cardNameList[index]
                if  self.remainingPool[card] > 0:
                    hand.append(card)
                    self.remainingPool[card] -= 1
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
        self.initCards = copy.deepcopy(cards)
        self.cards = copy.deepcopy(cards)
        self.cardSeq = []
        self.chopsticksNotUsed = False
        #number of maki rolls & puddings
        self.makiRolls = 0
        self.puddings = 0

    #add cards to the hand
    def addCards(self,hand):
        self.hand = hand

    #choose one card from the hand
    def chooseCard(self,card):
        self.cards[card] += 1
        self.cardSeq.append(card)
        self.hand.pop(self.hand.index(card))
        #check if the chosen card is chopsticks
        self.checkChopsticks()

    #choose two cards from the hand for chopsticks
    def useChopsticks(self,card1,card2):
        self.chopsticksNotUsed = False
        self.cards[card1] += 1
        self.cards[card2] += 1
        self.cardSeq.append(card1)
        self.hand.pop(self.hand.index(card1))
        self.checkChopsticks()
        self.cardSeq.append(card2)
        self.hand.pop(self.hand.index(card2))
        self.checkChopsticks()   
        #put chopsticks back when used
        index = self.cardSeq.index('Chopsticks')
        self.cardSeq.pop(index)
        self.cards['Chopsticks'] -= 1
        self.hand.append('Chopsticks')     

    #choose one card randomly
    def choose1Randomly(self):
        if len(self.hand) > 1:
            index = random.randint(0,len(self.hand)-1)
        else:
            index = 0
        return self.hand[index]

    #choose two cards randomly
    def choose2Randomly(self):
        if len(self.hand) > 2:
            index1 = random.randint(0,len(self.hand)-1)
            card1 = self.hand[index1]
            self.hand.pop(index1)
            index2 = random.randint(0,len(self.hand)-1)
            card2 = self.hand[index2]
            self.hand.append(card1)
        else:
            card1 = self.hand[0]
            card2 = self.hand[1]
        return card1,card2

    #give the current hand to the next player
    def switchHand(self,app):
        newPlayerSerial = self.serial % app.numOfPlayers
        newPlayer = app.players[newPlayerSerial]
        return newPlayer.hand

    #check if the chose card is chopsticks
    def checkChopsticks(self):
        if (self.cardSeq[-1] == 'Chopsticks' and
            len(self.hand) >= 2):
            self.chopsticksNotUsed = True

    #check the number of maki rolls
    def checkMakiRolls(self):
        self.makiRolls += self.cards['1 Maki roll'] * 1
        self.makiRolls += self.cards['2 Maki roll'] * 2
        self.makiRolls += self.cards['3 Maki roll'] * 3

    #check the number of puddings
    def checkPuddings(self):
        self.puddings += self.cards['Pudding']

    #count the bonus of wasabi
    def countWasabiBonus(self):
        WasabiNotUsed = False
        for card in self.cardSeq:
            if card == 'Wasabi':
                WasabiNotUsed = True
            elif card.endswith('Nigiri') and WasabiNotUsed:
                if card == 'Salmon Nigiri':
                    self.score += 2 * 2
                elif card == 'Squid Nigiri':
                    self.score += 2 * 3
                elif card == 'Egg Nigiri':
                    self.score += 2 * 1
                WasabiNotUsed = False

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

    #generate 2 lists: contain the name of players who have 1st/2nd most maki rolls
    def countNumOfMakiRoll(self,app):
        max1, max2 = 0, 0
        listMax1, listMax2 = [], []
        for player in app.players:
            #if player has the most maki rolls, update all of listMax1
            if player.makiRolls > max1:
                #max1 --> max2
                max2 = max1
                listMax2 = copy.deepcopy(listMax1)
                listMax1.clear()
                listMax1.append(player)
                max1 = player.makiRolls
            #if tie, simply add to the name list
            elif player.makiRolls == max1:
                listMax1.append(player)
            #if > max2 & < max1, update all of listMax2
            elif player.makiRolls > max2 and player.makiRolls < max1:
                listMax2.clear()
                listMax2.append(player)
                max2 = player.makiRolls
            #if tie, simply add to the name list
            elif player.makiRolls == max2:
                listMax2.append(player)  
        return listMax1, listMax2, max1, max2

    #count the score of maki rolls --- most: 6; second: 3; split ties
    def countMakiRollScore(self,app):
        listMax1, listMax2, max1, max2 = self.countNumOfMakiRoll(app)
        #split the score when tie     
        for player in listMax1:
            player.score += 6 // len(listMax1)
        for player in listMax2:
            player.score += 3 // len(listMax2)

    #count the score of puddings
    def countPuddingScore(self,app):
        max, min = 0, 10
        listMax, listMin = [], []
        for player in app.players:
            #if player has the most puddings, update all of listMax
            if player.puddings > max:
                listMax.clear()
                listMax.append(player)
                max = player.puddings
            #if tie, simply add to the name list
            elif player.puddings == max:
                listMax.append(player)
            #if player has the least puddings, update all of listMin
            if player.puddings < min:
                listMin.clear()
                listMin.append(player)
                min = player.puddings
            #if tie, simply add to the name list
            elif player.puddings == min:
                listMin.append(player)   
        #split the score when tie         
        for player in listMax:
            player.score += 6 // len(listMax)
        for player in listMin:
            player.score -= 6 // len(listMin)        

    # count the scores for every player
    def countScoreAll(self,app):
        for player in app.players:
            player.countFinalScore()
            player.checkMakiRolls()
            player.checkPuddings()
        self.countMakiRollScore(app)

    def chooseAllRandom(self,app):
        for player in app.players:
            if player.chopsticksNotUsed:
                card1,card2 = player.choose2Randomly()
                player.useChopsticks(card1,card2)
            else:
                card = player.choose1Randomly()
                player.chooseCard(card)

    def chooseElseRandom(self,app):
        for player in app.players[1:]:
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
            print(f"Player {player.serial} has chosen: {player.cardSeq}")

    #print the finals after a round ends
    def printScores(self,app):
        for player in app.players:
            print(f"Player {player.serial}:", player.score)

    def printRank(self,app):
        rankList = self.rank(app)
        rank = 1
        for i in range(len(rankList)):
            print (rank, "place: Player", rankList[i].serial)
            if i > 0 and rankList[i].score == rankList[i-1].score:
                pass
            else:
                rank += 1

    #-------------------- initialize functions -------------------
    def initRound(self,app):
        app.waitingForChoosing = True
        for player in app.players:
            player.cardSeq = []
            player.cards = copy.deepcopy(player.initCards)
            player.chopsticksNotUsed = False
            player.hand = []
            player.makiRolls = 0
            #puddings are not initialized!!

    #--------------------- play functions ------------------------

    #play a round
    def playRound(self,app):
        self.dealAll(app)
        remainingTurns = app.numOfCardsInHand
        while (remainingTurns > 0):
            self.chooseAllRandom(app)
            self.switchAll(app)
            remainingTurns -= 1
        self.countScoreAll(app)
        #self.printCardsChosen(app)
        #self.printScores(app)

    def playGame(self,app):
        for round in range(app.rounds):
            self.playRound(app)
            self.initRound(app)
        self.countPuddingScore(app)
        #self.printScores(app)
        #self.printRank(app)
