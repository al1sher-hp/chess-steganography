"""
elo_scanner.py — Lichess .zst faylidan Elo taqsimotini tezkor skanerlaydi.
Birinchi 100,000 o'yinni o'qib, Elo histogrammasini chiqaradi.
"""
import zstandard as zstd
import re
import io
from collections import Counter

ZST_FILE  = r'D:\lichess_db_standard_rated_2018-09.pgn.zst'
SCAN_LIMIT = 100_000   # Birinchi N ta o'yinni tekshir

white_elo_pattern = re.compile(r'\[WhiteElo\s+"(\d+)"\]')
black_elo_pattern = re.compile(r'\[BlackElo\s+"(\d+)"\]')

buckets  = Counter()   # Elo araliq statistikasi (har 100 lik)
game_count = 0
white_elo = -1
black_elo = -1

print(f"Skanerlash boshlandi: birinchi {SCAN_LIMIT:,} o'yin...")

with open(ZST_FILE, 'rb') as f:
    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(f) as reader:
        text_stream = io.TextIOWrapper(reader, encoding='utf-8', errors='replace')
        for line in text_stream:
            if line.startswith('[Event '):
                # Oldingi o'yinni qayd qilish
                if white_elo > 0 and black_elo > 0:
                    avg_elo = (white_elo + black_elo) // 2
                    bucket  = (avg_elo // 100) * 100
                    buckets[bucket] += 1
                    game_count += 1
                    if game_count >= SCAN_LIMIT:
                        break
                    if game_count % 10_000 == 0:
                        print(f"  {game_count:>6,} o'yin tekshirildi...", end='\r')
                white_elo = -1
                black_elo = -1

            elif line.startswith('[WhiteElo'):
                m = white_elo_pattern.search(line)
                if m:
                    white_elo = int(m.group(1))
            elif line.startswith('[BlackElo'):
                m = black_elo_pattern.search(line)
                if m:
                    black_elo = int(m.group(1))

print(f"\nJami {game_count:,} o'yin skanerlandi.\n")
print(f"{'Elo oralig':>12}  {'Soni':>8}  {'%':>6}  Bar")
print("-" * 50)
for elo_start in sorted(buckets.keys()):
    count = buckets[elo_start]
    pct   = count / game_count * 100
    bar   = '#' * int(pct / 0.5)
    print(f"  {elo_start:4d}-{elo_start+99:<4d}  {count:>8,}  {pct:>5.1f}%  {bar}")

# Top 3 eng ko'p uchraydigan oraliq
top3 = buckets.most_common(3)
print(f"\nEng ko'p o'yinlar:")
for elo_start, cnt in top3:
    print(f"  {elo_start}-{elo_start+99} Elo: {cnt:,} o'yin ({cnt/game_count*100:.1f}%)")
