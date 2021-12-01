#################################################
# Sushi GO!
#################################################
import math, copy, random
import environment as sushigo
from cmu_112_graphics import *

##########################################
# Splash Screen Mode
##########################################

def splashScreenMode_redrawAll(app, canvas):
    canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.background))
    font = 'Courier 26 italic bold'
    canvas.create_text(app.width/2, app.height - 50, text='Press any key to read the rules!', font=font)

def splashScreenMode_keyPressed(app, event):
    app.mode = 'helpScreenMode'

##########################################
# Help Screen Mode
##########################################

def splashScreenMode_drawPage0(app, canvas):
    font = 'Courier 26 italic bold'
    canvas.create_text(app.width/2, 350, text='Here are the instruction booklet!', font=font)
    canvas.create_text(app.width/2, 450, text='Press any key to turn the page!', font=font)

def splashScreenMode_drawPage5(app, canvas):
    font = 'Courier 26 italic bold'
    canvas.create_text(app.width/2, 350, text='Now you understand all the rules!', font=font)
    canvas.create_text(app.width/2, 450, text='Press any key to start the game!', font=font)

def helpScreenMode_redrawAll(app,canvas):
    if app.rulePage == 0:
        splashScreenMode_drawPage0(app, canvas)
    elif app.rulePage > 0 and app.rulePage < 5:
        canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.Rules[app.rulePage - 1]))
    else:
        splashScreenMode_drawPage5(app, canvas)

def helpScreenMode_keyPressed(app,event):
    app.rulePage += 1
    if app.rulePage > 5:
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

#reset the timing whenever a card is chosen
def gameMode_resetTiming(app):
    app.remainingTime = 10

#get the boundary of each card in hand
#every card is 123.5 * 190
def gameMode_getCellBound(app,i):
    width, height = 123.5, 190
    margin = width / 10
    x0 = width*i + margin * (i+1)
    y0 = app.height - 200
    x1 = x0 + width
    y1 = y0 + height
    return x0,y0,x1,y1     

#check if a card is chosen, return the card serial/None
def gameMode_chooseCard(app,x,y):
    hand = app.players[0].hand
    n = len(hand)
    #check if inside any card
    for i in range(n):
        x0,y0,x1,y1 = gameMode_getCellBound(app,i)
        if x >= x0 and x <= x1 and y >= y0 and y <= y1:
            return i
    return None

#if a combo can be achieved, choose combo first
def checkCombos(player):
    #if 1 Sashimi chosen, pick another one to pair up
    if player.cards['Sashimi'] % 3 > 0 and 'Sashimi' in player.hand:
        return 'Sashimi'
    #if 1 Tempura chosen, pick another one to pair up
    if player.cards['Tempura'] % 2 > 0 and 'Tempura' in player.hand:
        return 'Tempura'
    #if wasabi chosen, pick nigiri first (squid > salmon; don't choose egg)
    if len(player.cardSeq) == 0 or player.cardSeq[-1] == 'Wasabi':
        if 'Squid Nigiri' in player.hand:
            return 'Squid Nigiri'
        elif 'Salmon Nigiri' in player.hand:
            return 'Salmon Nigiri'
    return None

#Probability(# of same type of cards will be drawn this round)
def countProbability(app,card):
    #number of same type cards in the remaining card pool
    remainingCards = app.cardPool.remainingPool[card]
    #number of cards drawn in one round
    #number of cards in hand at first = 12 - # of players
    cardsPerRound = app.numOfPlayers * app.numOfCardsInHand
    #number of all remaining cards in the pool
    remainingAll = 108 - (3 - app.remainingRounds) * cardsPerRound
    prob = remainingCards / remainingAll * cardsPerRound
    return prob

#count the probability of getting a combo
#if probability > expectancy, return True; else, return False
def highYield(app,card):
    prob = countProbability(app,card)
    if card == 'Tempura' and prob > 2:
        return True
    if card == 'Sashimi' and prob > 3:
        return True
    #dumpScore = {0:0, 1:1, 2:3, 3:6, 4:10, 5:15}
    #>3 dumplings: >2 points/card, above average - pick
    #<=3 dumplings: <=2 points/card, below average - don't pick
    if card == 'Dumpling' and prob > 3:
        return True
    #if card is wasabi -- check remaining salmon nigiri/squid nigiri
    if card == 'Wasabi':
        probOfSquid = countProbability(app,'Squid Nigiri')
        probOfSalmon = countProbability(app,'Salmon Nigiri')
        if probOfSquid > 1 or probOfSalmon > 1:
            return True
    return False        

