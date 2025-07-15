import os
import pygame as pg
import sys
from typing import List
import random
import time


# --- 初期設定 ---
# Pygameライブラリの初期化
pg.init()

# 画面のサイズを設定
WIDTH, HEIGHT = 1920, 1080
screen = pg.display.set_mode((WIDTH, HEIGHT))

# ウィンドウのタイトルを設定
pg.display.set_caption("コマンド選択画面 + HPバー + HP表示 + ターン管理")

# 時間を管理するためのClockオブジェクト
clock = pg.time.Clock()

# マウスカーソルを非表示にする
pg.mouse.set_visible(False)

# --- 定数定義 ---
# 色の定義 (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREY = (150, 150, 150)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pg.init()  # pygameの初期化は必ず最初に行う

# 初期化後にフォント作成
WIDTH, HEIGHT = 1920, 1080
font = pg.font.SysFont("meiryo", 50)
small_font = pg.font.SysFont("meiryo", 36)

class TurnManager:
    """
    プレイヤーと敵のターンと攻撃処理を管理するステートマシン
    """
    def __init__(self, player, enemy, command_manager):
        self.state = "SELECTING"
        self.selected_index = 0
        self.target_index = 0
        self.display_text = ""
        self.player = player
        self.enemy = enemy
        self.cm = command_manager

    def handle_event(self, event):
        if event.type != pg.KEYDOWN:
            return

        key = event.key
        if key == pg.K_RETURN:
            if self.state == "SELECTING":
                if self.cm.commands[self.selected_index] == "こうげき":
                    self.state = "TARGET_SELECT_IN_BOX"
            elif self.state == "TARGET_SELECT_IN_BOX":
                # 攻撃実行
                self.enemy.take_damage(self.player.atk)
                self.display_text = f"＊{self.enemy.__class__.__name__}に{self.player.atk}ダメージ！"
                self.state = "ATTACK_MESSAGE"
            elif self.state == "ATTACK_MESSAGE":
                self.display_text = f"＊{self.enemy.__class__.__name__}のターン。"
                self.state = "ENEMY_TURN"
            elif self.state == "ENEMY_TURN":
                # 敵の攻撃
                self.player.hp = max(0, self.player.hp - self.enemy.atk)
                self.state = "SELECTING"

        # カーソル移動
        if self.state == "SELECTING":
            if key == pg.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.cm.commands)
            elif key == pg.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(self.cm.commands)
        elif self.state == "TARGET_SELECT_IN_BOX":
            # 敵が一体なら上下不要。キャンセルだけ。
            if key == pg.K_x:
                self.state = "SELECTING"

    def draw(self, screen):
        # HPバーは常に描画
        self.cm.draw_hp_bar(screen)

        if self.state == "SELECTING":
            self.cm.draw(screen, self.selected_index)
        elif self.state == "TARGET_SELECT_IN_BOX":
            self._draw_selection_box(screen, "だれを こうげきする？", [self.enemy.__class__.__name__], self.target_index)
        else:  # ATTACK_MESSAGE or ENEMY_TURN
            self._draw_message_box(screen, self.display_text)

    def _draw_selection_box(self, screen, title, items, sel):
        box = pg.Rect(400, HEIGHT-550, WIDTH-800, 150)
        pg.draw.rect(screen, BLACK, box)
        pg.draw.rect(screen, WHITE, box, 4)
        t = small_font.render(title, True, WHITE)
        screen.blit(t, (box.x+20, box.y+5))
        for i, it in enumerate(items):
            color = YELLOW if i == sel else WHITE
            s = small_font.render(f"＊ {it}", True, color)
            screen.blit(s, (box.x+40, box.y+45+i*45))

    def _draw_message_box(self, screen, text):
        box = pg.Rect(400, HEIGHT-550, WIDTH-800, 150)
        pg.draw.rect(screen, BLACK, box)
        pg.draw.rect(screen, WHITE, box, 4)
        s = small_font.render(text, True, WHITE)
        screen.blit(s, (box.x+40, box.y+30))

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
    """
    プレイヤーのHPと攻撃力を管理するクラス
    """
    def __init__(self, HP: int, ATK: int):
        self.former_hp = HP
        self.hp = self.former_hp
        self.former_atk = ATK
        self.atk = self.former_atk

    def attack(self, enemy):
        enemy.take_damage(self.atk)


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
    def __init__(self, player:Player, turn:TurnManager, font: pg.font.Font) -> None:
        self.box_width = 265
        self.box_height = 80
        self.box_y = HEIGHT - 300
        self.hp_bar_width = 160
        self.hp_bar_height = 20
        self.hp_bar_margin_top = 10
        self.hp_bar_y = self.box_y + self.box_height + self.hp_bar_margin_top + 15
        self.commands = __class__.commands
        self.font = font
        self.former_hp = player.former_hp
        self.hp = player.hp
        self.turn = turn

    def get_command_boxes(self) -> List[pg.Rect]:
        """
        コマンドボックスのpygame.Rectリストを生成する。
        """
        self.spacing = 40
        self.total_width = len(self.commands) * self.box_width + (len(self.commands) - 1) * self.spacing
        self.start_x = (WIDTH - self.total_width) // 2
        self.boxes = []
        for i in range(len(self.commands)):
            x = self.start_x + i * (self.box_width + self.spacing)
            self.boxes.append(pg.Rect(x, self.box_y, self.box_width, self.box_height))
        return self.boxes

    def draw(self, screen: pg.Surface, selected_index: int) -> None:
        """
        コマンドボックスを画面に描画する。選択中のコマンドは黄色で強調。
        """
        self.boxes = self.get_command_boxes()
        if self.turn.turn == "player":
            for i, rect in enumerate(self.boxes):
                self.color = YELLOW if i == selected_index else WHITE
                pg.draw.rect(screen, self.color, rect, 4)

                self.command_text = self.font.render(self.commands[i], True, WHITE)
                self.command_text_x = rect.x + (rect.width - self.command_text.get_width()) // 2
                self.command_text_y = rect.y + (rect.height - self.command_text.get_height()) // 2
                screen.blit(self.command_text, (self.command_text_x, self.command_text_y))

    def update(self, screen:pg.Surface):
        self.boxes = self.get_command_boxes()
        self.center_x = (self.boxes[1].centerx + self.boxes[2].centerx) // 2
        if self.hp <= 0:
            self.hp = 0
        self.hp_ratio = self.hp / self.former_hp
        self.hp_text = font.render(f"{self.hp} / {self.former_hp}", True, WHITE)
        self.command_text_x = self.center_x - self.hp_bar_width // 2 + self.hp_bar_width + 10
        self.command_text_y = self.hp_bar_y + 5 + (self.hp_bar_height - self.hp_text.get_height()) // 2
        # HPバー背景（黒）
        pg.draw.rect(screen, BLACK, (self.center_x - self.hp_bar_width // 2, self.hp_bar_y, self.hp_bar_width, self.hp_bar_height))
        # HPバー黄色部分（HPの割合に応じた幅）
        pg.draw.rect(screen, YELLOW, (self.center_x - self.hp_bar_width // 2, self.hp_bar_y, int(self.hp_bar_width * self.hp_ratio), self.hp_bar_height))
        # HPバー枠（白）
        pg.draw.rect(screen, WHITE, (self.center_x - self.hp_bar_width // 2, self.hp_bar_y, self.hp_bar_width, self.hp_bar_height), 2)
        # HPバー横にHP数値表示
        screen.blit(self.hp_text, (self.command_text_x, self.command_text_y))

    def draw_hp_bar(self, screen: pg.Surface):
        boxes = self.get_command_boxes()
        cx = (boxes[1].centerx + boxes[2].centerx)//2
        # 背景
        pg.draw.rect(screen, BLACK, (cx - self.hp_bar_width//2, self.hp_bar_y, self.hp_bar_width, self.hp_bar_height))
        # 黄色部分
        ratio = self.player.hp / self.player.former_hp
        pg.draw.rect(screen, YELLOW, (cx - self.hp_bar_width//2, self.hp_bar_y, int(self.hp_bar_width*ratio), self.hp_bar_height))
        # 枠
        pg.draw.rect(screen, WHITE, (cx - self.hp_bar_width//2, self.hp_bar_y, self.hp_bar_width, self.hp_bar_height), 2)
        # 数値
        txt = font.render(f"{self.player.hp} / {self.player.former_hp}", True, WHITE)
        screen.blit(txt, (cx - self.hp_bar_width//2 + self.hp_bar_width + 10,
                          self.hp_bar_y + (self.hp_bar_height - txt.get_height())//2))

class EnemyBoxManager():
    def __init__(self, player:Player, turn:TurnManager, command:CommandBoxManager, font: pg.font.Font):
        self.player = player
        self.turn = turn
        self.command = command
        self.font = font
        self.box_width = 1180
        self.box_height = 280
        self.enemybox_width = 280
        self.enemybox_height = 280
        self.start_x = (WIDTH - self.box_width) // 2
        self.start_y = self.command.box_y - (self.box_height + 20)
        self.comments_list = ["まずは練習だ",
                              "だんだん難しくなっていくぜ？",
                              "うまく避けろよ",
                              "どこまで耐えられるかな？",
                              "そろそろ本気だぜ？",
                              "まだいけるか？",
                              "そろそろ限界かな？",
                              "おまえ強いな",
                              "なんで生きてるの？",
                              "疲れたな",
                              "もはや怖いぞ？",
                              "もう疲れたよ",
                              "はよ〇ね",
                              "." * self.turn.num
                              ]
        self.comment = self.comments_list[0]  # 初期コメント
        self.death_comment = "\"GameOver\" だな"
        self.enemy_text = self.font.render(self.comment, True, WHITE)
        self.enemy_text_x = self.start_x + 30
        self.enemy_text_y = self.start_y + 30
        self.enemybox_x = (WIDTH - self.enemybox_width) // 2
        self.enemybox_y = self.command.box_y - (self.enemybox_height + 20)
        
    def drawbox(self, screen:pg.Surface):
        if self.turn.turn == "player":
            pg.draw.rect(screen, WHITE, (self.start_x, self.start_y, self.box_width, self.box_height), 4)
        elif self.turn.turn == "enemy":
            pg.draw.rect(screen, WHITE, (self.enemybox_x, self.enemybox_y, self.enemybox_width, self.enemybox_height), 4)
    
    def comments(self, screen: pg.Surface):
        if self.command.hp > 0:
            if self.turn.num < len(self.comments_list):
                self.comment = self.comments_list[self.turn.num]
            else:
                self.comment = self.comments_list[-1]
            self.enemy_text = self.font.render(self.comment, True, WHITE)
            screen.blit(self.enemy_text, (self.enemy_text_x, self.enemy_text_y))
        if self.command.hp == 0:
            self.comment = self.death_comment
            self.enemy_text = self.font.render(self.comment, True, WHITE)
            screen.blit(self.enemy_text, (self.enemy_text_x, self.enemy_text_y))


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


class Enemy():
    """
    敵に関するクラス
    """
    img0 = pg.image.load(f"photo/enemy1_bob_v2.gif")
    img = pg.transform.rotozoom(img0,0,0.3)
    def __init__(self, HP:int, ATK:int, command:CommandBoxManager, turn:TurnManager):
        self.hp = HP
        self.atk = ATK
        self.image = __class__.img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.centery = 300
        self.command = command
        self.turn = turn
        self.tmr = 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def update(self, screen: pg.Surface):
        self.tmr += 1
        if self.tmr >= 20 and self.command.hp > 0:
            if self.tmr % 80 == 20:
                self.rect.centerx += 20
                self.rect.centery += 10
            elif self.tmr % 80 == 40:
                self.rect.centerx -= 20
                self.rect.centery -= 10
            elif self.tmr % 80 == 60:
                self.rect.centerx -= 20
                self.rect.centery += 10
            elif self.tmr % 80 == 0:
                self.rect.centerx += 20
                self.rect.centery -= 10
        elif self.command.hp == 0:
            self.rect.centerx = WIDTH // 2
            self.rect.centery = 300
        screen.blit(self.image,self.rect)

class Heart():
    delta = {
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }
    
    def __init__(self, command:CommandBoxManager, enemy_box:EnemyBoxManager, turn:TurnManager):
        self.commannd = command
        self.box = enemy_box
        self.turn = turn
        self.image = pg.transform.rotozoom(pg.image.load(f"photo/heart.png"), 0, 0.05)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.box.enemybox_x + self.box.enemybox_width // 2
        self.rect.centery = self.box.enemybox_y + self.box.enemybox_height // 2
        self.speed = 6
        self.state = "alive"

    def update(self, key_lst:list[bool], screen: pg.Surface):
        sum_mv = [0, 0]
        if self.commannd.hp <= 0:
            self.state = "death"
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if self.state == "alive":
            self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
            if (self.rect.left < self.box.enemybox_x or self.rect.right > self.box.enemybox_x + self.box.enemybox_width) and (self.rect.top < self.box.enemybox_y or self.rect.bottom > self.box.enemybox_y + self.box.enemybox_height):
                self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
            if self.rect.left < self.box.enemybox_x or self.rect.right > self.box.enemybox_x + self.box.enemybox_width:
                self.rect.move_ip(-self.speed*sum_mv[0], 0)
            if self.rect.top < self.box.enemybox_y or self.rect.bottom > self.box.enemybox_y + self.box.enemybox_height:
                self.rect.move_ip(0, -self.speed*sum_mv[1])
        
        if self.turn.turn == "enemy":
            screen.blit(self.image, self.rect)
    
class Bomb():
    kk_imgs = [pg.image.load(f"photo/{i}.png") for i in range(10)]

    def __init__(self, enemy: Enemy, enemy_box: EnemyBoxManager, turn: TurnManager):
        self.enemy = enemy
        self.turn = turn
        self.box = enemy_box
        self.tmr = 0
        self.image = pg.transform.rotozoom(random.choice(__class__.kk_imgs), 0, 0.6)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(self.box.enemybox_x + 10, self.box.enemybox_x + self.box.enemybox_width - 10), self.box.enemybox_y - 40
        self.vx, self.vy = 0, 1
        self.interval = random.randint(0, 10)
        self.life = 600

    @classmethod
    def generate_bombs(cls, count: int, enemy:Enemy, box:EnemyBoxManager, turn:TurnManager) -> list:
        bombs = []
        base_interval = 0
        for _ in range(count):
            bomb = Bomb(enemy, box, turn)
            
            # ターン数に応じて最大インターバル値を短縮
            max_interval = max(20, 60 - turn.num * 5)  # 最大60 → 最小20秒まで
            interval = base_interval + random.randint(15, max_interval)
            
            bomb.interval = interval
            base_interval = interval
            bombs.append(bomb)
        return bombs

    def update(self, screen: pg.Surface):
        if self.turn.turn == "enemy":
            self.tmr += 1
            if self.tmr > self.interval:
                if self.life > 0:
                    screen.blit(self.image, self.rect)
                    self.rect.move_ip(self.vx, self.vy)
                    self.life -= 1

def draw_message_box(screen, text):
    box_rect = pg.Rect(400, HEIGHT - 550, WIDTH - 800, 150)
    pg.draw.rect(screen, BLACK, box_rect)
    pg.draw.rect(screen, WHITE, box_rect, 4)
    surf = small_font.render(text, True, WHITE)
    screen.blit(surf, (box_rect.x + 40, box_rect.y + 30))

def main():
    """
    メインゲームループ
    """
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("コマンド選択画面 + HPバー + HP表示")
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    turn = TurnManager()
    player = Player(50, 5)
    command_manager = CommandBoxManager(player, turn, font)
    enemy_manager = EnemyBoxManager(player, turn, command_manager, font)
    enemy = Enemy(50, 3, command_manager, turn)
    heart = Heart(command_manager, enemy_manager, turn)
    bombs_num = 15 + turn.num * 5
    bombs = Bomb.generate_bombs(bombs_num, enemy, enemy_manager, turn)
    selected_index = 0
    show_comment = False
    comment_text = ""
    comment_start_tmr = 0
    tmr = 0
    cnt = None
    items = [
        "こうかとんのから揚げ",
        "こうかとんのつくね",
        "こうかとんのぼんじり",
        "こうかとんのもも串",
        "こうかとんの皮串",
        "こうかとんだったもの",
    ]
    item_menu = ItemMenu(items, font, small_font)

    state = "PLAYER_TURN"  # "PLAYER_TURN", "PLAYER_ATTACK_MSG", "ENEMY_TURN", "GAME_OVER"
    show_damage_msg = False
    damage_msg = ""
    damage_msg_start_tmr = 0
    gameover_start_tmr = 0
    just_gameover = False
    while True:
        screen.fill(BLACK)
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            elif event.type == pg.K_q: #Qキーで終了
                return
            elif event.type == pg.KEYDOWN:
                if item_menu.is_open:
                    if event.key == pg.K_ESCAPE:
                        item_menu.is_open = False
                    elif event.key == pg.K_DOWN:
                        item_menu.selected_index = (item_menu.selected_index + 1) % len(item_menu.items)
                    elif event.key == pg.K_UP:
                        item_menu.selected_index = (item_menu.selected_index - 1) % len(item_menu.items)
                    elif event.key == pg.K_RETURN:
                        # アイテム使用時のHP回復処理
                        if command_manager.hp < command_manager.former_hp:
                            command_manager.hp += 10
                            if command_manager.hp > command_manager.former_hp:
                                command_manager.hp = command_manager.former_hp
                        item_menu.is_open = False
                else:
                    if state == "PLAYER_TURN":
                        if event.key == pg.K_RIGHT:
                            selected_index = (selected_index + 1) % len(CommandBoxManager.commands)
                        elif event.key == pg.K_LEFT:
                            selected_index = (selected_index - 1) % len(CommandBoxManager.commands)
                        elif event.key == pg.K_RETURN:
                            if CommandBoxManager.commands[selected_index] == "アイテム":
                                item_menu.is_open = True
                                item_menu.selected_index = 0
                            elif CommandBoxManager.commands[selected_index] == "こうげき":
                                if turn.turn == "player":
                                    player.attack(enemy)
                                    show_damage_msg = True
                                    damage_msg = f"{player.atk}ダメージ！"
                                    damage_msg_start_tmr = tmr
                                    state = "PLAYER_ATTACK_MSG"
                                    comment_text = f"{player.atk}ダメージを与えた！"
                                    comment_start_tmr = tmr
                                    turn.turn_change()
                            else:
                                if turn.turn == "player":
                                    if show_comment == False:
                                        show_comment = True
                                        comment_text = ""
                                        comment_start_tmr = tmr
                                    else:
                                        show_comment = False
                                        turn.turn_change()
                                else:
                                    turn.turn_change()
        if command_manager.hp == 0 and cnt is None:
            cnt = tmr
        if cnt is not None and tmr - cnt >= 60:
            turn.turn = "player"
            show_comment = True
            comment_text = ""
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    return
        # stateによる進行管理
        if state == "PLAYER_ATTACK_MSG":
            # ダメージメッセージのみ表示
            msg_surf = font.render(damage_msg, True, (255, 0, 0))
            msg_rect = msg_surf.get_rect(center=(enemy.rect.centerx, enemy.rect.top - 40))
            screen.blit(msg_surf, msg_rect)
            if tmr - damage_msg_start_tmr > 60:
                if command_manager.hp <= 0:
                    state = "GAME_OVER"
                    gameover_start_tmr = tmr
                    just_gameover = True
                else:
                    state = "ENEMY_TURN"
        elif state == "ENEMY_TURN":
            for bomb in bombs:
                if bomb.rect.bottom >= enemy_manager.enemybox_y + enemy_manager.enemybox_height:
                    bombs.remove(bomb)
                elif heart.rect.colliderect(bomb.rect):
                    bombs.remove(bomb)
                    command_manager.hp -= enemy.atk
                else:
                    bomb.update(screen)
            # 弾幕が全て消えたらプレイヤーターンに戻す
            if command_manager.hp <= 0:
                state = "GAME_OVER"
                gameover_start_tmr = tmr
                just_gameover = True
            elif turn.turn == "enemy" and all(bomb.life <= 0 for bomb in bombs):
                turn.turn_change()
                bombs_num = 15 + turn.num * 5
                bombs = Bomb.generate_bombs(bombs_num, enemy, enemy_manager, turn)
                state = "PLAYER_TURN"
        elif state == "PLAYER_TURN":
            if turn.turn == "player":
                enemy_manager.comments(screen)
            if command_manager.hp > 0:
                command_manager.draw(screen, selected_index)
        if state == "GAME_OVER":
            pg.draw.rect(screen, WHITE, (enemy_manager.start_x, enemy_manager.start_y, enemy_manager.box_width, enemy_manager.box_height), 4)
        else:
            enemy_manager.drawbox(screen)
        if state == "GAME_OVER":
            enemy_manager.comment = enemy_manager.death_comment
            enemy_manager.comments(screen)
            if just_gameover:
                pg.display.update()
                just_gameover = False
            if tmr - gameover_start_tmr > 120:
                return
        enemy.update(screen)
        command_manager.update(screen) # HPバーの描画と更新
        heart.update(key_lst, screen)
        if item_menu.is_open:
            item_menu.draw(screen)
        pg.display.update()
        clock.tick(60)
        tmr += 1
        for bomb in bombs:
            if heart.rect.colliderect(bomb.rect):
                bombs.remove(bomb)
                command_manager.hp -= enemy.atk
            else:
                bomb.update(screen)

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

    pg.init()
    main()
    pg.quit()
    sys.exit()
