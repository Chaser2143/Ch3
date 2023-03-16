"""
Updated Board Definition with Checkers Move Notation
|      | 01:B |      | 02:B |      | 03:B |      | 04:B |
| 05:B |      | 06:B |      | 07:B |      | 08:B |      |
|      | 09:B |      | 10:B |      | 11:B |      | 12:B |   North ^
| 13:_ |      | 14:_ |      | 15:_ |      | 16:_ |      |   South v
|      | 17:_ |      | 18:_ |      | 19:_ |      | 20:_ |
| 21:W |      | 22:W |      | 23:W |      | 24:W |      | 
|      | 25:W |      | 26:W |      | 27:W |      | 28:W |
| 29:W |      | 30:W |      | 31:W |      | 32:W |      | 

Display Notation: Location:PieceColor 
Notes:
(_ Denotes Vacancy)
(Single Digits have a Leading Zero for board consistency, do not include leading zeros on input)
InputMove Notation #CurrentLocation-#DesiredLocation (Ex. 2-7)

Return Notes:
1: Add Function to actually execute jump moves!
- Also add loop to continue taking input if further jumps for that peice exist
    - In this loop I need to only check from the landing position
- How do I validate moves?


3. Check Position is pretty inefficient, recreating a list every time i want to check a space, also because it iterates that list linearly for every single piece. 
How can I reduce this? Or does that not really matter?
Pythonic way of checking multiple conditions? Clean up the code a bit


Next Steps:
-Can I make this into a .exe eventually?

Ideas:
- Use Recursion to get a full moveset. Ie display moves as their entire chain. If their going to be king-ed, stop.

Notes:
-If you have a jump available, you must take it (and all the way), but if you have multiple jumps available, you can choose which one to take
-For the movement system, I can definitely find a better way than checking every single case, although they are all listed
    - For example, I could use sets to single out a characteristic (vacancies, captured spots) and compare it with the current board state
    - If things don't match up properly, you could cut the number of computations in half.
    - Further, I should be checking for jumps first, and then IFF no jumps are possible, I offer basic moves
    - Information gathered from the board by doing the jumps computation should closely relate to the basic move flows as well. 
ie : I wonder if there is a way to only compute the jumps and extract everything you need for the basic moves
    - Also, in the future, I should offer the complete jump sequence to the player at once, as they must take the entire sequence anyways; it'd prevent confusion and mistakes.

After completeing the movement system, implementing kings shouldn't be too hard.
"""
import os
from collections import OrderedDict

class piece():
    #W is White Team, B is Black Team
    def __init__(self, args):
        self.team = str(args[0])
        self.location = int(args[1].strip("\n"))
    
    def get_team(self):
        return self.team

    def get_location(self):
        return self.location

    def change_location(self, new_location):
        #Used to register a move for a piece
        self.location = new_location

class regular(piece):
    def __init__(self, args):
        super().__init__(args)
        self.type = "R"

    def get_type(self):
        return self.type

class king(piece):
    def __init__(self, args):
        super().__init__(args)
        self.type = "K"

    def get_type(self):
        return self.type

