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
          new_loc = ants.destination(loc, direction)
          if (ants.unoccupied(new_loc) and new_loc not in orders.values()) and ants.passable(new_loc) and new_loc not in ants.my_hills():
	    ants.issue_order((loc, direction))
            orders[loc] = new_loc
            if self.DEBUG:
              self.dbg_file.write('orders[{}] = {} \n'.format(str(loc), str(new_loc)))
            return True
          else:
            return False

        def do_move_location(loc, dest):
          directions = ants.direction(loc, dest)
          if self.DEBUG:
            self.dbg_file.write('do_move_location dest = {}\n'.format(str(dest)))
          for direction in directions:
            if do_move_direction(loc, direction):
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
            if ant in self.ant_objectives:
              if ants.distance(ant, self.ant_objectives[ant]) == 1:
                if self.DEBUG:
                  self.dbg_file.write('removing self.ant_objectives[{}], ant = {}\n'.format(str(self.ant_objectives[ant]), str(ant)))
                del self.ant_objectives[ant]
            if ant not in self.ant_objectives:
              for food in ants.food():
                distances[ant].append(ants.distance(ant,food))
                if self.DEBUG:
                  self.dbg_file.write('target[{}] = {} \n'.format(str(ant), str(distances[ant])))
              for hill_loc in ants.enemy_hills():
                distances[ant].append(ants.distance(ant,hill_loc[0]))
                if self.DEBUG:
                  self.dbg_file.write('target[{}] = {} \n'.format(str(ant), str(distances[ant])))
#              for unseen in self.unseen:
#                distances[ant].append(ants.distance(ant,unseen))
#                if self.DEBUG:
#                  self.dbg_file.write('target[{}] = {} \n'.format(str(ant), str(distances[ant])))
              # this is the heavy part, drop it if we are going to run out of time!
              if ants.time_remaining() < 10:
                break;
            else:
              new_dir = self.ant_objectives[ant]
              del self.ant_objectives[ant]
              do_move_location(ant, new_dir)
          return distances

        def setup_variances(distances):
          variance = {}
          for ant in distances:
            variance[ant] = get_list_variance(distances[ant])
            if self.DEBUG:
              self.dbg_file.write('variance[{}] = {} \n'.format(str(ant), str(variance[ant])))
          return variance
 
        def use_variance(dist, used_idx):
          food_vect = ants.food()
          hills_vect = ants.enemy_hills() 
          enemy_hill_offset = len(food_vect)
          # get the closest objective
          index_obj = dist[act_ant].index(min(dist[act_ant]))
          min_val = 0
          ant_objective = []
          while index_obj in used_idx and min_val < 10000000:
            dist[act_ant][index_obj] = 10000000; # setting the min to a very high value
            index_obj = dist[act_ant].index(min(dist[act_ant]))
            min_val = min(dist[act_ant]) 
	  if min_val < 10000000:
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
        var  = setup_variances(dist) 
        sorted_var = sorted(var, key=var.get, reverse=True)
        if self.DEBUG:
          self.dbg_file.write('sorted_var = {}\n'.format(str(sorted_var)))
        used_idx = []
        if self.DEBUG:
          self.dbg_file.flush()
        for act_ant in ants.my_ants():
          if act_ant in sorted_var:
            # get the closest objective
            [used_idx, ant_objective] = use_variance(dist, used_idx)
	    if not ant_objective:
              do_move_location(act_ant, self.unseen[random.randint(0, len(self.unseen) - 1)])
              if self.DEBUG:
                self.dbg_file.write('while ant {} is using a random point\n'.format(str(act_ant)))
	    else:
              do_move_location(act_ant, ant_objective)
              # write the objective to the list of objectives
              new_loc = orders[act_ant]
              self.ant_objectives[new_loc] = ant_objective
              if self.DEBUG:
                self.dbg_file.write('ant {} is using objective {}\n'.format(str(act_ant), str(ant_objective)))
                self.dbg_file.write('used_idx is {}\n'.format(str(used_idx)))
          else:
            do_move_location(act_ant, self.unseen[random.randint(0, len(self.unseen) - 1)])
            if self.DEBUG:
              self.dbg_file.write('while ant {} is using a random point\n'.format(str(act_ant)))
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
