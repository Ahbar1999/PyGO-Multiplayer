
import pygame
import socket
import json
import time
import sys

# pygame setup
pygame.init()
screen = pygame.display.set_mode((480, 360))
font = pygame.font.SysFont('roboto', 40)

clock = pygame.time.Clock()
HOST_IP = "127.0.0.1"
HOST_PORT = 3000
CURRENT_IP = "127.0.0.1"
CURRENT_PORT = 3001
RECV_BUF_SIZE = 2048 

player_pos = pygame.Vector2(400 / 2, 200 / 2)

'''
    We can either assign a new id for a new game
    or provide an id with args to initiate a game with that id   
'''
this_player = {
    'udp_addr': CURRENT_IP + ":" + str(CURRENT_PORT),
    'id': None,
    'pos': (player_pos.x, player_pos.y),
    'timestamp': None # added new field
}

other_players = {}

def update_game(dt):
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            return False

    screen.fill("purple")

    pygame.draw.circle(screen, "red", player_pos, 40)
    text = font.render(this_player["id"], True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=player_pos))
    
    for id in other_players:
        other = other_players[id] 
        print(other)
        pygame.draw.circle(screen, "red",  pygame.Vector2(int(other["pos"][0]), int(other["pos"][1])), 40)  
        text = font.render(other["id"], True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=pygame.Vector2(int(other["pos"][0]), int(other["pos"][1]))))
    
                    # move our character
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt

    this_player["pos"] = (player_pos.x, player_pos.y) 

    pygame.display.flip()

    return True

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    # bind to current port
    try:
        sock.bind((CURRENT_IP, CURRENT_PORT))
    except OSError:
        CURRENT_PORT += 1
        sock.bind((CURRENT_IP, CURRENT_PORT))
        this_player["udp_addr"] = CURRENT_IP + ":" + str(CURRENT_PORT)

    # check if id was provided
    if len(sys.argv) != 0:
        try:
            this_player["id"] = int(sys.argv[0])
        except ValueError:
            print("Either provide a proper numeric argument for id or dont provide one at all")

    dt = 0
    # initiate connection
    while this_player["id"] is None:
        sock.sendto("Join".encode(), (HOST_IP, HOST_PORT)) 
        data, addr = sock.recvfrom(RECV_BUF_SIZE)
        if data:
            this_player["id"] = data.decode()

    print("Connection initiated with HOST")
    print("Id recvd for player: ", this_player["id"])

    running = True
    begin_time = time.time()
    start_time = begin_time 
    # non blocking socket
    sock.setblocking(False)
    
    while running:
        running = update_game(dt)
        curr_time = time.time() 
        if curr_time - start_time >= 2.0:
            # send this data
            send_payload = json.dumps(this_player).encode()
            # print(curr_time - begin_time, send_payload)
            sock.sendto(send_payload, (HOST_IP, HOST_PORT))
            
            start_time = curr_time 
            
            # recv other data, if data is not immediately available then recvfrom throws an exception
            # we dont care about that exception so we just continue
            try:
                data, addr = sock.recvfrom(RECV_BUF_SIZE)
                # update world info
                data = json.loads(data.decode())
                other_players[data["id"]] = data
                print(this_player["id"], other_players)
            finally:
                continue
        # print(this_player["id"], other_players)
        # print(other_players) 
        dt = clock.tick(60) / 1000
    
    pygame.quit()