class Board_Util:
    """
    Basically performs every function within the game
    -Generates & Holds all the pieces
    -Makes and Validates Moves
    """
    def __init__(self):
        '''
        wt/bt is array of white/black team pieces
        ps is dictionary of every piece object's board location and its object
        ms is dictionary of every possible move (move set)
        '''
        self.wt = []
        self.bt = []
        self.ms = {}
        self.ps = {}
        self.load_board()

        #Defined as (Key: Initial Position) : Value (All End Locations from Key)
        self.South_moveFlow = {
            1:[5, 6], 
            2:[6, 7],
            3:[7, 8],
            4:[8],
            5:[9],
            6:[9, 10],
            7:[10, 11],
            8:[11, 12],
            9:[13,14],
            10:[14,15],
            11:[15,16],
            12:[16],
            13:[17],
            14:[17,18],
            15:[18,19],
            16:[19,20],
            17:[21,22],
            18:[22,23],
            19:[23,24],
            20:[24],
            21:[25],
            22:[25,26],
            23:[26,27],
            24:[27,28],
            25:[29,29],
            26:[30,31],
            27:[31,32],
            28:[32]
        }

        #Defined as (Key: Initial Position) : Value (All End Locations from Key)
        self.North_moveFlow = {
            32:[27,28],
            31:[26,27],
            30:[25,26],
            29:[25],
            28:[24],
            27:[23,24],
            26:[22,23],
            25:[21,22],
            24:[19,20],
            23:[18,19],
            22:[17,18],
            21:[17],
            20:[16],
            19:[15,16],
            18:[14,15],
            17:[13,14],
            16:[11,12],
            15:[10,11],
            14:[9,10],
            13:[9],
            12:[8],
            11:[7,8],
            10:[6,7],
            9:[5,6],
            8:[3,4],
            7:[2,3],
            6:[1,2],
            5:[1]
        }

        #Defined as left take going North, [Start, Take, Stop]
        #Defined as right take going South [Stop, Take, Start]
        self.left_take = {
            30:[25,21],
            22:[17,13],
            14:[9,5],
            26:[22,17],
            18:[14,9],
            10:[6,1],
            31:[26,22],
            23:[18,14],
            15:[10,6],
            27:[23,18],
            19:[15,10],
            11:[7,2],
            32:[27,23],
            24:[19,15],
            16:[11,7],
            28:[24,19],
            20:[16,11],
            12:[8,3]
        }

        #Defined as right take going North [Start, Take, Stop]
        #Defined as left take going South [Stop, Take, Start]
        self.right_take = {
            29:[25,22],
            21:[17,14],
            13:[9,6],
            25:[22,18],
            17:[14,10],
            9:[6,2],
            30:[26,23],
            22:[18,15],
            14:[10,7],
            26:[23,19],
            18:[15,11],
            10:[7,3],
            31:[27,24],
            23:[19,16],
            15:[11,8],
            27:[24,20],
            19:[16,12],
            11:[8,4]
        }

    def load_board(self):
        """Loads Checkers Pieces from CSV into Game"""
        with open(r"C:\Users\catch\BYU Coding\Proj\Ch3_Package\checkersData.csv", "r") as cdat:
            cdat.readline()
            for data in cdat:
                piecedat = data.split(',')
                if piecedat[0] == "B":
                    self.bt.append(regular(piecedat))
                elif piecedat[0] == "W":
                    self.wt.append(regular(piecedat))
        return None

    def update_locations(self):
        """Update all piece locations in ms dictionary"""
        for piece in self.wt:
            self.ps.update({piece.get_location(): piece})
        for piece in self.bt:
            self.ps.update({piece.get_location(): piece})
        return self.ps

    def update_moveList(self, team):
        """Pass in what team you want to move for, restricts movelist to your team
        Add support for kings somehow"""
        match team:
            case "W":
                for i in self.wt:
                    self.search_steps("North", i.get_location())
                    self.search_jumps("North", i.get_location())
            case "B":
                for i in self.bt:
                    self.search_steps("South", i.get_location())
                    self.search_jumps("South", i.get_location())
            case default:
                print("Error, Entered Default in function update_moveList. Exiting Game")
                exit()

    def search_steps(self, direction, position):
        """Checks and appends individual valid steps per given position"""
        temp_container = []
        match direction:
            case "North":
                for i in self.North_moveFlow.get(position):
                    if self.check_position(i):
                        temp_container.append(i)
                if temp_container != [None] and len(temp_container) != 0:
                    self.ms.update({position:temp_container})
                pass
            case "South":
                for i in self.South_moveFlow.get(position):
                    if self.check_position(i):
                        temp_container.append(i)
                if temp_container != [None] and len(temp_container) != 0:
                    self.ms.update({position:temp_container})
            case "King":
                pass

    def search_jumps(self, direction, position):
        """
        :::Helper Function to Update MoveList - ONLY used for a single Jump:::
        Direction is North, South or King
        Position is Current Starting Number
        Jumps is if a piece has executed a jump or not (single moves is not an option)

        CONDITIONS:
        1. You must have something to jump
        2. The space to jump to must exist and be vacant
        3. You must be jumping an object from a different team


        NOTE: We still have some "None" Sneaking Around in here
        """
        temp_container = []
        match direction:
            case "North":
                #Kept check to see if its in board to speed up computation
                if self.left_take.get(position) != None:  # Check the take exists
                    L_land = self.left_take.get(position)[1] #Check Left Land Spot
                    L_taken = self.left_take.get(position)[0]
                    if self.getTeam_byPos(L_taken) != None:
                        if(L_land != None and self.check_position(L_land) and self.getTeam_byPos(L_taken) != 'W' and self.getTeam_byPos(L_taken) != None): #Validate and add left Take
                            temp_container.append([position, taken, L_land])

                if self.right_take.get(position) != None:
                    R_land = self.right_take.get(position)[1] #Check Right Land Spot
                    R_taken = self.right_take.get(position)[0]
                    if self.getTeam_byPos(R_taken) != None:
                        if(R_land != None and self.check_position(R_land) and self.getTeam_byPos(R_taken) != 'W' and self.getTeam_byPos(R_taken) != None): #Validate and add right take
                            temp_container.append([position, taken, R_land])

                if len(temp_container) != 0:
                    temp_container.append(self.ms.get(position)) #Save Current Moves
                    self.ms.update({position : temp_container})
            case "South":
                L_land = position + 9 
                R_land = position + 7
                if self.left_take.get(L_land) != None:  # Check the take exists
                    if (0 <= L_land <= 32 and self.check_position(L_land)):  # Validate and add left Take
                        taken = self.left_take.get(L_land)[0]
                        if self.getTeam_byPos(taken) != 'B' and self.getTeam_byPos(taken) != None:
                            temp_container.append([position, taken, L_land])

                if self.right_take.get(R_land) != None: #Check that the take even exists
                    if (0 <= R_land <= 32 and self.check_position(R_land)):  # Validate and add right take
                        taken = self.right_take.get(R_land)[0]
                        if self.getTeam_byPos(taken) != 'B' and self.getTeam_byPos(taken) != None:
                            temp_container.append([position, taken, R_land])

                if len(temp_container) != 0:
                    temp_container.append(self.ms.get(position)) #Save Current Moves
                    self.ms.update({position : temp_container})
            case "King":
                pass
        return None
    
    def check_position(self, position):
        """Checks an individual position, Returns TRUE if empty and FALSE if taken"""
        if position in self.ps:
            return False
        return True
    
    def getTeam_byPos(self, position):
        peice = self.ps.get(position)
        if peice != None:
            return peice.get_team()
        else:
            return None


    def show_board(self):
        """Clears the terminal and displays the current board"""
        clear = lambda: os.system('cls')
        clear()
        #ps gives peice_location:peice
        #sl stands for spotlist. The strat is to fill it with 32 "_" spaces, and then overwrite it if a piece is there
        sl = ["_" for i in range(33)]
        sorted_ps = OrderedDict(sorted(self.ps.items()))
        # key_list = sorted_ps.keys()
        for i in sorted_ps:
            sl[i] = self.ps.get(i).get_team()

        print("__________________Current Ch3ck3rs Game__________________\n"
               f"|      | 01:{sl[1]} |      | 02:{sl[2]} |      | 03:{sl[3]} |      | 04:{sl[4]} |\n"
               f"| 05:{sl[5]} |      | 06:{sl[6]} |      | 07:{sl[7]} |      | 08:{sl[8]} |      |\n"
               f"|      | 09:{sl[9]} |      | 10:{sl[10]} |      | 11:{sl[11]} |      | 12:{sl[12]} |\n"
               f"| 13:{sl[13]} |      | 14:{sl[14]} |      | 15:{sl[15]} |      | 16:{sl[16]} |      |\n" 
               f"|      | 17:{sl[17]} |      | 18:{sl[18]} |      | 19:{sl[19]} |      | 20:{sl[20]} |\n"
               f"| 21:{sl[21]} |      | 22:{sl[22]} |      | 23:{sl[23]} |      | 24:{sl[24]} |      |\n" 
               f"|      | 25:{sl[25]} |      | 26:{sl[26]} |      | 27:{sl[27]} |      | 28:{sl[28]} |\n"
               f"| 29:{sl[29]} |      | 30:{sl[30]} |      | 31:{sl[31]} |      | 32:{sl[32]} |      |\n ")
        return None
    
    def print_moveSet(self):
        # for i in self.ms:
        #     print(i)
        print(self.ms)


