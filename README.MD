# Final Project for CS322 Artifical Intelligence

This project was created as a final project for my CS322 course during my senior year spring semester. 
Needed implementation to fulfill the project: 
- Open information Game with no dice or chance elements. 
- Ability to play human vs human
- Two A.I players
    - Alpha Beta Pruning player
    - Reinforcement model player that I will also train


GUI of a game was not neccesary, but I decided to create it anyways using PyGame library.

### Utility folder 

Utility folder contains classes that I used to make my code modular, simple to read, and managble. 

- Node Class -->  node.py

Alpha Beta Pruning uses a tree to portray possible moves and expected outcomes. I connected it under the same umbrella using node class with attributes such as children and game state. 

P.S ---->  Add this to readme.MD file under the utility folder. 

### A.I players folder 