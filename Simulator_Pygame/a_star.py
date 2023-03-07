import math
from queue import PriorityQueue

import settings


class astar:
    def __init__(self, grid_coordinate, car, algorithm, invalid_positions) -> None:
        self.grid_coordinates= grid_coordinate.copy() # make a copy of the grid coordinates(2d list(row,column)->bottom right of grid in pixels)
        self.algo = algorithm # lets us use algorithm functions
        self.car = car # lets us use car functions
        self.invalid_position = invalid_positions.copy()
        

    def get_neighbour(self,start):
        """Find all the neighbours it can move to using the 6 basic movements along with its cost"""
        # setup
        neighbours = []
        straight_dist = 1 * settings.grid_size
        straight_cost = 1 * settings.grid_size
        # turning_radius = 2 * settings.grid_size # rounded up both left and right turning radius
        turning_radius = settings.a_star_turning_radius # rounded up both left and right turning radius
        turning_cost = 999 * settings.grid_size
        # assume car always makes a 90 degree turn to next neighbour(might require left and right turning radius to be same)
        # same assumption for reverse
        # car always move straight by 1 grid

        #check possible neighbours for straight movements (move straight or reverse)
        straight_movement = [
            self.move_straight(start, straight_dist), # move straight
            self.move_straight(start, -straight_dist) # reverse
        ]

        straight_center = None # to keep consistent format with turning

        #if movement is valid, add it to the possible neighbours it can visit
        for movement_destination in straight_movement:
            movement_type = movement_destination[3]
            temp_movement_destination = [movement_destination[0],movement_destination[1],movement_destination[2]]
            if(self.algo.check_path_valid([temp_movement_destination],self.invalid_position,self.grid_coordinates)):
                neighbours.append([temp_movement_destination,movement_type, straight_cost, straight_center])
            

        #check possible neighbours for turning (turn left, right or reverse left, right)

        turning_movement = [
            self.move_turn(start,turning_radius, "L", False), # turn left
            self.move_turn(start,turning_radius, "R", False), # turn right
            self.move_turn(start,turning_radius, "L", True), # reverse left
            self.move_turn(start,turning_radius, "R", True), # reverse right
        ]
        counter=0
        for movement_destination in turning_movement:
            reverse_start = start
            reverse_start = list(reverse_start)
            movement_destination = list(movement_destination)
            turning_coordinates = []
            reverse_start[2] += 180 # reverse all direction
            if(reverse_start[2]>=270): #when deg is 90+180 = 270 then 270-360 = -90
                reverse_start[2] -= 360
            center = self.find_center(start,counter,turning_radius)
            center = center[0],center[1]
            # def move_car_curve(self, alpha, start, center , turn_direction):
            if(counter == 0): #forward left
                turning_coordinates = self.car.move_car_curve(90, [start[0],start[1]],center, "left")
                movement_destination[2] +=90
            elif(counter == 1): #forward right
                turning_coordinates = self.car.move_car_curve(-90, [start[0],start[1]],center, "right")
                movement_destination[2] -=90
            elif(counter == 2): #reverse left
                turning_coordinates = self.car.move_car_curve(-90, [reverse_start[0],reverse_start[1]],center, "right") # opposite direction
                movement_destination[2] -=90
            elif(counter == 3): # reverse right
                turning_coordinates = self.car.move_car_curve(90, [reverse_start[0],reverse_start[1]],center, "left") # opposite direction
                movement_destination[2] +=90

            if(movement_destination[2]>=270):
                movement_destination[2] -= 360
            elif(movement_destination[2]<=-180):
                movement_destination[2] += 360

            movement_type = movement_destination[3]
            temp_movement_destination = [movement_destination[0],movement_destination[1],movement_destination[2]]
            if(self.algo.check_path_valid(turning_coordinates,self.invalid_position,self.grid_coordinates)):
                neighbours.append([temp_movement_destination, movement_type, turning_cost, center]) #maybe append the movement command as well
            counter += 1


        #returns a list of all possible neighbours it can move to
        # tentatively neighbours format : [ [[x,y,direction],cost], [[x,y,direction],cost] ]
        return neighbours

    def heuristic(self,current_pos,target):
        """Calculate euclidean distance from current node to target node"""
        dx = abs(current_pos[0] - target[0])
        dy = abs(current_pos[1] - target[1])
        return math.sqrt(dx ** 2 + dy ** 2)
    
    def manhattan(self,current_pos,target):
        dx = abs(current_pos[0] - target[0])
        dy = abs(current_pos[1] - target[1])
        return (dy+dx)  

    def start_astar(self, current_pos, target_pos):
        print("Starting A* Search", end = '')
        #start and target is in (x,y,direction) format
        # setup
        frontier_nodes = PriorityQueue() # stores all of the frontier node
        backtrack = dict()
        cost = dict()
        movement_list = []
        start = tuple(current_pos.copy())
        target = tuple(target_pos.copy())
        counter = 0 # used for tie breaking should the total_cost and path_cost be the same

        # put starting_pos into queue
        frontier_nodes.put((0,0,counter,start))
        cost[start] = 0
        backtrack[start] = (None, None, None) # Parent, Command, center(to reduce recalculation later on)
        #start exploring
        while(not frontier_nodes.empty()): #when there are still frontier nodes to process
            #frontier format = total_cost, path_cost, counter, current_position
            # if total cost is tied, tie breaking is first determined by highest path cost, then counter if path cost also ties
            total_cost, _, _, current = frontier_nodes.get() # "_" is a dont care variable that will not be used
            print(".", end = '')
            if (abs(current[0]-target[0])<= 0.5*settings.grid_size and abs(current[1]-target[1])<= 0.5*settings.grid_size and current[2]==target[2]):
                print("A* Path Found!")
                if(backtrack[current][1]== "straight" or backtrack[current][1]== "reverse"): #For reaching target when compressing straight and reverse
                    movement_list.append([current, backtrack[current][1], None])
                #backtrack till root node
                while(backtrack[current]!=(None, None, None)):
                    #reconstruct the path
                    movement_list.append(backtrack[current])
                    current = backtrack[current][0] # move to parent node
                movement_list.reverse()
                return movement_list
            neighbour = self.get_neighbour(current)
            # tentatively neighbours format : [ [[x,y,direction],cost], [[x,y,direction],cost] ]
            #turning movement format : {[x,y,direction],cost, center]
            for new_pos, movement_type, weight, center in neighbour:
                new_pos = tuple(new_pos)
                if(new_pos in cost):
                    new_cost = cost.get(new_pos) + weight
                else:
                    new_cost = weight

                if new_pos not in backtrack or new_cost < cost[new_pos]:
                    counter += 1 #for tie breaking
                    # total_cost = new_cost + self.manhattan(new_pos,target)
                    total_cost = new_cost + 0
                    frontier_nodes.put((total_cost, new_cost, counter, new_pos))
                    backtrack[new_pos] = (current, movement_type, center)
                    cost[new_pos] = new_cost

        #if reach here no path is found
        print("A* Path Not Found")
        print()
        return None
                
    def move_straight(self,start, straight_dist):
        temp_start = start
        temp_start = list(temp_start)
        if (temp_start[2] == settings.right):
            temp_start[0] += straight_dist
        elif (temp_start[2] == settings.up):
            temp_start[1] -= straight_dist
        elif (temp_start[2] == settings.left):
            temp_start[0] -= straight_dist
        elif (temp_start[2] == settings.down):
            temp_start[1] += straight_dist
        if(straight_dist>=0):
            temp_start.append("straight")
        else:
            temp_start.append("reverse")
        return tuple(temp_start)

    def move_turn(self, start, turning_radius, direction, reverse):
        """Return target location after turning"""
        #could cut this down by half but i lazy
        if(direction== 'left'):
            direction = "L"
        elif(direction== 'right'):
            direction = "R"
        temp_start = start
        temp_start = list(temp_start)
        
        if (temp_start[2] == settings.right): #facing right
            if(direction == "L" and not reverse): # forward left
                temp_start[0] += turning_radius
                temp_start[1] -=turning_radius
            elif(direction == "R" and not reverse): # forward right
                temp_start[0] += turning_radius
                temp_start[1] +=turning_radius
            elif(direction == "L" and reverse): # reverse left
                temp_start[0] -= turning_radius
                temp_start[1] -=turning_radius
            elif(direction == "R" and reverse): # reverse right
                temp_start[0] -= turning_radius
                temp_start[1] +=turning_radius

        elif (temp_start[2] == settings.up): # facing up
            if(direction == "L" and not reverse): # forward left
                temp_start[0] -= turning_radius
                temp_start[1] -=turning_radius
            elif(direction == "R" and not reverse): # forward right
                temp_start[0] += turning_radius
                temp_start[1] -=turning_radius
            elif(direction == "L" and reverse): # reverse left
                temp_start[0] -= turning_radius
                temp_start[1] +=turning_radius
            elif(direction == "R" and reverse): # reverse right
                temp_start[0] += turning_radius
                temp_start[1] +=turning_radius

        elif (temp_start[2] == settings.left): # facing left
            if(direction == "L" and not reverse): # forward left
                temp_start[0] -= turning_radius
                temp_start[1] +=turning_radius
            elif(direction == "R" and not reverse): # forward right
                temp_start[0] -= turning_radius
                temp_start[1] -=turning_radius
            elif(direction == "L" and reverse): # reverse left
                temp_start[0] += turning_radius
                temp_start[1] +=turning_radius
            elif(direction == "R" and reverse): # reverse right
                temp_start[0] += turning_radius
                temp_start[1] -=turning_radius

        elif (temp_start[2] == settings.down): # facing down
            if(direction == "L" and not reverse): # forward left
                temp_start[0] += turning_radius
                temp_start[1] +=turning_radius
            elif(direction == "R" and not reverse): # forward right
                temp_start[0] -= turning_radius
                temp_start[1] +=turning_radius
            elif(direction == "L" and reverse): # reverse left
                temp_start[0] += turning_radius
                temp_start[1] -=turning_radius
            elif(direction == "R" and reverse): # reverse right
                temp_start[0] -= turning_radius
                temp_start[1] -=turning_radius

        if(direction == "L" and not reverse): # forward left
            temp_start.append("left")
        elif(direction == "R" and not reverse): # forward right
            temp_start.append("right")
        elif(direction == "L" and reverse): # reverse left
            temp_start.append("reverse left")
        elif(direction == "R" and reverse): # reverse right
            temp_start.append("reverse right")
        return tuple(temp_start)

    def find_center(self, start, counter, turning_radius):
        temp_start = start
        temp_start = list(temp_start)
        if((start[2] == settings.right and (counter==1 or counter == 3)) or (start[2] == settings.left and (counter == 0 or counter == 2))):
            temp_start[1] += turning_radius
        
        elif((start[2] == settings.right and (counter==0 or counter == 2)) or (start[2] == settings.left and (counter==1 or counter == 3))):
            temp_start[1] -= turning_radius

        elif((start[2] == settings.up and (counter==0 or counter == 2)) or (start[2] == settings.down and (counter==1 or counter == 3))):
            temp_start[0] -= turning_radius

        elif((start[2] == settings.up and (counter==1 or counter == 3)) or (start[2] == settings.down and (counter==0 or counter == 2))):
            temp_start[0] += turning_radius

        #counter:
        # 0 = turn left
        # 1 = turn right
        # 2 = reverse left
        # 3 = reverse right
        return tuple(temp_start)

    def a_star_path_compressor(self,path):
        """Compress the path, ie 3 straight command into 1 big straight command and make straight/reverse command to be destination rather than its current point"""
        path_list = list(map(list, path)) #idk why this works
        length = len(path_list)
        i = 0
        # path_list = list(map(list, path)) #idk why this works
        while(i<length):
            if(path_list[i][1]=='straight' or path_list[i][1]== 'reverse'):
                try:
                    if(path_list[i][1]==path_list[i+1][1]): # if the next is the same type, ie straight, straight then merge then tgt
                        path_list.remove(path_list[i])
                        length -=1
                        continue
                    # this ensures the straight or reverse will always reach its destination rather than stopping 1 grid before
                    elif(path_list[i+1][1]=='left' or path_list[i+1][1]=='right' or path_list[i+1][1]=='reverse left' or path_list[i+1][1]=='reverse right'):
                        path_list[i][0]= path_list[i+1][0]
                except IndexError:
                    pass
            i += 1
        return path_list
    
    def a_star_dubins(self,path_list,path_taken,algorithm,dubin,car,invalid_positions,grid_coordinates):
            """Check at every point of a* whether it can be cutshort by dubins"""
            print("astar dubin")
            next_pos = path_taken
            a_star_path = []
            destinations= []
            message_list = []
            print()
            for counter in range(len(path_list)-1):
                point = path_list[counter]
                car_current_pos = point[0]
                compiled_path_lists = algorithm.Dubin.get_shortest_path(dubin, car, path_taken, car_current_pos, next_pos)
                for path in compiled_path_lists:
                    # obtain list of coordinates travelled for 1 specific path type e.g. RSR
                    print(".........", end = '')
                    coordinates_list = car.move_car_dubin(path[0][0], path[0][1], next_pos, path[2],car_current_pos)
                    if(dubin.check_path_valid(coordinates_list, invalid_positions, grid_coordinates)):
                        destinations.extend(coordinates_list)
                        message_list.extend(path[3])
                        print("a_star dubin Path found!")
                        a_star_path.append(point)
                        return destinations, message_list, a_star_path
                a_star_path.append(point)
            print("No a_star_dubin")
            return None, None, None
    
    def adjust_to_irl_turning_radius(self, path_list):
        """Adds in extra movement to adjust for shorter turning radius"""
        left_turning_radius_diff = settings.a_star_turning_radius - settings.left_turn_radius
        right_turning_radius_diff = settings.a_star_turning_radius - settings.right_turn_radius
        temp_list = []
        #if the last movement is a turn, a straight or reverse need to be added to reach the target turning point
        last = len(path_list)-1
        if(path_list[last][1]=='left' or path_list[last][1]=='right'):
            target = self.move_turn(path_list[last][0],settings.a_star_turning_radius,path_list[last][1],False)
            target_coor = [target[0],target[1],target[2]]
            # path_list.append([target_coor, 'straight', None])
            path_list.append([target_coor, 'straight', None])

        elif(path_list[last][1]=='reverse left' or path_list[last][1]=='reverse right'):
            target = self.move_turn(path_list[last][0],settings.a_star_turning_radius,path_list[last][1],True)
            target_coor = [target[0],target[1],target[2]]
            path_list.append([target_coor, 'reverse', None])

        # if movement is a turn, change the starting point and center of the turn to compensate for the reduced turning radius
        # adjusted turning start and end point is still align to the same axis as the original therefore no straight path is added if the next path is a straight or reverse movement
        # for path, next_path in zip(path_list,path_list[1:]):
        for counter in range(len(path_list)):
            path = list(path_list[counter])
            path[0] = list(path[0])   
            if(path[2]!=None):
                path[2] = list(path[2])

            angle= path[0][2]
            if(path[1]=='left' or path[1]=='reverse left'):
                offset = left_turning_radius_diff
            elif(path[1]=='right' or path[1]=='reverse right'):
                offset = right_turning_radius_diff

            if(path[1]=='left' or path[1]=='right'):
                if(angle == settings.right):
                    path[0][0] += offset
                    path[2][0] += offset
                    if(path[1]=='left'):
                        path[2][1] += offset
                    else:
                        path[2][1] -= offset

                elif(angle == settings.up):
                    path[0][1] -= offset
                    path[2][1] -= offset
                    if(path[1]=='left'):
                        path[2][0] += offset
                    else:
                        path[2][0] -= offset

                elif(angle == settings.left):
                    path[0][0] -= offset
                    path[2][0] -= offset
                    if(path[1]=='left'):
                        path[2][1] -= offset
                    else:
                        path[2][1] += offset

                elif(angle == settings.down):
                    path[0][1] += offset
                    path[2][1] += offset
                    if(path[1]=='left'):
                        path[2][0] -= offset
                    else:
                        path[2][0] += offset
                temp_list.append(path)
                try:
                    next_path = path_list[counter+1]
                    if(next_path[1]== 'left' or next_path[1]== 'right'):
                        #insert a straight movement infront of path to make sure the car can go to the next turning point
                        # temp_list.insert(counter+1,[next_path[0], 'straight', None])
                        temp_list.append([next_path[0], 'straight', None])
                except IndexError:
                    pass

            elif(path[1]=='reverse left' or path[1]=='reverse right'):
                if(angle == settings.right):
                    path[0][0] -= offset
                    path[2][0] -= offset
                    if(path[1]=='reverse left'):
                        path[2][1] += offset
                    else:
                        path[2][1] -= offset

                elif(angle == settings.up):
                    path[0][1] += offset
                    path[2][1] += offset
                    if(path[1]=='reverse left'):
                        path[2][0] += offset
                    else:
                        path[2][0] -= offset

                elif(angle == settings.left):
                    path[0][0] += offset
                    path[2][0] += offset
                    if(path[1]=='reverse left'):
                        path[2][1] -= offset
                    else:
                        path[2][1] += offset
                    
                elif(angle == settings.down):
                    path[0][1] -= offset
                    path[2][1] -= offset
                    if(path[1]=='reverse left'):
                        path[2][0] -= offset
                    else:
                        path[2][0] += offset

                temp_list.append(path)
                try:
                    next_path = path_list[counter+1]
                    if(next_path[1]== 'reverse left' or next_path[1]== 'reverse right'):
                        #insert a straight movement infront of path
                        # temp_list.insert(counter+1,[next_path[0], 'reverse', None])
                        temp_list.append([next_path[0], 'reverse', None])
                except IndexError:
                    pass
            else:
                temp_list.append(path)
            
            # counter +=1
        
        #if the first movement is a turn, a straight or reverse need to be added to reach the offset turning point
        if(path_list[0][1]=='left' or path_list[0][1]=='right'):
            # path_list.insert(0,[path_list[0][0], 'straight', None])
            temp_list.insert(0,[temp_list[0][0], 'straight', None])
        elif(path_list[0][1]=='reverse left' or path_list[0][1]=='reverse right'):
            # path_list.insert(0,[path_list[0][0], 'reverse', None])
            temp_list.insert(0,[temp_list[0][0], 'reverse', None])
        return temp_list


    def coordinates_list_to_message(self,current,path_list):
        """Convert an a* path to message format"""
        temp_current= current.copy()
        message_list=[]
        turning_radius = 2 * settings.grid_size
        for path in path_list:
            if(path[1]== 'straight'):
                length = self.heuristic(temp_current,path[0]) / settings.grid_size * 10
                message_list.extend(['c:FS' + str(int((length * 1000))).zfill(6)])
                temp_current = path[0]
            elif(path[1]== 'reverse'):
                length = self.heuristic(temp_current,path[0]) / settings.grid_size * 10
                message_list.extend(['c:BS' + str(int((length * 1000))).zfill(6)])
                temp_current = path[0]
            elif(path[1]== 'left'):
                message_list.extend(['c:FL090000']) #forward left 90 deg
                temp_current = self.move_turn(path[0], turning_radius, 'L', False)
            elif(path[1]== 'right'):
                message_list.extend(['c:FR090000']) #forward right 90 deg
                temp_current = self.move_turn(path[0], turning_radius, 'R', False)
            elif(path[1]== 'reverse left'):
                message_list.extend(['c:BL090000']) #backwards left 90 deg
                temp_current = self.move_turn(path[0], turning_radius, 'L', True)
            elif(path[1]== 'reverse right'):
                message_list.extend(['c:BR090000']) #backwards right 90 deg
                temp_current = self.move_turn(path[0], turning_radius, 'R', True)

        return message_list