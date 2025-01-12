def print_state(input_state):
    for row in input_state:
        print(row)
            
def print_hex(input_state):
    out = [[0 for x in range(4)] for x in range(4)]

    for i in range(4):
        for j in range(4):
            out[i][j] = hex(input_state[i][j])

    print_state(out)