import pygame
import random

pygame.init()

WIDTH = 500
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

SKY = (135, 206, 235)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)

clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 35)

pipe_width = 80
pipe_gap = 260


def create_pipe(x_offset=0):
    height = random.randint(100, 300)
    top_pipe = pygame.Rect(WIDTH + x_offset, 0, pipe_width, height)
    bottom_pipe = pygame.Rect(WIDTH + x_offset, height + pipe_gap, pipe_width, HEIGHT - height - pipe_gap)
    return [top_pipe, bottom_pipe]


def reset_pipe(pair):
    height = random.randint(100, 300)
    pair[0].x = WIDTH + 100
    pair[0].height = height
    pair[1].x = WIDTH + 100
    pair[1].y = height + pipe_gap
    pair[1].height = HEIGHT - height - pipe_gap


def game_over_screen(score):
    while True:
        screen.fill(SKY)
        over_text = font.render("GAME OVER", True, RED)
        score_text = font.render(f"Score: {score // 60}", True, WHITE)
        restart_text = small_font.render("SPACE = Restart   Q = Quit", True, WHITE)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 250))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 330))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 410))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_q:
                    return False


while True:
    bird = pygame.Rect(100, 300, 40, 40)
    velocity = 0
    gravity = 0.5
    jump_strength = -10
    pipe_pairs = [create_pipe(x_offset=i * 250) for i in range(3)]
    score = 0
    running = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    velocity = jump_strength

        velocity += gravity
        bird.y += int(velocity)

        screen.fill(SKY)
        pygame.draw.rect(screen, YELLOW, bird)

        for pair in pipe_pairs:
            for pipe in pair:
                pipe.x -= 4
                pygame.draw.rect(screen, GREEN, pipe)
                if bird.colliderect(pipe):
                    running = False

            if pair[0].right < 0:
                reset_pipe(pair)

        score += 1
        screen.blit(font.render(str(score // 60), True, WHITE), (20, 20))

        if bird.top < 0 or bird.bottom > HEIGHT:
            running = False

        pygame.display.update()

    if not game_over_screen(score):
        break

pygame.quit()
