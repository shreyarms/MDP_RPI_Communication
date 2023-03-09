import pygame, sys
from pygame.locals import *
from Entities.grid import *
from Entities.car import *
from Entities.obstacle import *
import algorithm
import a_star
import settings
import path_planner

ROBOT_CUSHION = 0.5 * settings.grid_size
OBSTACLE_CUSHION = 1.5 * settings.grid_size # grid size
OBSTACLE_COUNT = 6

# initiating the system
pygame.init()
FPS = 60
FramePerSec = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((settings.Window_Size), RESIZABLE) 
pygame.display.set_caption("MDP Simulator")
#primary_surface is for resizeable purposes
primary_surface = DISPLAYSURF.copy()
primary_surface.fill([0,0,0])

# Setting the pillar coordinates
#[x,y,direction] top left is 0,0 

'''FOR CHECKLIST'''
# obstacle_positions = [[4,1,settings.right], [18,2,settings.left], [4,9,settings.right], [10,19,settings.up],[11,5,settings.left], [14, 13, settings.up]]  
# obstacle_positions = [[15, 1, 0], [10, 1, -90], [13, 6, -90], [6, 3, 90], [11, 13, -90], [18, 4, 180]] #first dubin path is bugged for this
# obstacle_positions = [[14, 14, -90], [13, 0, -90], [13, 1, -90], [2, 1, -90], [5, 16, 90]] # RLR is having a division zero error from an invalid obs
'''FLOWER'''
# obstacle_positions = [[9, 11, settings.down], [9,9, settings.up], [8, 10, settings.left], [10,10, settings.right]] 
# obstacle_positions = [[1, 5, settings.up], [16, 12, settings.up], [14, 1, settings.down], [13, 2, settings.up], [12, 13, settings.down]] wat de???
# obstacle_positions = [[1,11,settings.down], [11,14,settings.up], [14,8,settings.left], [17,15,settings.down]]#, [1,15,settings.right]] lounge layout
dubin = algorithm.Dubin()

# while True:
#     choice = int(input('''Select choice of input:
#                         1. Manual Input
#                         2. Random Generated\n'''))
#     if choice == 1:
#         obstacle_positions = algorithm.Dubin.read_obstacles(dubin)
#         break
#     elif choice == 2:
#         obstacle_positions = algorithm.Dubin.random_obstacle_generator(dubin, OBSTACLE_COUNT)
#         break
#     else:
#         print("Invalid Choice")
destinations = []
# obstacle_positions = algorithm.Dubin.random_obstacle_generator(dubin, OBSTACLE_COUNT)
# obstacle_positions= [[9, 6, -90], [17, 17, 90], [11, 12, -90], [13, 2, 180], [17, 12, 90]]
# obstacle_positions= [[11, 11, 0], [10, 0, -90], [13, 7, 90], [7, 3, 180], [2, 9, 90]]
 
# obstacle_positions = [[19, 12, 180], [0, 2, 0]] #LSL
# obstacle_positions = [[8,9,90], [19, 12, 180]] #all except LSR
# # obstacle_positions = [[2, 6, -90]]
# obstacle_positions = [[13,14,180], [3,6,0], [19, 2, 180]]
obstacle_positions = [[10,19,90], [3,6,0], [19, 2, 180]]

# obstacle_positions =  [[12, 7, 180], [0, 10, 0], [8, 18, 90], [9, 17, 0], [16, 7, -90], [8, 5, -90]] #[[19, 12, 180], [0, 2, 0]]

# obstacle_positions =  [[10, 13, -90], [1, 14, 0]]
# obstacle_positions =  [[7, 13, 90], [14, 7, 0], [4, 12, 90], [11, 13, 0], [12, 13, 0]]

# obstacle_positions = algorithm.Dubin.random_obstacle_generator(dubin, OBSTACLE_COUNT)

print("obstacle_positions = ", obstacle_positions)

path_plan = path_planner.path_planner(obstacle_positions)

print("Final Message List =", path_plan.final_message_list) # the message itself
# print("Final destination List =", path_plan.final_destination) # the message itself
destinations = path_plan.final_destination.copy()
show_path = path_plan.final_destination.copy()

OBSTACLE_COUNT = len(obstacle_positions)

# classes
grid = Grid()
car_starting_pos_pixel = grid.grid_to_pixel([settings.Car_starting_x,settings.Car_starting_y]) # finding the starting position of car
grid_coordinates = grid.grids.copy()
obs = Obstacle(grid.grids,obstacle_positions)
car = Car(car_starting_pos_pixel)


# variables
first = True
reverse_valid = False
invalid_positions = []
no_path = True
# destinations = []
# show_path = []
reverse_coordinates = []
message_list = []
timer = 0
send_message = False
forward = False
settings.Car_current_x = car_starting_pos_pixel[0]
settings.Car_current_y = car_starting_pos_pixel[1]
car_current_pos = [car_starting_pos_pixel[0],car_starting_pos_pixel[1],settings.up]


