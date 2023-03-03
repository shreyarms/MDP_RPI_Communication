#Pygames
import math
Scaling_Factor = 6

#Window Setting
Window_Size_x = 1000
Window_Size_y = 650
Window_Size = Window_Size_x,Window_Size_y

#Arena Settings
Arena_Offset = 50 #how far from left border
Arena_Size_x = Window_Size_x - 2 * Arena_Offset
Arena_Size_y = Window_Size_y - 2 * Arena_Offset
Arena_Size = Arena_Size_x, Arena_Size_y


#Grid Settings
Grid_Count = 20 #20x20
grid_size = Arena_Size_y//Grid_Count
grid_size = grid_size
Grid_Size = (grid_size,grid_size)

#obstacle Settings
stop_distance = 4* grid_size #car is 2 grid (20cm) away from image + 1 (10cm) grid as position is center of car 
car_length = 2.5 * grid_size

#Starting Grid Settings
Starting_Grid_Count = 5

#Car settings
Car_starting_x = 1 # column
Car_starting_y = 19 # row

Car_current_x = Car_starting_x
Car_current_y = Car_starting_y
Car_next_x = Car_current_x
Car_next_y = Car_current_y
Car_width = 3 * grid_size #Car is 3x3 grid big
Car_height = 3 * grid_size
step_distance = grid_size/10 * 2 #how fast the car moves 2cm/sec

irl_right_turn_radius = 2.6 #change this should turning radius change
irl_left_turn_radius = 2.5 #change this should turning radius change
right_turn_radius =  irl_left_turn_radius * grid_size
left_turn_radius = irl_right_turn_radius * grid_size
a_star_turning_radius = max(math.ceil(irl_left_turn_radius),math.ceil(irl_right_turn_radius)) * grid_size

right_angular_speed = step_distance / right_turn_radius * 180 / math.pi
left_angular_speed = step_distance / left_turn_radius * 180 / math.pi
angular_speed = right_angular_speed # temporary



#Target coordinate
#Curved line
target_pos = (Arena_Offset + 10.5 * grid_size, Arena_Offset + 3.5 * grid_size )
starting_pos = (Car_starting_x, Car_starting_y) #for bezier
intermediate_pos = (Arena_Offset + 1.5 * grid_size , Arena_Offset + 3.5 * grid_size ) #for bezier

#Direction
left = 180
up = 90
right = 0
down = -90