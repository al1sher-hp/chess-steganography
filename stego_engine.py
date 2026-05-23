import chess
import chess.pgn

class StegoChess:
    def __init__(self):
        pass
        
    def hide_payload(self, payload_bin: str) -> chess.pgn.Game:
        """
        Maxfiy ikkilik ma'lumotni shaxmat o'yini (PGN) ko'rinishida yashiradi.
        """
        board = chess.Board()
        game = chess.pgn.Game()
        node = game

        bit_index = 0
        while bit_index < len(payload_bin):
            legal_moves = sorted(board.legal_moves, key=lambda m: m.uci())
            
            if len(legal_moves) == 0:
                raise Exception("O'yin yakunlandi, lekin xabar to'liq yashirilmadi.")
                
            if len(legal_moves) == 1:
                # Majburiy yurish, bit ishlatilmaydi
                move = legal_moves[0]
            else:
                # 2 yoki undan ko'p yurish
                bit = payload_bin[bit_index]
                if bit == '0':
                    move = legal_moves[0]
                else:
                    move = legal_moves[1]
                bit_index += 1
                
            board.push(move)
            node = node.add_variation(move)
            
        return game
        
    def extract_payload(self, pgn_game: chess.pgn.Game, payload_length: int) -> str:
        """
        PGN o'yinidan yashirilgan ikkilik ma'lumotni ajratib oladi.
        """
        board = pgn_game.board()
        payload_bin = ""
        node = pgn_game
        
        while len(payload_bin) < payload_length and node.variations:
            legal_moves = sorted(board.legal_moves, key=lambda m: m.uci())
            next_node = node.variations[0]
            move = next_node.move
            
            if len(legal_moves) > 1:
                if move == legal_moves[0]:
                    payload_bin += '0'
                elif move == legal_moves[1]:
                    payload_bin += '1'
                else:
                    raise Exception(f"Kutilmagan yurish topildi: {move}. Yashirilgan ma'lumot buzilgan bo'lishi mumkin.")
                    
            board.push(move)
            node = next_node
            
        return payload_bin