#check if it is the right time to choose maki rolls:
def checkMakiRolls(app,player):
    #find the most maki rolls card in hand
    maxMaki = 0
    if '3 Maki roll' in player.hand:
        maxMaki = 3
    elif '2 Maki roll' in player.hand:
        maxMaki = 2
    elif '1 Maki roll' in player.hand:
        maxMaki = 1
    #if no maki rolls in hand, return None
    if maxMaki == 0:
        return None
    listMax1, listMax2, max1, max2 = app.game.countNumOfMakiRoll(app)
    #already have 1st most maki rolls and don't need split - don't pick
    if player in listMax1 and len(listMax1) == 1:
        return None
    #add the current card and have 1st/2nd most maki rolls - pick
    elif player in listMax1 and len(listMax1) > 1:
        return str(maxMaki) + ' Maki roll'
    elif player in listMax2 and player.makiRolls + maxMaki >= max1:
        return str(maxMaki) + ' Maki roll'
    elif player not in listMax2 and player.makiRolls + maxMaki >= max2:
        return str(maxMaki) + ' Maki roll'    
    #add the current card and still not the 1st/2nd place - don't pick
    return None    

#choose 1 card using the probability
def choose1Wisely(app,player):
    if checkCombos(player) != None:
        return checkCombos(player)
    if checkMakiRolls(app,player) != None:
        return checkMakiRolls(app,player)
    else:
        #if 'gambling' has high yield, choose the card
        for card in player.hand:
            if card in ['Tempura', 'Sashimi', 'Dumpling', 'Wasabi']:
                if highYield(app,card):
                    return card
        #if none of them fits, choose randomly
        return player.choose1Randomly()

#using 2 cards using the probability
def choose2Wisely(player):
    #if 2 Tempura in hand, choose both
    if player.hand.count('Tempura') >= 2:
        return 'Tempura','Tempura'
    #if a Wasabi and a Salmon/Squid Nigiri in hand, choose both
    elif 'Wasabi' in player.hand and 'Squid Nigiri' in player.hand:
        return 'Wasabi','Squid Nigiri'
    elif 'Wasabi' in player.hand and 'Salmon Nigiri' in player.hand:
        return 'Wasabi','Salmon Nigiri'
    else:
        return player.choose2Randomly()

def chooseElseWisely(app):
    for player in app.players[1:]:
        if player.chopsticksNotUsed:
            card1,card2 = choose2Wisely(player)
            player.useChopsticks(card1,card2)
        else:
            card = choose1Wisely(app,player)
            player.chooseCard(card)

#choose a card randomly for the player when the remaining time = 0
def gameMode_chooseCardRandomly(app):
    card = app.players[0].choose1Randomly()
    app.players[0].chooseCard(card)
    gameMode_playTurn(app)
    gameMode_resetTiming(app)     

#play a turn
def gameMode_playTurn(app):
    chooseElseWisely(app)
    app.game.switchAll(app)
    app.waitingForChoosing = True

def gameMode_keyPressed(app,event):
    #waiting for key pressed (game not started) -- press key 2-5 for player number
    if app.waitingForKeyPressed:
        if event.key >= '2' and event.key <= '5':
            app.validNumber = True
            app.waitingForKeyPressed = False
            gameMode_getPlayers(app,event.key)
            app.game.initRound(app)
            app.game.dealAll(app)
        else:
            app.validNumber = False
    else:
        if app.gameOver:
            if event.key == 'Return':
                app.showRank = True
        #if current round ends, press enter to start a new round
        elif app.roundOver:
            if event.key == 'Return':
                app.roundOver = False
                gameMode_resetTiming(app)
                app.game.initRound(app)
                app.game.dealAll(app)

