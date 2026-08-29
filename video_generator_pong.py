import numpy as np
import pygame, sys
import cv2
import csv


fps = 60
cell_size = 22

show_grid = False
# cell_size = 15

# screen_width = 40 * cell_size
# screen_height = 30 * cell_size

screen_width = 24 * cell_size
screen_height = 14 * cell_size

# screen_width = 10 * cell_size
# screen_height = 5 * cell_size

# paddle_height = cell_size * 10
paddle_height = cell_size * 6
# paddle_height = cell_size * 3


file_name = f"{screen_width}x{screen_height}_with_cell_size_{cell_size}_at_{fps}_show_grid_{show_grid}"

# ── cv2 ─────────────────────────────────────
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# Create video writer
video = cv2.VideoWriter(f"{file_name}.mp4", fourcc, fps, (screen_width, screen_height))

f = open(f"{file_name}.csv", "w", newline="")
writer = csv.writer(f)

writer.writerow(["paddle_left_x", "paddle_left_y", "ball_x", "ball_y", "paddle_right_x", "paddle_right_y", "frame"])

# ── pygame ─────────────────────────────────────
pygame.init()
clock = pygame.time.Clock()


screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Grid Pong')

ball = pygame.Rect(0, 0, cell_size, cell_size)

paddle_left = pygame.Rect(0, 0, cell_size, paddle_height)
paddle_right = pygame.Rect(screen_width // cell_size * cell_size - cell_size, 0, cell_size, paddle_height)

bg_color = pygame.Color('grey12')
color_crimson = pygame.Color('crimson')
light_grey = (200, 200, 200)


frame_count = 0


def absolute_pos_to_matrix_pos(x, y):
    return x // cell_size, y // cell_size


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


    # ── Movement ─────────────────────────────────────
    ball.x += cell_size

    if ball.right > screen_width:
        ball.y += cell_size
        ball.x = 0

    if ball.bottom > screen_height:
        ball.y = 0
        if paddle_right.bottom < screen_height:
            paddle_right.y += cell_size
        elif paddle_left.bottom < screen_height:
            paddle_left.y += cell_size
            paddle_right.top = 0
        else:
            print(f"Created video: {file_name}.mp4 with {frame_count} frames")
            video.release()
            pygame.quit()
            sys.exit()

    # ── DRAW ─────────────────────────────────────
    screen.fill(bg_color)

    if show_grid:
        # horizontal lines
        y = 0
        while y <= screen_height:
            pygame.draw.aaline(screen, light_grey, (0, y), (screen_width, y))
            y += cell_size

        # vertical lines
        x = 0
        while x <= screen_width:
            pygame.draw.aaline(screen, light_grey, (x, 0), (x, screen_width))
            x += cell_size


    if ball.colliderect(paddle_left) or ball.colliderect(paddle_right):
        continue

    ball_color = color_crimson if ball.colliderect(paddle_left) or ball.colliderect(paddle_right) else light_grey

    pygame.draw.rect(screen, light_grey, paddle_left)
    pygame.draw.rect(screen, light_grey, paddle_right)

    pygame.draw.rect(screen, ball_color, ball)


    # print(f"ball [{ball.x // cell_size}, {ball.y // cell_size}]")
    # print(f"map [{absolute_pos_to_matrix_pos(paddle_left.x, paddle_left.y)}|{paddle_right.top // cell_size}|{ball.top // cell_size}]")



    # pygame → numpy array (RGB, width x height)
    frame = pygame.surfarray.array3d(screen)
    # transpose from (width, height) to (height, width)
    frame = np.transpose(frame, (1, 0, 2))
    # convert RGB → BGR for opencv
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    video.write(frame)

    # "paddle_left_x", "paddle_left_y", "ball_x", "ball_y", "paddle_right_x", "paddle_right_y", "frame"
    writer.writerow([absolute_pos_to_matrix_pos(paddle_left.x, paddle_left.y)[0],
                     absolute_pos_to_matrix_pos(paddle_left.x, paddle_left.y)[1],
                     absolute_pos_to_matrix_pos(ball.x, ball.y)[0],
                     absolute_pos_to_matrix_pos(ball.x, ball.y)[1],
                     absolute_pos_to_matrix_pos(paddle_right.x, paddle_right.y)[0],
                     absolute_pos_to_matrix_pos(paddle_right.x, paddle_right.y)[1],
                     frame_count])
    frame_count += 1

    pygame.display.flip()
    clock.tick(fps)
