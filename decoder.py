import chess.pgn
from stego_engine import StegoChess
from encoder import text_to_binary, binary_to_text


def decode_pgn(pgn_path: str, payload_length: int) -> str | None:
    """
    PGN faylidan maxfiy xabarni o'qiydi va uni matnga aylantiradi.

    :param pgn_path: PGN fayl yo'li (string)
    :param payload_length: Yashirilgan xabarning bit uzunligi (int)
    :return: Dekod qilingan matn (str) yoki None
    """
    # PGN faylini ochib, chess.pgn.Game obyektiga parse qilamiz
    with open(pgn_path, "r", encoding="utf-8") as f:
        game = chess.pgn.read_game(f)

    if game is None:
        print("XATOLIK: PGN faylidan o'yin o'qib olinmadi.")
        return None

    engine = StegoChess()
    payload_bin = engine.extract_payload(game, payload_length)

    if payload_bin:
        text = binary_to_text(payload_bin)
        return text
    return None


if __name__ == "__main__":
    # --- CLI testi: "HELLO" so'zini kodlash va dekodlash ---
    secret_text = "HELLO"
    pgn_path = "test_hello.pgn"

    print(f"=== CLI Testi ===")
    print(f"Asl matn: {secret_text}")

    # 1. Ikkilik sanoqqa o'tkazish
    payload_bin = text_to_binary(secret_text)
    print(f"Binary: {payload_bin} (uzunligi: {len(payload_bin)} bit)")

    # 2. Encode: shaxmat o'yiniga yashirish
    engine = StegoChess()
    game = engine.hide_payload(payload_bin)
    with open(pgn_path, "w", encoding="utf-8") as f:
        f.write(str(game))
    print(f"PGN faylga saqlandi: {pgn_path}")

    # 3. Decode: fayldan qaytadan o'qish
    result = decode_pgn(pgn_path, len(payload_bin))
    print(f"Dekod qilingan matn: {result}")

    # 4. Natijani tekshirish
    if result == secret_text:
        print("[OK] Muvaffaqiyatli! Matn to'liq va to'g'ri qayta tiklandi.")
    else:
        print("[FAIL] Xatolik! Matn to'g'ri tiklanmadi.")
