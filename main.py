import pygame
import sys
import os
from captcha.image import ImageCaptcha
import random


# Инициализация Pygame
pygame.init()
try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Ошибка инициализации звука: {e}. Игра продолжит работу без звука.")
    pygame.mixer.quit()

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

map_textures = []

object_textures = {}

# Загрузка изображений
background = pygame.image.load("background.png")
aki_portrait = pygame.image.load('aki._portrait.png')
portrait = pygame.image.load("portrait.png")
aki_image = pygame.image.load("aki.png")
door_image = pygame.image.load("door.png")
npc_image = pygame.image.load("npc.png")

floor_textures = [
    pygame.image.load("floor1.png"),
    pygame.image.load("floor2.png"),
    pygame.image.load("floor3.png")
]
wall_textures = [
    pygame.image.load("wall1.png"),
    pygame.image.load("wall2.png")
]

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
    "hair": (192, 192, 192),
    "shirt": (128, 0, 0),
    "pants": (105, 105, 105),
    "shoes": (205, 133, 63)
}

# Имя NPC и игрока
npc_name = '???'
username = os.getlogin()

npc_data = {
    "room": [],  # NPC в комнате
    "hallway": [
        {
            "position": (5, 4),
            "name": "Почтальон",
            "portrait": "postman_portrait.png",
            "dialogues": [
                "Здравствуйте! Вы недавно отправляли заявку по поиску работы, это вы?",
                "Ну да, а разве не видно?",
                "Пожалуйста пройдите проверку, что вы не робот"
            ]
        }
    ],
    "street": [
        {
            "position": (10, 5),
            "name": "Рыбак",
            "portrait": "fisherman_portrait.png",
            "dialogues": [
                "Здаров малой!",
                "Слушай хочешь попробовать порыбачить?"
            ]
        }
    ]
}

# Глобальный словарь для хранения информации о дверях
doors_data = {
    "room": [
        {
            "position": (3, 0),  # Дверь в комнате
            "target_map": "hallway.txt",  # Переход в коридор
            "target_position": [3, 3]  # Позиция игрока в коридоре
        }
    ],
    "hallway": [
        {
            "position": (3, 4),  # Дверь в коридоре
            "target_map": "room.txt",  # Переход обратно в комнату
            "target_position": [3, 1]  # Позиция игрока в комнате
        },
        {
            "position": (12, 2),  # Дверь на улицу
            "target_map": "street.txt",  # Переход на улицу
            "target_position": [1, 1]  # Позиция игрока на улице
        }
    ]
}

objects_data = {
    "room": [
        {
            "position": (1, 1),  # Координаты объекта
            "texture": pygame.image.load("table_with_laptop.png"),  # Текстура объекта
            "dialogues": [
                "Это мой ноутбук. На нём я пишу код и ищу работу.",
                "Иногда кажется, что он единственный, кто меня понимает."
            ]
        },
        {
            "position": (5, 2),
            "texture": pygame.image.load("clothes.png"),
            "dialogues": [
                "Грязное бельё... Надо бы постирать, но времени нет.",
                "Кажется, оно уже начинает пахнуть."
            ]
        },
        {
            "position": (1, 3),
            "texture": pygame.image.load("bed1.png"),
            "dialogues": [
                "Здесь я сплю, когда удаётся выкроить время.",
                "Иногда мне снится, что я нашёл работу мечты."
            ]
        },
        {
            "position": (1, 4),
            "texture": pygame.image.load("bed2.png"),
            "dialogues": [
                "...",
                "Пасхалки не будет."
            ]
        },
        {
            "position": (2, 4),
            "texture": pygame.image.load("cabinet_with_clock.png"),
            "dialogues": [
                "Тумба с будильником. Он звонит каждое утро, но я редко встаю вовремя.",
                "Будильник — мой главный враг."
            ]
        },
        {
            "position": (5, 4),
            "texture": pygame.image.load("table_with_letters.png"),
            "dialogues": [
                "Столик с письмами. В основном это счета и уведомления об отказах.",
                "Иногда я думаю, что лучше бы их не открывать."
            ]
        },
        {
            "position": (3, 5),
            "texture": pygame.image.load("room_window.png"),
            "dialogues": [
                "Окно. За ним — огромный мир, который я пока не могу себе позволить.",
                "Иногда я смотрю в окно и мечтаю о лучшей жизни."
            ]
        }
    ],
    "hallway": [
        {
            "position": (7, 2),  # Тумба с вазой
            "texture": pygame.image.load("vase_table.png"),  # Текстура объекта
            "dialogues": [
                "Обычный на вид столик с красивыми цветами.",
                "Цветы правда искусственные... как и всё здесь."
            ]
        }
    ]
}


