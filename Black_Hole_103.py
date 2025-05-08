import os
import mpmath
import paq # Placeholder for PAQ compression

# Set precision for Pi digits
mpmath.mp.dps = 65536 * 5
pi_digits = str(mpmath.mp.pi)[2:]

# Optional: Save Pi digits to file
with open("pi_digits.txt", "w") as f:
    f.write(pi_digits)
print(f"Pi digits have been saved to 'pi_digits.txt'. Total digits: {len(pi_digits)}")

def transform_with_pattern(data, chunk_size=3):
    """Apply XOR 0xFF transformation per chunk."""
    transformed = bytearray()
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        transformed.extend(b ^ 0xFF for b in chunk)
    return transformed

def encode_with_compression():
    print("\nEncoding with XOR, zlib compression, and Pi-based index analysis")
    try:
        input_file = input("Enter input file: ").strip()
        output_base = input("Enter output base name (without .enc): ").strip()
    except EOFError:
        print("No input detected. Exiting encode mode.")
        return

    output_enc = output_base + ".enc"

    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        return

    if os.path.exists(output_enc):
        print(f"Warning: File '{output_enc}' already exists and will be overwritten.")

    try:
        with open(input_file, 'rb') as f:
            original_data = f.read()

        transformed_data = transform_with_pattern(original_data)
        compressed_data = paq.compress(bytes(transformed_data))

        with open(output_enc, 'wb') as f:
            f.write(compressed_data)

        print(f"Encoded and saved to {output_enc}")

        # Optional Pi-digit analysis
        print("Analyzing 3-byte chunks between 127 and 65535...")
        for i in range(0, len(compressed_data), 3):
            chunk = compressed_data[i:i + 3]
            if len(chunk) < 3:
                break
            value = (chunk[0] << 16) | (chunk[1] << 8) | chunk[2]
            if 127 <= value <= 65535:
                half_value = value // 2
                pi_index = int((mpmath.fmod(half_value, mpmath.pi)) * 1e5) % len(pi_digits)
                pi_digit = pi_digits[pi_index]
                # You can log or use pi_digit
                # print(f"Value: {value}, Half: {half_value}, Pi digit: {pi_digit}")

    except Exception as e:
        print(f"An error occurred during encoding: {e}")

def decode_with_compression():
    print("\nDecoding with zlib decompression and XOR reversal")
    try:
        input_enc = input("Enter encoded file (.enc): ").strip()
        output_file = input("Enter output file: ").strip()
    except EOFError:
        print("No input detected. Exiting decode mode.")
        return

    if not os.path.isfile(input_enc):
        print(f"Error: File '{input_enc}' does not exist.")
        return

    if os.path.exists(output_file):
        print(f"Warning: Output file '{output_file}' will be overwritten.")

    try:
        with open(input_enc, 'rb') as f:
            encoded_data = f.read()

        decompressed_data = paq.decompress(encoded_data)
        recovered_data = transform_with_pattern(decompressed_data)

        with open(output_file, 'wb') as f:
            f.write(recovered_data)

        print(f"Decoded and saved to {output_file}")
    except Exception as e:
        print(f"An error occurred during decoding: {e}")

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
        print("No input detected. Defaulting to Encode (1).")
        choice = '1'

    if choice == '1':
        encode_with_compression()
    elif choice == '2':
        decode_with_compression()