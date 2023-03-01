import pygame
import sys
import os
from collections import deque

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

class Grid:
    def __init__(self) -> None:
        self.grids = self.generate_grids()
        # self.grids = self.generate_grid_rect()

    #generate grid coordinates
    def generate_grids(self): 
        """Generate coordinates for all grids"""
        grids = []
        for i in range(settings.Grid_Count):
            row = []
            for j in range(settings.Grid_Count):
                x, y = ((settings.grid_size * j) + settings.Arena_Offset), ((settings.grid_size * i) + settings.Arena_Offset)
                row.append([x,y])
            grids.append(row)
        return grids

    def generate_grid_rect(self):
        """Generate the rect class for each grid"""
        for row in self.grids:
            for col in row:
                rect = pygame.Rect(0, 0, settings.grid_size, settings.grid_size)
                rect.bottomleft = (col[0],col[1])
                col.append(rect)
        return self.grids
        
    #draw grids
    def draw_grids(self, screen):
        """Draw grids based on the coordinate"""
        for row in self.grids:
            for col in row:
                rect = col[2]
                # rect.bottomleft = (col[0],col[1])
                pygame.draw.rect(screen,[255,255,255],rect,)
                pygame.draw.rect(screen,[0,0,0],rect,width=1)

    def draw_starting_grids(self, screen):
        """Change the color of the starting grids"""
        for i in range(settings.Starting_Grid_Count):
            for j in range(settings.Starting_Grid_Count):
                rect = pygame.Rect(0, 0, settings.grid_size, settings.grid_size)
                rect.bottomleft = [self.grids[i+settings.Grid_Count-settings.Starting_Grid_Count][j][0],self.grids[i+settings.Grid_Count-settings.Starting_Grid_Count][j][1]]
                pygame.draw.rect(screen,[102,178,255],rect,)
                pygame.draw.rect(screen,[0,0,0],rect,width=1)

    #draw arena
    # def draw_arena(self,screen):
    #     arena_surface = pygame.Rect(settings.Arena_Offset_x, settings.Arena_Offset_y, settings.Arena_Size_x, settings.Arena_Size_y)
    #     pygame.draw.rect(screen,[255,255,255],arena_surface)


    # #draw Arena and grids
    def draw(self,screen):
        """Set up the grids and starting grids"""
        self.draw_grids(screen)
        self.draw_starting_grids(screen)

    def grid_to_pixel(self,target_grid):
        """Convert grids to pixel"""
        x = target_grid[0] 
        y = target_grid[1] 
        offset = 0.5*settings.grid_size
        pixel_bottomleft = self.grids[y][x]
        #pixels_center = self.grids[y][x][2].center
        pixels_center = round(pixel_bottomleft[0] + offset), round(pixel_bottomleft[1] - offset)
        return pixels_center




            
