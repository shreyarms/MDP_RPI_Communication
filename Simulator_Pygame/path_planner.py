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

        settings.Car_current_x = car_starting_pos_pixel[0]
        settings.Car_current_y = car_starting_pos_pixel[1]
        target_positions = obs.get_target_pos()
        invalid_positions = self.find_invalid(obs)
        obstacles_grid = dict()
        for index in range(len(target_positions)):
            obstacles_grid[tuple(target_positions[index])] = obstacle_positions[index]
        astar = a_star.astar(grid_coordinates,car,dubin,invalid_positions)

        # find the hamiltonian path
        path_taken = algorithm.Dubin.shortest_path(dubin, obstacle_positions, target_positions)
       
        index = 0
        car_current_pos = [car_starting_pos_pixel[0],car_starting_pos_pixel[1],settings.up]
        for path in path_taken:
            if(path != path_taken[0]): #not first path
                message_reverse = 'c:BS' + str(int(round(20 * 1000))).zfill(6) # reverse by 2 grid, 20 cm
                message_list.append(message_reverse)
            _ , messa = self.plan_path(car,path,car_current_pos,dubin,invalid_positions,grid_coordinates,astar,obstacles_grid)
            if(messa!=None):
                message_list.extend(messa)
                _,temp = car.reverse(path)
                car_current_pos = temp
            else:
                path_taken.remove(path)
                path_taken.append(path)

        self.final_message_list = []
        self.final_message_list = message_list
        print("Finished modulizzed algo")
        # print("message_list = ", message_list)


    def plan_path(self,car,path_taken,car_current_pos,dubin,invalid_positions,grid_coordinates,astar,obstacles_grid):
        destinations = []
        show_path = []
        message_list = []
        next_pos = []
        while True:
    # find first path
        # DUBINS path planning -----------------------------------------------------------------------------------
            print()
            print("Entering dubins")
            next_pos = path_taken
            compiled_path_lists = algorithm.Dubin.get_shortest_path(dubin, car, path_taken, car_current_pos, next_pos)
            for path in compiled_path_lists:
                # obtain list of coordinates travelled for 1 specific path type e.g. RSR
                coordinates_list = car.move_car_dubin(path[0][0], path[0][1], next_pos, path[2],car_current_pos)
                if(dubin.check_path_valid(coordinates_list, invalid_positions, grid_coordinates)):
                    destinations.extend(coordinates_list)
                    show_path.extend(destinations)
                    message_list.extend(path[3])
                    print("Dubin path found")
                    break
            
            # END OF DUBIN --------------------------------------------------------------------------------------------
            # if dubin no find then astar
            # START A* SEARCH  ----------------------------------------------------------------------------------------
            if(not destinations): #when dubin failed to plan
                print("no dubins")
                print()
                movement_path = astar.start_astar(car_current_pos,path_taken) # A* path validity has already been checked, movement_path is always valid
                if(movement_path != None):
                    movement_path = astar.a_star_path_compressor(movement_path)
                    a_star_coordinate_list = car.move_car_a_star(car_current_pos,movement_path)
                    destinations.extend(a_star_coordinate_list)
                    show_path.extend(a_star_coordinate_list)
                    message_list.extend(astar.coordinates_list_to_message(car_current_pos,movement_path))

            if (destinations):
                message_coord = str(obstacles_grid[tuple(path_taken)][0] + 1) + "," + str(abs(20 - obstacles_grid[tuple(path_taken)][1]))
                message_list.extend(["c:END00000", "c:TAKEPIC" + message_coord])
                send_message = path_found = True
                no_path = False
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