def gameMode_mousePressed(app,event):
    hand = app.players[0].hand
    #game started - press inside the card to choose it
    if app.waitingForChoosing:
        x,y = event.x,event.y
        i = gameMode_chooseCard(app,x,y)
        #if a card is chosen, play turn
        if i != None:
            app.players[0].chooseCard(hand[i])
            gameMode_playTurn(app)
            gameMode_resetTiming(app) 

def gameMode_timerFired(app):
    #if not started, return
    if app.waitingForKeyPressed or app.gameOver: return
    #if the round ends, initialize a new round
    if app.remainingRounds > 0: 
        #if the round ends, init a new one or game over
        if not app.roundOver and len(app.players[0].hand) == 0: 
            app.game.countScoreAll(app)
            app.roundOver = True
            app.remainingRounds -= 1
        else:
            #while waiting for choosing, time - 1
            app.remainingTime -= 1
            #if remaining time = 0, choose card randomly
            if app.remainingTime == 0:
                gameMode_chooseCardRandomly(app)
    else:
        #game over, count pudding scores
        app.game.countPuddingScore(app)
        app.gameOver = True


#------------------------- draw functions ---------------------------
def gameMode_drawRequest(app,canvas):
    font = 'Courier 26 italic bold'
    canvas.create_text(app.width/2, app.height/2,  
        text = "Please choose the number of players (2 ~ 5)", font = font)

def gameMode_drawInvalid(app,canvas):
    font = 'Courier 26 italic bold'
    canvas.create_text(app.width/2, app.height/2, 
        text = "Invalid number! (Please choose between 2 ~ 5)", font = font)

def gameMode_drawStart(app,canvas):
    font = 'Courier 26 italic bold'
    canvas.create_text(app.width/2, app.height/2, text = "Start!", font = font) 

def gameMode_drawGameOver(app,canvas):
    font = 'Courier 26 italic bold'
    canvas.create_text(app.width/2, app.height/2 +200, text = "Game Over!", font = font) 
    canvas.create_text(app.width/2, app.height/2 + 250, text = "Press enter to see your rank!", 
        font = font) 

def gameMode_drawWallPaper(app,canvas):
    canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.wallPaper))    

def gameMode_drawDecoration(app,canvas):
    canvas.create_image(app.width/4*3, app.height/4*3, image=ImageTk.PhotoImage(app.decoration))

def gameMode_drawRank(app,canvas):
    font = 'Courier 26 italic bold'
    w = app.width / 2
    h = app.height/3
    rankList = app.game.rank(app)
    rank = 1
    for i in range(len(rankList)):
        if rankList[i].serial == 1:
            canvas.create_text(w, h + 50 * i, text = f"{rank} place: You", 
                font = font) 
        else:
            canvas.create_text(w, h + 50 * i, text = f"{rank} place: Player {rankList[i].serial}", 
                font = font) 
        if i > 0 and rankList[i].score == rankList[i-1].score:
            pass
        else:
            rank += 1
    canvas.create_text(app.width/2, app.height/2 + 250, text = "Goodbye :)", font = font) 

def gameMode_drawRemainingTime(app,canvas):
    font = 'Courier 26 italic bold'
    canvas.create_text(app.width-200,50,text = f"Remainging Time: {app.remainingTime}",
        font = font)

#text version
def gameMode_drawHand1(app,canvas):
    hand = app.players[0].hand
    n = len(hand)
    font = 'Courier 16 italic bold'
    for i in range(n):
        x0,y0,x1,y1 = gameMode_getCellBound(app,i)
        canvas.create_rectangle(x0,y0,x1,y1,width = 2)
        canvas.create_text((x0+x1)/2,(y0+y1)/2,font = font, text = hand[i])

#picture version
def gameMode_drawHand2(app,canvas):
    hand = app.players[0].hand
    n = len(hand)
    for i in range(n):
        x0,y0,x1,y1 = gameMode_getCellBound(app,i)
        canvas.create_image((x0+x1)/2, (y0+y1)/2, image=ImageTk.PhotoImage(app.cardImg[hand[i]]))
        
#text version
def gameMode_drawChosen1(app,canvas):
    height = app.height / 3 * 2
    cards = app.players[0].cardSeq
    canvas.create_text(50,height,text = f"your cards: {str(cards)}",anchor = 'nw')