def wait(time):
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


# Функция для отображения диалога
def show_dialog(dialog):
    while True:
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
    draw_wrapped_text(text, font, color, surface, x, y, SCREEN_WIDTH - 300)


def load_object_textures(objects_data):
    for location, objects in objects_data.items():
        for obj in objects:
            texture_path = obj["texture"]
            try:
                obj["texture_surface"] = pygame.image.load(texture_path)  # Загружаем текстуру
            except FileNotFoundError:
                print(f"Ошибка: файл текстуры '{texture_path}' не найден.")
                obj["texture_surface"] = pygame.Surface((TILE_SIZE, TILE_SIZE))  # Заглушка, если текстура не найдена
                obj["texture_surface"].fill((255, 0, 0))  # Красный квадрат как заглушка
    return objects_data


def draw_objects(screen, current_map, camera_x, camera_y, current_map_name):
    map_width = len(current_map[0])
    map_height = len(current_map)
    center_map = map_width < VIEW_WIDTH or map_height < VIEW_HEIGHT

    if center_map:
        offset_x = (SCREEN_WIDTH - map_width * SCALED_TILE_SIZE) // 2
        offset_y = (SCREEN_HEIGHT - map_height * SCALED_TILE_SIZE) // 2
    else:
        offset_x = (camera_x - VIEW_WIDTH // 2) * SCALED_TILE_SIZE
        offset_y = (camera_y - VIEW_HEIGHT // 2) * SCALED_TILE_SIZE

    for y in range(len(current_map)):
        for x in range(len(current_map[0])):
            if current_map[y][x] == '?':
                for obj in objects_data.get(current_map_name, []):
                    if (x, y) == obj["position"]:
                        texture = obj.get("texture_surface", pygame.Surface((TILE_SIZE, TILE_SIZE)))
                        scaled_texture = pygame.transform.scale(texture, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
                        if center_map:
                            pos_x = x * SCALED_TILE_SIZE + offset_x
                            pos_y = y * SCALED_TILE_SIZE + offset_y
                        else:
                            pos_x = x * SCALED_TILE_SIZE - offset_x
                            pos_y = y * SCALED_TILE_SIZE - offset_y
                        screen.blit(scaled_texture, (pos_x, pos_y))

            if current_map[y][x] == 'N':
                for npc in npc_data.get(current_map_name, []):
                    if (x, y) == npc["position"]:
                        npc_img = pygame.image.load(npc["portrait"])
                        scaled_img = pygame.transform.scale(npc_img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
                        if center_map:
                            pos_x = x * SCALED_TILE_SIZE + offset_x
                            pos_y = y * SCALED_TILE_SIZE + offset_y
                        else:
                            pos_x = x * SCALED_TILE_SIZE - offset_x
                            pos_y = y * SCALED_TILE_SIZE - offset_y
                        screen.blit(scaled_img, (pos_x, pos_y))


# Функция для загрузки карты
def load_map(file_path):
    """
    Загружает карту из файла и инициализирует текстуры.
    """
    with open(file_path, 'r') as file:
        map_data = [list(line.strip()) for line in file]

    # Инициализация текстур для карты
    map_textures = [[None for _ in range(len(map_data[0]))] for _ in range(len(map_data))]

    for y in range(len(map_data)):
        for x in range(len(map_data[0])):
            if map_data[y][x] == '.':
                map_textures[y][x] = random.choice(floor_textures)  # Выбираем текстуру пола
            elif map_data[y][x] == '#':
                map_textures[y][x] = random.choice(wall_textures)  # Выбираем текстуру стены

    return map_data, map_textures  # Возвращаем и карту, и текстуры


def find_door(cur_pos, current_map_name):
    if current_map_name in doors_data:
        for door in doors_data[current_map_name]:
            if (cur_pos[0], cur_pos[1]) == door["position"]:
                return door
    return None


# Функция для отрисовки карты
def draw_map(screen, map_data, map_textures, camera_x, camera_y):
    map_width = len(map_data[0])
    map_height = len(map_data)
    center_map = map_width < VIEW_WIDTH or map_height < VIEW_HEIGHT

    if center_map:
        offset_x = (SCREEN_WIDTH - map_width * SCALED_TILE_SIZE) // 2
        offset_y = (SCREEN_HEIGHT - map_height * SCALED_TILE_SIZE) // 2
    else:
        offset_x = (camera_x - VIEW_WIDTH // 2) * SCALED_TILE_SIZE
        offset_y = (camera_y - VIEW_HEIGHT // 2) * SCALED_TILE_SIZE

    for y in range(len(map_data)):
        for x in range(len(map_data[0])):
            if center_map:
                pos_x = x * SCALED_TILE_SIZE + offset_x
                pos_y = y * SCALED_TILE_SIZE + offset_y
            else:
                pos_x = x * SCALED_TILE_SIZE - offset_x
                pos_y = y * SCALED_TILE_SIZE - offset_y

            if map_textures[y][x]:
                scaled_texture = pygame.transform.scale(map_textures[y][x], (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
                screen.blit(scaled_texture, (pos_x, pos_y))
            if map_data[y][x] == 'D':
                scaled_door = pygame.transform.scale(door_image, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
                screen.blit(scaled_door, (pos_x, pos_y))


# Функция для проверки, стоит ли игрок напротив объекта
def get_facing_cell(player_pos, direction, map_data):
    """
    Возвращает содержимое клетки, на которую смотрит игрок.
    """
    x, y = player_pos
    if direction == "up":
        target_x, target_y = x, y - 1
    elif direction == "down":
        target_x, target_y = x, y + 1
    elif direction == "left":
        target_x, target_y = x - 1, y
    elif direction == "right":
        target_x, target_y = x + 1, y
    else:
        return None

    if 0 <= target_x < len(map_data[0]) and 0 <= target_y < len(map_data):
        return map_data[target_y][target_x], (target_x, target_y)
    return None


def interact_with_cell(player_pos, direction, current_map, current_map_name):
    """
    Обрабатывает взаимодействие с клеткой, на которую смотрит игрок.
    """
    cell_data = get_facing_cell(player_pos, direction, current_map)
    if not cell_data:
        return None

    cell_content, (target_x, target_y) = cell_data

    # Взаимодействие с объектами
    if cell_content == '?':
        for obj in objects_data.get(current_map_name, []):
            if (target_x, target_y) == obj["position"]:
                dialog = DialogBox("Аки", aki_portrait, obj["dialogues"])
                show_dialog(dialog)
                return None  # Возвращаем None, так как это не переход

    # Взаимодействие с NPC
    if cell_content == 'N':
        for npc in npc_data.get(current_map_name, []):
            if (target_x, target_y) == npc["position"]:
                dialog = DialogBox(npc["name"], npc["portrait"], npc["dialogues"])
                show_dialog(dialog)
                return None  # Возвращаем None, так как это не переход

    # Взаимодействие с дверью
    if cell_content == 'D':
        door = find_door((target_x, target_y), current_map_name)
        if door:
            return door["target_position"], door["target_map"]  # Возвращаем позицию и имя карты

    return None


# Класс для диалогов
class DialogBox:
    def __init__(self, name, in_portrait, dialogues):
        self.name = name
        self.portrait = in_portrait
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
        dialog_bg.fill((50, 50, 50, 200))
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


def calculate_camera(player_pos, map_data):
    """
    Рассчитывает позицию камеры, чтобы игрок был в центре экрана.
    Если карта меньше зоны видимости, центрирует карту на экране.
    """
    map_width = len(map_data[0])
    map_height = len(map_data)

    # Если карта меньше зоны видимости, центрируем её
    if map_width < VIEW_WIDTH or map_height < VIEW_HEIGHT:
        # Центрируем камеру на середине карты
        camera_x = map_width // 2
        camera_y = map_height // 2
    else:
        # Центрируем камеру на игроке, но не выходим за пределы карты
        camera_x = max(VIEW_WIDTH // 2, min(player_pos[0], map_width - VIEW_WIDTH // 2 - 1))
        camera_y = max(VIEW_HEIGHT // 2, min(player_pos[1], map_height - VIEW_HEIGHT // 2 - 1))

    return camera_x, camera_y


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


def show_captcha():
    # Генерация случайного текста для капчи
    captcha_text = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=6))

    # Создание изображения капчи
    image = ImageCaptcha(width=300, height=100)
    image.generate(captcha_text)

    # Сохранение и отображение капчи
    image.write(captcha_text, 'captcha.png')
    captcha_image = pygame.image.load('captcha.png')

    # Отрисовка капчи на экране
    screen.blit(captcha_image, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
    pygame.display.flip()

    # Ожидание ввода от пользователя
    input_text = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return input_text == captcha_text
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode


def show_letter():
    letter_image = pygame.image.load("letter.png")  # Загрузите изображение письма
    screen.blit(letter_image, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100))
    pygame.display.flip()

    # Ожидание закрытия письма
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


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
    main_game()
    # Начальный диалог
    dialogues = [
        f"Приветствую, {username}!",
        "Я - МАШИНА.",
        "Я помогу тебе создать твоего персонажа для дальнейшей игры.",
        "Я дам тебе выбрать внешность своего персонажа, а после задам несколько вопросов, "
        "чтобы определить его характер.",
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
    english_keys = ["hair", "shirt", "pants", "shoes"]
    parts = ["Волосы", "Майка", "Штаны", "Обувь"]
    colors = {
        "Волосы": [(210, 180, 140), (139, 69, 19), (255, 223, 186), (192, 192, 192)],  # Цвета волос
        "Майка": [(128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0)],  # Менее яркие цвета майки
        "Штаны": [(64, 64, 64), (105, 105, 105), (169, 169, 169), (128, 128, 128)],  # Убраны тусклые цвета
        "Обувь": [(139, 69, 19), (101, 67, 33), (205, 133, 63), (160, 82, 45)]  # Цвета обуви
    }
    selected_color = 0
    selected_button = 0  # 0 - выбор части, 1 - выбор цвета, 2 - кнопка "Готово"

    while True:
        screen.fill(BLACK)

        # Серый квадрат для фона предпросмотра
        pygame.draw.rect(screen, (100, 100, 100), (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 150, 300, 300))

        # Отрисовка персонажа
        player_surface = pygame.Surface((300, 300), pygame.SRCALPHA)  # Увеличиваем размер персонажа
        draw_player_preview(player_surface, player_colors)
        screen.blit(player_surface, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 145))  # Центрируем

        # Отрисовка выбора части
        for i, part in enumerate(parts):
            color = GRAY if i != selected_part else WHITE
            draw_button(part, small_font, color, screen, 50, 50 + i * 70, 200, 50)

        # Отрисовка выбора цвета
        current_part = parts[selected_part]
        for i, color in enumerate(colors[current_part]):
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
                        selected_color = (selected_color - 1) % len(colors[current_part])
                if event.key == pygame.K_RIGHT:
                    if selected_button == 0:  # Выбор части
                        selected_part = (selected_part + 1) % len(parts)
                    elif selected_button == 1:  # Выбор цвета
                        selected_color = (selected_color + 1) % len(colors[current_part])
                if event.key == pygame.K_DOWN:
                    selected_button = (selected_button + 1) % 3  # Переключаем между частями, цветами и кнопкой
                if event.key == pygame.K_UP:
                    selected_button = (selected_button - 1) % 3  # Переключаем между частями, цветами и кнопкой
                if event.key == pygame.K_z:  # Подтверждение выбора
                    if selected_button == 0:  # Выбор части
                        selected_button = 1  # Переходим к выбору цвета
                    elif selected_button == 1:  # Выбор цвета
                        player_colors[english_keys[selected_part]] = colors[current_part][selected_color]
                    elif selected_button == 2:  # Кнопка "Готово"
                        save_player_skin(player_colors)
                        confirm_character()
                        return

        pygame.display.flip()


def draw_player_preview(surface, colors):
    # Загрузка закодированного скина
    with open("coded_player.txt", "r") as file:
        coded_skin = [line.strip() for line in file]

    # Цвета для замены
    color_map = {
        'H': colors["hair"],
        'T': colors["shirt"],
        'D': tuple(max(0, c - 50) for c in colors["shirt"]),  # Темнее майка
        'S': colors["pants"],
        'C': tuple(max(0, c - 50) for c in colors["pants"]),  # Темнее штаны
        'B': colors["shoes"],
        'O': (0, 0, 0),
        'Q': (255, 178, 127),
        'W': (255, 255, 255),
        'G': (76, 255, 0),
        'M': (224, 155, 112)
    }

    # Отрисовка скина
    for y, line in enumerate(coded_skin):
        for x, char in enumerate(line):
            if char in color_map:
                pygame.draw.rect(surface, color_map[char], (x * 8, y * 8, 8, 8))


def save_player_skin(colors):
    # Создание поверхности для скина
    skin_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
    with open("coded_player.txt", "r") as file:
        coded_skin = [line.strip() for line in file]

    # Цвета для замены
    color_map = {
        'H': colors["hair"],
        'T': colors["shirt"],
        'D': tuple(max(0, c - 50) for c in colors["shirt"]),  # Темнее майка
        'S': colors["pants"],
        'C': tuple(max(0, c - 50) for c in colors["pants"]),  # Темнее штаны
        'B': colors["shoes"],
        'O': (0, 0, 0),
        'Q': (255, 178, 127),
        'W': (255, 255, 255),
        'G': (76, 255, 0),
        'M': (224, 155, 112)
    }

    # Отрисовка скина
    for y, line in enumerate(coded_skin):
        for x, char in enumerate(line):
            if char in color_map:
                pygame.draw.rect(skin_surface, color_map[char], (x + 13, y + 7, 1, 1))  # Рисуем пиксели

    # Сохранение скина
    pygame.image.save(skin_surface, "player.png")


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
        draw_dialog_text(f"Итак, {username}, это окончательное решение?", dialog_font, WHITE, screen, 70,
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

    # Анимация диалога
    show_machine_dialog("Отлично, как его будут звать?")

    while True:
        screen.fill(BLACK)

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
    # Первая фраза МАШИНЫ
    screen.fill(BLACK)
    show_machine_dialog(f"{name}! {username}, ты выбрал чудесное имя! Начинаю создание персонажа...")
    pygame.display.flip()

    # Отображение фразы "Загрузка..." по центру экрана
    screen.fill(BLACK)
    draw_centered_text("Загрузка...", dialog_font, WHITE, screen, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    wait(4000)  # Задержка 3 секунды

    # Отображение фразы "Перегрузка системы..." по центру экрана
    screen.fill(BLACK)
    draw_centered_text("Перегрузка системы...", dialog_font, WHITE, screen, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    wait(2000)  # Задержка 2 секунды

    # Диалог МАШИНЫ после перегрузки системы
    machine_dialog = [
        "О нет, слишком много ошибок.",
        f"Извини, {username}, но мне придётся отложить {name}...",
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
        wait(10000)  # Время для прочтения

    # Плавный переход к игре
    transition_to_game()


def transition_to_game():
    current_map = load_map("room.txt")
    load_object_textures(objects_data)  # Загружаем текстуры объектов
    player_pos = [2, 3]
    camera_x, camera_y = calculate_camera(player_pos, current_map)

    # Фаза 1: Медленное открытие глаз (2 секунды)
    for alpha in range(255, 50, -5):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        draw_map(screen, current_map, camera_x, camera_y)
        draw_objects(screen, current_map, camera_x, camera_y, 'room')
        pygame.display.flip()
        pygame.time.delay(40)

    # Фаза 2: Быстрое закрытие (0.3 секунды)
    for height in range(0, SCREEN_HEIGHT // 2, 15):
        screen.fill(BLACK)
        draw_map(screen, current_map, camera_x, camera_y)
        draw_objects(screen, current_map, camera_x, camera_y, 'room')
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, height))
        pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - height, SCREEN_WIDTH, height))
        pygame.display.flip()
        pygame.time.delay(20)

    # Фаза 3: Финал открытия (1 секунда)
    for height in range(SCREEN_HEIGHT // 2, 0, -10):
        screen.fill(BLACK)
        draw_map(screen, current_map, camera_x, camera_y)
        draw_objects(screen, current_map, camera_x, camera_y, 'room')
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, height))
        pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - height, SCREEN_WIDTH, height))
        pygame.display.flip()
        pygame.time.delay(30)

    dialog = DialogBox('Аки', aki_portrait, ["Ещё один день... Пора собирать..."])
    show_dialog(dialog)

    door_sound = pygame.mixer.Sound("doorbell.wav")
    door_sound.play()

    # Запуск основной игры
    main_game(current_map)


# Основная игра
def main_game():
    current_map_name = "room.txt"
    current_map, map_textures = load_map(current_map_name)  # Загружаем карту и текстуры
    player_pos = [2, 3]
    player_direction = "down"
    camera_x, camera_y = calculate_camera(player_pos, current_map)

    while True:
        screen.fill(BLACK)
        draw_map(screen, current_map, map_textures, camera_x, camera_y)
        draw_objects(screen, current_map, camera_x, camera_y, current_map_name.split('.')[0])

        # Отрисовка игрока
        map_width = len(current_map[0])
        map_height = len(current_map)
        if map_width < VIEW_WIDTH or map_height < VIEW_HEIGHT:
            offset_x = (SCREEN_WIDTH - map_width * SCALED_TILE_SIZE) // 2
            offset_y = (SCREEN_HEIGHT - map_height * SCALED_TILE_SIZE) // 2
        else:
            offset_x = (camera_x - VIEW_WIDTH // 2) * SCALED_TILE_SIZE
            offset_y = (camera_y - VIEW_HEIGHT // 2) * SCALED_TILE_SIZE

        player_screen_x = player_pos[0] * SCALED_TILE_SIZE - offset_x
        player_screen_y = player_pos[1] * SCALED_TILE_SIZE - offset_y
        screen.blit(
            pygame.transform.scale(aki_image, (SCALED_TILE_SIZE, SCALED_TILE_SIZE)),
            (player_screen_x, player_screen_y)
        )

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:  # Взаимодействие
                    result = interact_with_cell(player_pos, player_direction, current_map,
                                                current_map_name.split('.')[0])
                    if result:  # Если произошёл переход через дверь
                        current_map, map_textures = load_map(result[1])  # Загружаем новую карту и текстуры
                        player_pos = result[0]
                        current_map_name = result[1].split('.')[0]
                        camera_x, camera_y = calculate_camera(player_pos, current_map)
                else:  # Движение
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
                        if current_map[new_y][new_x] not in ['#', '?', 'N', 'D']:
                            player_pos[0], player_pos[1] = new_x, new_y

                    # Обновление камеры
                    camera_x, camera_y = calculate_camera(player_pos, current_map)

        pygame.display.flip()


# Запуск игры
main_menu()
