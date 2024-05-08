"""
Storing all the information about the current state of chess game.
Determining valid moves at current state.
It will keep move log.
"""


class GameState:
    def __init__(self):
        """
        Board is an 8x8 2d list, each element in list has 2 characters.
        The first character represents the color of the piece: 'b' or 'w'.
        The second character represents the type of the piece: 'R', 'N', 'B', 'Q', 'K' or 'p'.
        "--" represents an empty space with no piece.
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []
        self.enpassant_possible = ()  # coordinates for the square where en-passant capture is possible
        self.enpassant_possible_log = [self.enpassant_possible]
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]

    def makeMove(self, move):
        """
        Takes a Move as a parameter and executes it.
        (this will not work for castling, pawn promotion and en-passant)
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)  # log the move so we can undo it later
        self.white_to_move = not self.white_to_move  # switch players
        # update king's location if moved
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            # if not is_AI:
            #    promoted_piece = input("Promote to Q, R, B, or N:") #take this to UI later
            #    self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece
            # else:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        # enpassant move
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = "--"  # capturing the pawn

        # update enpassant_possible variable
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:  # only on 2 square pawn advance
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # king-side castle move
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1]  # moves the rook to its new square
                self.board[move.end_row][move.end_col + 1] = '--'  # erase old rook
            else:  # queen-side castle move
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col - 2]  # moves the rook to its new square
                self.board[move.end_row][move.end_col - 2] = '--'  # erase old rook

        self.enpassant_possible_log.append(self.enpassant_possible)

        # update castling rights - whenever it is a rook or king move
        self.updateCastleRights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                   self.current_castling_rights.wqs, self.current_castling_rights.bqs))

    def undoMove(self):
        """
        Undo the last move
        """
        if len(self.move_log) != 0:  # make sure that there is a move to undo
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move  # swap players
            # update the king's position if needed
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)
            # undo en passant move
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = "--"  # leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            # undo castle rights
            self.castle_rights_log.pop()  # get rid of the new castle rights from the move we are undoing
            self.current_castling_rights = self.castle_rights_log[
                -1]  # set the current castle rights to the last one in the list
            # undo the castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # king-side
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:  # queen-side
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'
            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        """
        Update the castle rights given the move
        """
        if move.piece_captured == "wR":
            if move.end_col == 0:  # left rook
                self.current_castling_rights.wqs = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_col == 0:  # left rook
                self.current_castling_rights.bqs = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.bks = False

        if move.piece_moved == 'wK':
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.bks = False

    def getValidMoves(self):
        """
        All moves considering checks.
        """
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        # advanced algorithm
        moves = []
        self.in_check, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.getAllPossibleMoves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]  # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # squares that pieces can move to
                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i,
                                        king_col + check[3] * i)  # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[
                            1] == check_col:  # once you get to piece and check
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].piece_moved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].end_row,
                                moves[i].end_col) in valid_squares:  # move doesn't block or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(king_row, king_col, moves)
        else:  # not in check - all moves are fine
            moves = self.getAllPossibleMoves()
            if self.white_to_move:
                self.getCastleMoves(self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.getCastleMoves(self.black_king_location[0], self.black_king_location[1], moves)

        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                # TODO stalemate on repeated moves
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.current_castling_rights = temp_castle_rights
        return moves

    def inCheck(self):
        """
        Determine if a current player is in check
        """
        if self.white_to_move:
            return self.squareUnderAttack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.squareUnderAttack(self.black_king_location[0], self.black_king_location[1])

    def squareUnderAttack(self, row, col):
        """
        Determine if enemy can attack the square row col
        """
        self.white_to_move = not self.white_to_move  # switch to opponent's point of view
        opponents_moves = self.getAllPossibleMoves()
        self.white_to_move = not self.white_to_move
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:  # square is under attack
                return True
        return False

    def getAllPossibleMoves(self):
        """
        All moves without considering checks.
        """
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)  # calls appropriate move function based on piece type
        return moves

    def checkForPinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "p" and (
                                (enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks

    def getPawnMoves(self, row, col, moves):
        """
        Get all the pawn moves for the pawn located at row, col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            move_amount = -1
            start_row = 6
            enemy_color = "b"
            king_row, king_col = self.white_king_location
        else:
            move_amount = 1
            start_row = 1
            enemy_color = "w"
            king_row, king_col = self.black_king_location

        if self.board[row + move_amount][col] == "--":  # 1 square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(Move((row, col), (row + move_amount, col), self.board))
                if row == start_row and self.board[row + 2 * move_amount][col] == "--":  # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2 * move_amount, col), self.board))
        if col - 1 >= 0:  # capture to the left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col - 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col - 1), self.board))
                if (row + move_amount, col - 1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col - 1), self.board, is_enpassant_move=True))
        if col + 1 <= 7:  # capture to the right
            if not piece_pinned or pin_direction == (move_amount, +1):
                if self.board[row + move_amount][col + 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col + 1), self.board))
                if (row + move_amount, col + 1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col + 1), self.board, is_enpassant_move=True))

    def getRookMoves(self, row, col, moves):
        """
        Get all the rook moves for the rook located at row, col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][
                    1] != "Q":  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if self.white_to_move else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check for possible moves only in boundaries of the board
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty space is valid
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # capture enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getKnightMoves(self, row, col, moves):
        """
        Get all the knight moves for the knight located at row col and add the moves to the list.
        """
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2),
                        (1, -2))  # up/left up/right right/up right/down down/left down/right left/up left/down
        ally_color = "w" if self.white_to_move else "b"
        for move in knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:  # so its either enemy piece or empty square
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    def getBishopMoves(self, row, col, moves):
        """
        Get all the bishop moves for the bishop located at row col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # diagonals: up/left up/right down/right down/left
        enemy_color = "b" if self.white_to_move else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check if the move is on board
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty space is valid
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # capture enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getQueenMoves(self, row, col, moves):
        """
        Get all the queen moves for the queen located at row col and add the moves to the list.
        """
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        """
        Get all the king moves for the king located at row col and add the moves to the list.
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece - empty or enemy
                    # place king on end square and check for checks
                    if ally_color == "w":
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == "w":
                        self.white_king_location = (row, col)
                    else:
                        self.black_king_location = (row, col)

    def getCastleMoves(self, row, col, moves):
        """
        Generate all valid castle moves for the king at (row, col) and add them to the list of moves.
        """
        if self.squareUnderAttack(row, col):
            return  # can't castle while in check
        if (self.white_to_move and self.current_castling_rights.wks) or (
                not self.white_to_move and self.current_castling_rights.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or (
                not self.white_to_move and self.current_castling_rights.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))

    def getQueensideCastleMoves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # in chess, fields on the board are described by two symbols, one of them being number between 1-8 (which is corresponding to rows)
    # and the second one being a letter between a-f (corresponding to columns), in order to use this notation we need to map our [row][col] coordinates
    # to match the ones used in the original chess game
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        # pawn promotion
        self.is_pawn_promotion = (self.piece_moved == "wp" and self.end_row == 0) or (
                self.piece_moved == "bp" and self.end_row == 7)
        # en passant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"
        # castle move
        self.is_castle_move = is_castle_move

        self.is_capture = self.piece_captured != "--"
        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        """
        Overriding the equals method.
        """
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        if self.is_pawn_promotion:
            return self.getRankFile(self.end_row, self.end_col) + "Q"
        if self.is_castle_move:
            if self.end_col == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.is_enpassant_move:
            return self.getRankFile(self.start_row, self.start_col)[0] + "x" + self.getRankFile(self.end_row,
                                                                                                self.end_col) + " e.p."
        if self.piece_captured != "--":
            if self.piece_moved[1] == "p":
                return self.getRankFile(self.start_row, self.start_col)[0] + "x" + self.getRankFile(self.end_row,
                                                                                                    self.end_col)
            else:
                return self.piece_moved[1] + "x" + self.getRankFile(self.end_row, self.end_col)
        else:
            if self.piece_moved[1] == "p":
                return self.getRankFile(self.end_row, self.end_col)
            else:
                return self.piece_moved[1] + self.getRankFile(self.end_row, self.end_col)

        # TODO Disambiguating moves

    def getRankFile(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]

    def __str__(self):
        if self.is_castle_move:
            return "0-0" if self.end_col == 6 else "0-0-0"

        end_square = self.getRankFile(self.end_row, self.end_col)

        if self.piece_moved[1] == "p":
            if self.is_capture:
                return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                return end_square + "Q" if self.is_pawn_promotion else end_square

        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += "x"
        return move_string + end_square










