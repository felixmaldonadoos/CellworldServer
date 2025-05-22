import pygame
import math

def normalize_mouse_pos(screen_width, screen_height):
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Mouse Position Normalization")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get raw mouse position
        raw_x, raw_y = pygame.mouse.get_pos()

        # Normalize coordinates (origin at bottom-left)
        norm_x = raw_x / screen_width
        norm_y = 1 - (raw_y / screen_height)  # Flip Y-axis

        print(f"Normalized Mouse Position: ({norm_x:.3f}, {norm_y:.3f})")

        pygame.display.flip()

    pygame.quit()

@staticmethod
def scale_legacy_y(y):
    return y * 0.5 * math.sqrt(3) + 0.5 - math.sqrt(3) / 4

@staticmethod
def get_mouse_position(screen_width, screen_height)->tuple:
    raw_x, raw_y = pygame.mouse.get_pos()
    return raw_x / screen_width, scale_legacy_y(1 - (raw_y / screen_height))

# Example usage
if __name__ == "__main__":
    normalize_mouse_pos(800, 600)
