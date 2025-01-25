import pygame
import sys
import time

# Инициализация Pygame
pygame.init()

# Настройки экрана
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
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

# Переменные для настроек
volume = 0.5  # Громкость звука
resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)  # Разрешение экрана

# Переменные для редактора персонажа
player_colors = {
    "hair": (255, 0, 0),  # Красный
    "shirt": (0, 255, 0),  # Зелёный
    "pants": (0, 0, 255),  # Синий
    "shoes": (255, 255, 0)  # Жёлтый
}

# Имя NPC
npc_name = "???"

npc_dialogues = {
        (6, 3): ["Приветствую! Я МАШИНА.", "Я помогу тебе создать твоего персонажа.", "Начнём?"],
        (8, 7): ["...", "Ты снова здесь?", "Что тебе нужно?"],
    }


# Функция для отображения диалога
def show_dialog(dialog):
    while True:
        screen.fill(BLACK)

        # Отрисовка диалога
        dialog.update()
        if dialog.finished:
            break
        else:
            dialog.draw(screen)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    if dialog.next_dialogue():
                        dialog = None
                        return

        pygame.display.flip()


def show_machine_dialog(text):
    dialog_box = DialogBox("МАШИНА", portrait, [text])
    while True:
        screen.fill(BLACK)
        dialog_box.update()
        dialog_box.draw(screen)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    if dialog_box.next_dialogue():
                        return

        pygame.display.flip()


def draw_centered_text(text, font, color, surface, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y))
    surface.blit(text_surface, text_rect)


# Функция для отрисовки текста с переносом строк
def draw_wrapped_text(text, font, color, surface, x, y, max_width):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + ' '
    lines.append(current_line.strip())

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y + i * font.get_height()))


# Функция для отрисовки текста в диалогах
def draw_dialog_text(text, font, color, surface, x, y):
    draw_wrapped_text(text, font, color, surface, x, y, SCREEN_WIDTH - 300)  # Уменьшили ширину текста


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
            return True  # Возвращаем True, если диалог завершён
        return False  # Возвращаем False, если диалог продолжается

    def draw(self, screen):
        # Создаём полупрозрачный фон для диалога
        dialog_bg = pygame.Surface((SCREEN_WIDTH - 100, 200), pygame.SRCALPHA)
        dialog_bg.fill((0, 0, 0, 128))  # Полупрозрачный чёрный
        screen.blit(dialog_bg, (50, SCREEN_HEIGHT - 250))

        # Отрисовка портрета (справа, квадрат 150x150)
        portrait_scaled = pygame.transform.scale(self.portrait, (150, 150))  # Квадратный портрет
        screen.blit(portrait_scaled, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250 + 25))  # Центрируем по вертикали

        # Отрисовка имени
        draw_dialog_text(self.name, dialog_font, WHITE, screen, 70, SCREEN_HEIGHT - 230)

        # Отрисовка текста
        draw_dialog_text(self.current_text, dialog_font, WHITE, screen, 70, SCREEN_HEIGHT - 200)


# Функция для отрисовки текста в главном меню
def draw_menu_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)


# Функция для отрисовки кнопок
def draw_button(text, font, color, surface, x, y, width, height):
    pygame.draw.rect(surface, color, (x, y, width, height))
    draw_menu_text(text, font, BLACK, surface, x + width // 2, y + height // 2)


# Меню паузы
def pause_menu():
    selected_button = 0
    buttons = ["Продолжить", "Сохранить", "Загрузить", "Настройки", "Выход"]

    while True:
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

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
                    if buttons[selected_button] == "Продолжить":
                        return
                    elif buttons[selected_button] == "Сохранить":
                        print("Игра сохранена")
                    elif buttons[selected_button] == "Загрузить":
                        print("Игра загружена")
                    elif buttons[selected_button] == "Настройки":
                        settings_menu()
                    elif buttons[selected_button] == "Выход":
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()


# Меню настроек
def settings_menu():
    global volume, resolution, screen
    selected_button = 0
    buttons = ["Громкость: " + str(int(volume * 100)) + "%",
               "Разрешение: " + str(resolution[0]) + "x" + str(resolution[1]), "Назад"]

    while True:
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Отрисовка кнопок
        for i, button_text in enumerate(buttons):
            color = GRAY if i != selected_button else WHITE
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 200 + i * 70, 300, 50)
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
                    if buttons[selected_button].startswith("Громкость"):
                        volume = (volume + 0.1) % 1.1  # Увеличиваем громкость на 10%
                        buttons[0] = "Громкость: " + str(int(volume * 100)) + "%"
                    elif buttons[selected_button].startswith("Разрешение"):
                        resolution = (1280, 720) if resolution == (1920, 1080) else (1920, 1080)
                        buttons[1] = "Разрешение: " + str(resolution[0]) + "x" + str(resolution[1])
                        screen = pygame.display.set_mode(resolution, pygame.RESIZABLE)
                    elif buttons[selected_button] == "Назад":
                        return

        pygame.display.flip()


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
                        new_game()
                    elif buttons[selected_button] == "Настройки":
                        settings_menu()
                    elif buttons[selected_button] == "Выход":
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()