# '''
# This class is responsible for all infomation about current state of game.
# Also responsible for valid moves at the current state with a move log.
# '''
# class GameState():
#     def __init__(self):
#         '''
#         The first letter represent color of the piece:
#             'b' -  black, 'w' - white
         
#         and the second one - type of the piece:
#             'B' - Bishop, 'N' - Knight, 'R' - Rook, 'Q' - Queen, 'K' - King, 'p' - Pawn
#         '''

#         #can use numpy for Ai and optimized
#         self.board = [ 
#             ["bR" , "bN" , "bB" , "bQ" , "bK" , "bB" , "bN" , "bR"],
#             ["bp" , "bp" , "bp" , "bp" , "bp" , "bp" , "bp" , "bp" ],
#             ["--" , "--" , "--" , "--" , "--" , "--" , "--" , "--"],
#             ["--" , "--" , "--" , "--" , "--" , "--" , "--" , "--"],
#             ["--" , "--" , "--" , "--" , "--" , "--" , "--" , "--"],
#             ["--" , "--" , "--" , "--" , "--" , "--" , "--" , "--"],
#             ["wp" , "wp" , "wp" , "wp" , "wp" , "wp" , "wp" , "wp" ],
#             ["wR" , "wN" , "wB" , "wQ" , "wK" , "wB" , "wN" , "wR"]
            
