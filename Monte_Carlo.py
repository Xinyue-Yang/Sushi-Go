import environment as sushigo
import main as main
from cmu_112_graphics import *

#Monte Carlo Simulation to find average score if randomly choose
def findAveScore(app):
    totalScore = 0
    for simulation in range (1,10**5):
        main.initializeGame(app)
        app.players = main.initializePlayers(5)
        app.numOfPlayers = 5
        app.numOfCardsInHand = 7
        app.game.playGame(app)
        for player in app.players:
            totalScore += player.score / 5
    avgScore = totalScore / (10 ** 5)
    print(avgScore)

