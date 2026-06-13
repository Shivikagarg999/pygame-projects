import pygame
import random
import sys

pygame.init()

WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

BLACK = (20, 20, 20)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
WHITE = (255, 255, 255)

font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 32)
clock = pygame.time.Clock()


def game_over_screen(score):
    while True:
        screen.fill(BLACK)
        screen.blit(font.render(f"Game Over! Score: {score}", True, WHITE), (WIDTH // 2 - 140, HEIGHT // 2 - 40))
        screen.blit(small_font.render("SPACE = Restart   Q = Quit", True, WHITE), (WIDTH // 2 - 130, HEIGHT // 2 + 20))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


while True:
    snake = [(300, 300)]
    direction = (CELL_SIZE, 0)
    food = (
        random.randrange(0, WIDTH, CELL_SIZE),
        random.randrange(0, HEIGHT, CELL_SIZE)
    )
    score = 0
    running = True

    while running:
        clock.tick(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                    direction = (0, -CELL_SIZE)
                elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                    direction = (0, CELL_SIZE)
                elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                    direction = (-CELL_SIZE, 0)
                elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                    direction = (CELL_SIZE, 0)

        head_x, head_y = snake[0]
        new_head = (head_x + direction[0], head_y + direction[1])

        if new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
            running = False
        if new_head in snake:
            running = False

        snake.insert(0, new_head)

        if new_head == food:
            score += 1
            food = (
                random.randrange(0, WIDTH, CELL_SIZE),
                random.randrange(0, HEIGHT, CELL_SIZE)
            )
        else:
            snake.pop()

        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, (food[0], food[1], CELL_SIZE, CELL_SIZE))
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        pygame.display.flip()

    game_over_screen(score)
