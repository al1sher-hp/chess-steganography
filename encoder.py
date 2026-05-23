def text_to_binary(text: str) -> str:
    """
    Maxfiy matnni ikkilik sanoq sistemasi (binary) oqimiga aylantiradi.
    """
    return ''.join(format(ord(c), '08b') for c in text)

def binary_to_text(binary_str: str) -> str:
    """
    Ikkilik (binary) oqimni orqaga, oddiy matnga o'giradi.
    """
    chars = [chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8)]
    return ''.join(chars)
