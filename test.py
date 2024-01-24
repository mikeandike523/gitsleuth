import re

def extract_color_escape_sequences(file_path):
    try:
        with open(file_path, 'rb') as file:
            raw_bytes = file.read()

            # Use a regular expression to find color escape sequences
            color_sequences = re.findall(b'\x1b\\[[0-9;]*m', raw_bytes)

            if color_sequences:
                decoded_sequences = [sequence.decode('utf-8') for sequence in color_sequences]
                return decoded_sequences
            else:
                return None

    except FileNotFoundError:
        return None

if __name__ == "__main__":
    file_path = "test.txt"  # Replace with the path to your text file
    color_sequences = extract_color_escape_sequences(file_path)

    if color_sequences:
        print("Color Escape Sequences Found:")
        for sequence in color_sequences:
            print(sequence)
    else:
        print("No Color Escape Sequences Found in the file.")