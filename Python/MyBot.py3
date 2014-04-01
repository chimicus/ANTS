#!/usr/bin/env python
from ants import *

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
class MyBot:
    def __init__(self):
        # define class level variables, will be remembered between turns
        self.dbg_file = open('local_debug.txt', 'w') 
        self.possible_directions = ['n' , 'w' , 's' , 'e']
        self.turn = 0
        self.targets = {}
        pass
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        self.hills = []
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
        self.dbg_file.write('turn %d\n' % self.turn)
        self.turn += 1
        # track all moves, prevent collisions
        orders = {}

        def do_move_direction(loc, direction):
          new_loc = ants.destination(loc, direction)
          if (ants.unoccupied(new_loc) and new_loc not in orders) and ants.passable(new_loc) and new_loc not in ants.my_hills():
	    ants.issue_order((loc, direction))
            orders[new_loc] = loc
            self.dbg_file.write('orders[{}] = {} \n'.format(str(new_loc), str(loc)))
#            self.dbg_file.write('do_move_direction is True\n')
            return True
          else:
#            self.dbg_file.write('do_move_direction is False\n')
            return False

        def do_move_location(loc, dest):
          directions = ants.direction(loc, dest)
          for direction in directions:
            if do_move_direction(loc, direction):
 #             self.dbg_file.write('do_move_location is True\n')
              return True
#          self.dbg_file.write('do_move_location is False\n')
          return False
      
        def do_get_alternate_dir(ant, first_dir):
          new_dir = self.possible_directions[random.randint(0,3)]          
          while new_dir == first_dir:
            new_dir = self.possible_directions[random.randint(0,3)]          
          if do_move_direction(ant, new_dir):
#            self.dbg_file.write('do_get_alternate_dir is True\n')
            return True
#          self.dbg_file.write('do_get_alternate_dir is False\n')
          return False
 
        def do_explore(ant):
          unseen_dist = []
          for unseen_loc in self.unseen:
            dist = ants.distance(ant, unseen_loc)
            unseen_dist.append((dist, unseen_loc))
          unseen_dist.sort()
          for dist, unseen_loc in unseen_dist:
            if do_move_location(ant, unseen_loc):
#              self.dbg_file.write('do_explore is True\n')
              return True
          if do_get_alternate_dir(ant, self.possible_directions[random.randint(0,3)]):
#            self.dbg_file.write('do_explore is True\n')
            return True
#          self.dbg_file.write('do_explore is False\n')
          return False
        
        def set_target_for_ant(ant, food_vect):
          min_dist = range(ants.cols) + range(ants.rows)
          for food in food_vect:
            try:
              af_dbg = ants.distance(self.targets[food], ant)
            except KeyError:
              af_dbg = 0
#            self.dbg_file.write('af_dbg %s\n' % str(af_dbg))
            if (food not in self.targets) or (af_dbg == 1):
              ant_dist = ants.distance(ant, food)
              if ant_dist < min_dist:
                min_dist = ant_dist
                food_loc = food
          try:
            self.targets[food_loc] = ant
            self.dbg_file.write('targets[{}] = {} \n'.format(str(food_loc), str(ant)))
#            self.dbg_file.write('food location for ant is %s\n' % str(food_loc))
            if do_move_location(ant, food_loc):
#              self.dbg_file.write('set_targe is True\n')
              return True
#            self.dbg_file.write('set_targe is False\n')
            return False
          except NameError:
#            self.dbg_file.write('NameError set_targe is False\n')
            return False

        food_idx = 0
        enemy_hill = 0
        # not seen territory setup
        for loc in self.unseen[:]:
          if ants.visible(loc):
            self.unseen.remove(loc)
        # enemy hill setup
        for hill_loc, hill_own in ants.enemy_hills():
          if hill_loc not in self.hills:
            self.hills.append(hill_loc)
        # main cycle, cycle trough all the ants
        for act_ant in ants.my_ants():
          self.dbg_file.write('checking ant %s\n' % str(act_ant))
          if food_idx < len(ants.food()) - 1:
            if set_target_for_ant(act_ant, ants.food()):
              # ant can go toward food
              food_idx += 1
            # algoritmo per assegnare un percorso alla formica incaricata di chiudere la tana
          else:
            # just explore
            do_explore(act_ant) 
            
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
