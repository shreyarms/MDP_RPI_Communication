import pygame
import sys
import os
import math 

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

class Obstacle:
    def __init__(self,grids,positions) -> None:
        self.obstacle_coordinates = self.generate_obstacle(grids,positions)
    
    def generate_obstacle(self,grids,positions):
        """Generate obstacle rect"""
        obstacle_coordinates = []
        for obs in positions:
            x = obs[0]
            y = obs[1]
            # if(obs[2]==settings.right):
            #     direction = 0
            # elif(obs[2]==settings.left):
            #     direction = 180
            # elif(obs[2]==settings.down):
            #     direction = -90
            # else: #Up
            #     direction = 90
            # image = pygame.image.load(os.path.join('Simulator','Entities','Assets','Obstacle.png')).convert_alpha()
            # image = pygame.transform.scale(image, (settings.grid_size,settings.grid_size))
            # rotated_obs = pygame.transform.rotate(image, obs[2])
            # rect = rotated_obs.get_rect()
            # rect.bottomleft = (grids[y][x][0],grids[y][x][1])
            
            obstacle_coordinates.append([grids[y][x][0],grids[y][x][1],obs[2]])
        return obstacle_coordinates

    def draw_obstacle(self, surface):
        """Draw obstacle into screen"""
        for obs in self.obstacle_coordinates:
            surface.blit(obs[0], obs[1]) 

    def get_target_pos(self):
        """Get the target position(infront of the image)"""
        target_pos= []
        offset = settings.stop_distance
        for obs in self.obstacle_coordinates:
            temp = list(obs)
            # temp.append(obs[2])
            if(obs[2]==settings.right):  
                temp[2] = 180
                temp[0] = temp[0] + offset     
            elif(obs[2]==settings.left):
                temp[2] = 0
                temp[0] = temp[0] - offset 
            elif(obs[2]==settings.down):
                temp[2] = 90
                temp[1] = temp[1] + offset 
            else: #Up
                temp[2] = -90
                temp[1] = temp[1] - offset
            # x = [temp, obs[2]]
            target_pos.append(temp)
        return target_pos
    
    def edit_target_pos(self, target_pos):
        for target in target_pos:
            direction = target[2]
            if direction == settings.right:
                target[0] -= settings.Car_height / 2
            
            elif(direction == settings.left):
                target[0] += settings.Car_height / 2
            
            elif(direction == settings.down):
                target[1] -= settings.Car_height / 2
            
            else:
                target[1] += settings.Car_height / 2

            target.append(0)

        return target_pos
    def draw_target_pos(self, surface, target_pos):
        """Draw a circle on infront of the obstacles"""
        count = 1 
        for obs in target_pos:
            #pygame.draw.circle(surface, (0, 0, 255), obs, 5)
            font = pygame.font.SysFont(None, 24)
            img = font.render(str(count), True, (0,0,255))
            surface.blit(img, obs)

            count += 1