#         ]

#         self.moveFunctions={
#             'p':self.getPawnMoves,
#             'R':self.getRookMoves,
#             'N':self.getKnightMoves,
#             'B':self.getBishopMoves,
#             'Q':self.getQueenMoves,
#             'K':self.getKingMoves
#         }

#         self.whiteToMove= True
#         self.moveLog=[]
#         self.whiteKingLocation=(7,4)
#         self.blackKingLocation=(0,4)
#         self.checkMate=False
#         self.staleMate=False
#         self.inCheck=False
#         self.pins=False
#         self.checks=[]


#     def make_move(self,move):
#         ''''
#         Takes move as parameter and executes it 
#         Exception --> This will not work for Casteling and en-passant
#         '''
#         self.board[move.startRow][move.startCol]= '--'
#         self.board[move.endRow][move.endCol]=move.piece_moved_from
#         self.moveLog.append(move)
#         self.whiteToMove= not self.whiteToMove

#         # update king's location if moved
#         if move.piece_moved_from=="wK":
#             self.whiteKingLocation=(move.endRow,move.endCol)
#         elif move.piece_moved_from=="bK":
#             self.blackKingLocation=(move.endRow,move.endCol)

    
#     def undoMove(self):
#         if len(self.moveLog) != 0:
#             move=self.moveLog.pop()
#             self.board[move.startRow][move.startCol]=move.piece_moved_from
#             self.board[move.endRow][move.endCol]=move.piece_captured_at
#             self.whiteToMove=not self.whiteToMove
#             # update king's location if needed
#             if move.piece_moved_from=="wK":
#                 self.whiteKingLocation=(move.startRow,move.startCol)
#             elif move.piece_moved_from=="bK":
#                 self.blackKingLocation=(move.startRow,move.startCol)
 


#     def valid_move(self ):
#         if len(self.moveLog)!=0:
#             move=self.moveLog.pop() 
#             self.board[move.startRow][move.startCol]=move.piece_moved_from
#             self.board[move.endRow][move.endCol]=move.piece_captured_at
#             return False
        

#     def get_valid_move(self):

