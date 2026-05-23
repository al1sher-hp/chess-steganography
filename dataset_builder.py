"""
dataset_builder.py
------------------
Ikki klassli (normal va stego) o'yinlar uchun balanced dataset yaratadi
va uni dataset.csv fayliga saqlaydi.

Label 0 (normal): Lichess filtered_500_600.pgn faylidan haqiqiy o'yinlar
Label 1 (stego):  stego_engine.py orqali tasodifiy payloadlar bilan
                  yaratilgan sintetik o'yinlar

Minimal hajm: har bir klassdan 500 ta namuna.
"""

import csv
import random
import string
import chess.pgn
import io

from stego_engine import StegoChess
from encoder import text_to_binary
from feature_extractor import extract_features, FEATURE_NAMES

# --- Konfiguratsiya ---
NORMAL_PGN_PATH   = "filtered_500_600.pgn"  # data_extractor.py chiqish fayli
OUTPUT_CSV_PATH   = "dataset.csv"
MIN_SAMPLES       = 500   # Har bir klassdan minimal namuna soni
RANDOM_SEED       = 42    # Takrorlanish uchun

random.seed(RANDOM_SEED)


# ─────────────────────────────────────────────
#  Yordamchi funksiyalar
# ─────────────────────────────────────────────

def random_payload_text(min_len: int = 3, max_len: int = 8) -> str:
    """3-8 ta tasodifiy ASCII harfdan iborat matn qaytaradi.

    Stego o'yini qonuniy yurishlar soni bilan cheklangan (taxminan 80-100
    yurish). 8 ta ASCII belgi = 64 bit, bu oddiy o'yin uchun yetarli.
    """
    length = random.randint(min_len, max_len)
    chars  = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def load_normal_games(pgn_path: str, limit: int) -> list:
    """
    Lichess PGN faylidan `limit` ta o'yin feature ro'yxatini o'qiydi.
    Fayl topilmasa yoki yetarli o'yin bo'lmasa, imkon qadar o'qiydi.
    """
    features_list = []
    try:
        with open(pgn_path, "r", encoding="utf-8", errors="replace") as f:
            count = 0
            while count < limit:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                feats = extract_features(game)
                # Bo'sh yoki juda qisqa o'yinlarni o'tkazib yuboramiz
                if feats[5] >= 4:
                    features_list.append(feats)
                    count += 1
                    if count % 100 == 0:
                        print(f"  Normal o'yinlar: {count}/{limit} o'qildi...", end="\r")
        print()
    except FileNotFoundError:
        print(f"[OGOHLANTIRISH] '{pgn_path}' fayli topilmadi.")
        print("  Normal o'yinlar uchun synthetic random o'yinlar yaratiladi (fallback).")

    return features_list


def generate_random_normal_game(max_moves: int = 60) -> chess.pgn.Game:
    """
    filtered_500_600.pgn mavjud bo'lmaganda fallback sifatida ishlatiladi.
    Tasodifiy qonuniy yurishlar bilan o'yin yaratadi — haqiqiy inson
    o'yinlariga o'xshash taqsimot hosil qiladi (0, 1 dan tashqari rank lar ham kiradi).
    """
    board = chess.Board()
    game  = chess.pgn.Game()
    node  = game
    num_moves = random.randint(20, max_moves)

    for _ in range(num_moves):
        legal = list(board.legal_moves)
        if not legal or board.is_game_over():
            break
        move = random.choice(legal)
        board.push(move)
        node = node.add_variation(move)

    return game


def generate_stego_game(max_retries: int = 10) -> chess.pgn.Game:
    """Tasodifiy matn bilan stego o'yin yaratadi.

    Agar o'yin yurishlar yetishmasligi sababli muvaffaqiyatsiz bo'lsa,
    kichikroq payload bilan qayta urinib ko'radi (max_retries marta).
    """
    engine = StegoChess()
    for attempt in range(max_retries):
        try:
            # Har bir urinishda payload uzunligini kamaytirgan holda sinab ko'ramiz
            max_len = max(2, 8 - attempt)  # 8, 7, 6, ... 2
            text        = random_payload_text(min_len=1, max_len=max_len)
            payload_bin = text_to_binary(text)
            return engine.hide_payload(payload_bin)
        except Exception:
            continue
    raise RuntimeError("Stego o'yin yaratib bo'lmadi — barcha urinishlar muvaffaqiyatsiz.")


