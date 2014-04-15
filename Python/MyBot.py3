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
        self.ant_objectives = {}
        # track all moves, prevent collisions
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
        orders = {}

        def do_move_direction(loc, direction):
#          if self.DEBUG:
#            self.dbg_file.write('do_move_direction()\n')
          new_loc = ants.destination(loc, direction)
#          if self.DEBUG:
#            self.dbg_file.write('orders.values = {}, new_loc = {} \n'.format(str(orders.values()), str(new_loc)))
          if (ants.unoccupied(new_loc) and new_loc not in orders.values()) and ants.passable(new_loc) and new_loc not in ants.my_hills():
	    ants.issue_order((loc, direction))
            orders[loc] = new_loc
            if self.DEBUG:
              self.dbg_file.write('ant {} is moving to {} \n'.format(str(loc), str(new_loc)))
            return True
          else:
            return False

        def do_move_location(loc, dest):
#          if self.DEBUG:
#            self.dbg_file.write('do_move_location()\n')
          directions = ants.direction(loc, dest)
          for direction in directions:
            if do_move_direction(loc, direction):
              return True
          return False
      
        def get_list_variance(input_list):
          # 1 get the average
          avg = sum(input_list)/len(input_list);
          list_variance = sum((avg - value) ** 2 for value in input_list) / len(input_list)
          return list_variance

        def setup_distances(turn_obj, my_ants):
          # setup food and ants target
          distances = defaultdict(list)
          for ant in my_ants:
            for obj in turn_obj:
              distances[ant].append(ants.distance(ant,obj))
          return distances

        def setup_variances(distances):
          variance = {}
          for ant in distances:
            variance[ant] = get_list_variance(distances[ant])
          return variance
 
        def use_variance(dist, my_ants, sorted_var, turn_objectives):
          used_idx = []
          ant_objective = {}
          for act_ant in sorted_var:
            # get the closest objective
            index_obj = dist[act_ant].index(min(dist[act_ant]))
            min_val = 0
            while index_obj in used_idx and min_val < 10000000:
              dist[act_ant][index_obj] = 10000000; # setting the min to a very high value
              index_obj = dist[act_ant].index(min(dist[act_ant]))
              min_val = min(dist[act_ant]) 
  	    if min_val < 10000000:
              used_idx.append(index_obj)
              # get the objective relative to that index
              ant_objective[act_ant] = turn_objectives[index_obj]
          return ant_objective

        # not seen territory setup
        for loc in self.unseen[:]:
          if ants.visible(loc):
            self.unseen.remove(loc)
        # setup
	# 1. create 1 vectors with all the objectives (food + enemy hills)
        my_ants = ants.my_ants()
        turn_objectives = ants.food() + [hills[0] for hills in ants.enemy_hills()]
        if self.DEBUG:
          self.dbg_file.write('\nStep 1\n')
          self.dbg_file.write('my_ants = {}\n'.format(str(my_ants)))
          self.dbg_file.write('turn_objectives = {}\n'.format(str(turn_objectives)))
          self.dbg_file.write('self.ant_objectives = {}\n'.format(str(self.ant_objectives)))
	# 2. remove from ant_objective ants close to their objective (1 space as already doing)
        for act_ant in ants.my_ants():
          if act_ant in self.ant_objectives:
            if ants.distance(act_ant, self.ant_objectives[act_ant]) == 1:
              del self.ant_objectives[act_ant]
        if self.DEBUG:
          self.dbg_file.write('\nStep 2\n')
          self.dbg_file.write('self.ant_objectives = {}\n'.format(str(self.ant_objectives)))
	# 3. remove from the objectives the food and enemy hills that are in ant_objectives
        for [rem_ant, obj] in self.ant_objectives:
          turn_objectives.remove(obj)
          my_ants.remove(rem_ant)
        if self.DEBUG:
          self.dbg_file.write('\nStep 3\n')
          self.dbg_file.write('my_ants = {}\n'.format(str(my_ants)))
          self.dbg_file.write('turn_objectives = {}\n'.format(str(turn_objectives)))
	# 4. update ant_objcetives
        dist = setup_distances(turn_objectives, my_ants)
        var  = setup_variances(dist) 
        sorted_var = sorted(var, key=var.get, reverse=True)
        if self.DEBUG:
          self.dbg_file.write('\nStep 4\n')
          self.dbg_file.write('sorted_var = {}\n'.format(str(sorted_var)))
          self.dbg_file.write('dist = {}\n'.format(str(dist)))
	# 5. create ant_objectives
        # get the closest objective
        ant_objective = use_variance(dist, my_ants, sorted_var, turn_objectives)
        if self.DEBUG:
          self.dbg_file.write('\nStep 5\n')
          self.dbg_file.write('ant_objective = {}\n'.format(str(ant_objective)))
          
	# 6. submit ants commands
        for act_ant in ant_objective:
          do_move_location(act_ant, ant_objective[act_ant])
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