print("Car Starting = ", car_starting_pos_pixel)
# Generate the target positions based on the pillar positions
target_positions = obs.get_target_pos()

obstacles_grid = dict()
for index in range(len(target_positions)):
    obstacles_grid[tuple(target_positions[index])] = obstacle_positions[index] 
# print(obstacles_grid)
# target_positions = obs.edit_target_pos(target_positions)
#print("obstacle position = ",obstacle_positions)
#print("target position = ",target_positions)

# Generate the boundary coordinates for the pillars
for obstacle in obs.obstacle_coordinates:
    bottom_left_x = round(obstacle[1].bottomleft[0] - OBSTACLE_CUSHION + 1)
    bottom_left_y = round(obstacle[1].bottomleft[1]  + OBSTACLE_CUSHION - 1)

    top_right_x = round(obstacle[1].bottomleft[0]  + OBSTACLE_CUSHION + settings.grid_size - 2)
    top_right_y = round(obstacle[1].bottomleft[1]  - OBSTACLE_CUSHION - settings.grid_size + 2)

    packet = [bottom_left_x, bottom_left_y, top_right_x, top_right_y]
    invalid_positions.append(packet)
    
#print("invalid =",invalid_positions)

# another class
astar = a_star.astar(grid_coordinates,car,dubin,invalid_positions)

# find the hamiltonian path
path_taken = algorithm.Dubin.shortest_path(dubin, obstacle_positions, target_positions)
# print("path taken= ", path_taken)
next_pos = []
first_path_found = False
index = 0

