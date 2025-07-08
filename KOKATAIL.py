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
    current_hp = 50

    commands = ["こうげき", "アクション", "アイテム", "にげる"]
    selected_index = 0

    box_width = 265
    box_height = 80
    box_y = HEIGHT - 300

    hp_bar_width = 160
    hp_bar_height = 20
    hp_bar_margin_top = 10

    command_manager = CommandBoxManager(commands, box_width, box_height, box_y, font)

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT:
                    selected_index = (selected_index + 1) % len(commands)
                elif event.key == pg.K_LEFT:
                    selected_index = (selected_index - 1) % len(commands)
                elif event.key == pg.K_RETURN:
                    # アイテムメニューなどはなし。ここに処理を書きたい場合は追記
                    pass

        screen.fill(BLACK)

        command_manager.draw(screen, selected_index)

        boxes = command_manager.get_command_boxes()
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

        pg.display.update()
        clock.tick(60)

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    WIDTH, HEIGHT = 1920, 1080

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)

    main()
