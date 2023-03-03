import pygame
from pygame.locals import *
from Entities.grid import *
from Entities.car import *
from Entities.obstacle import *
import settings
import path_planner

# Setting the pillar coordinates
#[x,y,direction] top left is 0,0 

'''FOR CHECKLIST'''
obstacle_positions = [[4,1,settings.right], [18,2,settings.left], [4,9,settings.right], [10,19,settings.up],[11,5,settings.left], [14, 13, settings.up]]  
# obstacle_positions = [[15, 1, 0], [10, 1, -90], [13, 6, -90], [6, 3, 90], [11, 13, -90], [18, 4, 180]] #first dubin path is bugged for this
# obstacle_positions = [[14, 14, -90], [13, 0, -90], [13, 1, -90], [2, 1, -90], [5, 16, 90]] # RLR is having a division zero error from an invalid obs
'''FLOWER'''
# obstacle_positions = [[9, 11, settings.down], [9,9, settings.up], [8, 10, settings.left], [10,10, settings.right]] 
# obstacle_positions = [[1, 5, settings.up], [16, 12, settings.up], [14, 1, settings.down], [13, 2, settings.up], [12, 13, settings.down]] wat de????
# initiating the system
pygame.init()
FPS = 60
FramePerSec = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((settings.Window_Size), RESIZABLE)
pygame.display.set_caption("MDP Simulator")
#primary_surface is for resizeable purposes
primary_surface = DISPLAYSURF.copy()
primary_surface.fill([0,0,0])

# Here lies the modulized algorithm for path planning
path_plan = path_planner.path_planner(obstacle_positions)
print("final mesage list= ", path_plan.final_message_list) # the message itself