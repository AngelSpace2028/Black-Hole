import os
import math
import paq  # Make sure you have a paq library or replace with zlib if needed

# Check if a number is prime
def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

# Find a divisor
def find_divisor(n):
    if n % 2 == 0:
        return 2
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return i
    return n  # prime number

# Write and read 4-byte integer
def write_4byte_int(f, value):
    f.write(value.to_bytes(4, 'big'))

def read_4byte_int(f):
    return int.from_bytes(f.read(4), 'big')

# Simple pattern transformation (bit-flipping example)
def transform_with_pattern(data, chunk_size=4):
    transformed = bytearray()
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        transformed.extend([b ^ 0xFF for b in chunk])
    return transformed

# Fake quantum encoding (simple number adjustment instead of real quantum logic)
def fake_quantum_encode(number):
    return number ^ 0xAAAAAAAA  # XOR with a pattern

def fake_quantum_decode(encoded_number):
    return encoded_number ^ 0xAAAAAAAA

# Compress using PAQ
def compress_with_paq(input_file, output_file):
    with open(input_file, 'rb') as f_in:
        data = f_in.read()
    compressed_data = paq.compress(data)
    with open(output_file, 'wb') as f_out:
        f_out.write(compressed_data)

# Decompress using PAQ
def decompress_with_paq(input_file, output_file):
    with open(input_file, 'rb') as f_in:
        compressed_data = f_in.read()
    decompressed_data = paq.decompress(compressed_data)
    with open(output_file, 'wb') as f_out:
        f_out.write(decompressed_data)

# Main encoding function
def encode():
    print("Simple Encoder (no Qiskit)")
    input_file = input("Enter input file: ").strip()
    output_base = input("Enter output base name (without .paq): ").strip()
    output_paq = output_base + ".paq"
    
    if not os.path.isfile(input_file):
        print("File does not exist.")
        return

    with open(input_file, 'rb') as f:
        original_data = f.read()

    transformed_data = transform_with_pattern(original_data)

    temp_file = output_base + "_temp"
    with open(temp_file, 'wb') as f:
        size = len(transformed_data)

        p = find_divisor(size)
        q = size // p

        # Special rule: if p is greater than 2, prepend 00000000, else prepend 00000001
        if is_prime(p) and p > 2:
            # Prepend 00000000 byte
            f.write(bytes([0x00]))
        else:
            # Prepend 00000001 byte
            f.write(bytes([0x01]))

        # Write p and q
        write_4byte_int(f, p)
        write_4byte_int(f, q)

        # Fake "quantum" encode the size
        encoded_size = fake_quantum_encode(size)
        write_4byte_int(f, encoded_size)

        # Write transformed data
        f.write(transformed_data)

    compress_with_paq(temp_file, output_paq)
    os.remove(temp_file)

    print(f"Encoding complete. Output saved to {output_paq}")

# Main decoding function
def decode():
    print("Simple Decoder (no Qiskit)")
    input_paq = input("Enter compressed file (.paq): ").strip()
    output_file = input("Enter output file: ").strip()

    if not os.path.isfile(input_paq):
        print("Compressed file does not exist.")
        return

    temp_file = input_paq.replace('.paq', '_temp')
    decompress_with_paq(input_paq, temp_file)

    with open(temp_file, 'rb') as f:
        # Read the prepended byte
        prepend_byte = f.read(1)
        if prepend_byte == b'\x00':
            # Means p > 2
            pass
        elif prepend_byte == b'\x01':
            # Means p == 2
            pass
        else:
            print("Unexpected prepend byte.")
            return
        
        p = read_4byte_int(f)
        q = read_4byte_int(f)
        encoded_size = read_4byte_int(f)
        size = fake_quantum_decode(encoded_size)

        transformed_data = f.read()

    recovered_data = transform_with_pattern(transformed_data)

    with open(output_file, 'wb') as f:
        f.write(recovered_data)

    os.remove(temp_file)
    print(f"Decoding complete. Output saved to {output_file}")

# CLI
if __name__ == "__main__":
    print("Created by Jurijus Pacalovas.")
    print("Options:")
    print("1 - Encode file")
    print("2 - Decode file")
    choice = input("Enter 1 or 2: ").strip()

    if choice == '1':
        encode()
    elif choice == '2':
        decode()
    else:
        print("Invalid choice.")