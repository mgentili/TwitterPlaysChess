def pos_ok(pos):
    return ((pos[0] >= 'a') and (pos[0] <= 'h') and (pos[1] >= '1') and (pos[1]
        <= '8'))
    
def move_ok(move):
    return pos_ok(move[0:2]) and pos_ok(move[2:4])


