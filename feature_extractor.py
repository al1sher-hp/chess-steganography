"""
feature_extractor.py
--------------------
Berilgan chess.pgn.Game obyektidan 6 ta statistik feature ajratib oladi.

Steganografiya detection mantiq:
  stego_engine.py faqat legal_moves[0] (bit=0) yoki legal_moves[1] (bit=1)
  ni tanlaydi — ya'ni rank har doim 0 yoki 1 bo'ladi.
  Haqiqiy inson o'yinlarida rank taqsimoti ko'proq tarqalgan bo'ladi.
  Bu farq klassifikatsiya uchun asos bo'ladi.
"""

import chess
import chess.pgn
import statistics


def extract_features(game: chess.pgn.Game) -> list[float]:
    """
    Berilgan o'yin (chess.pgn.Game) dan 6 ta feature ajratib qaytaradi.

    Features:
        [0] avg_move_rank       -- har bir yurish legal_moves ro'yxatidagi
                                   o'rtacha tartib raqami (rank)
        [1] rank_0_ratio        -- legal_moves[0] tanlangan yurishlar ulushi
        [2] rank_1_ratio        -- legal_moves[1] tanlangan yurishlar ulushi
        [3] rank_0_or_1_ratio   -- legal_moves[0] yoki [1] tanlangan yurishlar ulushi
        [4] rank_variance       -- rank qiymatlari dispersiyasi (variance)
        [5] game_length         -- o'yindagi umumiy yurishlar soni

    :param game: chess.pgn.Game obyekti
    :return: 6 ta float dan iborat list
    """
    board = game.board()
    node = game

    ranks = []  # Har bir yurish uchun rank ro'yxati

    while node.variations:
        next_node = node.variations[0]
        move = next_node.move

        # Qonuniy yurishlarni UCI bo'yicha alifbo tartibida saralab rank topamiz
        legal_moves = sorted(board.legal_moves, key=lambda m: m.uci())

        if move in legal_moves:
            rank = legal_moves.index(move)
        else:
            # Kutilmagan holat — mavjud legal move emas, rank ni -1 deb olamiz
            rank = -1

        ranks.append(rank)
        board.push(move)
        node = next_node

    game_length = len(ranks)

    if game_length == 0:
        # Bo'sh o'yin — barcha feature larni nolga tenglashtiramiz
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    # --- Feature hisoblash ---
    avg_move_rank = sum(ranks) / game_length

    rank_0_count = ranks.count(0)
    rank_1_count = ranks.count(1)

    rank_0_ratio      = rank_0_count / game_length
    rank_1_ratio      = rank_1_count / game_length
    rank_0_or_1_ratio = (rank_0_count + rank_1_count) / game_length

    # Variance: bir elementli ro'yxat uchun statistics.variance xato beradi
    if game_length > 1:
        rank_variance = statistics.variance(ranks)
    else:
        rank_variance = 0.0

    return [
        avg_move_rank,
        rank_0_ratio,
        rank_1_ratio,
        rank_0_or_1_ratio,
        rank_variance,
        float(game_length),
    ]


# Feature nomlari (CSV ustun sarlavhalari uchun)
FEATURE_NAMES = [
    "avg_move_rank",
    "rank_0_ratio",
    "rank_1_ratio",
    "rank_0_or_1_ratio",
    "rank_variance",
    "game_length",
]


if __name__ == "__main__":
    # Qisqa sinov: StegoChess bilan yaratilgan o'yin uchun feature lar
    from stego_engine import StegoChess
    from encoder import text_to_binary

    engine = StegoChess()
    payload = text_to_binary("TEST")
    stego_game = engine.hide_payload(payload)

    features = extract_features(stego_game)
    print("Stego o'yin feature lari:")
    for name, val in zip(FEATURE_NAMES, features):
        print(f"  {name:<22} = {val:.4f}")
