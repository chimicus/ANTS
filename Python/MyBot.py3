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
        self.ant_pref_dir = {}
        pass
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        self.hills = []
        self.unseen = []
        for row in range(ants.rows):
          for col in range(ants.cols):
            self.unseen.append((row,col))
        pass
    
    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        self.dbg_file.write('new turn\n')
        # track all moves, prevent collisions
        orders = {}
        targets = {}
        def do_move_direction(loc, direction):
          new_loc = ants.destination(loc, direction)
          if (ants.unoccupied(new_loc) and new_loc not in orders) and ants.passable(new_loc) and new_loc not in ants.my_hills():
	    ants.issue_order((loc, direction))
            orders[new_loc] = loc
            try:
              del self.ant_pref_dir[loc]
            except:
              pass
            self.ant_pref_dir[new_loc] = direction
            self.dbg_file.write('preferred dir [%s]' % ', '.join(map(str,self.ant_pref_dir)))
            self.dbg_file.write('\n')
            return True
          else:
            return False

        def do_move_location(loc, dest):
          directions = ants.direction(loc, dest)
          for direction in directions:
            if do_move_direction(loc, direction):
              targets[dest] = loc
              return True
          return False
      
        def do_get_alternate_dir(ant, first_dir):
          if first_dir == 'n':
            new_dir = 'w'        
          elif first_dir == 'w':
            new_dir = 's'        
          elif first_dir == 's':
            new_dir = 'e'        
          elif first_dir == 'e':
            new_dir = 'n'        
          if do_move_direction(ant, new_dir):
            return True
          return False

        def remove_dir(remove):
          self.dbg_file.write('ant has a direction, trying to remove both\n')
          new_dir = self.ant_pref_dir[act_ant]
          del self.ant_pref_dir[act_ant]
          if do_move_direction(act_ant, new_dir) is False:
            while do_get_alternate_dir(act_ant, new_dir):
              pass
          return True
 
        def do_explore(ant):
          unseen_dist = []
          for unseen_loc in self.unseen:
            dist = ants.distance(ant, unseen_loc)
            unseen_dist.append((dist, unseen_loc))
          unseen_dist.sort()
          for dist, unseen_loc in unseen_dist:
            if do_move_location(ant, unseen_loc):
              break
          return True

        food_idx = 0
        # not seen territory setup
        for loc in self.unseen[:]:
          if ants.visible(loc):
            self.unseen.remove(loc)
        # enemy hill setup
        for hill_loc, hill_own in ants.enemy_hill:
          if hill_loc not in self.hills
            self.hills.append(hill_loc)
        # main cycle, cycle trough all the ants
        for act_ant in ants.my_ants():
          self.dbg_file.write('checking ant %s\n' % str(act_ant))
          if food_idx < len(ants.food()) - 1:
            food_loc = ants.food()[food_idx]
            self.dbg_file.write('food location for ant is %s\n' % str(food_loc))
            if do_move_location(act_ant, food_loc):
              self.dbg_file.write('ant is moving toward food\n')
              food_idx += 1
          elif act_ant in self.ant_pref_dir:
            remove_dir(act_ant)
          else:
            # just explore
            do_explore(act_ant) 
            #self.dbg_file.write('ant is exploring\n')
            #for new_dir in self.possible_directions:
            #  if do_move_direction(act_ant, new_dir):
            #    break
            
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
