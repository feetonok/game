import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Матрица: Начало")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
TRANSPARENT_BLACK = (0, 0, 0, 128)  # Полупрозрачный чёрный

# Шрифты
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 50)
dialog_font = pygame.font.Font(None, 36)

# Загрузка изображений
background = pygame.image.load("background.png")
portrait = pygame.image.load("portrait.png")
player_image = pygame.image.load("player.png")
wall_image = pygame.image.load("wall.png")
floor_image = pygame.image.load("floor.png")
door_image = pygame.image.load("door.png")
npc_image = pygame.image.load("npc.png")

# Размер тайла
TILE_SIZE = 50

# Размер видимой области (9x5 клеток)
VIEW_WIDTH = 9
VIEW_HEIGHT = 5

# Масштабирование тайлов
SCALED_TILE_SIZE = SCREEN_WIDTH // VIEW_WIDTH


# Функция для отрисовки текста в главном меню
def draw_menu_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)


# Функция для отрисовки текста в диалогах
def draw_dialog_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(topleft=(x, y))
    surface.blit(text_obj, text_rect)


# Функция для отрисовки кнопок
def draw_button(text, font, color, surface, x, y, width, height):
    pygame.draw.rect(surface, color, (x, y, width, height))
    draw_menu_text(text, font, BLACK, surface, x + width // 2, y + height // 2)


# Класс для диалогов
class DialogBox:
    def __init__(self, name, portrait, dialogues):
        self.name = name
        self.portrait = portrait
        self.dialogues = dialogues
        self.current_dialogue = 0
        self.current_text = ""
        self.char_index = 0
        self.delay = 50  # Задержка между символами
        self.last_update = pygame.time.get_ticks()
        self.finished = False

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.delay:
            self.last_update = now
            if self.char_index < len(self.dialogues[self.current_dialogue]):
                self.current_text += self.dialogues[self.current_dialogue][self.char_index]
                self.char_index += 1

    def next_dialogue(self):
        if self.current_dialogue < len(self.dialogues) - 1:
            self.current_dialogue += 1
            self.current_text = ""
            self.char_index = 0
        else:
            self.finished = True

    def draw(self, screen):
        # Создаём полупрозрачный фон для диалога
        dialog_bg = pygame.Surface((SCREEN_WIDTH - 100, 200), pygame.SRCALPHA)
        dialog_bg.fill((0, 0, 0, 128))  # Полупрозрачный чёрный
        screen.blit(dialog_bg, (50, SCREEN_HEIGHT - 250))

        # Отрисовка портрета (справа)
        portrait_scaled = pygame.transform.scale(self.portrait, (150, 200))  # Растягиваем портрет
        screen.blit(portrait_scaled, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250))

        # Отрисовка имени
        draw_dialog_text(self.name, dialog_font, WHITE, screen, 70, SCREEN_HEIGHT - 230)

        # Отрисовка текста
        draw_dialog_text(self.current_text, dialog_font, WHITE, screen, 70, SCREEN_HEIGHT - 200)


# Функция для загрузки карты
def load_map(file_path):
    with open(file_path, 'r') as file:
        return [list(line.strip()) for line in file]