#         moves=[]
#         self.inCheck,self.pins,self.checks=self.checkForPinsAndChecks()
#         if self.whiteToMove:
#             kingRow=self.whiteKingLocation[0]
#             kingCol=self.whiteKingLocation[1]
#         else:
#             kingRow=self.blackKingLocation[0]
#             kingCol=self.blackKingLocation[1]
#         if self.inCheck:
#             if len(self.checks)==1: # only 1 check , block or move king
#                 moves=self.get_all_possible_moves()
#                 # to block the check, you must move the piece into one of the squares between the enemy piece and king
#                 check=self.checks[0] #check information
#                 checkRow=check[0]
#                 checkCol=check[1]
#                 pieceChecking=self.board[checkRow][checkCol] #enemy piece causing the check
#                 validSquares=[] # squares that pieces can move to
#                 # if knight, must capture knight or move king , other pieces can be blocked
#                 if pieceChecking[1]=="N":
#                     validSquares=[(checkRow,checkCol)]
#                 else:
#                     for i in range(1,8):
#                         validSquare=(kingRow +check[2]*i,kingCol+check[3]*i) # check[2] and check[3] are check directions
#                         validSquares.append(validSquare)
#                         if validSquare[0]==checkRow and validSquare[1]==checkCol:
#                             break
#                 # get rid of any moves that don't block check or move king
#                 for i in range(len(moves)-1,-1,-1): # go through backwards when you are removing from list
#                     if moves[i].piece_moved_from[1] !='K': # move dosen't move king so it must block or capture
#                         if not (moves[i].endRow,moves[i].endCol) in validSquares:# move dosen't block check or capture piece
#                             moves.remove(moves[i])
#             else: # double check , king has to move
#                 self.get_all_possible_moves(kingRow,kingCol,moves)
#         else: #not in check , so all moves are fine
#             moves=self.get_all_possible_moves()
        
#         return moves


#     def checkForPinsAndChecks(self):
#         pins=[] # squares where all allied pined pieces is and direction pinned from
#         checks=[] #squares where enemy is applying a check
#         inCheck=False
#         if self.whiteToMove:
#             enemyColor="b"
#             allyColor="w"
#             startRow=self.whiteKingLocation[0]
#             startCol=self.whiteKingLocation[1]
#         else:
#             enemyColor="w"
#             allyColor="b"
#             startRow=self.blackKingLocation[0]
#             startCol=self.blackKingLocation[1]
#         # check outward from king for pins and checks, keep track of pins
#         directions=((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
#         for j in range(len(directions)):
#             d=directions[j]
#             possiblePin=() #reset possible pin
#             for i in range(1,8):
#                 endRow=startRow+d[0]*i
#                 endCol=startCol+d[1]*i
#                 if 0<=endRow<0 and 0<=endCol<0:
#                     endPiece=self.board[endRow][endCol]
#                     if endPiece[0]==allyColor and endPiece[1] != "K":
#                         if possiblePin==(): #1st allied piece could be pinned
#                             possiblePin=(endRow,endCol,d[0],d[1])
#                         else: #2nd allied piece , so no pin or check possible in this direction
#                             break
#                     elif endPiece[0]==enemyColor:
#                         type=endPiece[1]
#                         # 5 possibilities in this complex condition
#                         # 1) orthogonaly away from king and piece is a rook
#                         # 2) diagonally away from king and piece is a bishop
#                         # 3) 1 square away fiagonally from king is a pawn
#                         # 4) any direction and any piece is a queen 
#                         # 5) any direction 1 square away and piece is a king (this is necessary to prevent a king move to a square controlled by another king)
#                         if (0<=j<=3 and type=="R") or (4<=j<=7 and type=="B") or (i==1 and type=="p" and ((enemyColor=="w" and 6<=j<=7) or (enemyColor=="b" and 4<=j<=5))) or (type=="Q") or (i==1 and type=="K"):

#                             if possiblePin == (): # no piece blocking , so check
#                                 inCheck=True
#                                 checks.append((endRow,endCol,d[0],d[1]))
#                                 break
#                             else: # piece blocking so pin 
#                                 pins.append(possiblePin)
#                                 break
#                         else: # enemy piece not applying checks
#                             break
#         # Check for knight checks
#         knightMoves=((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
#         for m in knightMoves:
#             endRow=startRow+m[0]
#             endCol=startCol+m[1]
#             if 0<=endRow<8 and 0<=endCol<8:
#                 endPiece=self.board[endRow][endCol]
#                 if endPiece[0]==enemyColor and endPiece[1]=="N": # enemy knight attacking king
#                     inCheck=True
#                     checks.append((endRow,endCol,m[0],m[1]))
#         return inCheck,pins,checks








