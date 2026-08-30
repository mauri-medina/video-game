import numpy as np
import pygame, sys
import cv2
import csv
import subprocess
import os

fps = 60
cell_size = 22
repeat = 3  # copies per state: 1 before + 1 exact + 1 after

show_grid = True

screen_width = 24 * cell_size
screen_height = 14 * cell_size

paddle_height = cell_size * 6

file_name = f"{screen_width}x{screen_height}_cell{cell_size}_fps{fps}_repeat{repeat}"

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
temp_file = f"{file_name}_temp.mp4"
video = cv2.VideoWriter(temp_file, fourcc, fps, (screen_width, screen_height))

f = open(f"{file_name}.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["paddle_left_x", "paddle_left_y", "ball_x", "ball_y", "paddle_right_x", "paddle_right_y", "frame"])


pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Grid Pong - Video Generator (YouTube)')

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
            print(f"Created video: {file_name} with {frame_count} game states, {frame_count * repeat} total frames")
            video.release()
            f.close()
            pygame.quit()

            # Re-encode with ffmpeg for smaller file size
            final_file = f"{file_name}.mp4"
            print(f"Re-encoding with ffmpeg (crf 35, no audio)...")
            subprocess.run([
                "ffmpeg", "-y",
                "-i", temp_file,
                "-c:v", "libx264",
                "-crf", "35",
                "-an",
                final_file
            ], check=True)
            os.remove(temp_file)
            print(f"Final video: {final_file}")
            sys.exit()

    # Draw to pygame screen
    screen.fill(bg_color)

    if show_grid:
        for y in range(0, screen_height + 1, cell_size):
            pygame.draw.aaline(screen, light_grey, (0, y), (screen_width, y))
        for x in range(0, screen_width + 1, cell_size):
            pygame.draw.aaline(screen, light_grey, (x, 0), (x, screen_height))

    if ball.colliderect(paddle_left) or ball.colliderect(paddle_right):
        continue

    pygame.draw.rect(screen, light_grey, paddle_left)
    pygame.draw.rect(screen, light_grey, paddle_right)
    pygame.draw.rect(screen, light_grey, ball)

    # Pygame screen to Frame
    frame = pygame.surfarray.array3d(screen)
    frame = np.transpose(frame, (1, 0, 2))
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # On YouTube you don't seek a frame, you seek a time: YouTube has to work
    # out which frame that time falls on, and sometimes it lands on one a bit
    # ahead or a bit behind the one we wanted. To reduce that error, the frame
    # is written with copies of itself before and after, and we tell YouTube to
    # seek the one in the middle. If it misses, it most likely lands on a
    # neighbor, which is a copy of the frame we wanted.
    for i in range(repeat):
        video.write(frame)


    middle_frame = frame_count * repeat + repeat // 2
    writer.writerow([
        absolute_pos_to_matrix_pos(paddle_left.x, paddle_left.y)[0],
        absolute_pos_to_matrix_pos(paddle_left.x, paddle_left.y)[1],
        absolute_pos_to_matrix_pos(ball.x, ball.y)[0],
        absolute_pos_to_matrix_pos(ball.x, ball.y)[1],
        absolute_pos_to_matrix_pos(paddle_right.x, paddle_right.y)[0],
        absolute_pos_to_matrix_pos(paddle_right.x, paddle_right.y)[1],
        middle_frame
    ])
    frame_count += 1

    pygame.display.flip()
    clock.tick(fps)
