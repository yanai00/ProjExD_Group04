import os 
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import pygame as pg
import sys

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
small_font = pg.font.SysFont("meiryo", 36)

# コマンド
commands = ["こうげき", "アクション", "アイテム", "にげる"]
selected_index = 0

# コマンドボックスサイズ
box_width = 265
box_height = 80
box_y = HEIGHT - 300

# HPバーサイズ
hp_bar_width = 160
hp_bar_height = 20
hp_bar_margin_top = 10  # コマンドボックスとHPバーの間の隙間

# HP値
max_hp = 50
current_hp = 50  # 0～max_hpで変更可能

# アイテム関連
items = ["こうかとんのから揚げ", "こうかとんのつくね", "こうかとんのぼんじり","こうかとんのもも串","こうかとんの皮串","こうかとんだったもの"]
item_menu_open = False
item_selected = 0

def draw_item_menu():
    menu_width = 800
    menu_height = 400
    menu_x = (WIDTH - menu_width) // 2
    menu_y = (HEIGHT - menu_height) // 2
    menu_rect = pg.Rect(menu_x, menu_y, menu_width, menu_height)

    # 背景と枠
    pg.draw.rect(screen, BLACK, menu_rect)
    pg.draw.rect(screen, WHITE, menu_rect, 3)

    # タイトル
    title = font.render("アイテム", True, WHITE)
    screen.blit(title, (menu_x + 20, menu_y + 10))

    # アイテムリスト表示
    for i, item in enumerate(items):
        color = YELLOW if i == item_selected else WHITE
        item_text = small_font.render(f"- {item}", True, color)
        screen.blit(item_text, (menu_x + 40, menu_y + 70 + i * 50))

def get_command_boxes():
    spacing = 40
    total_width = len(commands) * box_width + (len(commands) - 1) * spacing
    start_x = (WIDTH - total_width) // 2
    boxes = []
    for i in range(len(commands)):
        x = start_x + i * (box_width + spacing)
        boxes.append(pg.Rect(x, box_y, box_width, box_height))
    return boxes

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if item_menu_open:
                if event.key == pg.K_ESCAPE:
                    item_menu_open = False
                elif event.key == pg.K_DOWN:
                    item_selected = (item_selected + 1) % len(items)
                elif event.key == pg.K_UP:
                    item_selected = (item_selected - 1) % len(items)
                elif event.key == pg.K_RETURN:
                    # アイテム使用処理（HP +10、最大50）
                    if current_hp < max_hp:
                        current_hp += 10
                        if current_hp > max_hp:
                            current_hp = max_hp
                    item_menu_open = False
            else:
                if event.key == pg.K_RIGHT:
                    selected_index = (selected_index + 1) % len(commands)
                elif event.key == pg.K_LEFT:
                    selected_index = (selected_index - 1) % len(commands)
                elif event.key == pg.K_RETURN:
                    if commands[selected_index] == "アイテム":
                        item_menu_open = True
                        item_selected = 0

    screen.fill(BLACK)

    boxes = get_command_boxes()

    # コマンドボックス描画
    for i, rect in enumerate(boxes):
        color = YELLOW if i == selected_index else WHITE
        pg.draw.rect(screen, color, rect, 4)

        text = font.render(commands[i], True, WHITE)
        text_x = rect.x + (rect.width - text.get_width()) // 2
        text_y = rect.y + (rect.height - text.get_height()) // 2
        screen.blit(text, (text_x, text_y))

    # 真ん中2つのコマンドボックスの中心の真ん中を計算
    center_x = (boxes[1].centerx + boxes[2].centerx) // 2
    hp_bar_y = box_y + box_height + hp_bar_margin_top

    # HPバー背景（黒）
    pg.draw.rect(screen, BLACK, (center_x - hp_bar_width // 2, hp_bar_y, hp_bar_width, hp_bar_height))
    # HPバー黄色部分（HPの割合に応じた幅）
    hp_ratio = current_hp / max_hp
    pg.draw.rect(screen, YELLOW, (center_x - hp_bar_width // 2, hp_bar_y, int(hp_bar_width * hp_ratio), hp_bar_height))
    # HPバー枠（白）
    pg.draw.rect(screen, WHITE, (center_x - hp_bar_width // 2, hp_bar_y, hp_bar_width, hp_bar_height), 2)

    # HPバー横にHP数値表示
    hp_text = font.render(f"{current_hp} / {max_hp}", True, WHITE)
    text_x = center_x - hp_bar_width // 2 + hp_bar_width + 10
    text_y = hp_bar_y + (hp_bar_height - hp_text.get_height()) // 2
    screen.blit(hp_text, (text_x, text_y))

    # アイテムメニュー描画（開いているとき）
    if item_menu_open:
        draw_item_menu()

    pg.display.update()
    clock.tick(60)