#starting game loop
while True:

    #this allows us to close the pop-up window
    for event in pygame.event.get():          
        #handles quitting    
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # setup the screen
    #puts primary_surface ontop of DISPLAYSURF
    DISPLAYSURF.blit(pygame.transform.scale(primary_surface, DISPLAYSURF.get_rect().size), (0, 0))
    primary_surface.fill([0,0,0])
    grid.draw(primary_surface)
    obs.draw_obstacle(primary_surface)

    if(destinations):
        while(type(destinations[0])== str):
            if(destinations[0] == 'straight' or destinations[0] == 'left' or destinations[0] == 'right'):
                forward = True
                destinations.pop(0)
            elif(destinations[0] == 'reverse' or destinations[0] == 'reverse left' or destinations[0] == 'reverse right'):
                forward = False
                destinations.pop(0)
            if(len(destinations)==0):
                break
        if(len(destinations)>0):
            car.draw_car(primary_surface, destinations[0],forward)
            destinations.pop(0)
            # print(destinations)
    else: 
        car.maintain_car(primary_surface)

    if(show_path):
        for points in show_path:
            try:
                pygame.draw.circle(primary_surface, (0, 0, 255), points, 3)
            except TypeError:
                pass
    for point in path_plan.target_points:
        pygame.draw.circle(primary_surface, (255, 0, 255), [point[0],point[1]], 4)
    # # pt1 and pt2        
    # pygame.draw.circle(primary_surface, (255, 0, 0), [91.34718721234968, 508.41847086228853], 3)
    # pygame.draw.circle(primary_surface, (255, 0, 0), [318.1528127876503, 254.78152913771143], 3)
    # # midpoint of circles 
    # pygame.draw.circle(primary_surface, (255, 255, 0), [157.5, 495], 3)
    # pygame.draw.circle(primary_surface, (255, 255, 0), [252, 268.2], 3)
    # #current and next pos
    # pygame.draw.circle(primary_surface, (0, 255, 100), [90, 495], 3)
    # pygame.draw.circle(primary_surface, (0, 255, 100), [252, 198], 3)


    # pygame.draw.circle(primary_surface, (0, 255, 100), [522, 522], 3)

    #old sim planner
    # When there is still pillars to go to
    # if(path_taken and not no_path):

    #     # When timer has run out
    #     if(timer == 0):

    #         #After timer is over generate coordinates for reversing once
    #         if(reverse_valid):
    #             rev, _ =car.reverse(car.current_pos)
    #             reverse_coordinates.extend(rev)
    #             reverse_valid = False
    #             show_path.extend(reverse_coordinates)
    #             message_reverse = 'c:BS' + str(int(round(20 * 1000))).zfill(6) # reverse by 2 grid, 20 cm
    #             message_list.append(message_reverse)

    #         # When reverse coordinates are already generate, execute it
    #         else:
    #             #If there is reverse coordinates, reverse
    #             if(reverse_coordinates):
    #                 car.draw_car_reverse(primary_surface,reverse_coordinates[0])
    #                 reverse_coordinates.pop(0)
    #             else:
    #                 #move to destination when it is not empty
    #                 if(destinations):
    #                     #kinda like lock and key thingy to determine whether isit going forward or reversing
    #                     while(type(destinations[0])== str):
    #                         if(destinations[0] == 'straight' or destinations[0] == 'left' or destinations[0] == 'right'):
    #                             forward = True
    #                             destinations.pop(0)
    #                         elif(destinations[0] == 'reverse' or destinations[0] == 'reverse left' or destinations[0] == 'reverse right'):
    #                             forward = False
    #                             destinations.pop(0)
    #                         if(len(destinations)==0):
    #                             break
    #                     if(len(destinations)>0):
    #                         car.draw_car(primary_surface, destinations[0],forward)
    #                         destinations.pop(0)
    #                 else:
    #                     car.maintain_car(primary_surface)
    #                     #reached destination, remove it from path_taken list
    #                     if(abs(car.current_pos[0] - path_taken[0][0]) <= ROBOT_CUSHION and abs(car.current_pos[1] - path_taken[0][1]) <= ROBOT_CUSHION and car.current_pos[2]==path_taken[0][2] ):
    #                     #     print("opopopopopppoppoop")
    #                         path_taken.pop(0)
    #                         timer = 1 * 60 # start timer to mimic image regconition
    #                     else:
    #                     #when destinations is empty, generate destinations
    #                         path_found = False
    #                         index = 0
    #                         while True:
    #                             if (path_found == True):
    #                                 break

    #                             if (len(path_taken) == 0):
    #                                 no_path = True
    #                                 break
    #                             # DUBINS path planning ----------------------------------------------------------------------------------------------------------
    #                             print()
    #                             print("Entering Dubin")
    #                             next_pos = path_taken[0]
    #                             '''
    #                             one element in compiled_path_list is [coordinates, shortest_time, chosen_path, [message_one, message_two, message_three]]
    #                             compiled_path_list[x][y][z?]
    #                             x selects path type LSL, RSR etc
    #                             y selects one of the element in the list above
    #                             compiled_path_list is ordered ascendingly w.r.t. time
    #                             '''
    #                             car_current_pos = [int(x) for x in car.current_pos] #convert from float to int
    #                             compiled_path_lists = algorithm.Dubin.get_shortest_path(dubin, car, path_taken[0],car_current_pos, next_pos)
    #                             for path in compiled_path_lists:
    #                                 # obtain list of coordinates travelled for 1 specific path type e.g. RSR
    #                                 coordinates_list = car.move_car_dubin(path[0][0], path[0][1], next_pos, path[2],car_current_pos)
    #                                 # dubins path found
    #                                 if(dubin.check_path_valid(coordinates_list, invalid_positions, grid_coordinates)):
    #                                     destinations.extend(coordinates_list)
    #                                     show_path.extend(destinations)
    #                                     message_list.extend(path[3])
    #                                     print("Dubin path found")
    #                                     break
    #                             # END OF DUBIN ------------------------------------------------------------------------------------------------------------------

    #                             # START A* SEARCH  --------------------------------------------------------------------------------------------------------------
    #                             if(not destinations): #when dubin failed to plan
    #                                 print("No Dubin Path Found!")
    #                                 print("Finding A* Path")
    #                                 movement_path = astar.start_astar(car.current_pos,path_taken[0]) # A* path validity has already been checked, movement_path is always valid
    #                                 if(movement_path != None):
    #                                     movement_path = astar.a_star_path_compressor(movement_path)
    #                                     a_star_coordinate_list = car.move_car_a_star(car.current_pos, movement_path)
    #                                     destinations.extend(a_star_coordinate_list)
    #                                     show_path.extend(a_star_coordinate_list)
    #                                     message_list.extend(astar.coordinates_list_to_message(car.current_pos, movement_path))

    #                             if (destinations):
    #                                 message_coord = str(obstacles_grid[tuple(path_taken[0])][0] + 1) + "," + str(abs(20 - obstacles_grid[tuple(path_taken[0])][1]))
    #                                 message_list.extend(["c:END00000", "c:TAKEPIC" + message_coord])
    #                                 send_message = path_found = True
    #                                 no_path = False
                                
    #                             else:
    #                                 print(path_taken.pop(0))
    #                                 print("Obstacle Popped!")
    #                                 #if sim reaches this point, the path plan path might deviate from the sim path
    #                             # END OF A* SEARCH --------------------------------------------------------------------------------------------------------------
                                      
    #     else:
    #         timer -= 1
    #         car.maintain_car(primary_surface)
    #         reverse_valid = True
    # else:
    #     car.maintain_car(primary_surface)

    # # draw out the planned path
    # if(show_path):
    #     for points in show_path:
    #         try:
    #             pygame.draw.circle(primary_surface, (0, 0, 255), points, 3)
    #         except TypeError:
    #             pass
        
    # if (len(message_list) != 0 and send_message== True):
    #     print("Simulated Message List = ", message_list)
    #     print("-" * 100)
    #     send_message = False
    #     if(message_list == path_plan.final_message_list):
    #         print()
    #         print("Both simulator and path_plan gave the same message :)")

    # pygame.draw.circle(primary_surface, (255, 0, 0), [279.0, 63.0], 3)
    # pygame.draw.circle(primary_surface, (255, 255, 0), [333, 468], 3)

    pygame.display.update()
    FramePerSec.tick(FPS)
