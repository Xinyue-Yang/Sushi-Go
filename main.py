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
    
    #give out cards randomly to each player without replacement
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

    #count the score of maki rolls --- most: 6; second: 3; split ties
    def countMakiRollScore(self,app):
        max1, max2 = 0, 0
        listMax1, listMax2 = [], []
        for player in app.players:
            #if max1 = 0 and player'maki rolls > 0, update

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
            #self.printCardsToChoose(app)
            self.chooseAllRandom(app)
            self.switchAll(app)
            remainingTurns -= 1
        self.countScoreAll(app)
        self.printCardsChosen(app)
        self.printScores(app)

    def playGame(self,app):
        for round in range(app.rounds):
            self.playRound(app)
            self.initRound(app)
        self.countPuddingScore(app)
        self.printScores(app)
        self.printRank(app)

##########################################
# Splash Screen Mode
##########################################

def splashScreenMode_redrawAll(app, canvas):
    font = 'Courier 26 italic bold'
    canvas.create_text(app.width/2, 150, text='Welcome to Sushi GO!', font=font)
    canvas.create_text(app.width/2, 250, text='Press any key to start the game!', font=font)

def splashScreenMode_keyPressed(app, event):
    app.mode = 'gameMode'

#################################################
# Game Mode
#################################################

#get player number
def gameMode_getPlayers(app,n):
    app.numOfPlayers = int(n)
    #2 players-10 cards; 3 players-9 cards; 4 players-8 cards; 5 players-7 cards
    app.numOfCardsInHand = 12 - app.numOfPlayers
    app.players = initializePlayers(app.numOfPlayers)
    app.game.playGame(app)

def gameMode_keyPressed(app,event):
    if app.waitingForKeyPressed:
        if event.key >= '2' and event.key <= '5':
            app.validNumber = True
            app.waitingForKeyPressed = False
            gameMode_getPlayers(app,event.key)
        else:
            app.validNumber = False
            print("Invalid!")

        
def gameMode_timerFired(app):
    if not app.waitingForKeyPressed:
        pass


#------------------------- draw functions ---------------------------
def gameMode_drawRequest(app,canvas):
    font = 'Courier 26 italic bold'
    canvas.create_text(900/2, 700/2, text = "Please choose the number of players (2 ~ 5)",
        font = font)

def gameMode_drawInvalid(app,canvas):
    print("Invalid!")
    font = 'Courier 26 italic bold'
    canvas.create_text(900/2, 700/2, text = "Invalid number! (Please choose between 2 ~ 5)",
        font = font)

def gameMode_drawStart(app,canvas):
    font = 'Courier 26 italic bold'
    canvas.create_text(900/2, 700/2, text = "Start!",
        font = font) 

def gameMode_drawHand(app,canvas):
    pass   

#def drawHand(app,canvas):
    #for card in
    #canvas.create_image(200,300,image = ImageTk.PhotoImage(app.Sashimi))

def gameMode_redrawAll(app,canvas):
    if app.waitingForKeyPressed:
        if app.validNumber:
            gameMode_drawRequest(app,canvas)
        else:
            gameMode_drawInvalid(app,canvas)
    else:
        gameMode_drawStart(app,canvas)


#start the app
def gameMode_playSushiGO():
    runApp(width = 900, height = 700)


#################################################
# Setting
#################################################

def appStarted(app):
    app.mode = 'splashScreenMode'
    app.waitingForKeyPressed = True
    app.validNumber = True
    app.game = Game()
    #2 players-10 cards; 3 players-9 cards; 4 players-8 cards; 5 players-7 cards
    #app.numOfCardsInHand = 8 - app.numOfPlayers
    app.cardPool = CardPool()
    #app.players = initializePlayers(app.numOfPlayers)
    loadImage(app)
    #3 rounds in a game
    app.rounds = 3
    #app.game.playGame(app)
   
#load the images
def loadImage(app):
    app.makiroll1 = app.loadImage('1 Maki roll.jpg')
    app.Makiroll1 = app.scaleImage(app.makiroll1,1/20)
    app.makiroll2 = app.loadImage('2 Maki roll.jpg')
    app.Makiroll2 = app.scaleImage(app.makiroll2,1/15)
    app.Makiroll3 = app.loadImage('3 Maki roll.jpg')
    app.chopsticks = app.loadImage('Chopsticks.jpg')
    app.Chopsticks = app.scaleImage(app.chopsticks,1/15)
    app.Dumpling = app.loadImage('Dumpling.JPG')
    app.tempura = app.loadImage('Tempura.JPG')
    app.Tempura = app.scaleImage(app.tempura,1/15)
    app.Sashimi = app.loadImage('Sashimi.JPG')
    app.Pudding = app.loadImage('Pudding.JPG')
    app.EggNigiri = app.loadImage('Egg Nigiri.JPG')
    app.SalmonNigiri = app.loadImage('Salmon Nigiri.jpg')
    app.SquidNigiri = app.loadImage('Squid Nigiri.jpg')
    app.Wasabi = app.loadImage('Wasabi.JPG')

#add players to the list
def initializePlayers(n):
    players = []
    for i in range(n):
        players.append(Player(i+1))
    return players


#################################################
# main
#################################################

def main():
    gameMode_playSushiGO()

if __name__ == '__main__':
    main()
