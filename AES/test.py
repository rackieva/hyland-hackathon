from cipher import *

def test(input_str):
    encrypted_strs = []

    for i in range(5):
        encrypted_strs.append(encrypt_str(input_str))

    print(encrypted_strs)
    for string in encrypted_strs:
        decrypted_str = decrypt_str(string)
        print(decrypted_str)
        if decrypted_str != input_str:
            print("Failed. Input String: " + input_str + ". Encrypted String: " + string + ". Decrypted String: " + decrypted_string)

            return False

    return True

if test("abc") == True:
    print("all tests passed")