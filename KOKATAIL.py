import os
import pygame as pg
import sys
from typing import List
import random
import time

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pg.init()  # pygameの初期化は必ず最初に行う

# 初期化後にフォント作成
WIDTH, HEIGHT = 1920, 1080
font = pg.font.SysFont("meiryo", 50)
small_font = pg.font.SysFont("meiryo", 36)

class TurnManager():
    def __init__(self):
        self.num = 0
        self.turn = "player"

    def turn_change(self):
        if self.turn == "player":
            self.turn = "enemy"
        elif self.turn == "enemy":
            self.turn = "player"
            self.num += 1


class Player():

    def __init__(self, HP:int, ATK:int):
        self.former_hp = HP
        self.hp = self.former_hp
        self.former_atk = ATK
        self.atk = self.former_atk


class Escape():
    """
    逃げるコマンドの判定クラス
    20%の確率で成功（True）、それ以外は失敗（False）を返す
    逃げた回数や失敗回数も記録
    """
    def __init__(self):
        """
        Escapeオブジェクトを初期化する。
        success_count: 成功した逃走回数
        fail_count: 失敗した逃走回数
        last_result: 最後の逃走結果 (True=成功, False=失敗, None=未試行)
        """

        self.success_count = 0
        self.fail_count = 0
        self.last_result = None  # True:成功, False:失敗

    def try_escape(self) -> bool:
        """
        逃走を試みる。
        成功確率は10%。
        Returns:
            bool: 逃走成功ならTrue、失敗ならFalse
        """
        result = random.random() < 0.2 
        self.last_result = result
        if result:
            self.success_count += 1
        else:
            self.fail_count += 1
        return result
    
    def show_result(self, screen:pg.surface, font:pg.font.Font) -> None:
        """
        最後の逃走結果を画面中央に表示し、少し待機する。

        Args:
            screen (pg.Surface): 描画先のSurface
            font (pg.font.Font): 文字描画に使用するフォント
        """

        if self.last_result is None:
            return
        screen.fill(BLACK)
        if self.last_result:
            msg = font.render("逃げた", True, (0, 255, 0))
            msg_rect = msg.get_rect()
            msg_rect.center = (WIDTH // 2, HEIGHT // 2)
            screen.blit(msg, msg_rect)
            pg.display.update()
            time.sleep(2)
        else:
            msg = font.render("逃げれなかった", True, (255, 0, 0))

            msg_rect = msg.get_rect()
            msg_rect.center = (WIDTH // 2, HEIGHT // 2)
            screen.blit(msg, msg_rect)
            pg.display.update()
            time.sleep(1)

class CommandBoxManager:
    """
    コマンドボックスの位置計算と描画管理クラス
    """
    
    commands = ["こうげき", "アクション", "アイテム", "にげる"]
    box_width = 265
    box_height = 80
    box_y = HEIGHT - 300
    hp_bar_width = 160
    hp_bar_height = 20
    hp_bar_margin_top = 10
    hp_bar_y = box_y + box_height + hp_bar_margin_top

    def __init__(self, player:Player, font: pg.font.Font,) -> None: #enemy:Enemy
        self.commands = __class__.commands
        self.box_width = __class__.box_width
        self.box_height = __class__.box_height
        self.box_y = __class__.box_y
        self.font = font
        self.former_hp = player.former_hp
        self.hp = player.hp

    def get_command_boxes(self) -> List[pg.Rect]:
        """
        コマンドボックスのpygame.Rectリストを生成する。
        """
        spacing = 40
        total_width = len(self.commands) * __class__.box_width + (len(self.commands) - 1) * spacing
        start_x = (WIDTH - total_width) // 2
        boxes = []
        for i in range(len(self.commands)):
            x = start_x + i * (__class__.box_width + spacing)
            boxes.append(pg.Rect(x, __class__.box_y, __class__.box_width, __class__.box_height))
        return boxes

    def draw(self, screen: pg.Surface, selected_index: int) -> None:
        """
        コマンドボックスを画面に描画する。選択中のコマンドは黄色で強調。
        """
        self.boxes = self.get_command_boxes()
        for i, rect in enumerate(self.boxes):
            color = YELLOW if i == selected_index else WHITE
            pg.draw.rect(screen, color, rect, 4)

            self.text = self.font.render(self.commands[i], True, WHITE)
            self.text_x = rect.x + (rect.width - self.text.get_width()) // 2
            self.text_y = rect.y + (rect.height - self.text.get_height()) // 2
            screen.blit(self.text, (self.text_x, self.text_y))

    def update(self, screen:pg.Surface):
        self.boxes = self.get_command_boxes()
        self.center_x = (self.boxes[1].centerx + self.boxes[2].centerx) // 2
        # HPバー背景（黒）
        pg.draw.rect(screen, BLACK, (self.center_x - __class__.hp_bar_width // 2, __class__.hp_bar_y, __class__.hp_bar_width, __class__.hp_bar_height))
        # HPバー黄色部分（HPの割合に応じた幅）
        self.hp_ratio = self.hp / self.former_hp
        pg.draw.rect(screen, YELLOW, (self.center_x - __class__.hp_bar_width // 2, __class__.hp_bar_y, int(__class__.hp_bar_width * self.hp_ratio), __class__.hp_bar_height))
        # HPバー枠（白）
        pg.draw.rect(screen, WHITE, (self.center_x - __class__.hp_bar_width // 2, __class__.hp_bar_y, __class__.hp_bar_width, __class__.hp_bar_height), 2)

        # HPバー横にHP数値表示
        self.hp_text = font.render(f"{self.hp} / {self.former_hp}", True, WHITE)
        self.text_x = self.center_x - __class__.hp_bar_width // 2 + __class__.hp_bar_width + 10
        self.text_y = self.hp_bar_y + (__class__.hp_bar_height - self.hp_text.get_height()) // 2
        screen.blit(self.hp_text, (self.text_x, self.text_y))


def main():
    """
    メインゲームループ
    """
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("コマンド選択画面 + HPバー + HP表示")
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)

    player = Player(50, 5)
    # enemy = Enemy(50,5)
    escape = Escape()
    command_manager = CommandBoxManager(player, font)#enemy消した
    selected_index = 0

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT:
                    selected_index = (selected_index + 1) % len(CommandBoxManager.commands)
                elif event.key == pg.K_LEFT:
                    selected_index = (selected_index - 1) % len(CommandBoxManager.commands)
                elif event.key == pg.K_RETURN:
                    if CommandBoxManager.commands[selected_index] == "にげる":
                        if escape.try_escape():
                            escape.show_result(screen, font)
                            pg.quit()
                            sys.exit()
                        else:
                            escape.show_result(screen, font)



        screen.fill(BLACK)
        command_manager.draw(screen, selected_index)
        #enemy.update(screen)
        command_manager.update(screen)
        pg.display.update()
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()