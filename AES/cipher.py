from typing import List
import random
from lookup import *
from helpers import *

def create_state(char_buffer: List[str], missing_len: int) -> List[List]:
    out = [[missing_len for x in range(4)] for x in range(4)]
    index: int = 0;
    # print(char_buffer)
    
    for i in range(len(out)):
        for j in range(len(out[0])):
            if index == len(char_buffer):
                break

            out[j][i] = char_buffer[index]
            index += 1

    return out

def create_states(input_str: str):
    states: List = []
    char_buffer: List = []
    missing_len: int = 16 - (len(input_str) % 16)

    for i, c in enumerate(input_str):
        if i % 16 == 0 and i != 0:
            states.append(create_state(char_buffer, missing_len))
            char_buffer = []

        char_buffer.append(int(format(ord(c), "x"), 16))

    if len(char_buffer) != 16:
        states.append(create_state(char_buffer, missing_len))

    return states

def salt(input_str, mode="normal"):
    len_of_salt = (len(input_str) % 10) + 10

    if mode == "normal":
        salt = str(len(input_str) % 10)
        for i in range(len_of_salt):
            salt += format(random.randint(1, 15), "X")

        salt += input_str
        return salt


    if mode == "inverse":
        len_of_salt = int(input_str[0]) + 10
        return input_str[len_of_salt + 1:]

def sub_bytes(input_state, mode="normal"):
    out = [[0 for x in range(4)] for x in range(4)]

    for i in range(4):
        for j in range(4):
            if mode == "normal":
                out[i][j] = int(SBOX[input_state[i][j]], 16)

            elif mode == "inverse":
                out[i][j] = int(INVERSE_SBOX[input_state[i][j]], 16)
    
    return out

def shift_rows(input_state, mode="normal"):
    out = [[0 for x in range(4)] for x in range(4)]

    for i in range(4):
        for j in range(4):
            rotation_index = j

            if mode == "normal":
                rotation_index += i
            elif mode == "inverse":
                rotation_index -= i

            if rotation_index < 0:
                rotation_index += 4
            elif rotation_index > 3:
                rotation_index -= 4

            out[i][j] = input_state[i][rotation_index]

    return out

def GFM(byte, num): # Galois Field Multiplication
    match num:
        case 2: 
            out = byte << 1

            if byte & 0x80 != 0:
                out ^= 0x1B
                return out & 0xFF
            else:
                return out & 0xFF

        case 3:
            out = GFM(byte, 2) ^ byte
            return out & 0xFF


        case 9:
            out = GFM(byte, 2)
            out = GFM(out, 2)
            out = GFM(out, 2) ^ byte
            return out & 0xFF

        case 11:
            out = GFM(byte, 2) 
            out = GFM(out, 2) ^ byte
            out = GFM(out, 2) ^ byte
            return out & 0xFF

        case 13:
            out = GFM(byte, 2) ^ byte
            out = GFM(out, 2)
            out = GFM(out, 2) ^ byte
            return out & 0xFF

        case 14:
            out = GFM(byte, 2) ^ byte
            out = GFM(out, 2) ^ byte
            out = GFM(out, 2)
            return out & 0xFF

def mix_columns(input_state, mode="normal"):
    out = [[0 for x in range(4)] for x in range(4)]

    for col in range(4):
        if mode == "normal":
            out[0][col] = GFM(input_state[0][col], 2) ^ GFM(input_state[1][col], 3) ^ input_state[2][col] ^ input_state[3][col]
            out[1][col] = GFM(input_state[1][col], 2) ^ GFM(input_state[2][col], 3) ^ input_state[3][col] ^ input_state[0][col]
            out[2][col] = GFM(input_state[2][col], 2) ^ GFM(input_state[3][col], 3) ^ input_state[0][col] ^ input_state[1][col]
            out[3][col] = GFM(input_state[3][col], 2) ^ GFM(input_state[0][col], 3) ^ input_state[1][col] ^ input_state[2][col]
        
        elif mode == "inverse":
            out[0][col] = GFM(input_state[0][col], 14) ^ GFM(input_state[1][col], 11) ^ GFM(input_state[2][col], 13) ^ GFM(input_state[3][col], 9);
            out[1][col] = GFM(input_state[1][col], 14) ^ GFM(input_state[2][col], 11) ^ GFM(input_state[3][col], 13) ^ GFM(input_state[0][col], 9);
            out[2][col] = GFM(input_state[2][col], 14) ^ GFM(input_state[3][col], 11) ^ GFM(input_state[0][col], 13) ^ GFM(input_state[1][col], 9);
            out[3][col] = GFM(input_state[3][col], 14) ^ GFM(input_state[0][col], 11) ^ GFM(input_state[1][col], 13) ^ GFM(input_state[2][col], 9);

    return out

def key_to_state(input_str):
    out = [[0 for x in range(4)] for x in range(4)]
    char_buffer = []
    tmp_buffer: str = ""

    for i, c in enumerate(input_str):
        tmp_buffer += c

        if i % 2 != 0 and i != 0:
            char_buffer.append(int(tmp_buffer, 16))
            tmp_buffer = ""

    index = 0
    for i in range(4):
        for j in range(4):
            out[i][j] = char_buffer[index]
            index += 1

    return out

