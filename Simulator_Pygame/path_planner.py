from Simulator_Pygame.Entities.grid import *
from Simulator_Pygame.Entities.car import *
from Simulator_Pygame.Entities.obstacle import *
import algorithm
import a_star
import settings

#all encompassing class, should run without the simulator
class path_planner:
    #maybe rpi pass obs to us
    def __init__(self, obstacle_positions) -> None:
        dubin = algorithm.Dubin()
        self.OBSTACLE_COUNT = len(obstacle_positions)
        grid = Grid()
        car_starting_pos_pixel = grid.grid_to_pixel([settings.Car_starting_x,settings.Car_starting_y]) # finding the starting position of car
        grid_coordinates = grid.grids.copy()
        obs = Obstacle(grid.grids,obstacle_positions)
        car = Car(car_starting_pos_pixel)

        # variables
        message_list = []
        destination = []
        popped_path = []
        reverse_distance = 1* settings.grid_size

        settings.Car_current_x = car_starting_pos_pixel[0]
        settings.Car_current_y = car_starting_pos_pixel[1]
        target_positions = obs.get_target_pos()
        self.target_points = target_positions.copy()
        invalid_positions = self.find_invalid(obs)
        obstacles_grid = dict()
        for index in range(len(target_positions)):
            obstacles_grid[tuple(target_positions[index])] = obstacle_positions[index]
        astar = a_star.astar(grid_coordinates,car,dubin,invalid_positions)

        # find the hamiltonian path
        path_taken = algorithm.Dubin.shortest_path(dubin, obstacle_positions, target_positions)
       
        car_current_pos = [car_starting_pos_pixel[0],car_starting_pos_pixel[1],settings.up]


        message, desti, popped_path,car_current_pos =self.plan_overall_path(path_taken,car,dubin,invalid_positions,grid_coordinates,astar,obstacles_grid,car_current_pos,reverse_distance)
        message_list.extend(message)
        destination.extend(desti)

        if(popped_path): # if there is a popped path
            print("Checking for possible path to popped_path")
            message, desti, popped_path, car_current_pos =self.plan_overall_path(popped_path,car,dubin,invalid_positions,grid_coordinates,astar,obstacles_grid,car_current_pos,reverse_distance)
            if(message): # if there somehow is a path to the popped path
                message_list.extend(message)
                destination.extend(desti)

        # if(message_list[-1]== 'c:BS020000' or message_list[-1] == 'c:BS010000'): # theres always an extra reverse appended to the message, popped it
        #     message_list.pop()

        while message_list[-1][:9] != 'c:TAKEPIC':
            message_list.pop()
        
        # integrate messages to reduce instructions
        for index in range(len(message_list) - 1):
            instr = message_list[index][:4]
            next_instr = message_list[index + 1][:4]
            if (instr == 'c:FS' or instr == 'c:BS') and (next_instr == 'c:FS' or next_instr == 'c:BS'):
                resultant_magnitude = float(message_list[index][4:]) / 1000
                magnitude = float(message_list[index + 1][4:]) / 1000
                if instr == 'c:FS':
                    if next_instr == 'c:FS':
                        resultant_magnitude += magnitude
                    elif next_instr == "c:BS":
                        resultant_magnitude -= magnitude
                    if resultant_magnitude > 0:
                        message_list[index] = 'c:FS' + str(int(round(resultant_magnitude * 1000))).zfill(6)
                    elif resultant_magnitude < 0:
                        message_list[index] = 'c:BS' + str(int(round(abs(resultant_magnitude) * 1000))).zfill(6)
                    else:
                        message_list[index] = 'DEL'
                    message_list[index + 1] = 'DEL'
                
                elif instr == 'c:BS':
                    if next_instr == 'c:FS':
                        resultant_magnitude -= magnitude
                    elif next_instr == "c:BS":
                        resultant_magnitude += magnitude
                    if resultant_magnitude > 0:
                        message_list[index] = 'c:BS' + str(int(round(resultant_magnitude * 1000))).zfill(6)
                    elif resultant_magnitude < 0:
                        message_list[index] = 'c:FS' + str(int(round(abs(resultant_magnitude) * 1000))).zfill(6)
                    else:
                        message_list[index] = 'DEL'
                    message_list[index + 1] = 'DEL'

        self.final_message_list = []
        self.final_message_list = [x for x in message_list if x != 'DEL'] # delete all redundant messages
        
        print(f"Messages cut: {len(message_list) - len(self.final_message_list)}")
        
        self.final_destination = []
        self.final_destination = destination


    def plan_overall_path(self,path_taken,car,dubin,invalid_positions,grid_coordinates,astar,obstacles_grid,car_current_pos,reverse_distance):
        index = 1
        message_list = []
        destination = []
        popped_path = []
        for path in path_taken:
            print("Finding path to Pillar ", index, ", path =",path)
            possible_reverse_distance = reverse_distance
            desti , messa = self.plan_path_to_point(car,path,car_current_pos,dubin,invalid_positions,grid_coordinates,astar,obstacles_grid)
            if(messa!=None):
                destination.extend(desti)
                message_list.extend(messa)
                reverse_d,temp = car.reverse(path,possible_reverse_distance)
                # check_path_valid(self,coordinates_list, obs_invalid_positions,grid):
                while(not dubin.check_path_valid(reverse_d,invalid_positions,grid_coordinates)): # while reverse is not valid, initial reverse distance is 2 grids
                    possible_reverse_distance -= settings.grid_size # reduce reverse distance by 1 grid
                    reverse_d,temp = car.reverse(path,possible_reverse_distance) # generate coordinate for reduced reverse distance
                message_reverse = 'c:BS' + str(int(round((possible_reverse_distance/2.7) * 1000))).zfill(6) # reverse by 2 grid, 20 cm
                message_list.append(message_reverse)
                destination.extend(reverse_d)
                car_current_pos = temp
            else:
                popped_path.append(path)
            index += 1
            print(130*'#')
        return message_list, destination, popped_path, car_current_pos


    def plan_path_to_point(self,car,path_taken,car_current_pos,dubin,invalid_positions,grid_coordinates,astar,obstacles_grid):
        destinations = []
        show_path = []
        message_list = []
        next_pos = []
        while True:
    # find first path
        # DUBINS path planning -----------------------------------------------------------------------------------
            print()
            print("Finding Dubin Path")
            next_pos = path_taken
            compiled_path_lists = algorithm.Dubin.get_shortest_path(dubin, car, path_taken, car_current_pos, next_pos)
            for path in compiled_path_lists:
                # obtain list of coordinates travelled for 1 specific path type e.g. RSR
                print(".........", end = '')
                coordinates_list = car.move_car_dubin(path[0][0], path[0][1], next_pos, path[2],car_current_pos)
                if(dubin.check_path_valid(coordinates_list, invalid_positions, grid_coordinates)):
                    destinations.extend(coordinates_list)
                    show_path.extend(destinations)
                    message_list.extend(path[3])
                    print("Dubin Path found!")
                    break
            
            # END OF DUBIN --------------------------------------------------------------------------------------------
            # if dubin no find then astar
            # START A* SEARCH  ----------------------------------------------------------------------------------------
            if(not destinations): #when dubin failed to plan
                print("No Dubin Path found!\n")
                print("-" * 100)
                print("\nFinding A* Path")
                a_star_dubin_destination= None
                # last_turn= False
                movement_path = astar.start_astar(car_current_pos,path_taken) # A* path validity has already been checked, movement_path is always valid
                if(movement_path!= None):
                    # a_star_dubin_destination, a_star_dubin_message, a_star_path= astar.a_star_dubins(movement_path,path_taken,algorithm,dubin,car,invalid_positions,grid_coordinates)
                    if(a_star_dubin_destination== None): # No dubin in path or dubin only gives a straight command
                        movement_path = astar.adjust_to_irl_turning_radius(movement_path)
                        movement_path = astar.a_star_path_compressor(movement_path)
                        print()
                        print("movement_path = ",movement_path)
                        print()
                        a_star_coordinate_list = car.move_car_a_star(car_current_pos,movement_path)
                        destinations.extend(a_star_coordinate_list)
                        show_path.extend(a_star_coordinate_list)
                        message_list.extend(astar.coordinates_list_to_message(car_current_pos,movement_path))

                    # else: # if theres dubin
                    #     movement_path= a_star_path.copy() #remaining a* path needs to be processed
                    #     movement_path = list(map(list, movement_path))
                    #     last = movement_path[-1] # an extra movement is kept to ensure we know the target point
                    #     print("movemen_path= ",movement_path)
                    #     if(last[1]=='left' or last[1]=='right' or last[1]=='reverse left' or last[1]=='reverse right'): 
                    #         # coordinate where the turn starts is needed for adjusting
                    #         last_turn = True
                    #     else: # extra point is pop as straight movement will be auto adjusted
                    #         movement_path.pop()
                    #     movement_path = astar.adjust_to_irl_turning_radius(movement_path)
                    #     movement_path = astar.a_star_path_compressor(movement_path)
                    #     if(last_turn): # extra point is pop
                    #         movement_path.pop()
                    #     a_star_coordinate_list = car.move_car_a_star(car_current_pos,movement_path)
                    #     destinations.extend(a_star_coordinate_list)
                    #     show_path.extend(a_star_coordinate_list)
                    #     message_list.extend(astar.coordinates_list_to_message(car_current_pos,movement_path))
                    #     destinations.extend(a_star_dubin_destination)
                    #     show_path.extend(a_star_dubin_destination)
                    #     message_list.extend(a_star_dubin_message)


            if (destinations):
                message_coord = str(obstacles_grid[tuple(path_taken)][0] + 1) + "," + str(abs(20 - obstacles_grid[tuple(path_taken)][1]))
                message_list.extend(["c:END00000", "c:TAKEPIC" + message_coord])
                return destinations, message_list
            else:
                return None, None

    def find_invalid(self,obs):
        OBSTACLE_CUSHION = 1.5 * settings.grid_size # grid size
        invalid_positions = []
        for obstacle in obs.obstacle_coordinates:
            bottom_left_x = round(obstacle[1].bottomleft[0] - OBSTACLE_CUSHION + 1)
            bottom_left_y = round(obstacle[1].bottomleft[1]  + OBSTACLE_CUSHION - 1)

            top_right_x = round(obstacle[1].bottomleft[0]  + OBSTACLE_CUSHION + settings.grid_size - 2)
            top_right_y = round(obstacle[1].bottomleft[1]  - OBSTACLE_CUSHION - settings.grid_size + 2)

            packet = [bottom_left_x, bottom_left_y, top_right_x, top_right_y]
            invalid_positions.append(packet)

        return invalid_positions