# ─────────────────────────────────────────────
#  Asosiy funksiya
# ─────────────────────────────────────────────

def build_dataset(
    normal_pgn_path: str = NORMAL_PGN_PATH,
    output_path: str     = OUTPUT_CSV_PATH,
    min_samples: int     = MIN_SAMPLES,
) -> None:

    print("=" * 55)
    print("  Dataset yaratish boshlandi")
    print("=" * 55)

    # ── 1. LABEL 0: Normal o'yinlar ──────────────────────────
    print(f"\n[1/4] Label 0 (normal): '{normal_pgn_path}' dan o'qilmoqda...")
    normal_features = load_normal_games(normal_pgn_path, limit=min_samples)

    # Agar fayl bo'lmasa yoki yetarli bo'lmasa — fallback
    fallback_count = min_samples - len(normal_features)
    if fallback_count > 0:
        print(f"  Fallback: {fallback_count} ta tasodifiy normal o'yin yaratilmoqda...")
        for i in range(fallback_count):
            game  = generate_random_normal_game()
            feats = extract_features(game)
            normal_features.append(feats)
            if (i + 1) % 100 == 0:
                print(f"  Fallback normal: {i+1}/{fallback_count}", end="\r")
        print()

    print(f"  Normal namunalar: {len(normal_features)} ta")

    # ── 2. LABEL 1: Stego o'yinlar ───────────────────────────
    print(f"\n[2/4] Label 1 (stego): {min_samples} ta sintetik stego o'yin yaratilmoqda...")
    stego_features = []
    for i in range(min_samples):
        game  = generate_stego_game()
        feats = extract_features(game)
        stego_features.append(feats)
        if (i + 1) % 100 == 0:
            print(f"  Stego: {i+1}/{min_samples}", end="\r")
    print()
    print(f"  Stego namunalar: {len(stego_features)} ta")

    # ── 3. Dataset yig'ish va aralashtirish ──────────────────
    print(f"\n[3/4] Dataset yig'ilmoqda va aralashtirilmoqda...")
    rows = []
    for feats in normal_features:
        rows.append(feats + [0])   # label = 0
    for feats in stego_features:
        rows.append(feats + [1])   # label = 1

    random.shuffle(rows)

    # ── 4. CSV ga saqlash ─────────────────────────────────────
    print(f"\n[4/4] '{output_path}' ga saqlanmoqda...")
    header = FEATURE_NAMES + ["label"]
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows)

    # ── 5. Statistika chiqarish ───────────────────────────────
    print("\n" + "=" * 55)
    print("  Dataset statistikasi")
    print("=" * 55)

    total = len(rows)
    n_normal = sum(1 for r in rows if r[-1] == 0)
    n_stego  = sum(1 for r in rows if r[-1] == 1)
    print(f"  Jami namunalar : {total}")
    print(f"  Label 0 (normal): {n_normal} ({100*n_normal/total:.1f}%)")
    print(f"  Label 1 (stego) : {n_stego}  ({100*n_stego/total:.1f}%)")

    # Feature o'rtachalari (har bir klass bo'yicha)
    print()
    print(f"  {'Feature':<22}  {'Normal (label=0)':>17}  {'Stego (label=1)':>16}")
    print("  " + "-" * 59)
    for fi, fname in enumerate(FEATURE_NAMES):
        vals_normal = [r[fi] for r in rows if r[-1] == 0]
        vals_stego  = [r[fi] for r in rows if r[-1] == 1]
        mean_n = sum(vals_normal) / len(vals_normal)
        mean_s = sum(vals_stego)  / len(vals_stego)
        print(f"  {fname:<22}  {mean_n:>17.4f}  {mean_s:>16.4f}")

    print("=" * 55)
    print(f"  Dataset saqlandi: {output_path}")
    print("=" * 55)


if __name__ == "__main__":
    build_dataset()