KEY_PATH = "key.txt"
def generate_keys():
    with open(KEY_PATH, "r") as f:
        data = f.read()
        key_state = key_to_state(data)
        words = []

        for word in key_state:
            words.append(word)

        for i in range(4, 44):
            if i % 4 == 0:
                rot_word = [words[i-1][1], words[i-1][2], words[i-1][3], words[i-1][0]]
                sub_bytes = []
                for byte in rot_word:
                    sub_bytes.append(int(SBOX[byte], 16))

                sub_bytes[0] ^= RCON[(i//4)-1]

                out = []
                for j, byte in enumerate(sub_bytes):
                    out.append(byte ^ words[i-4][j])

                words.append(out)
            else:
                out = []
                for byte1, byte2 in zip(words[i-1], words[i-4]):
                    out.append(byte1 ^ byte2)

                words.append(out)

        out_keys = []
        key_buff = []

        for i, word in enumerate(words):
            key_buff.append(word)

            if (i + 1) % 4 == 0:
                rotated_matrix = [[0 for x in range(4)] for x in range(4)]

                for col in range(4):
                    for row in range(4):
                        rotated_matrix[row][col] = key_buff[col][row]

                out_keys.append(rotated_matrix)
                key_buff = []

        return out_keys

def xor_state(state1, state2):
    out = [[0 for x in range(4)] for x in range(4)]

    for i in range(4):
        for j in range(4):
            out[i][j] = state1[i][j] ^ state2[i][j]

    return out

IV_PATH = "IV.txt"
def encrypt_str(input_str):
    salted_str = salt(input_str)

    out = []
    states = create_states(salted_str)
    keys = generate_keys()
    iv_string = ""

    with open(IV_PATH, "r") as f:
        iv_string = f.read()

    iv = key_to_state(iv_string)

    states[0] = xor_state(states[0], iv)

    for state_number, state in enumerate(states):
        if state_number != 0:
            state = xor_state(state, out[state_number - 1])

        cipher_text = xor_state(state, keys[0])

        for i in range(1, 10):
            cipher_text = sub_bytes(cipher_text)
            cipher_text = shift_rows(cipher_text)
            cipher_text = mix_columns(cipher_text)
            cipher_text = xor_state(cipher_text, keys[i])

        cipher_text = sub_bytes(cipher_text)
        cipher_text = shift_rows(cipher_text)
        cipher_text = xor_state(cipher_text, keys[len(keys) - 1])

        out.append(cipher_text)

    out_string = ""

    for out_state in out:
        for col in range(4):
            for row in range(4):
                out_string += format(out_state[row][col], "02X")

    return out_string

def decrypt_str(input_str):
    output = []
    states = []
    tmp_array = [0 for x in range(16)]
    buffer = ""
    count = 0
    
    for i, c in enumerate(input_str):
        buffer += c
        if i % 2 != 0:
            tmp_array[count] = int(buffer, 16)
            buffer = ""
            count += 1
            
        if count == 16:
            states.append(create_state(tmp_array, 0))
            count = 0
    
    keys = generate_keys()
    previous_state = [[0 for x in range(4)] for x in range(4)]
    
    for state_number, state in enumerate(states):
        deciphered_state = [[0 for x in range(4)] for x in range(4)]
        
        for i, key in enumerate(reversed(keys)):
            if i == 0:
                deciphered_state = xor_state(state, key)
                deciphered_state = shift_rows(deciphered_state, "inverse")
                deciphered_state = sub_bytes(deciphered_state, "inverse")
            elif 0 < i < 10:
                deciphered_state = xor_state(deciphered_state, key)
                deciphered_state = mix_columns(deciphered_state, "inverse")
                deciphered_state = shift_rows(deciphered_state, "inverse")
                deciphered_state = sub_bytes(deciphered_state, "inverse")
            else:
                deciphered_state = xor_state(deciphered_state, key)
        
        if state_number != 0:
            deciphered_state = xor_state(deciphered_state, previous_state)
        
        previous_state = state
        output.append(deciphered_state)
    
    byte_array = []
    
    with open(IV_PATH, 'r') as f:
        iv_string = f.read()
    
    iv = key_to_state(iv_string)
    output[0] = xor_state(output[0], iv)
    
    for state in output:
        for column in range(4):
            for row in range(4):
                byte_array.append(state[row][column])
    
    if byte_array[-1] <= 16:
        padding_length = byte_array[-1]
        byte_array = byte_array[:-padding_length]
    
    unsalted_str = bytes(byte_array).decode('utf-8')
    return salt(unsalted_str, "inverse")

# print(decrypt_str(encrypt_str("abalks;jdf;lksafjdsafefghijklmnopqrstuvwxyz")))

# print(salt(salt("abcdefghijklmnopqrstuvwxyz"), "inverse"))

# states = create_states("abcdefghijklmnopqrstuvwxyz")
# print_state(states[0])
# print_state(shift_rows(shift_rows(states[0]), "inverse"))
# print_state(mix_columns(mix_columns(states[0]), "inverse"))

# print_hex(key_to_state("2b7e151628aed2a6abf7158809cf4f3c"))
# generate_keys()
# for i, key in enumerate(generate_keys()):
#     print("key " + str(i))
#     print_hex(key)