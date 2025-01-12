import random

def generate_key():
    out = ""
    for i in range(32):
        out += format(random.randint(1, 16), "X")

    return out

with open("IV.txt", "w") as f:
    f.write(generate_key())

with open("key.txt", "w") as f:
    f.write(generate_key())
        