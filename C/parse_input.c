#include <stdio.h>
#include <string.h>
#include "ants.h"

static char *command_list[] = {
"loadtime",       // in milliseconds, time given for bot to start up after it is given "ready" (see below)
"turntime",       // in milliseconds, time given to the bot each turn
"rows",           // number of rows in the map
"cols",           // number of columns in the map
"turns",          // maximum number of turns in the game
"viewradius2",    // view radius squared
"attackradius2",  // battle radius squared
"spawnradius2",   // food gathering radius squared (name is an unfortunate historical artifact)
"player_seed"     // seed for random number generator, useful for reproducing games
};

char *GetLine(char *input_buf)
{
    char *ret_ptr;
    ret_ptr = input_buf;
    while((*ret_ptr != '\n') &&
          (*ret_ptr != '\0'))
    {
        ret_ptr++;
    } 
    return ret_ptr;
}

void UpdateParameter(char *line, GAME_INFO *Info)
{
    char *command = line;
    int value;
    int ii = 0;

    while((line[ii] != '\0') && (line[ii] != ' '))
    { 
        ii++;
    }
    if (line[ii] != '\0')
    {
        // increment by 1 to get the value of the parameter
        value = atoi(line[ii+1]);
        line[ii] = '\0';
    }    
    ii = 0;
    while (strcmp(*command, *command_list[ii]) != 0) 
    {
        ii++;
    }
}

