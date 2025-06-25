import os
import random
import struct
import paq


def apply_minus_operation(value):
    """Applies a modified minus operation."""
    if value <= 0:
        return value + (2**255 - 1)
    elif value <= (2**24 - 1):
        return value + 3
    else:
        return value + 1


def reverse_chunks_at_positions(input_filename, reversed_filename, chunk_size, number_of_positions):
    with open(input_filename, 'rb') as infile:
        data = infile.read()

    chunked_data = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    if len(chunked_data[-1]) < chunk_size:
        chunked_data[-1] += b'\x00' * (chunk_size - len(chunked_data[-1]))

    max_position = len(chunked_data)
    positions = [i * (2**31) // max_position for i in range(number_of_positions)]

    for pos in positions:
        if 0 <= pos < len(chunked_data):
            chunked_data[pos] = chunked_data[pos][::-1]

    with open(reversed_filename, 'wb') as outfile:
        outfile.write(b"".join(chunked_data))


def compress_with_paq(reversed_filename, compressed_filename, chunk_size, positions, previous_size, original_size, first_attempt):
    with open(reversed_filename, 'rb') as infile:
        reversed_data = infile.read()

    metadata = struct.pack(">Q", original_size)
    metadata += struct.pack(">I", chunk_size)
    metadata += struct.pack(">I", len(positions))
    metadata += struct.pack(f">{len(positions)}I", *positions)

    # KEEP full metadata (do not slice or corrupt)
    # new_metadata_len = apply_minus_operation(len(metadata))
    # metadata = metadata[:new_metadata_len]  ← removed this

    compressed_data = paq.compress(metadata + reversed_data)
    compressed_size = len(compressed_data)

    if first_attempt:
        with open(compressed_filename, 'wb') as outfile:
            outfile.write(compressed_data)
        first_attempt = False
        return compressed_size, first_attempt
    elif compressed_size < previous_size:
        with open(compressed_filename, 'wb') as outfile:
            outfile.write(compressed_data)
        print(f"Improved compression with chunk size {chunk_size} and {len(positions)} reversed positions.")
        print(f"Compression size: {compressed_size} bytes, Compression ratio: {compressed_size / original_size:.4f}")
        return compressed_size, first_attempt
    else:
        return previous_size, first_attempt


def decompress_and_restore_paq(compressed_filename):
    if not os.path.exists(compressed_filename):
        raise FileNotFoundError(f"Compressed file not found: {compressed_filename}")

    with open(compressed_filename, 'rb') as infile:
        compressed_data = infile.read()

    decompressed_data = paq.decompress(compressed_data)

    original_size = struct.unpack(">Q", decompressed_data[:8])[0]
    chunk_size = struct.unpack(">I", decompressed_data[8:12])[0]
    num_positions = struct.unpack(">I", decompressed_data[12:16])[0]
    positions = list(struct.unpack(f">{num_positions}I", decompressed_data[16:16 + num_positions * 4]))

    chunked_data = decompressed_data[16 + num_positions * 4:]
    total_chunks = len(chunked_data) // chunk_size
    chunked_data = [chunked_data[i * chunk_size:(i + 1) * chunk_size] for i in range(total_chunks)]

    for pos in positions:
        if 0 <= pos < len(chunked_data):
            chunked_data[pos] = chunked_data[pos][::-1]

    restored_data = b"".join(chunked_data)
    restored_data = restored_data[:original_size]

    restored_filename = compressed_filename.replace('.compressed.bin', '')

    with open(restored_filename, 'wb') as outfile:
        outfile.write(restored_data)

    print(f"Decompression complete. Restored file saved as: {restored_filename}")
    print(f"Restored file size: {len(restored_data)} bytes")


def find_best_chunk_strategy(input_filename):
    file_size = os.path.getsize(input_filename)
    best_chunk_size = 1
    best_positions = []
    best_compression_ratio = float('inf')

    previous_size = 10**12
    first_attempt = True

    while True:
        for chunk_size in range(1, 256):
            max_positions = file_size // chunk_size
            if max_positions > 0:
                positions_count = random.randint(1, min(max_positions, 64))
                positions = [i * (2**31) // file_size for i in range(positions_count)]

                reversed_filename = f"{input_filename}.reversed.bin"
                reverse_chunks_at_positions(input_filename, reversed_filename, chunk_size, positions_count)

                compressed_filename = f"{input_filename}.compressed.bin"
                compressed_size, first_attempt = compress_with_paq(
                    reversed_filename,
                    compressed_filename,
                    chunk_size,
                    positions,
                    previous_size,
                    file_size,
                    first_attempt
                )

                if compressed_size < previous_size:
                    previous_size = compressed_size
                    best_chunk_size = chunk_size
                    best_positions = positions
                    best_compression_ratio = compressed_size / file_size

                    print(f"\n✔ Best so far: chunk={best_chunk_size}, ratio={best_compression_ratio:.4f}, positions={len(best_positions)}\n")


def main():
    print("Created by Jurijus Pacalovas.")

    while True:
        try:
            mode = int(input("Enter mode (1 for compress, 2 for extract): "))
            if mode not in [1, 2]:
                print("Error: Please enter 1 or 2.")
            else:
                break
        except ValueError:
            print("Error: Invalid input. Please enter a number.")

    if mode == 1:
        input_filename = input("Enter input file name to compress: ")
        if not os.path.exists(input_filename):
            print(f"Error: File {input_filename} not found!")
            return
        find_best_chunk_strategy(input_filename)

    elif mode == 2:
        compressed_filename_base = input("Enter base name of compressed file (without .compressed.bin): ")
        compressed_filename = f"{compressed_filename_base}.compressed.bin"

        if not os.path.exists(compressed_filename):
            print(f"Error: Compressed file {compressed_filename} not found!")
            return

        decompress_and_restore_paq(compressed_filename)


if __name__ == "__main__":
    main()