#     def inCheck(self):
#         '''
#         Determines if current player is in check
#         '''
#         if self.whiteToMove:
#             return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
#         else:
#             return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
    
#     def squareUnderAttack(self,r,c):
#         '''
#         determine if the enemy can attack the square r,c
#         '''
#         self.whiteToMove= not self.whiteToMove # switch to opponent turn
#         oppMoves=self.get_all_possible_moves() 
#         self.whiteToMove=not self.whiteToMove # switch the turn back
#         for move in oppMoves:
#             if move.endRow==r and move.endCol==c: # square is under attack
#                 return True
#         return False


#     def get_all_possible_moves(self):
#         moves=[]
#         for r in range(len(self.board)):
#             for c in range(len(self.board[r])):
#                 turn=self.board[r][c][0]
#                 if (turn=='w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
#                     piece=self.board[r][c][1]
#                     self.moveFunctions[piece](r,c,moves)
#         return moves
    

#     def getPawnMoves(self,r,c,moves):
#         '''
#         get all the pawn moves for the pawn located at row, col, and add these moves to the list
#         '''
#         if self.whiteToMove:
#             if self.board[r-1][c]=="--": # 1 square pawn advance
#                 moves.append(Move((r,c),(r-1,c),self.board))
#                 if r==6 and self.board[r-2][c]=="--":# 2 square pawn advance
#                     moves.append(Move((r,c),(r-2,c),self.board)) 
#                     # print("Pawn Moved")
            
#             if c-1>=0: # capture at left
#                 if self.board[r-1][c-1][0]=='b':# check enemy piece to capture
#                     moves.append(Move((r,c),(r-1,c-1),self.board))
#                     # print("White Pawn captured enemy at left")

#             if c+1<=7: # capture at right
#                 if self.board[r-1][c+1][0]=='b':# check enemy piece to capture
#                     moves.append(Move((r,c),(r-1,c+1),self.board))
#                     # print("White Pawn captured enemy at right")

#         else: #black pawn
#             if self.board[r+1][c]=="--": #square move
#                 moves.append(Move((r,c),(r+1,c),self.board))
#                 if r==1 and self.board[r+2][c]=="--": # 2 square move
#                     moves.append(Move((r,c),(r+2,c),self.board))
                
#                 #captures
#                 if c-1>=0: # captures to left
#                     if self.board[r+1][c-1][0]=='w':
#                         moves.append(Move((r,c),(r+1,c-1),self.board))
#                         # print("Black Pawn captured enemy at left")
#                 if c+1<=7: # captures to right
#                     if self.board[r+1][c+1][0]=='w':
#                         moves.append(Move((r,c),(r+1,c+1),self.board))
#                         # print("Black Pawn captured enemy at right")
#                 #add pawn promotion
  
#     def getRookMoves(self,r,c,moves):
#         '''
#         get all the rook moves for the pawn located at row, col, and add these moves to the list
#         '''
#         directions=((-1,0),(0,-1),(1,0),(0,1)) # up ,left, down ,right
#         enemyColor="b" if self.whiteToMove else "w"

#         for d in directions:
#             for i in range(1,8):
#                 endRow=r+d[0]*i
#                 endCol=c+d[1]*i
#                 if 0<=endRow<8 and 0<=endCol<8: # on board
#                     endPiece=self.board[endRow][endCol]
#                     if endPiece=="--": # empty space valid
#                         moves.append(Move((r,c),(endRow,endCol),self.board))
#                         # print("rook moved")
#                     elif endPiece[0]==enemyColor: # enemy piece valid
#                         moves.append(Move((r,c),(endRow,endCol),self.board))
#                         # print("rook captured enemy")
#                         break
#                     else : # friendly pieces invalid
#                         break
#                 else: # off board
#                     break

