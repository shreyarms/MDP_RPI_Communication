import pygame
import sys
import os
import math
from Entities.grid import *
import random
from difflib import get_close_matches as gcm
from Entities.car import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

HALFPI = math.pi * 0.5
STOPDISTANCE = 3

class Dubin:
    def __init__(self) -> None:
        pass

    def read_obstacles(self):
        count = int(input("Obstacle count: "))
        obstacle_positions = []
        for index in range(count):
            print("Coordinates are 1 - indexed")
            while True:
                x = int(input("X Coordinate: "))
                if 1 <= x <= 20:
                    x -= 1
                    break
            while True:
                y = int(input("Y Coordinate: "))
                if 1 <= y <= 20:
                    y = 20 - y
                    break
            while True:
                directions = ['up', 'down', 'left', 'right']
                z = input("Z Orientation: ")
                direction = str("".join(gcm(z, directions, 1, 0.7)))
                
                if direction == directions[0]:
                    z = settings.up
                    break
                elif direction == directions[1]:
                    z = settings.down
                    break
                elif direction == directions[2]:
                    z = settings.left
                    break
                elif direction == directions[3]:
                    z = settings.right
                    break
                
            print(f"Appended ({x}, {y}, {z}) successfully")
            obstacle_positions.append([x,y,z])

        return obstacle_positions
    
    def random_obstacle_generator(self, obstacle_count):
        obstacle_positions = []
        direction = [settings.up, settings.down, settings.left, settings.right]
        while obstacle_count != 0:
            z = direction[random.randint(0,3)]
            
            if z == settings.up:
                x = random.randint(0,19)
                y = random.randint(3,19)
                target_point = [x, y - STOPDISTANCE]
            elif z == settings.down:
                x = random.randint(0,19)
                y = random.randint(0,16)
                target_point = [x, y + STOPDISTANCE]

            if z == settings.right:
                x = random.randint(0,16)
                y = random.randint(0,19)
                target_point = [x + STOPDISTANCE, y]
            
            if z == settings.left:
                x = random.randint(3,19)
                y = random.randint(0,19)
                target_point = [x - STOPDISTANCE, y]

            # obstacles not generated in starting area
            if 0 <= x <= 4 and 15 <= y <= 19:
                continue

            tx = target_point[0]
            ty = target_point[1]
            flag = True
            
            if 0 <= tx <= 4 and 15 <= ty <= 19:
                continue
            
            if 1 < tx < 18 and 1 < ty < 18:
                for obstacle in obstacle_positions:
                    if obstacle[0] - 3 <= tx <= obstacle[0] + 3 and obstacle[1] - 3 <= ty <= obstacle[1] + 3:
                        flag = False
                        break
            
                if flag == True:
                    obstacle_positions.append([x,y,z])
                    obstacle_count -= 1

        return obstacle_positions
    
    def check_obstacle(self,coordinates_list,obs_invalid_positions):
        for coordinate in coordinates_list:
        # if invalid coordinate is found, we can eliminate the whole path
        # cross check every point with every invalid range
            for invalid in obs_invalid_positions:
                # invalid coordinates stored as [bottom_left_x, bottom_left_y, top_right_x, top_right_y]
                try: # prevents strs like 'straight' from giving error
                    # one invalid point is found -> whole path is discarded
                    if(invalid[0] < coordinate[0] and coordinate[0] < invalid[2] and invalid[3] < coordinate[1] and coordinate[1] < invalid[1]):
                        return False
                except TypeError: 
                    pass
        return True
    #shortest overall path for 6 obstacles
    def shortest_path(self, obstacle_positions, target_positions):
        path_taken = []
        while True:
            if len(path_taken) == len(obstacle_positions):
                break
            euclidean_distance = 999
            next_x = 0
            next_y = 0
            for target in target_positions:
                # find shortest euclidean distance from current point to next point
                distance = math.dist([target[0],target[1]], [settings.Car_current_x, settings.Car_current_y])
                if distance < euclidean_distance:
                    euclidean_distance = distance
                    next_x = target[0]
                    next_y = target[1]
                    direction = target[2]

            # set current car coordinates to next obstacle
            settings.Car_current_x = next_x
            settings.Car_current_y = next_y
                
            path_taken.append([next_x, next_y, direction])
            target_positions.remove([next_x,next_y, direction])
        return path_taken
   
    def return_message(path_direction, value):
        return 'c:F' + path_direction.upper() + str(int(round(value * 1000))).zfill(6)

    def rotate_vector(self, vector, direction, radians):
        new_x = vector[0] * math.cos(radians) - vector[1] * math.sin(radians)
        new_y = vector[0] * math.sin(radians) + vector[1] * math.cos(radians)

        if direction == 'CW':
            new_x, new_y = -new_x, -new_y

        return [new_x, new_y]

    def calculate_arc_length(self, startpoint, endpoint, circle, turn_type):
        center_x, center_y = circle[0], circle[1]
        start_x, start_y = startpoint[0], startpoint[1]
        end_x, end_y = endpoint[0], endpoint[1]
        v1 = [start_x - center_x, start_y - center_y]
        v2 = [end_x - center_x, end_y - center_y]

        alpha = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])
        if turn_type == 'L':
            radius = settings.left_turn_radius
            if alpha < 0:
                alpha += 2 * math.pi
        elif turn_type == 'R':
            radius = settings.right_turn_radius
            if alpha > 0:
                alpha -= 2 * math.pi
        alpha *= -1
        alpha_tmp = 360 - abs(math.degrees(alpha))
        arc_length = alpha_tmp * radius / 360
        return arc_length, alpha
    
    def calculate_time_taken_arc(self, arc_length, turn_type):
        if turn_type == 'R':
            return arc_length / settings.right_angular_speed 
        return arc_length / settings.left_angular_speed

    # shortest path from obstacle to obstacle wrt time
    def get_shortest_path(self, car, target, car_current_pos, next_pos):
        compiled_path_details = []
        path_types = [Dubin.RSR, Dubin.LSL, Dubin.LSR, Dubin.RSL]
        path_names = ["RSR", "LSL", "LSR", "RSL"]
        
        # path_types = [Dubin.RSR, Dubin.LSL]
        # path_names = ["RSR", "LSL"]
        
        # path_types = [Dubin.LSR, Dubin.RSL]
        # path_names = ["LSR", "RSL"]

        # path_types = [Dubin.LSR]
        # path_names = ["LSR"]

        # path_types = [Dubin.RSL]
        # path_names = ["RSL"]

        for index, path in enumerate(path_types):
            #initialise radius and angular velocity values to original values
            turn_type_one = path_names[index][0]
            turn_type_two = path_names[index][2]
            chosen_path = path_names[index]
            if turn_type_one == 'R':
                circle1 = car.find_circle(car_current_pos, turn_type_one, settings.right_turn_radius)
            else: 
                circle1 = car.find_circle(car_current_pos, turn_type_one, settings.left_turn_radius)

            if turn_type_two == 'R':
                circle2 = car.find_circle(target, turn_type_two, settings.right_turn_radius)
            else:
                circle2 = car.find_circle(target, turn_type_two, settings.left_turn_radius)
            
            coordinates, distance, details = path(self, circle1, circle2, car_current_pos, next_pos)
            print(chosen_path, distance)
            print()
            if distance == 9999:
                continue
            message = []
            alpha_one = 360 - abs(math.degrees(details[0]))
            alpha_three = 360 - abs(math.degrees(details[2]))
            length = details[1] / settings.grid_size * 10

            if alpha_one != 360 and alpha_one != 0:
                message_one = Dubin.return_message(chosen_path[0], alpha_one)
                message.append(message_one)
            message_two = Dubin.return_message(chosen_path[1], length)
            message.append(message_two)
            if alpha_three != 360 and alpha_three != 0:
                message_three = Dubin.return_message(chosen_path[2], alpha_three)
                message.append(message_three)
            
            compiled_path_details.append([coordinates, distance, chosen_path, message])
        # sort path according to time
        def takeSecond(elem):
            return elem[1]
        
        compiled_path_details.sort(key = takeSecond, reverse = False)

        return compiled_path_details
    
    def RSR(self, circle1, circle2, current_pos, next_pos):
        p1 = pygame.math.Vector2(*circle1) #center coordinates
        p2 = pygame.math.Vector2(*circle2) #center coordinates
        length = p2.distance_to(p1)
        v1 = p2 - p1
        v2 = Dubin.rotate_vector(self, v1, 'CW', HALFPI) # we are using clockwise rotation
        if length != 0:
            pt1_x = p1[0] + settings.right_turn_radius/length * v2[0]
            pt1_y = p1[1] + settings.right_turn_radius/length * v2[1]
        else:
            pt1_x = p1[0]
            pt1_y = p1[1]
        pt1 = [pt1_x,pt1_y]
        pt2 = pt1 + v1

        distance = length
        startpoint = [current_pos[0], current_pos[1]]
        #calculate arc length for circle1
        arc_length, alpha_one = Dubin.calculate_arc_length(self, startpoint, pt1, p1, 'R')
        distance += arc_length

        endpoint = [next_pos[0], next_pos[1]]
        #calculate arc_length for circle2
        arc_length, alpha_two = Dubin.calculate_arc_length(self, pt2, endpoint, p2, 'R')
        distance += arc_length

        return [pt1,pt2], distance, [alpha_one, length, alpha_two] #the start and end point of the line connecting the two circles
    
    def LSL(self, circle1, circle2, current_pos, next_pos):
        p1 = pygame.math.Vector2(*circle1) #center coordinates
        p2 = pygame.math.Vector2(*circle2) #center coordinates

        length = p2.distance_to(p1)
        v1 = p2 - p1
        v2 = Dubin.rotate_vector(self, v1, 'ACW', HALFPI) # we are using anti-clockwise rotation

        if length != 0:
            pt1_x = p1[0] + settings.left_turn_radius/length * v2[0]
            pt1_y = p1[1] + settings.left_turn_radius/length * v2[1]
        else:
            pt1_x = p1[0]
            pt1_y = p1[1]
        pt1 = [pt1_x,pt1_y]
        pt2 = pt1 + v1

        distance = length
        # print("Length: ", length)
        startpoint = [current_pos[0], current_pos[1]]
        #calculate arc length for circle1
        arc_length, alpha_one = Dubin.calculate_arc_length(self, startpoint, pt1, p1, 'L')
        distance += arc_length
        # print("Arc Length 1: ", arc_length, alpha_one)

        endpoint = [next_pos[0], next_pos[1]]
        #calculate arc_length for circle2
        arc_length, alpha_two = Dubin.calculate_arc_length(self, pt2, endpoint, p2, 'L')
        distance += arc_length
        # print("Arc Length 2:", arc_length, alpha_two)

        return [pt1,pt2], distance, [alpha_one, length, alpha_two] #the start and end point of the line connecting the two circles
    
    def RSL(self, circle1, circle2, current_pos, next_pos):
        # print("current pos= ", current_pos, ", next_pos= ", next_pos, ", circle1= ",circle1, ", circle2= ", circle2)
        p1 = pygame.math.Vector2(*circle1) #center coordinates
        p2 = pygame.math.Vector2(*circle2) #center coordinates
        # print("p1= ",p1,", p2= ",p2)
        d = p2.distance_to(p1)
        combined_radius = settings.left_turn_radius + settings.right_turn_radius

        if d < combined_radius:
            return [999,999], 9999, []
        else:
            length = math.sqrt(d ** 2 - combined_radius ** 2) # length of straight line travel
            delta = math.acos((combined_radius) / d)
        v1 = p2 - p1
        # print("left= ",settings.left_turn_radius,", right= ",settings.right_turn_radius, ", d= ",d, ", delta= ",delta, "length= ", length)
        # counterclockwise rotation (x, y) > (-y, x) but we are using clockwise (x, y) > (y, -x)
        v2 = Dubin.rotate_vector(self, v1, 'CW', math.pi - delta)

        pt1x = p1[0] + settings.right_turn_radius/d * v2[0]
        pt1y = p1[1] + settings.right_turn_radius/d * v2[1]  
        
        #reverse vector v2
        v3 = Dubin.rotate_vector(self, v2, 'ACW', math.pi)

        pt2x = p2[0] + settings.right_turn_radius/d * v3[0]
        pt2y = p2[1] + settings.right_turn_radius/d * v3[1]

        pt1 = [pt1x, pt1y]
        pt2 = [pt2x, pt2y]

        # print("distance btw pt1 and pt2: ", pygame.math.Vector2(pt1).distance_to(pygame.math.Vector2(pt2)))
        # print("pt1 = ", pt1, ", pt2= ", pt2, ", v1= ",v1,", v2= ",v2,", v3= ",v3)
        distance = length
        # print("Length: ", length)
        #calculate arc length for circle 1
        startpoint = [current_pos[0], current_pos[1]]
        arc_length, alpha_one = Dubin.calculate_arc_length(self, startpoint, pt1, p1, 'R')
        distance += arc_length
        # print("Arc Length 1:", arc_length)

        #calculate arc length for circle 2
        endpoint = [next_pos[0], next_pos[1]]
        arc_length, alpha_two = Dubin.calculate_arc_length(self, pt2, endpoint, p2, 'L')
        distance += arc_length
        # print("Arc Length 2:", arc_length)

        return [pt1, pt2], distance, [alpha_one, length, alpha_two]
    
    def LSR(self, circle1, circle2, current_pos, next_pos):
        p1 = pygame.math.Vector2(*circle1) #center coordinates
        p2 = pygame.math.Vector2(*circle2) #center coordinates
        d = p2.distance_to(p1)
        combined_radius = settings.left_turn_radius + settings.right_turn_radius

        if d < combined_radius:
            return [999,999], 9999, []
        else:
            length = math.sqrt(d ** 2 - combined_radius ** 2) # length of straight line travel
            delta = math.acos((combined_radius) / d)
        v1 = p2 - p1
        # clockwise rotation (x, y) > (y, -x) but we are using anti-clockwise (x, y) > (-y, x)
        v2 = Dubin.rotate_vector(self, v1, 'ACW', delta) 
        # print(v1, v2)
        pt1x = p1[0] + settings.left_turn_radius/d * v2[0]
        pt1y = p1[1] + settings.left_turn_radius/d * v2[1]

        # reverse vector v2
        v3 = Dubin.rotate_vector(self, v2, 'ACW', math.pi)

        pt2x = p2[0] + settings.right_turn_radius/d * v3[0]
        pt2y = p2[1] + settings.right_turn_radius/d * v3[1]

        pt1 = [pt1x, pt1y]
        pt2 = [pt2x, pt2y]

        distance = length
        #calculate arc length for circle 1
        startpoint = [current_pos[0], current_pos[1]]
        arc_length, alpha_one = Dubin.calculate_arc_length(self, startpoint, pt1, p1, 'L')
        distance += arc_length

        #calculate arc length for circle 2
        endpoint = [next_pos[0], next_pos[1]]
        arc_length, alpha_two = Dubin.calculate_arc_length(self, pt2, endpoint, p2, 'R')
        distance += arc_length

        return [pt1, pt2], distance, [alpha_one, length, alpha_two]  

    def check_path_valid(self,coordinates_list, obs_invalid_positions,grid):
        # return true only if both valid
        if(coordinates_list== None):
            return False
        return (self.check_arena(coordinates_list,grid) and self.check_obstacle(coordinates_list, obs_invalid_positions))

    def check_arena(self,coordinates_list,grid_coordinate):
        if coordinates_list == None:
            return False
        top_left = grid_coordinate[0][0].copy()
        top_left[1] -= settings.grid_size
        bottom_right = grid_coordinate[19][19].copy()
        bottom_right[0] += settings.grid_size
        for coordinate in coordinates_list:
            try: # prevents strs like 'straight' from giving error
                if(coordinate[0]<=top_left[0] or coordinate[0]>=bottom_right[0] or coordinate[1]<=top_left[1] or coordinate[1]>=bottom_right[1]):
                    return False
            except TypeError:
                pass
        return True