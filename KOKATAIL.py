import os
import pygame as pg
import sys
from typing import List
# 初期設定/main


# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pg.init()

# フォント
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

class CommandBoxManager:
    """
    コマンドボックスの位置計算と描画管理クラス
    """
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
    hp_bar_y = box_y + box_height + hp_bar_margin_top
    # HP値
    max_hp = 50
    current_hp = 50

    def __init__(self, player:Player, enemy:Enemy, font: pg.font.Font,) -> None:
            self.commands = __class__.commands
            self.box_width = __class__.box_width
            self.box_height = __class__.box_height
            self.box_y = __class__.box_y
            self.font = font
            self.former_hp = player.former_hp
            self.hp = player.hp

    def get_command_boxes(self) -> List[pg.Rect]:
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

def _draw_message_box(self, screen, text):
    # 1行のメッセージを持つテキストボックスを描画する
    box_rect = pg.Rect(400, HEIGHT - 400, WIDTH - 800, 150)
    pg.draw.rect(screen, BLACK, box_rect)
    pg.draw.rect(screen, WHITE, box_rect, 4)
    surf = small_font.render(text, True, WHITE)
    screen.blit(surf, (box_rect.x + 40, box_rect.y + 30))

class main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("コマンド選択画面 + HPバー + HP表示")
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)

    player = Player(50, 5)
    enemy = Enemy(50,5)
    command_manager = CommandBoxManager(player, enemy, font)
    selected_index = 0

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                

            elif event.type == pg.KEYDOWN:
                if in_action_command == 1:
                    if event.key == pg.K_LEFT:
                        action_selected_index = (action_selected_index - 1) % len(CommandBoxManager.action_commands)
                    elif event.key == pg.K_RIGHT:
                        action_selected_index = (action_selected_index + 1) % len(CommandBoxManager.action_commands)
                    elif event.key == pg.K_RETURN:
                        print(f"{CommandBoxManager.action_commands[action_selected_index]} を選択しました！")
                        in_action_command = 2
                    elif event.key == pg.K_ESCAPE:
                        in_action_command = 0

                else:
                    if event.key == pg.K_RIGHT:
                        selected_index = (selected_index + 1) % len(CommandBoxManager.commands)
                    elif event.key == pg.K_LEFT:
                        selected_index = (selected_index - 1) % len(CommandBoxManager.commands)
                    elif event.key == pg.K_RETURN:
                        if CommandBoxManager.commands[selected_index] == "アクション":
                            in_action_command = 1
                            action_selected_index = 0  # 初期化

        if in_action_command == 2:
            if CommandBoxManager.action_commands[action_selected_index] == "はなす":
                _draw_message_box(screen,screen,"話しかけたが返事はなかった")
            elif CommandBoxManager.action_commands[action_selected_index] == "ぶんせき":
                _draw_message_box(screen,screen,"AT:3 DF:5  油断しなければ勝てるだろう") 
            else:
                _draw_message_box(screen,screen,"静寂に包まれた")
            if event.key == pg.K_RETURN:
                in_action_command == 0



        if in_action_command ==1:
            CommandBoxManager.draw_action_menu()
        elif in_action_command == 0:
            boxes = CommandBoxManager.get_command_boxes()
            for i, rect in enumerate(boxes):
                color = YELLOW if i == selected_index else WHITE
                pg.draw.rect(screen, color, rect, 4)

                text = font.render(CommandBoxManager.commands[i], True, WHITE)
                text_x = rect.x + (rect.width - text.get_width()) // 2
                text_y = rect.y + (rect.height - text.get_height()) // 2
                screen.blit(text, (text_x, text_y))

            # HPバー
            center_x = (boxes[1].centerx + boxes[2].centerx) // 2
            hp_bar_y = CommandBoxManager.box_y + CommandBoxManager.box_height + CommandBoxManager.hp_bar_margin_top
            pg.draw.rect(screen, BLACK, (center_x - CommandBoxManager.hp_bar_width // 2, hp_bar_y, CommandBoxManager.hp_bar_width, CommandBoxManager.hp_bar_height))
            hp_ratio = CommandBoxManager.current_hp / CommandBoxManager.max_hp
            pg.draw.rect(screen, YELLOW, (center_x - CommandBoxManager.hp_bar_width // 2, hp_bar_y, int(CommandBoxManager.hp_bar_width * hp_ratio), CommandBoxManager.hp_bar_height))
            pg.draw.rect(screen, WHITE, (center_x - CommandBoxManager.hp_bar_width // 2, hp_bar_y, CommandBoxManager.hp_bar_width, CommandBoxManager.hp_bar_height), 2)

            hp_text = font.render(f"{CommandBoxManager.current_hp} / {CommandBoxManager.max_hp}", True, WHITE)
            text_x = center_x - CommandBoxManager.hp_bar_width // 2 + CommandBoxManager.hp_bar_width + 10
            text_y = hp_bar_y + (CommandBoxManager.hp_bar_height - hp_text.get_height()) // 2
            screen.blit(hp_text, (text_x, text_y))

        screen.fill(BLACK)
        command_manager.draw(screen,selected_index)
        enemy.update(screen)
        command_manager.update(screen)
        pg.display.update()
        clock.tick(60)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
