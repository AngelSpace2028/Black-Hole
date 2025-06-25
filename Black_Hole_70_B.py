import os
import random
import struct
import paq  # Make sure you have your PAQ compression/decompression module ready


def reverse_chunks_at_positions(input_filename, reversed_filename, chunk_size, positions):
    with open(input_filename, 'rb') as infile:
        data = infile.read()

    chunked_data = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    # Pad last chunk if needed
    if len(chunked_data[-1]) < chunk_size:
        chunked_data[-1] += b'\x00' * (chunk_size - len(chunked_data[-1]))

    # Reverse specified chunks
    for pos in positions:
        if 0 <= pos < len(chunked_data):
            chunked_data[pos] = chunked_data[pos][::-1]

    with open(reversed_filename, 'wb') as outfile:
        outfile.write(b"".join(chunked_data))


def compress_with_paq(reversed_filename, compressed_filename, chunk_size, positions, original_size, previous_best_size, first_attempt):
    with open(reversed_filename, 'rb') as infile:
        reversed_data = infile.read()

    # Metadata format: original_size (Q), chunk_size (I), num_positions (I), positions (I * N)
    metadata = struct.pack(">Q", original_size)
    metadata += struct.pack(">I", chunk_size)
    metadata += struct.pack(">I", len(positions))
    metadata += struct.pack(f">{len(positions)}I", *positions)

    compressed_data = paq.compress(metadata + reversed_data)
    compressed_size = len(compressed_data)

    if first_attempt or compressed_size < previous_best_size:
        with open(compressed_filename, 'wb') as outfile:
            outfile.write(compressed_data)
        print(f"Saved better compression: chunk={chunk_size}, reversed={len(positions)}, size={compressed_size}, ratio={compressed_size/original_size:.4f}")
        return compressed_size, False  # No longer first attempt
    return previous_best_size, first_attempt


def decompress_and_restore_paq(compressed_filename):
    if not os.path.exists(compressed_filename):
        raise FileNotFoundError(f"Compressed file not found: {compressed_filename}")

    with open(compressed_filename, 'rb') as infile:
        compressed_data = infile.read()

    decompressed_data = paq.decompress(compressed_data)

    # Parse metadata
    original_size = struct.unpack(">Q", decompressed_data[:8])[0]
    chunk_size = struct.unpack(">I", decompressed_data[8:12])[0]
    num_positions = struct.unpack(">I", decompressed_data[12:16])[0]
    positions = list(struct.unpack(f">{num_positions}I", decompressed_data[16:16 + num_positions * 4]))

    # Extract transformed data
    chunked_data_start = 16 + num_positions * 4
    transformed_data = decompressed_data[chunked_data_start:]
    chunks = [transformed_data[i:i + chunk_size] for i in range(0, len(transformed_data), chunk_size)]

    # Reverse back chunks
    for pos in positions:
        if 0 <= pos < len(chunks):
            chunks[pos] = chunks[pos][::-1]

    restored_data = b''.join(chunks)[:original_size]

    restored_filename = compressed_filename.replace('.compressed.bin', '')
    with open(restored_filename, 'wb') as outfile:
        outfile.write(restored_data)

    print(f"Decompression complete. Restored file: {restored_filename} (size: {len(restored_data)} bytes)")


def find_best_chunk_strategy(input_filename):
    original_size = os.path.getsize(input_filename)
    previous_best_size = 10**12
    first_attempt = True
    iteration = 0

    while True:  # Infinite loop to keep searching
        iteration += 1
        for chunk_size in range(1, 256):
            max_chunks = original_size // chunk_size
            if max_chunks == 0:
                continue

            num_positions = random.randint(1, min(max_chunks, 64))
            positions = random.sample(range(max_chunks), num_positions)

            reversed_filename = f"{input_filename}.reversed.bin"
            reverse_chunks_at_positions(input_filename, reversed_filename, chunk_size, positions)

            compressed_filename = f"{input_filename}.compressed.bin"
            previous_best_size, first_attempt = compress_with_paq(
                reversed_filename,
                compressed_filename,
                chunk_size,
                positions,
                original_size,
                previous_best_size,
                first_attempt
            )

        if iteration % 100 == 0:
            print(f"Iteration {iteration} complete.")


def main():
    print("Created by Jurijus Pacalovas.")
    while True:
        try:
            mode = int(input("Enter mode (1 = compress, 2 = extract): "))
            if mode in [1, 2]:
                break
            print("Invalid input. Enter 1 or 2.")
        except ValueError:
            print("Invalid input. Enter a number.")

    if mode == 1:
        input_filename = input("Enter the input file name to compress: ")
        if not os.path.exists(input_filename):
            print(f"File '{input_filename}' not found.")
            return
        find_best_chunk_strategy(input_filename)

    elif mode == 2:
        base = input("Enter the base name of the file to extract (without '.compressed.bin'): ")
        compressed_filename = f"{base}.compressed.bin"
        if not os.path.exists(compressed_filename):
            print(f"Compressed file '{compressed_filename}' not found.")
            return
        decompress_and_restore_paq(compressed_filename)


if __name__ == "__main__":
    main()
