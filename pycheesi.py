#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 17:25:00 2021

@author: johnwendebornmac
"""
import numpy as np
import copy

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import pygame
pygame.init()

from pawn import *
from space import *
from player import *
from display import *

debug = False

###

SPACE_COLOR = (250, 200, 150)
RED_COLOR = (200, 0, 0)
SAFE_COLOR = (179, 224, 250)

BLUE_COLOR = (40, 40, 255)
PURPLE_COLOR = (200, 0, 200)
GREEN_COLOR = (0, 200, 0)
YELLOW_COLOR = (220, 180, 30)

WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
GREY_COLOR = (128, 128, 128)
LIGHT_GREY_COLOR = (164, 164, 164)

class parcheesi:
    
    def __init__(self, n_players = 4, 
                 player_colors = [BLUE_COLOR, PURPLE_COLOR, GREEN_COLOR, YELLOW_COLOR],
                 player_names = ['Player 1', 'Player 2', 'Player 3', 'Player 4'],
                 n_pawns = 4,
                 window_size = 600):
        
        # Setup some basics about the game
        # Note that anything other 4-player, 4-pawn, and 2-dice are not yet implemented
        self.n_players = n_players
        self.player_names = player_names
        self.player_colors = player_colors
        self.n_pawns = 4
        
        # Initialize some  basic variables for gameplay
        self.doubles = 0
        self.active_pawn = None
        self.active_pawn_buttons = []
        self.dice = []
        self.active_dice = []
        self.used_dice = []
        self.prev_states = []
        self.newer_states = []
        
        self.moves = []
        self.move_buttons = []
        
        # Initialize display parameters
        self.window_dim = window_size # Dimension of the parcheesi board itself. Will be a square
        
        self.button_width = self.window_dim // 4
        self.button_height = self.window_dim // 7
        self.button_buffer = self.button_height // 4
        
        self.space_dim = self.window_dim // 22 # Short dimension of spaces
        self.space_highlight_width = self.space_dim // 10 # Width of outline when space is highlighted 
        self.space_outline_width = int(self.space_highlight_width // 1.5) # Width of outline around each space
        
        self.home_square_size = self.space_dim * 8
        self.home_circle_size = self.home_square_size // 2.1
        self.home_offset = self.space_dim * 14 + self.space_outline_width

        self.pawn_size = self.window_dim // 45
        self.pawn_highlight_width = self.pawn_size // 4
        self.pawn_highlight_size = self.pawn_size // 2
        
        self.die_size = self.window_dim // 10
        self.die_buffer = self.die_size // 2
        self.die_highlight_width = self.die_size // 20
        
        self.barrier_width = 10
        
        self.extra_space = int(self.die_size + 2 * self.barrier_width + 2 * self.die_buffer \
            + self.button_width + 2 * self.button_buffer)
        self.window_dim_x = int(self.window_dim + self.extra_space)
        
        self.fps = 10
        
        self.space_font = pygame.font.Font('freesansbold.ttf', 2 * self.space_dim // 3)
        self.dice_font = pygame.font.Font('freesansbold.ttf', self.die_size)
        self.button_font = pygame.font.Font('freesansbold.ttf', self.button_height // 3)
        
        self.message_2 = ''
        self.message = ''
        
        # Initialize players and spaces
        self.init_players()
        self.init_spaces()
        
        # Display the board
        self.display()
    
    def init_players(self):
        
        self.players = []
        for i, (name, color) in enumerate(zip(self.player_names, self.player_colors)):
            
            self.players.append(player(name = name, color = color, n_pawns = self.n_pawns))
            
            dim = self.home_square_size / 2
            entry_space = i * 17
            last_space = (63 + entry_space) % 68
            red_start_false = entry_space + 64
            red_start_true = 68 + i * 7
            red_end_false = red_start_false + 6
            red_end_true = red_start_true + 6
            extra_spaces = 72 - i * 10
            if i == 0:
                loc_x = dim
                loc_y = dim
                # entry_space = 0
                # last_space = 63
                # red_start_false = 64
                # red_start_true = 68
                # red_end_false = 70
                # red_end_true = 74
                # extra_spaces = 72
            elif i == 1:
                loc_x = dim
                loc_y = dim + self.home_offset
                # entry_space = 17
                # last_space = 12
                # red_start_false = 81
                # red_start_true = 75
                # red_end_false = 87
                # red_end_true = 81
                # extra_spaces = 62
            elif i == 2:
                loc_x = dim + self.home_offset
                loc_y = dim + self.home_offset
                # entry_space = 34
                # last_space = 29
                # red_start_false = 98
                # red_start_true = 82
                # red_end_false = 104
                # red_end_true = 88
                # extra_spaces = 52
            elif i == 3:
                loc_x = dim + self.home_offset
                loc_y = dim
                # entry_space = 51
                # last_space = 46
                # red_start_false = 115
                # red_start_true = 89
                # red_end_false = 121
                # red_end_true = 95
                # extra_spaces = 42
            
            self.players[i].heaven_space_num = red_end_true + 1
            self.players[i].entry_space = entry_space
            self.players[i].last_space = last_space
            self.players[i].red_start_false = red_start_false
            self.players[i].red_start_true = red_start_true
            self.players[i].red_end_true = red_end_true
            self.players[i].red_end_false = red_end_false
            self.players[i].extra_spaces = extra_spaces
            self.players[i].init_pawns(player = self.players[i],
                                       center_x = loc_x, center_y = loc_y, 
                                       dx = self.window_dim / 12)
            
        self.active_player = self.players[0]
    
    def init_spaces(self):

        col0 = 8 * self.space_dim
        col1 = 10 * self.space_dim
        col2 = 12 * self.space_dim
        row0 = 8 * self.space_dim
        row1 = 10 * self.space_dim
        row2 = 12 * self.space_dim
        
        self.space_locs = [(col0, 4 * self.space_dim), (col0, 5 * self.space_dim), (col0, 6 * self.space_dim), (col0, 7 * self.space_dim), 
                        (7 * self.space_dim, row0), (6 * self.space_dim, row0), (5 * self.space_dim, row0), (4 * self.space_dim, row0), (3 * self.space_dim, row0), (2 * self.space_dim, row0), (1 * self.space_dim, row0), (0 * self.space_dim, row0),
                        (0, row1),
                        (0 * self.space_dim, row2), (1 * self.space_dim, row2), (2 * self.space_dim, row2), (3 * self.space_dim, row2), (4 * self.space_dim, row2), (5 * self.space_dim, row2), (6 * self.space_dim, row2), (7 * self.space_dim, row2),
                        (col0, 14 * self.space_dim), (col0, 15 * self.space_dim), (col0, 16 * self.space_dim), (col0, 17 * self.space_dim), (col0, 18 * self.space_dim), (col0, 19 * self.space_dim), (col0, 20 * self.space_dim), (col0, 21 * self.space_dim),
                        (col1, 21 * self.space_dim),
                        (col2, 21 * self.space_dim), (col2, 20 * self.space_dim), (col2, 19 * self.space_dim), (col2, 18 * self.space_dim), (col2, 17 * self.space_dim), (col2, 16 * self.space_dim), (col2, 15 * self.space_dim), (col2, 14 * self.space_dim),
                        (14 * self.space_dim, row2), (15 * self.space_dim, row2), (16 * self.space_dim, row2), (17 * self.space_dim, row2), (18 * self.space_dim, row2), (19 * self.space_dim, row2), (20 * self.space_dim, row2), (21 * self.space_dim, row2),
                        (21 * self.space_dim, row1),
                        (21 * self.space_dim, row0), (20 * self.space_dim, row0), (19 * self.space_dim, row0), (18 * self.space_dim, row0), (17 * self.space_dim, row0), (16 * self.space_dim, row0), (15 * self.space_dim, row0), (14 * self.space_dim, row0),
                        (col2, 7 * self.space_dim), (col2, 6 * self.space_dim), (col2, 5 * self.space_dim), (col2, 4 * self.space_dim), (col2, 3 * self.space_dim), (col2, 2 * self.space_dim), (col2, 1 * self.space_dim), (col2, 0 * self.space_dim),
                        (col1, 0),
                        (col0, 0 * self.space_dim), (col0, 1 * self.space_dim), (col0, 2 * self.space_dim), (col0, 3 * self.space_dim),
           
                        (col1, 1 * self.space_dim), (col1, 2 * self.space_dim), (col1, 3 * self.space_dim), (col1, 4 * self.space_dim), (col1, 5 * self.space_dim), (col1, 6 * self.space_dim), (col1, 7 * self.space_dim),
                        (1 * self.space_dim, row1), (2 * self.space_dim, row1), (3 * self.space_dim, row1), (4 * self.space_dim, row1), (5 * self.space_dim, row1), (6 * self.space_dim, row1), (7 * self.space_dim, row1),
                        (col1, 20 * self.space_dim), (col1, 19 * self.space_dim), (col1, 18 * self.space_dim), (col1, 17 * self.space_dim), (col1, 16 * self.space_dim), (col1, 15 * self.space_dim), (col1, 14 * self.space_dim),
                        (20 * self.space_dim, row1), (19 * self.space_dim, row1), (18 * self.space_dim, row1), (17 * self.space_dim, row1), (16 * self.space_dim, row1), (15 * self.space_dim, row1), (14 * self.space_dim, row1)
                        ]
        
        n_spaces = self.n_players * 17
        last_space = self.n_players * 17 - 1
        n_spaces += self.n_players * 7
        
        spaces = []
        for i in range(n_spaces):
            
            loc_x = self.space_locs[i][0]
            loc_y = self.space_locs[i][1]
            
            # These spaces are oriented horizontal
            if (i <= 3) or (i <= 67 and i >= 55) or (i > 20 and i < 38) or (i >= 68 and i <= 74) or (i >= 82 and i <= 88):
                dim_x = self.space_dim * 2
                dim_y = self.space_dim
            # These are oriented vertical
            else:
                dim_x = self.space_dim
                dim_y = self.space_dim * 2
                
            occupants = []
            is_safe = False
            whose_safe = None
            red_space = False
            color = SPACE_COLOR
            
            if i % 17 == 0 and i < last_space:
                is_safe = True
                color = SAFE_COLOR
                whose_safe = i // 17
                self.players[i // 17].safe_space = space(occupants = occupants, 
                                                          is_safe = is_safe, 
                                                          whose_safe = whose_safe,
                                                          red_space = red_space,
                                                          num = i, 
                                                          loc = (loc_x, loc_y),
                                                          dims = (dim_x, dim_y),
                                                          color = color)
                
            elif (((i - 7) % 17 == 0) or ((i - 12) % 17 == 0)) and (i < last_space):
                is_safe = True
                color = SAFE_COLOR
                
            elif i > last_space:
                red_space = True
                color = RED_COLOR
                self.players[(i - last_space - 1) // 7].red_spaces.append(space(occupants = occupants, 
                                                                                is_safe = is_safe, 
                                                                                whose_safe = whose_safe,
                                                                                red_space = red_space,
                                                                                num = i, 
                                                                                loc = (loc_x, loc_y),
                                                                                dims = (dim_x, dim_y),
                                                                                color = color))
            
            spaces.append(space(occupants = occupants, 
                              is_safe = is_safe, 
                              whose_safe = whose_safe,
                              red_space = red_space,
                              num = i, 
                              loc = (loc_x, loc_y), 
                              dims = (dim_x, dim_y),
                              color = color))
            
        self.spaces = spaces
        self.active_pawn = self.active_player.pawns[0]
        
    def display(self):
    
        self.window_size = (self.window_dim + self.extra_space, self.window_dim)
        self.window = pygame.display.set_mode(self.window_size)
        self.window.fill(WHITE_COLOR)
        pygame.display.set_caption('Parcheesi')
        
        self.turn()
        self.update_display()
        
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(self.fps)
            
            for event in pygame.event.get():
                
                # Quit the game
                if event.type == pygame.QUIT:
                    self.update_display()
                    run = False
                    pygame.quit()  
                
                # Check for Key Presses
                if event.type == pygame.KEYDOWN:
                    self.check_key_press(event)
                    self.update_display()
                
                # Check for mouse presses
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:                    
                    pos = pygame.mouse.get_pos()
                    self.check_click(pos)
                    self.update_display()
                                                
    def update_display(self):
        
        self.update_spaces()
        self.update_pawn_locs()
        
        self.window.fill(WHITE_COLOR)
        
        # Draw the board
        self.display_board()
        
        # Display messages
        self.display_message()
        
        # Draw the buttons
        self.display_buttons()
        
        # Draw the dice
        self.display_dice()
        
        # Emphasize the active pawn
        self.display_active_pawn()
        
        # Emphasize active die/dice
        self.display_active_dice()
        
        # Emphasize spaces with possible moves
        if self.active_pawn is None or self.active_dice == []:
            self.moves = []
            self.move_buttons = []
        else:
            self.display_possible_moves()
        
        pygame.display.update()
        
    def save_board_state(self):
        
        self.prev_state = {
            'players' : copy.copy(self.players),
            'active_player' : copy.copy(self.active_player),
            'spaces' : copy.copy(self.spaces),
            'dice' : copy.copy(self.dice),
            'used_dice' : copy.copy(self.used_dice),
            'active_pawn' : copy.copy(self.active_pawn),
            'doubles' : copy.copy(self.doubles)
            }
        
    def undo(self):
        
        # print('#####')
        print('Undo')
        self.message_2 = copy.copy(self.message)
        self.message = 'Undo not yet implemented'
        # print(self.active_player in self.players)
        # for pawn in self.active_player.pawns:
        #     if pawn.space is not None:
        #         print(pawn.space.num)
        # # print(self.dice)
        
        # # print(prev_state)
        
        # self.players = copy.copy(self.prev_state['players'])
        # self.spaces = copy.copy(self.prev_state['spaces'])
        # self.update_spaces()
        # self.update_pawn_locs()
        # self.active_player = copy.copy(self.prev_state['active_player'])
        # self.dice = copy.copy(self.prev_state['dice'])
        # self.used_dice = copy.copy(self.prev_state['used_dice'])
        # self.moves = []
        # self.move_buttons = []
        # self.dice_buttons = []
        # self.active_pawn = self.active_player.pawns[0]#copy.copy(self.prev_state['active_pawn'])
        # self.doubles = copy.copy(self.prev_state['doubles'])
        # self.update_display()
        # # self.update_spaces()
        # # self.update_pawn_locs()
        
        # # self.newer_states.append(self.prev_states[-1])
        # # self.prev_states.pop(-1)
        
        # # print(self.active_pawn)
        # # print(self.dice)
        # print(self.active_player in self.players)
        # for pawn in self.active_player.pawns:
        #     if pawn.space is not None:
        #         print(pawn.space.num)
        
    def update_pawn_locs(self):
        
        for player in self.players:
            player.update(spaces = self.spaces)
            
                    
    def update_spaces(self):
        
        for space in self.spaces:
            space.occupants = []
            for player in self.players:
                for pawn in player.pawns:
                    if pawn.space is not None and pawn.space.num == space.num:
                        space.occupants.append(pawn)
                        pawn.space = space
        
    def get_pawn_from_pos(self, pos):
        
        for player in self.players:
            for pawn in player.pawns:
                if pawn.rect.collidepoint(pos) and player == self.active_player:
                    self.active_pawn = pawn
                        
    def check_for_pawn_click(self, pos):
        print('running')
        for pawn_button in self.active_pawn_buttons:
            if pawn_button.collidepoint(pos):
                self.get_pawn_from_pos(pos)
                if self.active_pawn is not None and self.active_dice not in [None, []]:
                    self.find_possible_moves(dice = self.active_dice)
                
    def check_for_dice_click(self, pos):
        print('running 2')
        for dice_button in self.dice_buttons:
            if dice_button.collidepoint(pos):
                ind = self.dice_buttons.index(dice_button)
                if self.dice[ind] in self.active_dice:
                    if self.dice.count(self.dice[ind]) == self.active_dice.count(self.dice[ind]):
                        self.active_dice = []
                    else:
                        self.active_dice.append(self.dice[ind])
                else:
                    self.active_dice.append(self.dice[ind])
                if self.active_pawn is not None and self.active_dice not in [None, []]:
                    self.find_possible_moves(dice = self.active_dice)
    
    def check_for_move_click(self, pos):
        print('running 3')
        if self.move_buttons not in [None, []] and self.active_pawn is not None:
            self.save_board_state()
            
            for i,move_button in enumerate(self.move_buttons):
                
                if move_button.collidepoint(pos) and self.moves[0] != 'heaven':
                    space = self.moves[0]
                    # print(space.occupants)
                    if len(space.occupants) == 0:
                        self.active_pawn.move(new_space = space)
                        # space.occupants.append(self.active_pawn)
                        for die in self.active_dice:
                            self.used_dice.append(die)
                            self.dice.remove(die)
                        self.active_dice = []
                        self.active_pawn = None
                        self.moves = []
                        self.move_buttons = []
                    elif len(space.occupants) == 1:
                        if space.occupants[0].player == self.active_player:
                            self.active_pawn.move(new_space = space)
                            # space.occupants.append(self.active_pawn)
                            for die in self.active_dice:
                                self.used_dice.append(die)
                                self.dice.remove(die)
                            self.active_dice = []
                            self.active_pawn = None
                            self.moves = []
                            self.move_buttons = []
                        else:
                            if not space.is_safe or space == self.active_player.safe_space:
                                space.occupants[0].go_home()
                                self.dice.append(20)
                                self.active_pawn.move(new_space = space)
                                # space.occupants.append(self.active_pawn)
                                for die in self.active_dice:
                                    self.used_dice.append(die)
                                    self.dice.remove(die)
                                self.active_dice = []
                                self.active_pawn = None
                                self.moves = []
                                self.move_buttons = []
                    elif len(space.occupants) == 2:
                        pass
                
                elif move_button.collidepoint(pos) and self.moves[0] == 'heaven':
                    self.active_player.pawns.remove(self.active_pawn)
                    self.dice.append(10)
                    for die in self.active_dice:
                        self.used_dice.append(die)
                        self.dice.remove(die)
                    self.active_dice = []
                    self.active_pawn = None
                    self.moves = []
                    self.move_buttons = []
                    
    def do_move(self, event = None):
        
        if (self.move_buttons != [] and self.active_pawn is not None):
            
            # self.save_board_state()
            
            if self.moves[0] != 'heaven':
                space = self.moves[0]
                if len(space.occupants) != 2:
                    if len(space.occupants) == 1:
                        if not space.is_safe and space.occupants[0].player == self.active_player:
                            pass
                        elif not space.is_safe:
                            self.message = f'{self.active_player.name} ate {space.occupants[0].player.name}!'
                            space.occupants[0].go_home()
                            self.dice.append(20)
                        elif space.is_safe and space.occupants[0].player == self.active_player:
                            pass
                        elif space.is_safe and space == self.active_player.safe_space:
                            self.message = f'{self.active_player.name} ate {space.occupants[0].player.name}!'
                            space.occupants[0].go_home()
                            self.dice.append(20)
                        elif space.is_safe:
                            return
                            
                    self.active_pawn.move(new_space = space)
                    for die in self.active_dice:
                        self.used_dice.append(die)
                        self.dice.remove(die)
                    self.active_dice = []
                    self.moves = []
                    self.move_buttons = []

                elif len(space.occupants) == 2:
                    return

            elif self.moves[0] == 'heaven':
                self.active_player.pawns.remove(self.active_pawn)
                if self.active_player.get_n_pawns() == 0:
                    self.message_2 = ''
                    self.message = f'{self.active_player.name} wins!'
                    return
                self.dice.append(10)
                self.message = f'{self.active_player.name} sent a pawn to heaven.'
                for die in self.active_dice:
                    self.used_dice.append(die)
                    self.dice.remove(die)
                self.active_dice = []
                self.active_pawn = self.active_player.pawns[0]
                self.moves = []
                self.move_buttons = []
                
    def toggle_dice(self, ind):
        
        try:
            if self.dice[ind] in self.active_dice:
                if self.dice.count(self.dice[ind]) == self.active_dice.count(self.dice[ind]):
                    self.active_dice = []
                else:
                    self.active_dice.append(self.dice[ind])
            else:
                self.active_dice.append(self.dice[ind])
            if self.active_pawn is not None and self.active_dice not in [None, []]:
                self.find_possible_moves(dice = self.active_dice)
        except:
            pass
    
    def check_click(self, pos):
        
        # Check if any side buttons were pressed
        if self.quit_button.collidepoint(pos):
            run = False
            pygame.quit()
        elif self.nextTurn_button.collidepoint(pos):
            self.next_turn()
        elif self.undo_button.collidepoint(pos):
            self.undo()
            
        # Check if any spaces were clicked
        if self.move_buttons != []:
            if self.move_buttons[0].collidepoint(pos):
                self.do_move()
            
        # Check is any pawns were clicked
        for pawn_button in self.active_pawn_buttons:
            if pawn_button.collidepoint(pos):
                self.get_pawn_from_pos(pos)
                if self.active_pawn is not None and self.active_dice not in [None, []]:
                    self.find_possible_moves(dice = self.active_dice)
        
        # Check if any dice were clicked
        for dice_button in self.dice_buttons:
            if dice_button.collidepoint(pos):
                ind = self.dice_buttons.index(dice_button)
                self.toggle_dice(ind)

    def check_key_press(self, event):
        
        # Quit the game with the Q button
        if event.key == pygame.K_q:
            run = False
            pygame.quit() 

        # Switch active pawn with the ARROW KEYS
        elif event.key in [pygame.K_DOWN, pygame.K_LEFT]:
            if self.active_pawn is None:
                self.active_pawn = self.active_player.pawns[0]
            else:
                self.active_pawn = self.active_player.pawns[self.active_player.pawns.index(self.active_pawn) - 1]
            if self.active_dice != []:
                self.find_possible_moves(self.active_dice)
        elif event.key in [pygame.K_RIGHT, pygame.K_UP]:
            if self.active_pawn is None:
                self.active_pawn = self.active_player.pawns[0]
            else:
                i_active_pawn = self.active_player.pawns.index(self.active_pawn)
                if i_active_pawn != len(self.active_player.pawns) - 1:
                    self.active_pawn = self.active_player.pawns[i_active_pawn + 1]
                else:
                    self.active_pawn = self.active_player.pawns[0]
            if self.active_dice != []:
                self.find_possible_moves(self.active_dice)
            
        # Toggle certain dice with the NUMBER KEYS
        # 1 -> die 0, 2 -> die 1, etc.
        elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, 
                           pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8] and self.dice != []:
            
            ind = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, 
                   pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8].index(event.key)
            self.toggle_dice(ind)

            
        # Complete the move with the ENTER/RETURN button
        elif event.key == pygame.K_RETURN:
            
            self.do_move()

        # Go to the next turn with the SPACE button
        elif event.key == pygame.K_SPACE:
            
            self.save_board_state()
            self.next_turn()
    
    def next_turn(self):
        
        # Check if the player can make any mroe moves
        if self.dice != []:
            
            all_dice_combos = [die for die in self.dice]
            if len(self.dice) == 3:
                all_dice_combos.append(self.dice[0] + self.dice[1])
                all_dice_combos.append(self.dice[0] + self.dice[2])
                all_dice_combos.append(self.dice[1] + self.dice[1])
            all_dice_combos.append(sum(self.dice))
            for pawn in self.active_player.pawns:
                for die in set(all_dice_combos):
                    self.find_possible_moves(die)
                    if self.moves != []:
                        self.message_2 = copy.copy(self.message)
                        print('You can still make at least one more move!')
                        self.message = 'You can still move!'
                        self.active_dice = []
                        self.moves = []
                        return
                
        
        # Go to the next turn
        self.active_pawn = None
        
        # If not doubles, go to next player
        if self.doubles == 0:
            if self.active_player == self.players[-1]:
                self.active_player = self.players[0]
            else:
                player_ind = self.players.index(self.active_player)
                self.active_player = self.players[player_ind + 1]
            pawn_spaces = [pawn.space for pawn in self.active_player.pawns]
            for space, pawn in zip(pawn_spaces, self.active_player.pawns):
                if space is not None:
                    self.active_pawn = pawn
                    break
        
        if self.active_pawn is None:
            self.active_pawn = self.active_player.pawns[0]
        
        self.turn()
            
        self.active_dice = []
        self.used_dice = []
        self.move_buttons = []
        self.moves = []
    
    def turn(self):
        
        self.message_2 = copy.copy(self.message)
        self.message = ''
        print(f'{self.active_player.name}\'s turn!')
        self.player_turn_message = f'{self.active_player.name}\'s turn!'
        self.dice, self.doubles = self.roll_dice(self.active_player, doubles = self.doubles)
        
        if self.doubles == 3:
            self.message_2 = copy.copy(self.message)
            self.message = f'{self.active_player.name} rolled 3 doubles! Turn over.'
            print('That\'s three doubles! Sending furthest pawn back to home and ending turn.')
            # self.dice = []
            self.doubles = 0
            dists = []
            for pawn in self.active_player.pawns:
                if pawn.space is None:
                    dists.append(-999)
                else:
                    space_num = pawn.space.num
                    if space_num < self.active_player.entry_space or space_num >= self.active_player.red_start_true:
                        dist = (space_num + 67) - self.active_player.last_space
                    else:
                        dist = space_num - self.active_player.last_space
                    dists.append(dist)
            i_furthest = np.argmax([dists], axis = 1)
            for i in i_furthest:
                self.active_player.pawns[i].go_home()
            self.next_turn()
    
    def roll_dice(self, player, n_dice = 2, doubles = 0):
        
        dice = np.random.choice([1, 2, 3, 4, 5, 6], replace = True, size = n_dice)
        if dice[0] == dice[1]:
            doubles += 1
            if self.active_player.get_pawns_out() == self.active_player.get_n_pawns():
                dice = np.insert(dice, 0, 7 - dice[-1])
                dice = np.insert(dice, 0, 7 - dice[-1])
                self.message_2 = copy.copy(self.message)
                self.message = 'Foooouuuurteen!'
        else:
            doubles = 0
                
        return dice.tolist(), doubles
    
    def calc_new_space(self, old, dice):
        
        new = old + sum(dice)
        
        # 96 is the highest possible space. If 'new' > 96, can't be a valid move
        if new > 130:
            return
        
        if old < self.active_player.red_start_true: # Pawn not already in red
            if new > 67: # Pawn starts before the space-number reset
                if new <= self.active_player.red_end_false:
                    if not self.check_for_bridge(old, new % 68):
                        if new < self.active_player.red_start_false:
                            if not self.spaces[new % 68].is_safe: 
                                self.moves.append(self.spaces[new % 68])
                            elif len(self.spaces[new % 68].occupants) == 1:
                                if self.spaces[new % 68].occupants[0].player != self.active_player:
                                    return
                                else:
                                    self.moves.append(self.spaces[new % 68])
                            else:
                                self.moves.append(self.spaces[new % 68])
                        elif self.spaces[(new % 68) + self.active_player.extra_spaces].occupants == []:
                            if not self.spaces[(new % 68) + self.active_player.extra_spaces].is_safe: 
                                self.moves.append(self.spaces[(new % 68) + self.active_player.extra_spaces])
                            elif len(self.spaces[(new % 68) + self.active_player.extra_spaces].occupants) == 1:
                                if self.spaces[(new % 68) + self.active_player.extra_spaces].occupants[0].player != self.active_player:
                                    return
                                else:
                                    self.moves.append(self.spaces[(new % 68) + self.active_player.extra_spaces])
                            else:
                                self.moves.append(self.spaces[(new % 68) + self.active_player.extra_spaces])
                elif new == self.active_player.red_end_false + 1:
                    self.moves.append('heaven')
            else:
                if old <= self.active_player.last_space:
                    if new > self.active_player.last_space:
                        if new + self.active_player.extra_spaces == self.active_player.red_end_true + 1:
                            self.moves.append('heaven')
                        elif new + self.active_player.extra_spaces < self.active_player.red_end_true + 1 and self.spaces[new + self.active_player.extra_spaces].occupants == []:
                            if not self.spaces[new + self.active_player.extra_spaces].is_safe: 
                                self.moves.append(self.spaces[new + self.active_player.extra_spaces])
                            elif len(self.spaces[new + self.active_player.extra_spaces].occupants) == 1:
                                if self.spaces[new + self.active_player.extra_spaces].occupants[0].player != self.active_player:
                                    return
                                else:
                                    self.moves.append(self.spaces[new + self.active_player.extra_spaces])
                            else:
                                self.moves.append(self.spaces[new + self.active_player.extra_spaces])
                    elif not self.check_for_bridge(old, new):
                        if not self.spaces[new].is_safe: 
                            self.moves.append(self.spaces[new])
                        elif len(self.spaces[new].occupants) == 1:
                            if self.spaces[new].occupants[0].player != self.active_player:
                                return
                            else:
                                self.moves.append(self.spaces[new])
                        else:
                            self.moves.append(self.spaces[new])
                elif old >= self.active_player.entry_space and not self.check_for_bridge(old, new):
                    if not self.spaces[new].is_safe: 
                        self.moves.append(self.spaces[new])
                    elif len(self.spaces[new].occupants) == 1:
                        if self.spaces[new].occupants[0].player != self.active_player:
                            return
                        else:
                            self.moves.append(self.spaces[new])
                    else:
                        self.moves.append(self.spaces[new])
        elif new == self.active_player.red_end_true + 1:
            self.moves.append('heaven')
            
    def check_for_bridge(self, old, new):
         
         if old < new: 
             spaces_traversed = np.arange(old + 1, new + 1)
         else:
             spaces_traversed = np.concatenate((np.arange(old + 1, 68), 
                                                np.arange(0, new + 1)),
                                               axis = None)
         
         is_bridge = False
         for space_num in spaces_traversed:
             if len(self.spaces[space_num].occupants) == 2:
                 is_bridge = True
         return is_bridge
    
    def find_possible_moves(self, dice):
        
        self.moves = []
            
        if self.active_pawn.space is None:
            if sum(dice) == 5:
                if len(self.spaces[self.active_player.safe_space.num].occupants) == 2:
                    pass
                else:
                    self.moves.append(self.active_player.safe_space)
        else:
            old = self.active_pawn.space.num
            self.calc_new_space(old, dice)

    def display_buttons(self):
        
        # Quit Button
        quit_rect = pygame.Rect(self.window_dim + 2 * self.barrier_width + self.die_size + 2 * self.die_buffer + self.button_buffer, 
                                self.window_dim - self.button_height - self.button_buffer, 
                                self.button_width, self.button_height)
        self.quit_button = pygame.draw.rect(self.window, RED_COLOR, 
                                            quit_rect)
        text = self.button_font.render('    QUIT', True, BLACK_COLOR)
        self.window.blit(text, quit_rect)
        
        # Next Turn Button
        nextTurn_rect = pygame.Rect(self.window_dim + 2 * self.barrier_width + self.die_size + 2 * self.die_buffer + self.button_buffer, 
                                    self.button_buffer,
                                    self.button_width, self.button_height)
        self.nextTurn_button = pygame.draw.rect(self.window, RED_COLOR, nextTurn_rect)
        text = self.button_font.render(' Next Turn', True, BLACK_COLOR)
        self.window.blit(text, nextTurn_rect)
        
        # Undo Button
        undo_rect = pygame.Rect(self.window_dim + 2 * self.barrier_width + self.die_size + 2 * self.die_buffer + self.button_buffer, 
                                self.button_height + 2 * self.button_buffer,
                                self.button_width, self.button_height)
        self.undo_button = pygame.draw.rect(self.window, RED_COLOR, undo_rect)
        text = self.button_font.render('    Undo', True, BLACK_COLOR)
        self.window.blit(text, undo_rect)
        
    def display_message(self):
        
        playerTurn_rect = pygame.Rect(8.1 * self.space_dim, 8.1 * self.space_dim,
                                      6 * self.space_dim, 2 * self.space_dim)
        text = self.space_font.render(self.player_turn_message, True, self.active_player.color)
        self.window.blit(text, playerTurn_rect)
        
        message_rect = pygame.Rect(8 * self.space_dim, 10.8 * self.space_dim,
                                   6 * self.space_dim, 2 * self.space_dim)
        text = self.space_font.render(self.message, True, self.active_player.color)
        self.window.blit(text, message_rect)
        
        message_2_rect = pygame.Rect(8 * self.space_dim, 13.3 * self.space_dim,
                                     6 * self.space_dim, 2 * self.space_dim)
        text = self.space_font.render(self.message_2, True, BLACK_COLOR)
        self.window.blit(text, message_2_rect)
        
    def display_board(self):

        # Display the spaces
        for i,space in enumerate(self.spaces):
            space_rect = pygame.Rect(space.loc[0], space.loc[1], 
                                     space.dims[0], space.dims[1])
            pygame.draw.rect(self.window, space.color, space_rect)
            pygame.draw.rect(self.window, LIGHT_GREY_COLOR, space_rect, 
                             width = self.space_outline_width)
            # text = space_font.render(str(i), True, BLACK_COLOR)
            # window.blit(text, space_rect)
        
        # Display the colored squares for each player
        active_pawn_buttons = []
        for i, player in enumerate(self.players):
            if player == self.players[0]:
                loc_x = 0
                loc_y = 0
            elif player == self.players[1]:
                loc_x = 0
                loc_y = self.home_offset#1.7565 * dim_y
            elif player == self.players[2]:
                loc_x = self.home_offset#1.7565 * dim_y
                loc_y = self.home_offset#1.7565 * dim_x
            elif player == self.players[3]:
                loc_x = self.home_offset#1.7565 * dim_x
                loc_y = 0
    
            pygame.draw.rect(self.window, player.color, 
                            (loc_x, loc_y, 
                             self.home_square_size, self.home_square_size))
            pygame.draw.circle(self.window, WHITE_COLOR, 
                                (loc_x + self.home_square_size / 2, 
                                 loc_y + self.home_square_size / 2), 
                                self.home_circle_size)
            text = self.space_font.render(player.name, True, BLACK_COLOR)
            self.window.blit(text, (loc_x, loc_y, self.home_square_size, self.home_square_size))
    
            # Draw the pawns
            for pawn in player.pawns:
                player = pawn.player
                if pawn.space is not None:
                    if len(pawn.space.occupants) < 2:
                        x, y = pawn.loc
                        if (x, y) == (pawn.space.loc[0], pawn.space.loc[1]):
                            if (x <= 7 * self.window_dim / 22 or x >= 13 * self.window_dim / 22):
                                x += self.window_dim // 44
                                y += self.window_dim // 22
                            elif (y <= 7 * self.window_dim / 22 or y >= 13 * self.window_dim / 22):
                                x += self.window_dim // 22
                                y += self.window_dim // 44
                            pawn.loc = [x, y]
                        if player == self.active_player:
                            pawn_button = pygame.draw.circle(self.window, player.color, 
                                                             center = (x, y), 
                                                             radius = self.pawn_size)
                            pygame.draw.circle(self.window, BLACK_COLOR,
                                                center = (x, y),
                                                radius = self.pawn_size,
                                                width = self.pawn_highlight_width)
                            self.active_pawn_buttons.append(pawn_button)
                        else:
                            pawn_button = pygame.draw.circle(self.window, player.color, 
                                                center = (x, y), 
                                                radius = self.pawn_size)
                        pawn.rect = pawn_button
                    elif len(pawn.space.occupants) == 2:
                        for i,pawn in enumerate(pawn.space.occupants):
                            x, y = pawn.loc
                            if (x, y) == (pawn.space.loc[0], pawn.space.loc[1]):
                                if (x <= 7 * self.window_dim // 22 or x >= 13 * self.window_dim // 22):
                                    x += self.window_dim // 44
                                    y += self.window_dim // 22
                                    if i == 0:
                                        y += self.window_dim // 44
                                    if i == 1:
                                        y -= self.window_dim // 44
                                elif (y <= 7 * self.window_dim // 22 or y >= 13 * self.window_dim // 22):
                                    x += self.window_dim // 22
                                    y += self.window_dim // 44
                                    if i == 0:
                                        x += self.window_dim // 44
                                    if i == 1:
                                        x -= self.window_dim // 44
                                pawn.loc = [x, y]
                            if player == self.active_player:
                                pawn_button = pygame.draw.circle(self.window, player.color, 
                                                                 center = (x, y), 
                                                                 radius = self.pawn_size)
                                pygame.draw.circle(self.window, BLACK_COLOR,
                                                    center = (x, y),
                                                    radius = self.pawn_size,
                                                    width = self.pawn_highlight_width)
                                self.active_pawn_buttons.append(pawn_button)
                            else:
                                pawn_button = pygame.draw.circle(self.window, player.color, 
                                                    center = (x, y), 
                                                    radius = self.pawn_size)
                            pawn.rect = pawn_button
                else:
                    x, y = pawn.loc
                    if player == self.active_player:
                        pawn_button = pygame.draw.circle(self.window, player.color, 
                                                         center = (x, y), 
                                                         radius = self.pawn_size)
                        pygame.draw.circle(self.window, BLACK_COLOR,
                                            center = (x, y),
                                            radius = self.pawn_size,
                                            width = self.pawn_highlight_width)
                        self.active_pawn_buttons.append(pawn_button)
                    else:
                        pawn_button = pygame.draw.circle(self.window, player.color, 
                                            center = (x, y), 
                                            radius = self.pawn_size)
                    pawn.rect = pawn_button
                    
        # Draw black borders to the right of the board
        pygame.draw.lines(self.window, BLACK_COLOR, 
                          closed = False,
                          points = ((self.window_dim - 2 * self.space_outline_width, 0), 
                                    (self.window_dim - 2 * self.space_outline_width, self.window_dim)),
                          width = self.barrier_width)
        pygame.draw.lines(self.window, BLACK_COLOR, 
                          closed = False,
                          points = ((self.window_dim + self.die_size + 2 * self.die_buffer, 0), 
                                    (self.window_dim + self.die_size + 2 * self.die_buffer, self.window_dim)),
                          width = self.barrier_width)
    
    def display_possible_moves(self):

        self.move_buttons = []
        if self.moves != []:
            for space in self.moves:
                if space == 'heaven':
                    space_outline = pygame.draw.rect(self.window, color = BLACK_COLOR,
                                                     rect = (self.window_dim // 2 - self.window_dim // 12,
                                                             self.window_dim // 2 - self.window_dim // 12, 
                                                             self.window_dim // 6, self.window_dim // 6), 
                                                     width = self.space_highlight_width)
                else:
                    space_outline = pygame.draw.rect(self.window, color = BLACK_COLOR,
                                                     rect = (space.loc[0], space.loc[1], 
                                                     space.dims[0], space.dims[1]), 
                                                     width = self.space_highlight_width)
                self.move_buttons.append(space_outline)
    
    def display_dice(self):
        
        self.dice_buttons = []
        if len(self.dice) > 0:
            for i,die in enumerate(self.dice):
                dice_button = pygame.draw.rect(self.window, GREY_COLOR, 
                                               (self.window_dim + self.die_buffer, 
                                                self.die_buffer + i * (self.die_size + self.die_buffer), 
                                                self.die_size, self.die_size))
                self.dice_buttons.append(dice_button)
                text = self.dice_font.render(str(die), True, BLACK_COLOR)
                self.window.blit(text, (self.window_dim + self.die_buffer, 
                                       self.die_buffer + (i * (self.die_size + self.die_buffer)), 
                                       self.die_size, self.die_size))
    
    def display_active_pawn(self):
        
        if self.active_pawn is not None:
            x, y = self.active_pawn.loc
            pygame.draw.circle(self.window, self.active_pawn.player.color, 
                                center = (x, y), 
                                radius = self.pawn_size)
            pygame.draw.circle(self.window, BLACK_COLOR,
                                center = (x, y),
                                radius = self.pawn_size,
                                width = self.pawn_highlight_width)
            pygame.draw.circle(self.window, WHITE_COLOR,
                                center = (x, y),
                                radius = self.pawn_highlight_size)
            
    def display_active_dice(self):
        
        highlighted_dice = []
        unhighlighted_dice = copy.copy(self.active_dice)
        if self.active_dice not in [None, []]:
            for i,die in enumerate(self.dice):
                if die in self.active_dice and die in unhighlighted_dice:
                    pygame.draw.rect(self.window, BLACK_COLOR, 
                                    rect = (self.window_dim + self.die_buffer, 
                                            self.die_buffer + (i * (self.die_size + self.die_buffer)), 
                                            self.die_size, self.die_size),
                                    width = self.die_highlight_width)
                    highlighted_dice.append(die)
                    unhighlighted_dice.remove(die)
                if sorted(highlighted_dice) == sorted(self.active_dice):
                    break

##############################################################################
                
class pawn:
    
    def __init__(self, space = None, space_num = 0, loc = [0, 0], rect = None, player = None):
        
        self.space = space
        self.space_num = space_num
        self.loc_init = loc
        self.loc = loc
        self.rect = rect
        self.player = player
    
    # Methods
    def move(self, new_space):
        
        self.space = new_space
        
    def leave_home(self, player):
        
        self.space = player.safe_space
        self.loc = player.safe_space.loc
    
    def go_home(self):
        
        self.space = None
        self.loc = self.loc_init
    
    def go_heaven(self):
        
        self.space = -1
        self.player.n_pawns -= 1

##############################################################################
        
class player:
    
    def __init__(self, name = 'Player', color = 'blue', 
                 safe_space = None, red_spaces = [],
                 n_pawns = 4, 
                 heaven_space_num = -1,
                 entry_space = -1,
                 last_space = -1,
                 red_start_false = -1,
                 red_start_true = -1,
                 red_end_false = -1,
                 red_end_true = -1,
                 extra_spaces = -1):
        
        self.name = name
        self.color = color
        
        self.n_pawns = n_pawns
        self.safe_space = safe_space
        self.red_spaces = red_spaces
        self.pawns_out = 0
        
    def init_pawns(self, player, center_x, center_y, dx):
        
        self.pawns = []
        for i in range(self.n_pawns):
            if i == 0:
                loc_x = center_x - dx
                loc_y = center_y - dx
            elif i == 1:
                loc_x = center_x - dx
                loc_y = center_y + dx
            elif i == 2:
                loc_x = center_x + dx
                loc_y = center_y + dx
            elif i == 3:
                loc_x = center_x + dx
                loc_y = center_y - dx
            
            self.pawns.append(pawn(space = None, loc = [loc_x, loc_y], player = player))

    def get_pawns_out(self):
        n_pawns_out = 0
        for pawn in self.pawns:
            if pawn.space is not None:
                n_pawns_out += 1
                
        return n_pawns_out
    
    def get_n_pawns(self):
        
        return len(self.pawns)
            
    def update(self, spaces):
        
        i_safe_space = self.safe_space.num
        for space in spaces:
            if space.num == i_safe_space:
                self.safe_space = space
                
        self.pawns_out = 0
        for pawn in self.pawns:
            if pawn.space is not None:
                pawn.loc = pawn.space.loc
                self.pawns_out += 1

##############################################################################
                
class space:
    
    def __init__(self, n_players = 4, occupants = [], is_safe = None, whose_safe = None,
                 red_space = False, num = 0, loc = [0, 0], dims = (0, 0),
                 color = (0, 0, 0)):
        
        self.n_players = 4
        self.occupants = occupants
        self.is_safe = is_safe
        self.whose_safe = whose_safe
        self.red_space = red_space
        self.num = num
        self.loc = loc
        self.dims = dims
        self.color = color
        
    def init_coords(self, window_size):
        
        window_dim = min(window_size)
        dx = window_dim / 11
        dy = window_dim / 22
        col0 = 8 * dy
        col1 = 10 * dy
        col2 = 12 * dy
        row0 = 8 * dy
        row1 = 10 * dy
        row2 = 12 * dy

    
    def clear(self):
        
        self.occupants = []
        
##############################################################################

if __name__ == '__main__':
    parcheesi(player_names = ['Lisa', 'Maya', 'Peter', 'John'],
                 window_size = 700)

            