import os
import paq
import sys

# Generate primes up to 2**24
def generate_primes(limit):
    primes = []
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for num in range(2, limit + 1):
        if sieve[num]:
            primes.append(num)
            for multiple in range(num * num, limit + 1, num):
                sieve[multiple] = False
    return primes

prime_limit = 2**24
primes = generate_primes(prime_limit)
with open("primes.txt", "w") as f:
    f.write("\n".join(map(str, primes)))
print(f"Prime numbers saved. Total: {len(primes)}")

def transform_with_pattern(data, chunk_size=3):
    """XOR each 3-byte chunk with 0xFF."""
    transformed = bytearray()
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        transformed.extend(b ^ 0xFF for b in chunk)
    return transformed

def encode_with_compression():
    print("\nEncoding with XOR and zlib compression")
    try:
        input_file = input("Enter input file: ").strip()
        output_base = input("Enter output base name (without .enc): ").strip()
    except EOFError:
        print("No input detected.")
        return

    output_enc = output_base + ".enc"
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' not found.")
        return
    if os.path.exists(output_enc):
        print(f"Warning: '{output_enc}' will be overwritten.")

    try:
        with open(input_file, 'rb') as f:
            original_data = f.read()

        transformed_data = transform_with_pattern(original_data)
        compressed_data =paq.compress(bytes(transformed_data))

        with open(output_enc, 'wb') as f:
            f.write(compressed_data)

        print(f"Encoded file saved as {output_enc}")
        print("Analyzing 3-byte chunks...")

        for i in range(0, len(compressed_data), 3):
            chunk = compressed_data[i:i + 3]
            if len(chunk) < 3:
                break
            value = (chunk[0] << 16) | (chunk[1] << 8) | chunk[2]
            if 127 <= value < prime_limit:
                half_value = value // 10
                prime_index = half_value % len(primes)
                _ = primes[prime_index]  # Prime analysis placeholder

    except Exception as e:
        print(f"Encoding error: {e}")

def decode_data(data):
    try:
        decompressed =paq.decompress(data)
        recovered = transform_with_pattern(decompressed)
        return recovered
    except Exception:
        return None

def try_every_3byte_combo(compressed_data):
    """Try every 3-byte aligned chunk for possible decompression with progress bar."""
    results = []
    total = len(compressed_data) - 2
    print("Trying 3-byte combinations with progress:")

    for i in range(0, total, 3):
        # Progress bar
        progress = int((i / total) * 50)
        bar = '[' + '#' * progress + '-' * (50 - progress) + ']'
        sys.stdout.write(f'\r{bar} {i}/{total}')
        sys.stdout.flush()

        chunk = compressed_data[i:i + 3]
        modified = compressed_data[:i] + chunk + compressed_data[i+3:]
        result = decode_data(modified)
        if result:
            results.append(result)

    print(f"\nSuccessful recoveries: {len(results)}")
    return results

def decode_with_compression():
    print("\nDecoding with zlib and XOR reversal")
    try:
        input_enc = input("Enter encoded file (.enc): ").strip()
        output_file = input("Enter output file: ").strip()
    except EOFError:
        print("No input detected.")
        return

    if not os.path.isfile(input_enc):
        print(f"Error: File '{input_enc}' not found.")
        return
    if os.path.exists(output_file):
        print(f"Warning: '{output_file}' will be overwritten.")

    try:
        with open(input_enc, 'rb') as f:
            encoded_data = f.read()

        decompressed_data = paq.decompress(encoded_data)
        recovered_data = transform_with_pattern(decompressed_data)

        with open(output_file, 'wb') as f:
            f.write(recovered_data)

        print(f"Decoded output saved to {output_file}")

        # Optional recovery attempts
        try_every_3byte_combo(encoded_data)

    except Exception as e:
        print(f"Decoding error: {e}")

if __name__ == "__main__":
    print("Software")
    print("Created by Jurijus Pacalovas.")
    print("File Encoding/Decoding System")
    print("Options:")
    print("1 - Encode file")
    print("2 - Decode file")

    try:
        choice = input("Enter 1 or 2: ").strip()
        if choice not in ('1', '2'):
            print("Invalid choice. Exiting.")
            exit()
    except EOFError:
        print("No input detected. Defaulting to Encode.")
        choice = '1'

    if choice == '1':
        encode_with_compression()
    elif choice == '2':
        decode_with_compression()