#picture version
def gameMode_drawChosen2(app,canvas):
    font = 'Courier 22 italic bold'
    width = 20
    height = app.height / 3 * 2
    cards = app.players[0].cardSeq
    canvas.create_text(width,height,text = "your cards: ",anchor = 'nw', font = font)
    for i in range(len(cards)):
        img = app.scaleImage(app.cardImg[cards[i]],1/3)
        canvas.create_image(70*(i+3), height, image=ImageTk.PhotoImage(img))        

#text version
def gameMode_drawComponents1(app,canvas):
    h = 150
    for player in app.players[1:]:
        h += 50
        canvas.create_text(50,h,text = f"Player {player.serial}'s cards: {str(player.cardSeq)}",
            anchor = 'nw')

#picture version
def gameMode_drawComponents2(app,canvas):
    font = 'Courier 22 italic bold'
    h = 120
    for player in app.players[1:]:
        h += 80
        canvas.create_text(20,h,text = f"Player {player.serial}'s cards: ",
            anchor = 'nw', font = font)
        cards = player.cardSeq
        for i in range(len(cards)):
            img = app.scaleImage(app.cardImg[cards[i]],1/3)
            canvas.create_image(70*(i+4), h, image=ImageTk.PhotoImage(img))  

#draw instructions on the top of the screen
def gameMode_drawMenu(app,canvas):
    canvas.create_image(app.width/3, 70, image=ImageTk.PhotoImage(app.menu))

def gameMode_drawScore(app,canvas):
    font = 'Courier 26 italic bold'
    w = app.width / 2
    h = app.height/3
    canvas.create_text(w, h , text = f"Score for round {3 - app.remainingRounds}", font = font)  
    for player in app.players:
        i = player.serial
        if i == 1:
            canvas.create_text(w, h + 50 * i, text = f"You: {player.score}", font = font) 
        else:
            canvas.create_text(w, h + 50 * i, text = f"Player {i}: {player.score}", font = font) 

def gameMode_drawNextRound(app,canvas):
    font = 'Courier 26 italic bold'
    canvas.create_text(app.width/2, app.height/2 +200, text = "Press enter to start next round!", 
        font = font) 
   

def gameMode_redrawAll(app,canvas):
    #if not started, waiting for user to enter number of players
    if app.waitingForKeyPressed:
        if app.validNumber:
            gameMode_drawRequest(app,canvas)
        else:
            gameMode_drawInvalid(app,canvas)
    #if the game ends and the user wants to see the rank
    elif app.showRank:
        gameMode_drawWallPaper(app,canvas)
        gameMode_drawRank(app,canvas)
        #gameMode_drawDecoration(app,canvas)
    else:
        gameMode_drawWallPaper(app,canvas)
        #draw scores after every round
        if app.roundOver:
            gameMode_drawScore(app,canvas)
            #the hint at the bottom change (next round/game over)
            if app.gameOver:
                gameMode_drawGameOver(app,canvas)
            else:
                gameMode_drawNextRound(app,canvas)
        #while the game is on, draw cards in hand and chosen cards
        else:
            gameMode_drawMenu(app,canvas)
            gameMode_drawHand2(app,canvas)
            gameMode_drawChosen2(app,canvas)
            gameMode_drawComponents2(app,canvas)
            gameMode_drawRemainingTime(app,canvas)


#start the app
def gameMode_playSushiGO():
    runApp(width = 1440, height = 778)


#################################################
# Setting
#################################################


def appStarted(app):
    app.width = 1440
    app.height = 778
    app.timerDelay = 1000
    loadImage(app)
    loadBackground(app)
    app.Rules = loadRules(app)
    app.mode = 'splashScreenMode'
    app.waitingForKeyPressed = True
    app.waitingForChoosing = True
    app.validNumber = True
    app.game = sushigo.Game()
    app.roundOver = False
    app.gameOver = False
    app.showRank = False
    #2 players-10 cards; 3 players-9 cards; 4 players-8 cards; 5 players-7 cards
    #app.numOfCardsInHand = 8 - app.numOfPlayers
    app.cardPool = sushigo.CardPool()
    #3 rounds in a game
    app.rounds = 3
    app.remainingRounds = 3
    #0-enter to next page; 1~4-rules; 5-enter to start game
    app.rulePage = 0
    #every turn has at most 10 seconds
    app.remainingTime = 10
    #findAveScore(app)