#     def getKnightMoves(self,r,c,moves):
#         '''
#         get all the Kingt moves for the pawn located at row, col, and add these moves to the list
#         '''
#         knightMoves=((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
#         allyColor="w" if self.whiteToMove else "b"
#         for m in knightMoves:
#             endRow=r+m[0]
#             endCol=c+m[1]
#             if 0 <= endRow < 8 and 0 <= endCol < 8:
#                 endPiece= self.board[endRow][endCol]
#                 if endPiece[0] != allyColor: # enemy or empty , then it is valid
#                     moves.append(Move((r,c),(endRow,endCol),self.board))

#     def getBishopMoves(self,r,c,moves):
#         '''
#         get all the Bishop moves for the pawn located at row, col, and add these moves to the list
#         '''
#         directions=((-1,-1),(-1,1),(1,-1),(1,1)) # 4 diagonals
#         enemyColor="b" if self.whiteToMove else "w"

#         for d in directions:
#             for i in range(1,8):
#                 endRow=r+d[0]*i
#                 endCol=c+d[1]*i
#                 if 0<=endRow<8 and 0<=endCol<8: # on board
#                     endPiece=self.board[endRow][endCol]
#                     if endPiece=="--": # empty space valid
#                         moves.append(Move((r,c),(endRow,endCol),self.board))
#                         # print("rook moved")
#                     elif endPiece[0]==enemyColor: # enemy piece valid
#                         moves.append(Move((r,c),(endRow,endCol),self.board))
#                         # print("rook captured enemy")
#                         break
#                     else : # friendly pieces invalid
#                         break
#                 else: # off board
#                     break

#         pass
    
#     def getQueenMoves(self,r,c,moves):
#         '''
#         get all the Queen moves for the pawn located at row, col, and add these moves to the list --> uses abstraction method
#         '''
#         self.getRookMoves(r,c,moves)
#         self.getBishopMoves(r,c,moves)

#     def getKingMoves(self,r,c,moves):
#         '''
#         get all the King moves for the pawn located at row, col, and add these moves to the list
#         '''
#         kingMoves=((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
#         allyColor="w" if self.whiteToMove else "b"
#         for i in range(8):
#             endRow=r+kingMoves[i][0]
#             endCol=c+kingMoves[i][1]
#             if 0 <= endRow < 8 and 0<=endCol<8:
#                 endPiece=self.board[endRow][endCol]
#                 if endPiece[0] !=allyColor: # not an ally piece or empty is valid
#                     moves.append(Move((r,c),(endRow,endCol),self.board)) 


                    




# class Move():

#     # Maping rows and columns to numbers
#     ranks_to_rows={
#         "1": 7,
#         "2": 6,
#         "3": 5,
#         "4": 4,
#         "5": 3,
#         "6": 2,
#         "7": 1,
#         "8": 0
#     }
#     rows_to_ranks={v:k for k,v in ranks_to_rows.items()}

#     files_to_cols = {
#     "A": 0,
#     "B": 1,
#     "C": 2,
#     "D": 3,
#     "E": 4,
#     "F": 5,
#     "G": 6,
#     "H": 7
#     }

#     cols_to_files = {v: k for k, v in files_to_cols.items()}

#     def __init__(self,start_sq,end_sq,board):
#         self.startRow =start_sq[0]
#         self.startCol =start_sq[1]
#         self.endRow =end_sq[0]
#         self.endCol =end_sq[1]
#         self.piece_moved_from = board[self.startRow] [self.startCol]
#         self.piece_captured_at = board[self.endRow][self.endCol]
#         self.moveID=self.startRow * 1000 + self.startCol *100 +self.endRow*10+self.endCol
#         print("Move ID = ", self.moveID)


#     def __eq__(self,other):
#         '''
#         overriding the equals method
#         '''
#         if isinstance(other,Move):
#             return self.moveID==other.moveID
#         return False


#     def get_chess_notation(self):
#         return self.get_rank_file(self.startRow,self.startCol)+self.get_rank_file(self.endRow,self.endCol)
    
#     def get_rank_file(self,r,c):
#         return self.cols_to_files[c]+self.rows_to_ranks[r]
    
