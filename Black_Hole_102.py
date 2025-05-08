import os
import mpmath
import paq  # Placeholder for PAQ compression

# Set precision to 65535 * 5 digits for Pi calculation
mpmath.mp.dps = 65535 * 5
pi_digits = str(mpmath.mp.pi)[2:]  # Skip the '3.'

# Save Pi digits to a file
with open("pi_digits.txt", "w") as f:
    f.write(pi_digits)
print(f"Pi digits have been saved to 'pi_digits.txt'. Total digits: {len(pi_digits)}")

# Function to apply XOR transformation per chunk
def transform_with_pattern(data, chunk_size=4):
    """Apply XOR 0xFF transformation per chunk."""
    transformed = bytearray()
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        transformed.extend(b ^ 0xFF for b in chunk)
    return transformed

# Function to encode data with XOR and zlib compression
def encode_with_compression():
    print("\nSimple Encoder (XOR + zlib compression + Pi-based analysis)")

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

        # Apply XOR transformation
        transformed_data = transform_with_pattern(original_data)
        
        # Compress the data using zlib (PAQ placeholder)
        compressed_data = paq.compress(bytes(transformed_data))

        # Save the compressed data to the output file
        with open(output_enc, 'wb') as f:
            f.write(compressed_data)

        print(f"Encoded and saved to {output_enc}")

        # Pi digit analysis (optional)
        for i in range(0, len(compressed_data), 2):
            byte_pair = compressed_data[i:i + 2]
            if len(byte_pair) < 2:
                break
            byte_value = (byte_pair[0] << 8) | byte_pair[1]
            index = byte_value % len(pi_digits)
            pi_digit = pi_digits[index]
            # You can log or analyze pi_digit if needed

    except Exception as e:
        print(f"An error occurred during encoding: {e}")

# Function to decode data with zlib decompression and XOR reversal
def decode_with_compression():
    print("\nSimple Decoder (zlib decompression + XOR reversal)")

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

        # Decompress the data using zlib
        decompressed_data =paq.decompress(encoded_data)
        
        # Reverse the XOR transformation
        recovered_data = transform_with_pattern(decompressed_data)

        # Save the recovered data to the output file
        with open(output_file, 'wb') as f:
            f.write(recovered_data)

        print(f"Decoded and saved to {output_file}")
    except Exception as e:
        print(f"An error occurred during decoding: {e}")

# Main function to drive encoding and decoding
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