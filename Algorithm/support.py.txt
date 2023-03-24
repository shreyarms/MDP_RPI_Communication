import settings
class support:

    def convert_coordinates(self, coord_list):
        obstacle_positions = []
        for obs in coord_list:
            x = int(obs[0])
            y = int(obs[1])
            if obs[-1] == 3:
                direction = settings.down
            elif obs[-1] == 4:
                direction = settings.left
            elif obs[-1] == 1:
                direction = settings.up
            else:
                direction = settings.right
                
            obstacle = [x, 19 - y, direction]
            obstacle_positions.append(obstacle)
            
        return obstacle_positions