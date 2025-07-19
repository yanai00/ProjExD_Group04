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

    def __init__(self, player:Player, font: pg.font.Font,) -> None:
        self.commands = __class__.commands
        self.box_width = __class__.box_width
        self.box_height = __class__.box_height
        self.box_y = __class__.box_y
        self.font = font
        self.former_hp = player.former_hp
        self.hp = player.hp

    def get_command_boxes(self) -> List[pg.Rect]:
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


class Action():
    commands = ["はなす", "分析", "黙る"]
    command_result = ["話しかけたが返事はなかった",
                      "AT:3 DF:5  油断しなければ勝てるだろう",
                      "静寂に包まれた"]
    def __init__(self, command:CommandBoxManager, turn:TurnManager, font:pg.font.Font):
        self.command = command
        self.index = command.selected_index
        self.command_result = __class__.command_result
        self.state = False
        self.action_num = 0
        self.turn = turn
        self.font = font
        self.box_width = 1180
        self.box_height = 280
        self.start_x = (WIDTH - self.box_width) // 2
        self.start_y = self.command.box_y - self.box_height - 20
        self.commands = __class__.commands
        self.text_x = self.start_x + 30
        self.text_y = self.start_y + 30
        self.tmr = 0

    def draw_box(self, screen:pg.Surface):
        pg.draw.rect(screen, WHITE, (self.start_x, self.start_y, self.box_width, self.box_height), 4)

    def select_command(self, screen:pg.Surface):
        if self.turn.turn == "player" and self.state == True:
            for i in range(len(self.commands)):
                self.text = self.font.render(self.commands[i], True, WHITE)
                screen.blit(self.text, (self.text_x, self.text_y + i * 46))
                if i == self.action_num:
                    self.text = self.font.render(self.commands[i], True, YELLOW)
                    screen.blit(self.text, (self.text_x, self.text_y + i * 46))

def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("コマンド選択画面 + HPバー + HP表示")
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)

    player = Player(50, 5)
    turn = TurnManager()
    command_manager = CommandBoxManager(player, font)
    action = Action(command_manager, turn, small_font)
    selected_index = 0
    tmr = 0
    com_cnt = None

    while True:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT and action.state == False:
                    selected_index = (selected_index - 1) % len(CommandBoxManager.commands)
                elif event.key == pg.K_RIGHT and action.state == False:
                    selected_index = (selected_index + 1) % len(CommandBoxManager.commands)
                elif event.key == pg.K_UP:
                    if action.state == True:
                        if action.action_num == 0:
                            action.action_num = len(action.commands) - 1
                        else:
                            action.action_num -= 1
                elif event.key == pg.K_DOWN:
                    if action.state == True:
                        if action.action_num == len(action.commands) - 1:
                            action.action_num = 0
                        else:
                            action.action_num += 1
                elif event.key == pg.K_RETURN:
                    if selected_index == 1 and action.state == False:
                        action.state = True
                    elif action.state == True:
                        com_cnt = tmr
                elif event.key == pg.K_q:
                    return
                


        screen.fill(BLACK)

        
        if com_cnt != None and tmr - com_cnt >= 10:
            action.state = False
            action.text = action.font.render(action.command_result[action.action_num], True, WHITE)
            screen.blit(action.text, (action.text_x, action.text_y))
            
        if com_cnt != None and tmr - com_cnt >= 120:
            com_cnt = None

        if turn.turn == "player":
            action.draw_box(screen)
            action.select_command(screen)
        command_manager.draw(screen,selected_index)
        command_manager.update(screen)
        pg.display.update()
        clock.tick(60)
        tmr += 1

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