#This class needs to check if an individual move is valid
#Also needs to congregate all valid moves

class Checkers_FSM():
    """
    Exclusively facilitates the gameplay and moves between players
    """
    def __init__(self, Board_Util):
        self.Board = Board_Util
        self.cs = "init"
        self.run_FSM()

    def run_FSM(self, state="init"):
        try:
            match state:
                case "init":
                    print("Enter 1 for Single Player, or 2 for Two Player")
                    play_style = int(input())
                    if (play_style == 1):
                        self.cs = "solo"
                    elif (play_style == 2):
                        self.cs = "p1"
                    self.Board.update_locations()
                    self.Board.update_moveList("B")

                case "p1":
                    # Print Board
                    self.Board.show_board()

                    # Take Input
                    print("Black's Turn! Move List: ")
                    self.Board.print_moveSet()
                    print(
                        "Please type a move via this format: PieceCurrentPosition,DesiredLocation")
                    curPos, move = map(int, input().split(","))

                    # Execute Move
                    piece_Obj = self.Board.ps.get(curPos)
                    piece_Obj.change_location(move)
                    self.Board.ps.pop(curPos)
                    print(f"{piece_Obj} moved from {curPos} to {move}")

                    # Reset and Check Win (Other Player Can't Move)
                    self.Board.ms.clear()
                    self.Board.update_locations()
                    #Maybe add a while loop here to continue for extra jumps
                    self.Board.update_moveList("W")
                    if (len(self.Board.ms) == 0):
                            self.cs = "win"
                    else:
                        self.cs = "p2"

                case "p2":
                    self.Board.show_board()

                    # Take Input
                    print("White's Turn! Move List: ")
                    self.Board.print_moveSet()
                    print(
                        "Please type a move via this format: PieceCurrentPosition,DesiredLocation")
                    curPos, move = map(int, input().split(","))

                    # Execute Move
                    piece_Obj = self.Board.ps.get(curPos)
                    piece_Obj.change_location(move)
                    self.Board.ps.pop(curPos)
                    print(f"{piece_Obj} moved from {curPos} to {move}")

                    # Reset and Check Win (Other Player Can't Move)
                    self.Board.ms.clear()
                    self.Board.update_locations()
                    self.Board.update_moveList("B")
                    if (len(self.Board.ms) == 0):
                            self.cs = "win"
                    else:
                        self.cs = "p1"

                case "solo":
                    pass
                case "comp":
                    pass
                case "win":
                    self.Board.show_board()
                    print("The game is over.")
                    exit()

            self.run_FSM(self.cs)

        except Exception as e:
            self.cs = "ERR"
            print("Entered Error State, Game Terminating")
            print(e)
            exit()

if __name__ == "__main__":
    a = Board_Util()
    b = Checkers_FSM(a)