# Функция для отрисовки карты
def draw_map(screen, map_data, camera_x, camera_y):
    # Определяем границы видимой области
    start_x = max(0, camera_x - VIEW_WIDTH // 2)
    start_y = max(0, camera_y - VIEW_HEIGHT // 2)
    end_x = min(len(map_data[0]), start_x + VIEW_WIDTH)
    end_y = min(len(map_data), start_y + VIEW_HEIGHT)

    # Отрисовка видимой области
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            # Отрисовка пола
            screen.blit(
                pygame.transform.scale(floor_image, (SCALED_TILE_SIZE, SCALED_TILE_SIZE)),
                ((x - start_x) * SCALED_TILE_SIZE, (y - start_y) * SCALED_TILE_SIZE)
            )
            # Отрисовка объектов
            if map_data[y][x] == '#':
                screen.blit(
                    pygame.transform.scale(wall_image, (SCALED_TILE_SIZE, SCALED_TILE_SIZE)),
                    ((x - start_x) * SCALED_TILE_SIZE, (y - start_y) * SCALED_TILE_SIZE)
                )
            elif map_data[y][x] == 'D':
                screen.blit(
                    pygame.transform.scale(door_image, (SCALED_TILE_SIZE, SCALED_TILE_SIZE)),
                    ((x - start_x) * SCALED_TILE_SIZE, (y - start_y) * SCALED_TILE_SIZE)
                )
            elif map_data[y][x] == '?':
                screen.blit(
                    pygame.transform.scale(npc_image, (SCALED_TILE_SIZE, SCALED_TILE_SIZE)),
                    ((x - start_x) * SCALED_TILE_SIZE, (y - start_y) * SCALED_TILE_SIZE)
                )


# Главное меню
def main_menu():
    selected_button = 0
    buttons = ["Новая игра", "Настройки", "Выход"]

    while True:
        screen.blit(background, (0, 0))
        draw_menu_text("Матрица: Начало", font, WHITE, screen, SCREEN_WIDTH // 2, 100)

        # Отрисовка кнопок
        for i, button_text in enumerate(buttons):
            color = GRAY if i != selected_button else WHITE
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 200 + i * 70, 200, 50)
            pygame.draw.rect(screen, color, button_rect)
            draw_menu_text(button_text, small_font, BLACK, screen, SCREEN_WIDTH // 2, 225 + i * 70)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_button = (selected_button + 1) % len(buttons)
                if event.key == pygame.K_UP:
                    selected_button = (selected_button - 1) % len(buttons)
                if event.key == pygame.K_z:  # Подтверждение выбора
                    if buttons[selected_button] == "Новая игра":
                        game_loop()
                    elif buttons[selected_button] == "Настройки":
                        print("Настройки")
                    elif buttons[selected_button] == "Выход":
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()


# Функция для проверки, стоит ли игрок напротив объекта
def is_facing_object(player_pos, direction, map_data, object_char):
    x, y = player_pos
    if direction == "up":
        return map_data[y - 1][x] == object_char
    elif direction == "down":
        return map_data[y + 1][x] == object_char
    elif direction == "left":
        return map_data[y][x - 1] == object_char
    elif direction == "right":
        return map_data[y][x + 1] == object_char
    return False


# Функция для поиска двери на карте
def find_door(map_data):
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            if tile == 'D':
                return x, y
    return None


# Игровой цикл
def game_loop():
    player_pos = [5, 5]  # Начальная позиция игрока в комнате
    current_map = load_map("room.txt")  # Загрузка первой карты
    dialog = None
    player_direction = "down"  # Направление игрока
    camera_x, camera_y = player_pos[0], player_pos[1]  # Камера следует за игроком

    # Диалоги для NPC
    npc_dialogues = {
        (6, 3): ["Приветствую! Я МАШИНА.", "Я помогу тебе создать твоего персонажа.", "Начнём?"],
        (8, 7): ["...", "Ты снова здесь?", "Что тебе нужно?"],
    }

    while True:
        screen.fill(BLACK)  # Очистка экрана

        # Отрисовка карты
        draw_map(screen, current_map, camera_x, camera_y)

        # Отрисовка игрока
        player_screen_x = (player_pos[0] - (camera_x - VIEW_WIDTH // 2)) * SCALED_TILE_SIZE
        player_screen_y = (player_pos[1] - (camera_y - VIEW_HEIGHT // 2)) * SCALED_TILE_SIZE
        screen.blit(
            pygame.transform.scale(player_image, (SCALED_TILE_SIZE, SCALED_TILE_SIZE)),
            (player_screen_x, player_screen_y)
        )

        # Отрисовка диалога
        if dialog:
            dialog.update()
            dialog.draw(screen)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not dialog or dialog.finished:
                    new_x, new_y = player_pos[0], player_pos[1]
                    if event.key == pygame.K_UP:
                        new_y -= 1
                        player_direction = "up"
                    if event.key == pygame.K_DOWN:
                        new_y += 1
                        player_direction = "down"
                    if event.key == pygame.K_LEFT:
                        new_x -= 1
                        player_direction = "left"
                    if event.key == pygame.K_RIGHT:
                        new_x += 1
                        player_direction = "right"

                    # Проверка коллизии
                    if 0 <= new_x < len(current_map[0]) and 0 <= new_y < len(current_map):
                        if current_map[new_y][new_x] not in ['#', 'D', '?']:  # Если нет стены, двери или NPC
                            player_pos[0], player_pos[1] = new_x, new_y

                    # Обновление камеры
                    camera_x = player_pos[0]
                    camera_y = player_pos[1]

                    # Ограничение камеры краями карты
                    camera_x = max(VIEW_WIDTH // 2, min(camera_x, len(current_map[0]) - VIEW_WIDTH // 2 - 1))
                    camera_y = max(VIEW_HEIGHT // 2, min(camera_y, len(current_map) - VIEW_HEIGHT // 2 - 1))

                if event.key == pygame.K_z:  # Взаимодействие
                    if dialog:
                        if dialog.finished:
                            dialog = None  # Завершаем диалог
                        else:
                            dialog.next_dialogue()  # Переход к следующей реплике
                    else:
                        if is_facing_object(player_pos, player_direction, current_map, '?'):  # NPC
                            npc_pos = (player_pos[0], player_pos[1] - 1) if player_direction == "up" else \
                                (player_pos[0], player_pos[1] + 1) if player_direction == "down" else \
                                    (player_pos[0] - 1, player_pos[1]) if player_direction == "left" else \
                                        (player_pos[0] + 1, player_pos[1])
                            if npc_pos in npc_dialogues:
                                print(f"Взаимодействие с NPC на позиции: {npc_pos}")  # Отладочное сообщение
                                dialog = DialogBox("NPC", portrait, npc_dialogues[npc_pos])
                        elif is_facing_object(player_pos, player_direction, current_map, 'D'):  # Дверь
                            if current_map == load_map("room.txt"):  # Переход из комнаты на улицу
                                current_map = load_map("street.txt")
                                door_pos = find_door(current_map)  # Ищем дверь на улице
                                if door_pos:
                                    player_pos = [door_pos[0], door_pos[1] + 1]  # Появляемся напротив двери
                            elif current_map == load_map("street.txt"):  # Переход с улицы в комнату
                                current_map = load_map("room.txt")
                                door_pos = find_door(current_map)  # Ищем дверь в комнате
                                if door_pos:
                                    player_pos = [door_pos[0], door_pos[1] + 1]  # Появляемся напротив двери

        pygame.display.flip()


# Запуск игры
main_menu()
