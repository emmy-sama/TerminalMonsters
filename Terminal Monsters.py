import art
import os
from Classes import *
# Game Opening
# Write an opening at some point
# Decide on font for title


def openingcls():
    os.system('cls' if os.name == 'nt' else 'clear')
    art.tprint("Welcome To Terminal Monsters")
    print("intro text goes here")

openingcls()
player_name = input("\nPlease enter your name: ")
if player_name == "":
    player_name = "Ash"

openingcls()
player_pronouns = input("\nPlease enter your pronouns(Ie She/Her He/Him They/Them): ")
if player_pronouns == "":
    player_pronouns = "They/Them"

print(player_name)
print(player_pronouns)

# Start Select Screen
# Pick font
os.system('cls' if os.name == 'nt' else 'clear')
art.tprint("Starter Select", space=1)
print("""
Bulbasaur is a grass type pokemon with a strange seed on its back that sprouts and grows as Bulbasaur does. 
Charmander is a fire type pokemon the flame that burns at the tip of its tail is an indication of its emotions.
Squirtle is a water type pokemon its shell is not just for protection it enables Squirtle to swim at high speeds.
Random""")
starter = input("\nPlease enter the name of the starter you would like: ")
team = [starter]
player = Player(player_name, player_pronouns, starter, team)