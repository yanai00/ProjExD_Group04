import pygame as pg
import sys

# 初期設定
WIDTH, HEIGHT = 1920, 1080
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("コマンド選択画面")
clock = pg.time.Clock()
pg.mouse.set_visible(False)

# 色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# フォント
font = pg.font.SysFont("meiryo", 50)

# コマンド設定
commands = ["こうげき", "アクション", "アイテム", "にげる"]
selected_index = 0

# コマンドボックス（全体はもうなくして各コマンド個別に枠を表示する形に）
box_width = 250
box_height = 80
box_y = HEIGHT - 250  # 画面下から少し上に

# コマンドごとのx座標
def get_command_boxes():
    spacing = 40  # コマンドボックス間の隙間
    total_width = len(commands) * box_width + (len(commands) - 1) * spacing
    start_x = (WIDTH - total_width) // 2
    boxes = []
    for i in range(len(commands)):
        x = start_x + i * (box_width + spacing)
        boxes.append(pg.Rect(x, box_y, box_width, box_height))
    return boxes

# メインループ
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT:
                selected_index = (selected_index + 1) % len(commands)
            elif event.key == pg.K_LEFT:
                selected_index = (selected_index - 1) % len(commands)

    screen.fill(BLACK)

    boxes = get_command_boxes()
    for i, rect in enumerate(boxes):
        # 選択中は黄色枠、それ以外は白枠
        color = YELLOW if i == selected_index else WHITE
        pg.draw.rect(screen, color, rect, 4)

        # テキスト描画（中央寄せ）
        text = font.render(commands[i], True, WHITE)
        text_x = rect.x + (rect.width - text.get_width()) // 2
        text_y = rect.y + (rect.height - text.get_height()) // 2
        screen.blit(text, (text_x, text_y))

    pg.display.update()
    clock.tick(60)
