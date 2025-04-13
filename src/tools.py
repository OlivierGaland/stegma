import hashlib
import sys

from PIL import Image, ImageChops,ImageDraw
import matplotlib.pyplot as plt
import numpy as np

def progress_bar(text, current, total, bar_length=100):
    percent = current / total
    completed = int(bar_length * percent)
    bar = '█' * completed + '-' * (bar_length - completed)
    sys.stdout.write(f'\r{text} |{bar}| {int(percent * 100)}%')
    sys.stdout.flush()

def progress_bar_end(text, bar_length=100):
    progress_bar(text, 1, 1, bar_length)
    print()

def encode_string(data: str) -> str:
    return ''.join(format(ord(c), '08b') for c in data)

def decode_string(data: str) -> str:
    return ''.join(chr(int(data[i:i+8], 2)) for i in range(0, len(data), 8))

def get_hash_from_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def get_salted_hash_from_bytes(b: bytes, salt: bytes = b"") -> str:
    return hashlib.sha256(b + salt).hexdigest()

def xor_encrypt_decrypt(key: str, data: str):
    return ''.join(str(int(data[i]) ^ int(key[i % len(key)])) for i in range(len(data)))    

def get_int_from_hash(hash_hex: str, limit: int) -> int:
    # return determinist integer from hash ranged from 0 to limit-1
    if not isinstance(hash_hex, str): raise Exception("get_int_from_hash : Input must be a string.")
    if limit <= 0: raise Exception("get_int_from_hash : Limit must be greater than 0.")
    hash_hex = hash_hex.strip().lower().replace("0x", "")
    hash_int = int(hash_hex, 16)
    return hash_int % limit


def show_pictures_diff(file_in,file_out):
    original = Image.open(file_in).convert("RGB")
    embed = Image.open(file_out+".tmp").convert("RGB")
    stego = Image.open(file_out).convert("RGB")

    if original.size != embed.size: raise ValueError("Images have different sizes.")
    if original.size != stego.size: raise ValueError("Images have different sizes.")

    diff_embed = ImageChops.difference(original, embed)
    diff_embed_np = np.array(diff_embed)  
    diff_embed_np = (diff_embed_np > 0).astype(np.uint8) * 255 
    diff_embed_visible = Image.fromarray(diff_embed_np)

    diff = ImageChops.difference(original, stego)
    diff_np = np.array(diff)  
    diff_np = (diff_np > 0).astype(np.uint8) * 255 
    diff_visible = Image.fromarray(diff_np)

    # Crée une grille 2x2 pour afficher les images
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))

    # Affichage de l'image originale
    axs[0, 0].imshow(original)
    axs[0, 0].set_title("Former image")
    axs[0, 0].axis("off")

    # Affichage de l'image steganographique
    axs[0, 1].imshow(stego)
    axs[0, 1].set_title("Steganographed image")
    axs[0, 1].axis("off")

    # Affichage de la différence entre l'image originale et l'image d'intégration
    axs[1, 0].imshow(diff_embed_visible)
    axs[1, 0].set_title("Differences (Secret only)")
    axs[1, 0].axis("off")

    # Affichage de la différence entre l'image originale et l'image steganographique
    axs[1, 1].imshow(diff_visible)
    axs[1, 1].set_title("Differences (Final, with noise)")
    axs[1, 1].axis("off")

    plt.tight_layout()
    plt.show()


def show_pictures_diff_alt(file_in,file_out):
    original = Image.open(file_in).convert("RGB")
    stego = Image.open(file_out).convert("RGB")

    diff = ImageChops.difference(original, stego)
    pixel_size = 3
    diff_np = np.array(diff)
    
    w, h = original.size
    amplified = Image.new('RGB', (w, h), (0, 0, 0))
    draw = ImageDraw.Draw(amplified)

    for y in range(h):
        for x in range(w):
            if np.any(diff_np[y, x] > 0):
                draw.rectangle(
                    [(x - pixel_size // 2, y - pixel_size // 2), 
                     (x + pixel_size // 2, y + pixel_size // 2)],
                    fill=(255, 255, 255)
                )

    fig, axs = plt.subplots(1, 3, figsize=(30, 10))

    axs[0].imshow(original)
    axs[0].set_title("Former image")
    axs[0].axis("off")
    axs[1].imshow(stego)
    axs[1].set_title("Steganographed image")
    axs[1].axis("off")
    axs[2].imshow(amplified)
    axs[2].set_title(f"Differences (size {pixel_size}px)")
    axs[2].axis("off")

    plt.tight_layout()
    plt.show()