# Новая игра
def new_game():
    global npc_name
    # Начальный диалог
    dialogues = [
        "Приветствую, Игрок!",
        "Я - МАШИНА.",
        "Я помогу тебе создать твоего персонажа для дальнейшей игры.",
        "Я дам тебе выбрать внешность своего персонажа, а после задам несколько вопросов, чтобы определить его характер.",
        "Всё понятно? Начнём!"
    ]
    dialog = DialogBox(npc_name, portrait, dialogues)

    running = True
    while running:
        screen.fill(BLACK)

        # Отрисовка диалога
        if dialog:
            dialog.update()
            if dialog.finished:
                break  # Выходим из цикла после завершения диалога
            else:
                # Меняем имя NPC на "МАШИНА" после второго диалога
                if dialog.current_dialogue >= 1:
                    dialog.name = "МАШИНА"
                dialog.draw(screen)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    if dialog.next_dialogue():
                        dialog = None
                        running = False

        pygame.display.flip()

    # Переход к редактору персонажа
    character_editor()


# Редактор персонажа
def character_editor():
    global player_colors
    selected_part = 0
    parts = ["Волосы", "Майка", "Штаны", "Обувь"]
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (128, 0, 128)]
    selected_color = 0
    selected_button = 0  # 0 - выбор части, 1 - выбор цвета, 2 - кнопка "Готово"

    while True:
        screen.fill(BLACK)

        # Отрисовка персонажа
        player_surface = pygame.Surface((SCALED_TILE_SIZE * 2, SCALED_TILE_SIZE * 2))
        player_surface.fill(player_colors["hair"])  # Волосы
        player_surface.fill(player_colors["shirt"],
                            (0, SCALED_TILE_SIZE // 2, SCALED_TILE_SIZE * 2, SCALED_TILE_SIZE))  # Майка
        player_surface.fill(player_colors["pants"],
                            (0, SCALED_TILE_SIZE, SCALED_TILE_SIZE * 2, SCALED_TILE_SIZE))  # Штаны
        player_surface.fill(player_colors["shoes"],
                            (0, SCALED_TILE_SIZE * 1.5, SCALED_TILE_SIZE * 2, SCALED_TILE_SIZE // 2))  # Обувь
        screen.blit(player_surface, (SCREEN_WIDTH // 2 - SCALED_TILE_SIZE, SCREEN_HEIGHT // 2 - SCALED_TILE_SIZE))

        # Отрисовка выбора части
        for i, part in enumerate(parts):
            color = GRAY if i != selected_part else WHITE
            draw_button(part, small_font, color, screen, 50, 50 + i * 70, 200, 50)

        # Отрисовка выбора цвета
        for i, color in enumerate(colors):
            border_color = WHITE if i == selected_color and selected_button == 1 else BLACK
            pygame.draw.rect(screen, color, (300 + i * 70, 50, 50, 50))
            pygame.draw.rect(screen, border_color, (300 + i * 70, 50, 50, 50), 3)

        # Отрисовка кнопки "Готово"
        button_color = GRAY if selected_button != 2 else WHITE
        draw_button("Готово", small_font, button_color, screen, SCREEN_WIDTH - 250, SCREEN_HEIGHT - 100, 200, 50)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if selected_button == 0:  # Выбор части
                        selected_part = (selected_part - 1) % len(parts)
                    elif selected_button == 1:  # Выбор цвета
                        selected_color = (selected_color - 1) % len(colors)
                if event.key == pygame.K_RIGHT:
                    if selected_button == 0:  # Выбор части
                        selected_part = (selected_part + 1) % len(parts)
                    elif selected_button == 1:  # Выбор цвета
                        selected_color = (selected_color + 1) % len(colors)
                if event.key == pygame.K_DOWN:
                    selected_button = (selected_button + 1) % 3  # Переключаем между частями, цветами и кнопкой
                if event.key == pygame.K_UP:
                    selected_button = (selected_button - 1) % 3  # Переключаем между частями, цветами и кнопкой
                if event.key == pygame.K_z:  # Подтверждение выбора
                    if selected_button == 0:  # Выбор части
                        selected_button = 1  # Переходим к выбору цвета
                    elif selected_button == 1:  # Выбор цвета
                        player_colors[parts[selected_part].lower()] = colors[selected_color]
                    elif selected_button == 2:  # Кнопка "Готово"
                        confirm_character()
                        return

        pygame.display.flip()


# Подтверждение выбора персонажа
def confirm_character():
    global npc_name
    selected_button = 0
    buttons = ["Да", "Нет"]

    while True:
        screen.fill(BLACK)

        # Отрисовка диалога
        dialog_bg = pygame.Surface((SCREEN_WIDTH - 100, 200), pygame.SRCALPHA)
        dialog_bg.fill((0, 0, 0, 128))  # Полупрозрачный чёрный
        screen.blit(dialog_bg, (50, SCREEN_HEIGHT - 250))

        # Отрисовка текста
        draw_dialog_text(f"Итак, Игрок, это окончательное решение?", dialog_font, WHITE, screen, 70,
                         SCREEN_HEIGHT - 230)

        # Отрисовка кнопок "Да" и "Нет"
        for i, button_text in enumerate(buttons):
            color = GRAY if i != selected_button else WHITE
            button_rect = pygame.Rect(100, SCREEN_HEIGHT - 150 + i * 70, 150, 50)
            pygame.draw.rect(screen, color, button_rect)
            draw_menu_text(button_text, small_font, BLACK, screen, 175, SCREEN_HEIGHT - 125 + i * 70)

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
                    if buttons[selected_button] == "Да":
                        name_input()
                        return
                    elif buttons[selected_button] == "Нет":
                        # Возвращаемся к редактору персонажа
                        dialog = DialogBox("МАШИНА", portrait, ["Оу... тогда я дам тебе ещё время подумать."])
                        show_dialog(dialog)
                        character_editor()  # Возврат в редактор персонажа
                        return

        pygame.display.flip()


# Ввод имени персонажа
def name_input():
    global npc_name
    name = ""
    keyboard = [
        "йцукенгшщзхъ",
        "фывапролджэ",
        "ячсмитьбю"
    ]
    selected_key = (0, 0)  # Выбранная клавиша (строка, символ)
    selected_button = 0  # 0 - клавиатура, 1 - кнопка "Удалить", 2 - кнопка "Готово"

    while True:
        screen.fill(BLACK)

        # Отрисовка диалога от МАШИНЫ
        dialog_bg = pygame.Surface((SCREEN_WIDTH - 100, 200), pygame.SRCALPHA)
        dialog_bg.fill((0, 0, 0, 128))  # Полупрозрачный чёрный
        screen.blit(dialog_bg, (50, 50))  # Подняли диалог выше

        # Отрисовка портрета МАШИНЫ
        portrait_scaled = pygame.transform.scale(portrait, (150, 150))  # Квадратный портрет
        screen.blit(portrait_scaled, (SCREEN_WIDTH - 200, 75))  # Центрируем по вертикали

        # Отрисовка текста
        draw_dialog_text("МАШИНА", dialog_font, WHITE, screen, 70, 70)
        draw_dialog_text("Отлично, как его будут звать?", dialog_font, WHITE, screen, 70, 110)

        # Отрисовка строки ввода
        input_bg = pygame.Surface((SCREEN_WIDTH - 300, 50), pygame.SRCALPHA)
        input_bg.fill((100, 100, 100, 128))  # Серый полупрозрачный фон
        screen.blit(input_bg, (150, 300))  # Подняли поле ввода выше
        draw_dialog_text(name, dialog_font, WHITE, screen, 160, 310)

        # Отрисовка клавиатуры
        for i, row in enumerate(keyboard):
            for j, char in enumerate(row):
                x = 200 + j * 60
                y = 400 + i * 60  # Подняли клавиатуру выше
                color = WHITE if (i, j) == selected_key and selected_button == 0 else GRAY
                pygame.draw.rect(screen, color, (x, y, 50, 50))
                draw_menu_text(char, small_font, BLACK, screen, x + 25, y + 25)

        # Отрисовка кнопки "Удалить"
        delete_color = WHITE if selected_button == 1 else GRAY
        draw_button("Удалить", small_font, delete_color, screen, SCREEN_WIDTH - 250, 460, 200, 50)  # Шире и выше

        # Отрисовка кнопки "Готово"
        done_color = WHITE if selected_button == 2 else GRAY
        draw_button("Готово", small_font, done_color, screen, SCREEN_WIDTH - 250, 530, 200, 50)  # Шире и выше

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if selected_button == 1:  # Возврат с кнопки "Удалить"
                        selected_button = 0
                        selected_key = (1, len(keyboard[1]) - 1)  # Последний символ второй строки
                    elif selected_button == 2:  # Возврат с кнопки "Готово"
                        selected_button = 0
                        selected_key = (2, len(keyboard[2]) - 1)  # Последний символ третьей строки
                    elif selected_button == 0:  # Клавиатура
                        selected_key = (selected_key[0], (selected_key[1] - 1) % len(keyboard[selected_key[0]]))
                if event.key == pygame.K_RIGHT:
                    if selected_button == 0:  # Клавиатура
                        # Переход на кнопку "Удалить" с последнего символа второй строки
                        if selected_key == (1, len(keyboard[1]) - 1):  # Последний символ второй строки ("э")
                            selected_button = 1
                        # Переход на кнопку "Готово" с последнего символа третьей строки
                        elif selected_key == (2, len(keyboard[2]) - 1):  # Последний символ третьей строки ("ю")
                            selected_button = 2
                        else:
                            selected_key = (selected_key[0], (selected_key[1] + 1) % len(keyboard[selected_key[0]]))
                if event.key == pygame.K_DOWN:
                    if selected_button == 1:  # Переход с "Удалить" на "Готово"
                        selected_button = 2
                    elif selected_button == 0:  # Клавиатура
                        selected_key = ((selected_key[0] + 1) % len(keyboard), selected_key[1])
                if event.key == pygame.K_UP:
                    if selected_button == 2:  # Переход с "Готово" на "Удалить"
                        selected_button = 1
                    elif selected_button == 0:  # Клавиатура
                        selected_key = ((selected_key[0] - 1) % len(keyboard), selected_key[1])
                if event.key == pygame.K_z:  # Подтверждение выбора
                    if selected_button == 0:  # Клавиатура
                        if len(name) < 10:  # Ограничение на 10 символов
                            # Делаем первую букву заглавной
                            new_char = keyboard[selected_key[0]][selected_key[1]]
                            if not name:
                                new_char = new_char.upper()
                            name += new_char
                    elif selected_button == 1:  # Удалить
                        name = name[:-1]  # Удаляем последний символ
                    elif selected_button == 2:  # Готово
                        if name:
                            finalize_character(name)
                            return

        pygame.display.flip()


# Завершение создания персонажа
def finalize_character(name):
    global npc_name
    # Первая фраза МАШИНЫ
    screen.fill(BLACK)
    show_machine_dialog(f"{name}! {npc_name}, ты выбрал чудесное имя! Начинаю создание персонажа...")
    pygame.display.flip()

    # Отображение фразы "Загрузка..." по центру экрана
    screen.fill(BLACK)
    draw_centered_text("Загрузка...", dialog_font, WHITE, screen, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    pygame.time.delay(4000)  # Задержка 3 секунды

    # Отображение фразы "Перегрузка системы..." по центру экрана
    screen.fill(BLACK)
    draw_centered_text("Перегрузка системы...", dialog_font, WHITE, screen, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    pygame.time.delay(2000)  # Задержка 2 секунды

    # Диалог МАШИНЫ после перегрузки системы
    machine_dialog = [
        "О нет, слишком много ошибок.",
        f"Извини, {npc_name}, но мне придётся отложить {name}...",
        "Твоим 'компаньоном' в данной истории будет...",
        "Аки"
    ]

    # Отображение диалога МАШИНЫ
    for text in machine_dialog:
        show_machine_dialog(text)

    # Биография ГГ
    biography = [
        "Аки — обычный человек лет 20 в мире киберпанка.",
        "У него мало денег, поэтому он параллельно учится и ищет себе работу, чтобы на что-то жить.",
        "Его жизнь полна трудностей, но он не сдаётся и продолжает бороться за своё место в этом мире."
    ]

    # Отображение биографии по центру экрана
    for line in biography:
        screen.fill(BLACK)
        draw_centered_text(line, dialog_font, WHITE, screen, SCREEN_HEIGHT // 2 - 50)
        pygame.display.flip()
        pygame.time.delay(10000)  # Время для прочтения

    # Переход к основной игре
    main_game()


# Основная игра
def main_game():

    player_pos = [5, 5]  # Начальная позиция игрока в комнате
    current_map = load_map("room.txt")  # Загрузка первой карты
    dialog = None
    player_direction = "down"  # Направление игрока
    camera_x, camera_y = player_pos[0], player_pos[1]  # Камера следует за игроком

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
