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

#get the boundary of each card in hand
def gameMode_getCellBound(app,i):
    hand = app.players[0].hand
    n = len(hand)
    width = app.width / (1.6 * n)
    margin = width / 2
    height = app.height / 7
    x0 = width*i + margin * (i+1)
    y0 = height * 5
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

#play a turn
def gameMode_playTurn(app):
    app.game.chooseElseWisely(app)
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
            #app.timerDelay -= 1
            pass
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

def gameMode_drawRank(app,canvas):
    font = 'Courier 26 italic bold'
    w = app.width / 2
    h = app.height/3
    rankList = app.game.rank(app)
    rank = 1
    for i in range(len(rankList)):
        canvas.create_text(w, h + 50 * i, text = f"{rank} place: Player {rankList[i].serial}", 
            font = font) 
        if i > 0 and rankList[i].score == rankList[i-1].score:
            pass
        else:
            rank += 1
    canvas.create_text(app.width/2, app.height/2 + 250, text = "Goodbye :)", font = font) 

def gameMode_drawHand(app,canvas):
    hand = app.players[0].hand
    n = len(hand)
    font = 'Courier 16 italic bold'
    for i in range(n):
        x0,y0,x1,y1 = gameMode_getCellBound(app,i)
        canvas.create_rectangle(x0,y0,x1,y1,width = 2)
        canvas.create_text((x0+x1)/2,(y0+y1)/2,font = font, text = hand[i])
        
def gameMode_drawChosen(app,canvas):
    height = app.height / 3 * 2
    cards = app.players[0].cardSeq
    canvas.create_text(50,height,text = f"your cards: {str(cards)}",anchor = 'nw')

def gameMode_drawComponents(app,canvas):
    h = 50
    for player in app.players[1:]:
        h += 50
        canvas.create_text(50,h,text = f"Player {player.serial}'s cards: {str(player.cardSeq)}",
            anchor = 'nw')

def gameMode_drawScore(app,canvas):
    font = 'Courier 26 italic bold'
    w = app.width / 2
    h = app.height/3
    canvas.create_text(w, h , text = f"Score for round {3 - app.remainingRounds}", font = font)  
    for player in app.players:
        i = player.serial
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
        gameMode_drawRank(app,canvas)
    else:
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
            gameMode_drawHand(app,canvas)
            gameMode_drawChosen(app,canvas)
            gameMode_drawComponents(app,canvas)


#start the app
def gameMode_playSushiGO():
    runApp(width = 1440, height = 778)


#################################################
# Setting
#################################################

def appStarted(app):
    app.width = 1440
    app.height = 778
    #app.timerDelay = 500000
    #loadImage(app)
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
    app.remainingRounds = 3
    #0-enter to next page; 1~4-rules; 5-enter to start game
    app.rulePage = 0

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
    Background = app.loadImage('background.jpg')
    app.background = app.scaleImage(Background,1/2)


"""
#load the images
#pictures scanned from Gamewright
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
"""

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
    app.cardPool = sushigo.CardPool()
    #3 rounds in a game
    app.remainingRounds = 3



#################################################
# main
#################################################

def main():
    gameMode_playSushiGO()

if __name__ == '__main__':
    main()
