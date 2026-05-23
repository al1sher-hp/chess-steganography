import chess.pgn
from encoder import text_to_binary, binary_to_text
from stego_engine import StegoChess

def main():
    print("=== AI Chess Steganography Tool (Red Team) ===")
    
    # 1. Maxfiy matn va uni ikkilik ko'rinishga o'tkazish
    secret_text = "SECRET"
    print(f"Asl matn: {secret_text}")
    
    payload_bin = text_to_binary(secret_text)
    print(f"Ikkilik (binary) matn: {payload_bin} (Uzunligi: {len(payload_bin)} bit)")
    
    # 2. Yashirish (Encoding)
    engine = StegoChess()
    game = engine.hide_payload(payload_bin)
    
    pgn_path = "secret_game.pgn"
    with open(pgn_path, "w", encoding="utf-8") as f:
        f.write(str(game))
    print(f"\nYashiringan ma'lumot PGN faylga saqlandi: {pgn_path}")
    
    # 3. O'qib olish (Decoding)
    with open(pgn_path, "r", encoding="utf-8") as f:
        loaded_game = chess.pgn.read_game(f)
        
    extracted_bin = engine.extract_payload(loaded_game, len(payload_bin))
    print(f"\nAjratib olingan ikkilik matn: {extracted_bin}")
    
    extracted_text = binary_to_text(extracted_bin)
    print(f"Dekod qilingan matn: {extracted_text}")
    
    if payload_bin == extracted_bin and secret_text == extracted_text:
        print("\nMuvaffaqiyatli! Matn to'liq va to'g'ri qayta tiklandi.")
    else:
        print("\nXatolik! Matn to'liq qayta tiklanmadi.")

if __name__ == "__main__":
    main()