#copyright of images belongs to Gamewright
#https://gamewright.com/pdfs/Rules/SushiGoTM-RULES.pdf
def loadRules(app):
    Rule1 = app.loadImage('Rule1.JPEG')
    rule1 = app.scaleImage(Rule1,1/2)
    Rule2 = app.loadImage('Rule2.JPEG')
    rule2 = app.scaleImage(Rule2,1/2)
    Rule3 = app.loadImage('Rule3.JPEG')
    rule3 = app.scaleImage(Rule3,1/2)
    Rule4 = app.loadImage('Rule4.JPEG')
    rule4 = app.scaleImage(Rule4,1/2)
    Rules = [rule1,rule2,rule3,rule4]
    return Rules

#snapshot from youtube video https://www.youtube.com/watch?v=OfRgPA1M5Y0
def loadBackground(app):
    app.wallPaper = app.loadImage('Wall2.jpeg')
    Background = app.loadImage('background.jpg')
    app.background = app.scaleImage(Background,1/2)
    app.decoration = app.loadImage('Decoration.jpeg')
    Menu = app.loadImage('Menu.jpg')
    app.menu = app.scaleImage(Menu,1/4)

#copyright of images belongs to Gamewright
#https://gamewright.com/pdfs/Rules/SushiGoTM-RULES.pdf
def loadImage(app):
    #put all the images into a dictionary
    app.cardImg = dict()
    makiroll1 = app.loadImage('1 Maki roll.jpg')
    app.cardImg['1 Maki roll'] = app.scaleImage(makiroll1,1/8)
    makiroll2 = app.loadImage('2 Maki roll.JPG')
    app.cardImg['2 Maki roll'] = app.scaleImage(makiroll2,1/8)
    makiroll3 = app.loadImage('3 Maki roll.JPG')
    app.cardImg['3 Maki roll'] = app.scaleImage(makiroll3,1/8)
    chopsticks = app.loadImage('Chopsticks.png')
    app.cardImg['Chopsticks'] = app.scaleImage(chopsticks,1/8)
    dumpling = app.loadImage('Dumpling.png')
    app.cardImg['Dumpling'] = app.scaleImage(dumpling,1/8)
    tempura = app.loadImage('Tempura.png')
    app.cardImg['Tempura'] = app.scaleImage(tempura,1/8)
    sashimi = app.loadImage('Sashimi.png')
    app.cardImg['Sashimi'] = app.scaleImage(sashimi,1/8)
    pudding = app.loadImage('Pudding.png')
    app.cardImg['Pudding'] = app.scaleImage(pudding,1/8)
    eggNigiri = app.loadImage('Egg Nigiri.jpeg')
    app.cardImg['Egg Nigiri'] = app.scaleImage(eggNigiri,1/8)
    salmonNigiri = app.loadImage('Salmon Nigiri.png')
    app.cardImg['Salmon Nigiri'] = app.scaleImage(salmonNigiri,1/8)
    squidNigiri = app.loadImage('Squid Nigiri.jpeg')
    app.cardImg['Squid Nigiri'] = app.scaleImage(squidNigiri,1/8)
    wasabi = app.loadImage('Wasabi.png')
    app.cardImg['Wasabi'] = app.scaleImage(wasabi,1/8)

#add players to the list
def initializePlayers(n):
    players = []
    for i in range(n):
        players.append(sushigo.Player(i+1))
    return players

#initialize game
def initializeGame(app):
    app.mode = 'splashScreenMode'
    app.waitingForKeyPressed = True
    app.waitingForChoosing = True
    app.validNumber = True
    app.game = sushigo.Game()
    app.gameOver = False
    #2 players-10 cards; 3 players-9 cards; 4 players-8 cards; 5 players-7 cards
    #app.numOfCardsInHand = 8 - app.numOfPlayers
    app.cardPool.remainingPool = app.cardPool.pool
    #3 rounds in a game
    app.remainingRounds = 3

#################################################
# main
#################################################

def main():
    gameMode_playSushiGO()

if __name__ == '__main__':
    main()
