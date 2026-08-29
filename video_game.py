import csv
import random
import sys

import cv2
import numpy as np
import pygame

fps = 15
cell_size = 22


def load_frame_map(filename):
    frame_map = {}
    f = open(filename, "r")
    reader = csv.reader(f)
    next(reader)  # skip header

    for row in reader:
        paddle_left_x, paddle_left_y, ball_x, ball_y, paddle_right_x, paddle_right_y, frame = row
        state = (
            int(paddle_left_x), int(paddle_left_y),
            int(ball_x), int(ball_y),
            int(paddle_right_x), int(paddle_right_y)
        )
        frame_map[state] = int(frame)

    f.close()
    return frame_map


def absolute_pos_to_matrix_pos(x, y):
    return x // cell_size, y // cell_size


file_name = "528x308_with_cell_size_22_at_60"
frame_map = load_frame_map(f"{file_name}.csv")

pygame.init()
clock = pygame.time.Clock()

screen_width = 24 * cell_size
screen_height = 14 * cell_size

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Pong')

paddle_height = cell_size * 6
paddle_left = pygame.Rect(0, 0, cell_size, paddle_height)
paddle_right = pygame.Rect(23 * cell_size, 0 * cell_size, cell_size, paddle_height)

player_speed = cell_size * 2
player_velocity = 0

ball = pygame.Rect(12 * cell_size, 7 * cell_size, cell_size, cell_size)

ball_speed_x = -cell_size
ball_speed_y = -cell_size

cap = cv2.VideoCapture(f"{file_name}.mp4")
playing = True
current_frame = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                player_velocity = player_speed
            if event.key == pygame.K_UP:
                player_velocity = -player_speed
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                player_velocity = 0

    paddle_left.y += player_velocity
    if paddle_left.top <= 0:
        paddle_left.top = 0
    if paddle_left.bottom >= screen_height:
        paddle_left.bottom = screen_height

    # print(f"paddle_left.y={paddle_left.y}")

    # MOVE BALL
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    if ball.colliderect(paddle_left) or ball.colliderect(paddle_right):
        ball_speed_x *= -1
        ball.x += ball_speed_x * 2

    if ball.top <= 0 or ball.bottom >= screen_height:
        ball_speed_y *= -1
        # ball.y += ball_speed_y * 2

    if ball.left <= 0 or ball.right >= screen_width:
        ball.x = 12 * cell_size
        ball.y = 7 * cell_size

    paddle_left_matrix_pos = absolute_pos_to_matrix_pos(paddle_left.x, paddle_left.y)
    ball_matrix_pos = absolute_pos_to_matrix_pos(ball.x, ball.y)
    # print(f"matrix_pos={matrix_pos}")
    # print(f"ball_x={ball.x}, ball_y={ball.y}, ball_matrix_pos={ball_matrix_pos}")
    frame_number = frame_map.get((
        paddle_left_matrix_pos[0], paddle_left_matrix_pos[1],
        ball_matrix_pos[0], ball_matrix_pos[1],
        23, 0
    ), 0)


    # print(f"frame_number={frame_number}")

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = np.transpose(frame_rgb, (1, 0, 2))
    surface = pygame.surfarray.make_surface(frame_rgb)

    screen.blit(surface, (0, 0))
    pygame.display.flip()

    clock.tick(fps)
