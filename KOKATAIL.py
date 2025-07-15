import os
import pygame as pg
import sys
from typing import List

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pg.init()  # pygameの初期化は必ず最初に行う

# 初期化後にフォント作成
font = pg.font.SysFont("meiryo", 50)
small_font = pg.font.SysFont("meiryo", 36)


class CommandBoxManager:
    """
    コマンドボックスの位置計算と描画管理クラス
    """

    def __init__(
        self,
        commands: List[str],
        box_width: int,
        box_height: int,
        box_y: int,
        font: pg.font.Font,
    ) -> None:
        self.commands = commands
        self.box_width = box_width
        self.box_height = box_height
        self.box_y = box_y
        self.font = font

    def get_command_boxes(self) -> List[pg.Rect]:
        """
        コマンドボックスのpygame.Rectリストを生成する。
        """
        spacing = 40
        total_width = len(self.commands) * self.box_width + (len(self.commands) - 1) * spacing
        start_x = (WIDTH - total_width) // 2
        boxes = []
        for i in range(len(self.commands)):
            x = start_x + i * (self.box_width + spacing)
            boxes.append(pg.Rect(x, self.box_y, self.box_width, self.box_height))
        return boxes

    def draw(self, screen: pg.Surface, selected_index: int) -> None:
        """
        コマンドボックスを画面に描画する。選択中のコマンドは黄色で強調。
        """
        boxes = self.get_command_boxes()
        for i, rect in enumerate(boxes):
            color = YELLOW if i == selected_index else WHITE
            pg.draw.rect(screen, color, rect, 4)

            text = self.font.render(self.commands[i], True, WHITE)
            text_x = rect.x + (rect.width - text.get_width()) // 2
            text_y = rect.y + (rect.height - text.get_height()) // 2
            screen.blit(text, (text_x, text_y))


class ItemMenu:
    """
    アイテムメニューの描画と操作管理クラス
    """

    def __init__(self, items: List[str], font: pg.font.Font, small_font: pg.font.Font) -> None:
        self.items = items
        self.font = font
        self.small_font = small_font
        self.selected_index = 0
        self.is_open = False

        self.menu_width = 800
        self.menu_height = 400
        self.menu_x = (WIDTH - self.menu_width) // 2
        self.menu_y = (HEIGHT - self.menu_height) // 2
        self.menu_rect = pg.Rect(self.menu_x, self.menu_y, self.menu_width, self.menu_height)

    def draw(self, screen: pg.Surface) -> None:
        """
        アイテムメニューを画面に描画する。
        """
        # 背景と枠
        pg.draw.rect(screen, BLACK, self.menu_rect)
        pg.draw.rect(screen, WHITE, self.menu_rect, 3)

        # タイトル
        title = self.font.render("アイテム", True, WHITE)
        screen.blit(title, (self.menu_x + 20, self.menu_y + 10))

        # アイテムリスト表示
        for i, item in enumerate(self.items):
            color = YELLOW if i == self.selected_index else WHITE
            item_text = self.small_font.render(f"- {item}", True, color)
            screen.blit(item_text, (self.menu_x + 40, self.menu_y + 70 + i * 50))


def main() -> None:
    """
    メインゲームループ
    """
    global screen, clock

    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("コマンド選択画面 + HPバー + HP表示")
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)

    max_hp = 50
    current_hp = 1

    commands = ["こうげき", "アクション", "アイテム", "にげる"]
    selected_index = 0

    box_width = 265
    box_height = 80
    box_y = HEIGHT - 300

    hp_bar_width = 160
    hp_bar_height = 20
    hp_bar_margin_top = 10

    command_manager = CommandBoxManager(commands, box_width, box_height, box_y, font)
    item_menu = ItemMenu(items, font, small_font)

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.KEYDOWN:
                if item_menu.is_open:
                    if event.key == pg.K_ESCAPE:
                        item_menu.is_open = False
                    elif event.key == pg.K_DOWN:
                        item_menu.selected_index = (item_menu.selected_index + 1) % len(item_menu.items)
                    elif event.key == pg.K_UP:
                        item_menu.selected_index = (item_menu.selected_index - 1) % len(item_menu.items)
                    elif event.key == pg.K_RETURN:
                        if current_hp < max_hp:
                            current_hp += 10
                            if current_hp > max_hp:
                                current_hp = max_hp
                        item_menu.is_open = False
                else:
                    if event.key == pg.K_RIGHT:
                        selected_index = (selected_index + 1) % len(commands)
                    elif event.key == pg.K_LEFT:
                        selected_index = (selected_index - 1) % len(commands)
                    elif event.key == pg.K_RETURN:
                        if commands[selected_index] == "アイテム":
                            item_menu.is_open = True
                            item_menu.selected_index = 0

        screen.fill(BLACK)

        command_manager.draw(screen, selected_index)

        boxes = command_manager.get_command_boxes()
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

        if item_menu.is_open:
            item_menu.draw(screen)

        pg.display.update()
        clock.tick(60)

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    WIDTH, HEIGHT = 1920, 1080

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)

    items = [
        "こうかとんのから揚げ",
        "こうかとんのつくね",
        "こうかとんのぼんじり",
        "こうかとんのもも串",
        "こうかとんの皮串",
        "こうかとんだったもの",
    ]

    main()
