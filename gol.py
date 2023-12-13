import pygame
import numpy as np
import time
import pickle

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))

n_cells_x, n_cells_y = 40, 30
cell_width = width // n_cells_x
cell_height = height // n_cells_y

game_state = np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[0.8, 0.2])

white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)
green = (0, 255, 0)

button_width, button_height = 200, 50
button_x, button_y = (width - button_width) // 2, height - button_height - 10

def draw_button(text):
    pygame.draw.rect(screen, green, (button_x, button_y, button_width, button_height))
    font = pygame.font.Font(None, 36)
    button_text = font.render(text, True, black)
    text_rect = button_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
    screen.blit(button_text, text_rect)

def draw_grid():
    for y in range(0, height, cell_height):
        for x in range(0, width, cell_width):
            cell = pygame.Rect(x, y, cell_width, cell_height)
            pygame.draw.rect(screen, gray, cell, 1)

def next_generation(game_state):
    new_state = np.copy(game_state)

    for y in range(n_cells_y):
        for x in range(n_cells_x):
            n_neighbors = game_state[(x - 1) % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state[(x)     % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state[(x + 1) % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state[(x - 1) % n_cells_x, (y)     % n_cells_y] + \
                          game_state[(x + 1) % n_cells_x, (y)     % n_cells_y] + \
                          game_state[(x - 1) % n_cells_x, (y + 1) % n_cells_y] + \
                          game_state[(x)     % n_cells_x, (y + 1) % n_cells_y] + \
                          game_state[(x + 1) % n_cells_x, (y + 1) % n_cells_y]

            if game_state[x, y] == 1 and (n_neighbors < 2 or n_neighbors > 3):
                new_state[x, y] = 0
            elif game_state[x, y] == 0 and n_neighbors == 3:
                new_state[x, y] = 1

    return new_state

def draw_cells(game_state):
    for y in range(n_cells_y):
        for x in range(n_cells_x):
            cell = pygame.Rect(x * cell_width, y * cell_height, cell_width, cell_height)
            if game_state[x, y] == 1:
                pygame.draw.rect(screen, black, cell)

class Command:
    def execute(self):
        pass

class SimulationCommand(Command):
    def __init__(self, function, game_state):
        self._function = function
        self._game_state = game_state

    def execute(self):
        self._game_state[:] = self._function(self._game_state)

class Button:
    def __init__(self, command, text):
        self._command = command
        self._text = text

    def on_click(self):
        self._command.execute()

class Observable:
    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.update()

class Simulation(Observable):
    def __init__(self, game_state):
        super().__init__()
        self._game_state = game_state
        self._running = False

    def start(self):
        self._running = True

    def pause(self):
        self._running = False

    def is_running(self):
        return self._running

    def get_game_state(self):
        return self._game_state

    def set_game_state(self, new_state):
        self._game_state = new_state

# Function to save the game state
def save_game(game_state):
    with open("game_state.pickle", "wb") as file:
        pickle.dump(game_state, file)

# Function to load the game state
def load_game():
    try:
        with open("game_state.pickle", "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return None

# Create the Simulation object
simulation = Simulation(game_state)

# Command objects
simulation_command = SimulationCommand(next_generation, game_state)
button_command = Button(simulation_command, "Next Generation")

simulation.add_observer(button_command)

running = True
pause_simulation = False
save_game_state = False

while running:
    screen.fill(white)
    draw_grid()
    draw_cells(game_state)
    draw_button(button_command._text)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_x <= event.pos[0] <= button_x + button_width and button_y <= event.pos[1] <= button_y + button_height:
                if simulation.is_running():
                    simulation.pause()
                    button_command._text = "Resume"
                else:
                    simulation.start()
                    button_command._text = "Pause"
            else:
                x, y = event.pos[0] // cell_width, event.pos[1] // cell_height
                game_state[x, y] = not game_state[x, y]

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save_game(game_state)
                print("Game state saved.")
            elif event.key == pygame.K_l:
                loaded_state = load_game()
                if loaded_state is not None:
                    game_state = loaded_state
                    print("Game state loaded.")
                else:
                    print("No saved game state found.")

    if simulation.is_running() and not pause_simulation:
        simulation_command.execute()
        time.sleep(0.1)

pygame.quit()
