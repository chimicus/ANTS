#!/usr/bin/env python
from ants import *
from collections import defaultdict

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
class MyBot:
    

    def __init__(self):
        # define class level variables, will be remembered between turns
        self.DEBUG = True
        if self.DEBUG:
          self.dbg_file = open('local_debug.txt', 'w') 
        self.possible_directions = ['n' , 'w' , 's' , 'e']
        self.turn = 0
        pass
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        self.unseen = []
        self.turn += 1
        for row in range(ants.rows):
          for col in range(ants.cols):
            self.unseen.append((row,col))
        pass
    
    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        if self.DEBUG:
          self.dbg_file.write('turn %d\n' % self.turn)
        self.turn += 1
        # track all moves, prevent collisions
        orders = {}

        def do_move_direction(loc, direction):
          new_loc = ants.destination(loc, direction)
          if (ants.unoccupied(new_loc) and new_loc not in orders) and ants.passable(new_loc) and new_loc not in ants.my_hills():
	    ants.issue_order((loc, direction))
            orders[new_loc] = loc
            if self.DEBUG:
              self.dbg_file.write('orders[{}] = {} \n'.format(str(new_loc), str(loc)))
            return True
          else:
            return False

        def do_move_location(loc, dest):
          directions = ants.direction(loc, dest)
          for direction in directions:
            if do_move_direction(loc, direction):
              return True
          return False
      
        def do_get_alternate_dir(ant, first_dir):
          new_dir = self.possible_directions[random.randint(0,3)]          
          while new_dir == first_dir:
            new_dir = self.possible_directions[random.randint(0,3)]          
          if do_move_direction(ant, new_dir):
            return True
          return False

        def get_list_variance(input_list):
          # 1 get the average
          avg = sum(input_list)/len(input_list);
          list_variance = sum((avg - value) ** 2 for value in input_list) / len(input_list)
          return list_variance

        def setup_distances():
          # setup food and ants target
          distances = defaultdict(list)
          for ant in ants.my_ants():
            for food in ants.food():
              distances[ant].append(ants.distance(ant,food))
              if self.DEBUG:
                self.dbg_file.write('target[{}] = {} \n'.format(str(ant), str(distances[ant])))
            for hill_loc in ants.enemy_hills():
              distances[ant].append(ants.distance(ant,hill_loc))
              if self.DEBUG:
                self.dbg_file.write('target[{}] = {} \n'.format(str(ant), str(distances[ant])))
#            for unseen in self.unseen:
#              distances[ant].append(ants.distance(ant,unseen))
#              if self.DEBUG:
#                self.dbg_file.write('target[{}] = {} \n'.format(str(ant), str(distances[ant])))
            # this is the heavy part, drop it if we are going to run out of time!
            if ants.time_remaining() < 10:
              break;
          return distances

        def setup_variances(distances):
          variance = {}
          for ant in distances:
            variance[ant] = get_list_variance(distances[ant])
            if self.DEBUG:
              self.dbg_file.write('variance[{}] = {} \n'.format(str(ant), str(variance[ant])))
          return variance
 
        def use_variance(dist, used_idx):
          # get the closest objective
          index_obj = dist[act_ant].index(min(dist[act_ant]))
          min_val = 0
          while index_obj in used_idx and min_val < 10000000:
            dist[act_ant][index_obj] = 10000000; # setting the min to a very high value
            index_obj = dist[act_ant].index(min(dist[act_ant]))
            min_val = min(dist[act_ant])         
          used_idx.append(index_obj)
          # get the objective relative to that index
          if index_obj >= enemy_hill_offset:
          # objectie is an enemy hill
            ant_objective = hills_vect[index_obj]
          else:
          # objective is food
            ant_objective = food_vect[index_obj]
          return [used_idx, ant_objective]

        # not seen territory setup
        for loc in self.unseen[:]:
          if ants.visible(loc):
            self.unseen.remove(loc)
        # setup
        dist = setup_distances()
        ants.time_remaining()
        var  = setup_variances(dist) 
        sorted_var = sorted(var, key=var.get, reverse=True)
        if self.DEBUG:
          self.dbg_file.write('sorted_var = {}\n'.format(str(sorted_var)))
        food_vect = ants.food()
        hills_vect = ants.enemy_hills() 
        enemy_hill_offset = len(food_vect)
        # main cycle, cycle trough all the ants
        used_idx = []
        # problemi su questo if
        if not sorted_var:
          do_move_location(act_ant, self.unseeni[random.randint(0, len(self.unseen-1))])
        else:
          for act_ant in sorted_var:
            # get the closest objective
            [used_idx, ant_objective] = use_variance(dist, used_idx)
          do_move_location(act_ant, ant_objective)
        if self.DEBUG:
          self.dbg_file.write('\n\n\n')
          self.dbg_file.flush()

if __name__ == '__main__':
    # psyco will speed up python a little, but is not needed
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        Ants.run(MyBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
