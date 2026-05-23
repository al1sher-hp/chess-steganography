import zstandard as zstd
import re
import io

def extract_games(zst_file_path, output_pgn_path, min_elo=1500, max_elo=1600, limit=10000):
    # Regex naqshlar Elo reytinglarini ajratib olish uchun
    white_elo_pattern = re.compile(r'\[WhiteElo\s+"(\d+)"\]')
    black_elo_pattern = re.compile(r'\[BlackElo\s+"(\d+)"\]')
    
    with open(zst_file_path, 'rb') as f:
        # Zstandard decompressor yaratish
        dctx = zstd.ZstdDecompressor()
        
        # Oqimli (streaming) rejimida o'qish
        with dctx.stream_reader(f) as reader:
            # Faylni qatorma-qator matn sifatida o'qish uchun TextIOWrapper ishlatamiz
            text_stream = io.TextIOWrapper(reader, encoding='utf-8', errors='replace')
            
            with open(output_pgn_path, 'w', encoding='utf-8') as out_f:
                game_buffer = []
                white_elo = -1
                black_elo = -1
                match_count = 0
                
                for line in text_stream:
                    # Yangi o'yin boshlansa, oldingisini tekshiramiz
                    if line.startswith('[Event ') and game_buffer:
                        # Agar ikkala o'yinchi ham kerakli reyting oralig'ida bo'lsa
                        if min_elo <= white_elo <= max_elo and min_elo <= black_elo <= max_elo:
                            out_f.writelines(game_buffer)
                            match_count += 1
                            
                            if match_count % 1000 == 0:
                                print(f"Holat: {match_count} ta o'yin topildi va saqlandi.")
                                
                            # Limitga yetsa tsiklni to'xtatamiz
                            if match_count >= limit:
                                print(f"Maqsadli {limit} o'yin topildi. To'xtatilmoqda...")
                                return
                        
                        # Yangi o'yin uchun o'zgaruvchilarni tozalash
                        game_buffer = []
                        white_elo = -1
                        black_elo = -1
                        
                    game_buffer.append(line)
                    
                    # White va Black Elo reytinglarni qator ichidan izlash
                    if line.startswith('[WhiteElo'):
                        match = white_elo_pattern.search(line)
                        if match:
                            white_elo = int(match.group(1))
                            
                    elif line.startswith('[BlackElo'):
                        match = black_elo_pattern.search(line)
                        if match:
                            black_elo = int(match.group(1))
                            
                # Fayl oxirida qolib ketgan o'yinni saqlash (agar limitga yetmagan bo'lsa)
                if game_buffer and match_count < limit:
                    if min_elo <= white_elo <= max_elo and min_elo <= black_elo <= max_elo:
                        out_f.writelines(game_buffer)
                        match_count += 1
                        
                print(f"Jarayon yakunlandi. Jami: {match_count} ta o'yin saqlandi.")

if __name__ == '__main__':
    zst_file = r'D:\lichess_db_standard_rated_2018-09.pgn.zst'
    out_pgn  = r'D:\AIml\filtered_500_600.pgn'
    # Haqiqiy Elo taqsimotiga asosan 1500-1600 oralig'i eng ko'p o'yinlarga ega
    print(f"'{zst_file}' faylini oqim (stream) orqali o'qish boshlandi...")
    print("Filtr: Elo 1500-1600 | Limit: 10,000 o'yin")
    try:
        extract_games(zst_file, out_pgn, min_elo=1500, max_elo=1600, limit=10000)
    except FileNotFoundError:
        print(f"XATOLIK: '{zst_file}' fayli topilmadi. Iltimos uni joriy papkaga joylashtiring.")

