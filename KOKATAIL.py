import pygame as pg
import sys
import time
# 初期設定
WIDTH, HEIGHT = 1920, 1080
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("コマンド選択画面 + HPバー + HP表示")
clock = pg.time.Clock()
pg.mouse.set_visible(False)

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# フォント
font = pg.font.SysFont("meiryo", 50)
small_font = pg.font.SysFont("meiryo", 40)

# メインコマンド
commands = ["こうげき", "アクション", "アイテム", "にげる"]
selected_index = 0

# サブコマンド（アクション時）
action_commands = ["はなす", "ぶんせき","だまる"]
action_selected_index = 0
in_action_command = 0

# コマンドボックスサイズ
box_width = 265
box_height = 80
box_y = HEIGHT - 300

# HPバーサイズ
hp_bar_width = 160
hp_bar_height = 20
hp_bar_margin_top = 10

# HP値
max_hp = 50
current_hp = 50

def get_command_boxes():
    spacing = 40
    total_width = len(commands) * box_width + (len(commands) - 1) * spacing
    start_x = (WIDTH - total_width) // 2
    boxes = []
    for i in range(len(commands)):
        x = start_x + i * (box_width + spacing)
        boxes.append(pg.Rect(x, box_y, box_width, box_height))
    return boxes

def draw_action_menu():
    box_width = 400
    box_height = 80
    spacing = 20
    start_x = 350
    start_y = HEIGHT-300
    for i, act in enumerate(action_commands):
        rect = pg.Rect(start_x + i * (box_width + spacing), start_y, box_width, box_height)
        color = YELLOW if i == action_selected_index else WHITE
        pg.draw.rect(screen, color, rect, 3)
        text = font.render(act, True, WHITE)
        text_x = rect.x + (box_width - text.get_width()) // 2
        text_y = rect.y + (box_height - text.get_height()) // 2
        screen.blit(text, (text_x, text_y))


def _draw_message_box(self, screen, text):
    # 1行のメッセージを持つテキストボックスを描画する
    box_rect = pg.Rect(400, HEIGHT - 200, WIDTH - 800, 150)
    pg.draw.rect(screen, BLACK, box_rect)
    pg.draw.rect(screen, WHITE, box_rect, 4)
    surf = small_font.render(text, True, WHITE)
    screen.blit(surf, (box_rect.x + 40, box_rect.y + 30))

    
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        elif event.type == pg.KEYDOWN:
            if in_action_command == 1:
                if event.key == pg.K_LEFT:
                    action_selected_index = (action_selected_index - 1) % len(action_commands)
                elif event.key == pg.K_RIGHT:
                    action_selected_index = (action_selected_index + 1) % len(action_commands)
                elif event.key == pg.K_RETURN:
                    print(f"{action_commands[action_selected_index]} を選択しました！")
                    if action_commands[action_selected_index] == "はなす":
                        in_action_command = 2
                    elif action_commands[action_selected_index] == "ぶんせき":
                        in_action_command = 2
                    else:
                        in_action_command = 2
                elif event.key == pg.K_ESCAPE:
                    in_action_command = 0

            else:
                if event.key == pg.K_RIGHT:
                    selected_index = (selected_index + 1) % len(commands)
                elif event.key == pg.K_LEFT:
                    selected_index = (selected_index - 1) % len(commands)
                elif event.key == pg.K_RETURN:
                    if commands[selected_index] == "アクション":
                        in_action_command = 1
                        action_selected_index = 0  # 初期化

    screen.fill(BLACK)
    # if in_action_command == 2:
        # _draw_message_box(screen,screen,"")
        



    if in_action_command ==1:
        draw_action_menu()
    else:
        boxes = get_command_boxes()
        for i, rect in enumerate(boxes):
            color = YELLOW if i == selected_index else WHITE
            pg.draw.rect(screen, color, rect, 4)

            text = font.render(commands[i], True, WHITE)
            text_x = rect.x + (rect.width - text.get_width()) // 2
            text_y = rect.y + (rect.height - text.get_height()) // 2
            screen.blit(text, (text_x, text_y))

        # HPバー
        center_x = (boxes[1].centerx + boxes[2].centerx) // 2
        hp_bar_y = box_y + box_height + hp_bar_margin_top
        pg.draw.rect(screen, BLACK, (center_x - hp_bar_width // 2, hp_bar_y, hp_bar_width, hp_bar_height))
        hp_ratio = current_hp / max_hp
        pg.draw.rect(screen, YELLOW, (center_x - hp_bar_width // 2, hp_bar_y, int(hp_bar_width * hp_ratio), hp_bar_height))
        pg.draw.rect(screen, WHITE, (center_x - hp_bar_width // 2, hp_bar_y, hp_bar_width, hp_bar_height), 2)

        hp_text = font.render(f"{current_hp} / {max_hp}", True, WHITE)
        text_x = center_x - hp_bar_width // 2 + hp_bar_width + 10
        text_y = hp_bar_y + (hp_bar_height - hp_text.get_height()) // 2
        screen.blit(hp_text, (text_x, text_y))

    pg.display.update()
    clock.tick(60)
