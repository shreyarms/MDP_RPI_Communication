import pygame
import sys
import os
import math 

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

class Car:
    def __init__(self, car_starting_pos) -> None:
        self.image = pygame.image.load(os.path.join('Simulator_Pygame','Entities','Assets','Robot.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (settings.Car_width,settings.Car_height))
        self.rect = self.image.get_rect()
        self.current_pos = [car_starting_pos[0], car_starting_pos[1], 90] #based on center of image (x,y,θ)
        self.next_pos = [car_starting_pos[0], car_starting_pos[1], 90]
        # self.current_angle = 90 #initially facing up
        # self.maintain_car(surface)

    def maintain_car(self,surface):
        """Spawns car in its current location"""
        rotated_car = pygame.transform.rotate(self.image, self.current_pos[2])
        self.rect.center = (self.current_pos[0],self.current_pos[1])
        surface.blit(rotated_car, self.rect) 

    def draw_car(self, surface, target_pos,forward):
        """Spawn car in target location"""
        target_pos[0] = round(target_pos[0],3)
        target_pos[1] = round(target_pos[1],3)
        angle = self.calculate_angle(target_pos,forward)
        rotated_car = pygame.transform.rotate(self.image, angle)
        self.rect = rotated_car.get_rect(center = target_pos)
        surface.blit(rotated_car, self.rect)
        self.current_pos[0] = target_pos[0]
        self.current_pos[1] = target_pos[1]
        self.current_pos[2] = angle

    def move_car_a_star(self,current,path):
        current_pos = [current[0],current[1]]
        destinations = []
        for point in path:
            destinations.append(point[1])
            target_pos = [point[0][0],point[0][1]]
            #do straight pathing, maybe reverse?
            if(point[1]=='straight' or point[1]== 'reverse'):
                next_point = self.move_car_straight(current_pos,target_pos)
                destinations.extend(next_point)
            #do forward left/right
            elif(point[1]=='left'):
                # move_car_curve(self, alpha, start, center, turn_direction)
                next_point = self.move_car_curve(90,current_pos,point[2],"left".lower())
                destinations.extend(next_point)
                pass
            elif(point[1]=='right'):
                next_point = self.move_car_curve(-90,current_pos,point[2],"right".lower())
                destinations.extend(next_point)
            #do reverse left/right idk how, maybe merge with
            elif(point[1]=='reverse left'):
                next_point = self.move_car_curve(-90,current_pos,point[2],"right".lower())
                destinations.extend(next_point)
            elif(point[1]=='reverse right'):
                next_point = self.move_car_curve(90,current_pos,point[2],"left".lower())
                destinations.extend(next_point)
            if(destinations[-1]!=None):
                while(destinations and type(destinations[-1])== str):
                    destinations.pop(-1)
                try:
                    if(destinations[-1]!=None):
                        current_pos = destinations[-1].copy()
                except IndexError:
                    pass

        return destinations

    def move_car_dubin(self,pt1,pt2,target_pos,dubin,current_pos):
        #target should be (x,y,direction)

        destinations = [] #a list of coordinates
        x = 0
        y = 1
        p = [current_pos[x],current_pos[y]] #start point
        pt3 = [target_pos[x], target_pos[y]] #end points
        if(dubin == "RSR"):
            p1 = self.find_circle(current_pos,"R", settings.right_turn_radius) #circle at car
            p3 = self.find_circle(target_pos,"R", settings.right_turn_radius) #circle at obstacle   
            #first turn
            alpha = self.calculate_alpha(p,p1,pt1,"right") #calculate alpha of first turn
            next_point = self.move_car_curve(alpha,p,p1,"right")  
            destinations.append("right")             
            destinations.extend(next_point)
            #Straight
            next_point = self.move_car_straight(pt1,pt2)
            destinations.append("straight")   
            destinations.extend(next_point)
            #Second turn
            alpha = self.calculate_alpha(pt2,p3,pt3,"right") #calculate alpha of first turn
            next_point = self.move_car_curve(alpha,pt2,p3,"right")
            destinations.append("right")          
            destinations.extend(next_point)
            return destinations

        elif(dubin == "LSL"):
            p1 = self.find_circle(current_pos,"L", settings.left_turn_radius)
            p3 = self.find_circle(target_pos,"L", settings.left_turn_radius)
            #first turn
            alpha = self.calculate_alpha(p,p1,pt1,"left") #calculate alpha of first turn
            next_point = self.move_car_curve(alpha,p,p1,"left")  
            destinations.append("left")              
            destinations.extend(next_point)
            #Straight
            next_point = self.move_car_straight(pt1,pt2) 
            destinations.append("straight")        
            destinations.extend(next_point)
            #Second turn
            alpha = self.calculate_alpha(pt2,p3,pt3,"left") #calculate alpha of first turn
            next_point = self.move_car_curve(alpha,pt2,p3,"left")                
            destinations.append("left")
            destinations.extend(next_point)
            return destinations

        elif(dubin == "RSL"):
            p1 = self.find_circle(current_pos,"R", settings.right_turn_radius)
            p3 = self.find_circle(target_pos,"L", settings.left_turn_radius)
            #first turn
            alpha = self.calculate_alpha(p,p1,pt1,"right") #calculate alpha of first turn
            next_point = self.move_car_curve(alpha,p,p1,"right")
            destinations.append("right")              
            destinations.extend(next_point)
            #Straight
            next_point = self.move_car_straight(pt1,pt2)
            destinations.append("straight")        
            destinations.extend(next_point)
            #Second turn
            alpha = self.calculate_alpha(pt2,p3,pt3,"left") #calculate alpha of first turn
            next_point = self.move_car_curve(alpha,pt2,p3,"left")
            destinations.append("left")    
            destinations.extend(next_point)
            return destinations

        elif(dubin == "LSR"):
            p1 = self.find_circle(current_pos,"L", settings.left_turn_radius)
            p3 = self.find_circle(target_pos,"R", settings.right_turn_radius)
            #first turn
            alpha = self.calculate_alpha(p,p1,pt1,"left") #calculate alpha of first turn
            next_point = self.move_car_curve(alpha,p,p1,"left")     
            destinations.append("left")           
            destinations.extend(next_point)
            #Straight
            next_point = self.move_car_straight(pt1,pt2)    
            destinations.append("straight")     
            destinations.extend(next_point)
            #Second turn
            alpha = self.calculate_alpha(pt2,p3,pt3,"right") #calculate alpha of first turn
            next_point = self.move_car_curve(alpha,pt2,p3,"right")  
            destinations.append("right")              
            destinations.extend(next_point)
            return destinations

    def move_car_straight(self,current_pos, target_pos):
        """calculate coordinates for movement in a straight line"""
        destinations = [] #a list of coordinates
        current_vector = pygame.math.Vector2(*current_pos)
        target_vector = pygame.math.Vector2(*target_pos)
       
        while(current_vector != target_vector):
            distance = current_vector.distance_to(target_vector)
            direction_vector = (target_vector - current_vector) / distance
            if distance<settings.step_distance:
                new_current = current_vector + direction_vector * distance
            else:
                new_current = current_vector + direction_vector * settings.step_distance
                new_current = [round(new_current[0],3),round(new_current[1],3)]

            destinations.append(new_current)
            current_vector = pygame.math.Vector2(*new_current)

        return destinations

    def move_car_curve(self, alpha, start, center , turn_direction):
        destinations = [] #a list of coordinates
        current_alpha = 0
        start = pygame.math.Vector2(start)
        center = pygame.math.Vector2(center)
        V = pygame.math.Vector2(start - center)
        turn_direction = turn_direction.lower()
        alpha = -alpha
        while(current_alpha != alpha):
            V = pygame.math.Vector2(start - center)
            if(abs(alpha-current_alpha)<settings.angular_speed):
                current_alpha = alpha
            elif(turn_direction=="left"):
                current_alpha -= settings.angular_speed
            elif(turn_direction == "right"):
                current_alpha += settings.angular_speed
            V.rotate_ip(current_alpha)   
            next_coordinates = V + center
            next_coordinates[0] = self.rounding(next_coordinates[0])
            next_coordinates[1] = self.rounding(next_coordinates[1])
            destinations.append(next_coordinates)
        return destinations

    def calculate_alpha(self,start,center,end,direction):
        x = 0
        y = 1
        V1 = [start[x]-center[x], start[y]-center[y]]
        V2 = [end[x]-center[x],end[y]-center[y]]

        alpha = math.atan2(V2[y],V2[x]) - math.atan2(V1[y],V1[x])
        # alpha = math.atan2(abs(V2[x] - V1[x]), abs(V2[y] - V1[y]))

        if(alpha < 0 and direction == "right"):
            alpha += 2 * math.pi
        elif(alpha > 0 and direction == "left"):
            alpha -= 2 * math.pi   
        alpha *= -1

        return math.degrees(alpha)

    def find_circle(self,point,turn,radius):
        #target should be (x,y,direction)
        center = [point[0],point[1]]
        if turn == 'R':
            if point[2] == settings.left:
                center[1] -= radius
            elif point[2] == settings.up:
                center[0] += radius
            elif point[2] == settings.right:
                center[1] += radius
            else:
                center[0] -= radius
        else:
            if point[2] == settings.left:
                center[1] += radius
            elif point[2] == settings.up:
                center[0] -= radius
            elif point[2] == settings.right:
                center[1] -= radius
            else:
                center[0] += radius
            
        return center

    def calculate_angle(self, target_pos, forward):
        """Calculate angle difference from current pos to target pos"""
        if(forward):
            center = pygame.math.Vector2(*(self.current_pos[0],self.current_pos[1]))
            end = pygame.math.Vector2(*target_pos)
        else:
            end = pygame.math.Vector2(*(self.current_pos[0],self.current_pos[1]))
            center = pygame.math.Vector2(*target_pos)
        if(center == end):
            return self.current_pos[2]
        start = center.copy()
        start[1] -= end.distance_to(center)
        alpha = self.calculate_alpha(start,center,end,"left")
        alpha += 90
        # if(alpha >=360):
        #     alpha -=360
        if(alpha >180):
            alpha -= 360
        return alpha

    def reverse(self,current,reverse_distance):
        """Generate coordinates for reversing"""
        target = current.copy()
        if(current[2]==settings.up):
            target[1] += reverse_distance
        elif(current[2]==settings.right):
            target[0] -= reverse_distance
        elif(current[2]==270 or current[2]== settings.down):
            target[1] -= reverse_distance 
        elif(current[2]==settings.left):
            target[0] += reverse_distance
        destination = self.move_car_straight([current[0],current[1]],[target[0],target[1]])
        return destination, target

    def draw_car_reverse(self, surface, target_pos):
        """Spawn car in target location maintaining the same angle"""
        angle = self.current_pos[2]
        rotated_car = pygame.transform.rotate(self.image, angle)
        self.rect = rotated_car.get_rect(center = target_pos)
        surface.blit(rotated_car, self.rect)
        self.current_pos[0] = target_pos[0]
        self.current_pos[1] = target_pos[1]
        self.current_pos[2] = angle

    def rounding(self,value):
        value_up = math.ceil(value)
        value_down = math.floor(value)
        if(value_up-value>=value-value_down):
            return value_down
        else:
            return value_up
