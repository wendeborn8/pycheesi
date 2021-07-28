# pycheesi
Classic Parcheesi board game built in Python

Very much still a work in progress.

Still to do:
- Properly display pawns
    - Currently are on corners of spaces
    - Multiple pawns on space overlap
- Eating mechanism
    - Eaten pawn goes back to home
    - 20 extra spaces awarded
    - Can't eat your own pawn/bridge
- Bridge mechanism
    - Can bridge with your own pawn
    - Only 2 pawns to a bridge
    - No pawn (even your own) can pass through a bridge
    - Bridge on player's entry space prevents them form coming out
- 14's
    - Get original roll + bottom of dice
    - Only given if all pawns are out
    - Must use all 14 spaces, or none of it (still need to do with regular doubles)
- Going to heaven (putting a pawn in)
    - Limiting movement in red spaces
    - No bridges in red
    - Get 10 extra spaces
- Winning
- Undo mechansim
    - Keep track all moves made within one move
    - Discard previous board states once a turn is over
- Save game states/statistics
    - Quit then resume a game
        - Save board/player/space/pawn states as a pickle file?
    - Save stats for each game
        - Player names, moves made, who won, pawns left, pawns eaten, etc.
- Asthetic changes
    - Rounded corners
    - Nicer colors
    - Messages/prompts in console and on board
- Create AI to play automatically
    - Simple, random AI
    - More advanced AI that weighs different moves
