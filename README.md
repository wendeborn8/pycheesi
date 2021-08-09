# pycheesi
Classic Parcheesi board game built in Python

Is still a work-in-progress, but is mostly playable in its current state.

Still to do:
- Certain dice must be used, if possible
    - For doubles, the entire roll must be used, or none of it can be used at all
    - If only one die can be used, use the higher die
- Winning
    - Currently, only displays that the winning player has won
    - End the game
    - Give option to play again or quit
- Undo mechansim
    - Keep track of all moves made within one turn. Discard previous board states once a turn is over
    - Alternatively, save ALL board states, allowing to undo since the beginning of the game
    - Also a "redo" mechanism, to undo an undo
- Save game states/statistics
    - Quit then resume a game
        - Save board states as a pickle file?
    - Save stats for each game
        - Player names, moves made, who won, pawns left, pawns eaten, etc.
- Asthetic changes
    - Rounded corners?
    - Nicer colors
    - Messages/prompts in console and on board
        - Some messages displayed in center of board, but are not very pleasing
- Create AI to play automatically
    - Simple, random AI
    - More advanced AI that weighs different moves
- Ability to modify rules
    - Currently, the rules are mostly those of my own family, not exactly the default rules, and are firm
    - Rules to change woud include:
        - "Red spaces" start on safe space prior to red alley
        - Number of pawns
        - Number/probability of dice
        - 
- 3-, 5-, 6-player games
    - This is a big task. Requires generation of new boards, whose spaces and locs would be manually determined
    - Additionally, allow for 2-3 players to play on a 4-player board
        - 3-player: One player slot is just empty and is skipped over
        - 2-player: Either the same as 3-player (except 2 player slots are skipped) or each human controls 2 players
- Bug fixes
    - Player 1's pawns entering the red alley is imperfect. Some moves can't be done
    - Rolling 3 doubles has some quirks
    - At the end of the turn, it is checked whether a move can still be made. This isn't always accurate
    - Board isn't displayed fully accurately for different sizes
        - 500-1000 pix looks good. Smaller is overcrowded by space outlines
- Code changes
    - Make pawn/player/space classes more robust
        - Should allow main code to be cleaner/simpler
        - 
