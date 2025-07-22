import os
import pygame as pg
import sys
from typing import List
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pg.init()  # pygameの初期化は必ず最初に行う

# 初期化後にフォント作成
WIDTH, HEIGHT = 1920, 1080
font = pg.font.SysFont("meiryo", 50)
small_font = pg.font.SysFont("meiryo", 36)
enemy_font = pg.font.SysFont("meiryo", 45)

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
    def __init__(self, HP:int, ATK:int, turn:TurnManager):
        self.former_hp = HP
        self.hp = self.former_hp
        self.former_atk = ATK
        self.atk = self.former_atk
        self.turn = turn

class CommandBoxManager():
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
        self.textbox_width = 1180
        self.textbox_height = 280
        self.textbox_start_x = (WIDTH - self.textbox_width) // 2
        self.textbox_start_y = self.box_y - (self.textbox_height + 20)
        self.hp_bar_y = self.box_y + self.box_height + self.hp_bar_margin_top + 15
        self.comment_x = self.textbox_start_x + 30
        self.comment_y = self.textbox_start_y + 20
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
                
    def text_box(self, screen:pg.Surface):
        if self.turn.turn == "player":
            pg.draw.rect(screen, WHITE, (self.textbox_start_x, self.textbox_start_y, self.textbox_width, self.textbox_height), 4)

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
        
class Enemy():
    """
    敵に関するクラス
    """
    img0 = pg.image.load(f"photo/enemy1_bob_v2.gif")
    img = pg.transform.rotozoom(img0,0,0.3)
    def __init__(self, HP:int, ATK:int, command:CommandBoxManager, turn:TurnManager, font):
        self.formal_hp = HP
        self.hp = self.formal_hp
        self.atk = ATK
        self.font = font
        self.name = "サンズとん"
        self.image = __class__.img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.centery = 300
        self.command = command
        self.turn = turn
        self.tmr = 0

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

class EnemyBoxManager():
    def __init__(self, player:Player, turn:TurnManager, command:CommandBoxManager, enemy:Enemy, font:pg.font.Font, crear_font:pg.font.Font):
        self.player = player
        self.turn = turn
        self.command = command
        self.enemy = enemy
        self.font = font
        self.crear_font = crear_font
        self.enemybox_width = 280
        self.enemybox_height = 280
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
        self.crear_comment = self.enemy.name + "を倒した"
        # self.enemy_text = self.font.render(self.comment, True, WHITE)
        self.enemybox_x = (WIDTH - self.enemybox_width) // 2
        self.enemybox_y = self.command.box_y - (self.enemybox_height + 20)
        
    def drawbox(self, screen:pg.Surface):
        if self.turn.turn == "enemy":
            pg.draw.rect(screen, WHITE, (self.enemybox_x, self.enemybox_y, self.enemybox_width, self.enemybox_height), 4)
    
    def comments(self, screen: pg.Surface):
        if self.command.hp == 0:
            self.comment = self.death_comment
            self.enemy_text = self.font.render(self.comment, True, (255, 0, 0))
        
        elif self.enemy.hp == 0:
            self.comment = self.crear_comment
            self.enemy_text = self.crear_font.render(self.comment, True, WHITE)
            
        elif self.command.hp > 0:
            if self.turn.num < len(self.comments_list):
                self.comment = self.comments_list[self.turn.num]
            else:
                self.comment = self.comments_list[-1]
            self.enemy_text = self.font.render(self.comment, True, (255, 0, 0))
        screen.blit(self.enemy_text, (self.command.comment_x, self.command.comment_y))

class ItemMenu():
    """
    アイテムメニューの描画と操作管理クラス
    """
    items = [
        "こうかとんのから揚げ",
        "こうかとんのつくね",
        "こうかとんのぼんじり",
        "こうかとんのもも串",
        "こうかとんの皮串",
        "こうかとんだったもの",
    ]
    healing_point = [10, 10, 10, 10, 10, 10]
    
    def __init__(self, small_font: pg.font.Font, command:CommandBoxManager) -> None:
        self.items = __class__.items
        self.point = __class__.healing_point
        self.small_font = small_font
        self.selected_index = 0
        self.is_open = False
        self.command = command
        self.num = None

    def draw(self, screen: pg.Surface) -> None:
        """
        アイテムメニューを画面に描画する。
        """
        if self.is_open == True:
            # タイトル
            title = self.small_font.render("アイテム", True, WHITE)
            screen.blit(title, (self.command.comment_x, self.command.comment_y))

            # アイテムリスト表示
            for i, item in enumerate(self.items):
                color = YELLOW if i == self.selected_index else WHITE
                item_text = self.small_font.render(f"- {item}", True, color)
                if self.command.comment_y + (i + 1) * 50 + 36 < self.command.textbox_start_y + self.command.textbox_height:
                    screen.blit(item_text, (self.command.comment_x + 40, self.command.comment_y + (i + 1) * 50))
                elif self.num != None:
                    screen.blit(item_text, (self.command.comment_x + 40 + self.command.textbox_width // 2, self.command.comment_y + (i + 1 - self.num) * 50))
                else:
                    self.num = i
    
    def use_item(self):
        self.is_open = False
        self.command.hp += self.point[self.selected_index]
        if self.command.hp > self.command.former_hp:
            self.command.hp = self.command.former_hp
        
    def item_comment(self, screen:pg.Surface):
        self.use_text = self.small_font.render(f"{self.items[self.selected_index]}を使った。", True, WHITE)
        self.heal_text = self.small_font.render(f"HPを{self.point[self.selected_index]}回復した。", True, WHITE)
        screen.blit(self.use_text, (self.command.comment_x, self.command.comment_y))
        screen.blit(self.heal_text, (self.command.comment_x, self.command.comment_y + 50))

class Escape():
    """
    逃げるコマンドの判定クラス
    20%の確率で成功（True）、それ以外は失敗（False）を返す
    逃げた回数や失敗回数も記録
    """
    def __init__(self, turn:TurnManager, command:CommandBoxManager):
        """
        Escapeオブジェクトを初期化する。
        success_count: 成功した逃走回数
        fail_count: 失敗した逃走回数
        last_result: 最後の逃走結果 (True=成功, False=失敗, None=未試行)
        """
        self.turn = turn
        self.command = command
        self.last_result = None  # True:成功, False:失敗
        self.escape_p = 0.2

    def try_escape(self) -> bool:
        """
        逃走を試みる。
        成功確率は10%。
        Returns:
            bool: 逃走成功ならTrue、失敗ならFalse
        """
        result = random.random() < self.escape_p
        self.last_result = result
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
        if self.last_result:
            msg = font.render("逃げた", True, (0, 255, 0))
        else:
            msg = font.render("逃げれなかった", True, WHITE)
        screen.blit(msg, (self.command.comment_x, self.command.comment_y))

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
        if self.state is "alive":
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

class Attack():
    
    targets = ["サンズとん"]
    
    def __init__(self, command:CommandBoxManager, player:Player, enemy:Enemy, font):
        self.command = command
        self.player = player
        self.enemy = enemy
        self.font = font
        self.selected_index = 0
        self.targets = __class__.targets
        self.is_open = False
        self.num = None
        
    def draw(self, screen: pg.Surface) -> None:
        """
        アイテムメニューを画面に描画する。
        """
        if self.is_open == True:
            # タイトル
            title = self.font.render("誰をこうげきする？", True, WHITE)
            screen.blit(title, (self.command.comment_x, self.command.comment_y))

            # アイテムリスト表示
            for i, target in enumerate(self.targets):
                color = YELLOW if i == self.selected_index else WHITE
                target_text = self.font.render(f"- {target}", True, color)
                if self.command.comment_y + (i + 1) * 50 + 36 < self.command.textbox_start_y + self.command.textbox_height:
                    screen.blit(target_text, (self.command.comment_x + 40, self.command.comment_y + (i + 1) * 50))
                elif self.num != None:
                    screen.blit(target_text, (self.command.comment_x + 40 + self.command.textbox_width // 2, self.command.comment_y + (i + 1 - self.num) * 50))
                else:
                    self.num = i
        
    def attack_enemy(self):
        self.enemy.hp -= self.player.atk
        if self.enemy.hp < 0:
            self.enemy.hp == 0
            
    def attack_comment(self, screen:pg.Surface):
        self.attack_text = self.font.render(f"{self.targets[self.selected_index]}に{self.player.atk}ダメージ！", True, WHITE)
        screen.blit(self.attack_text, (self.command.comment_x, self.command.comment_y))
        
class Action():
    commands = ["はなしかける", "分析", "黙る"]
    def __init__(self, command:CommandBoxManager, enemy:Enemy, turn:TurnManager, escape:Escape, font:pg.font.Font):
        self.command = command
        self.enemy = enemy
        self.selected_index = 0
        self.turn = turn
        self.escape_p = escape.escape_p
        self.font = font
        self.commands = __class__.commands
        self.tmr = 0
        self.enemy_state = (self.enemy.hp * 5 / self.enemy.formal_hp - 0.5) // 1
        self.is_open = False
        self.num = None
        self.comments_list = ["シカトされた",
                        "戦いに集中しよう",
                        "目が合うようになってきた",
                        "笑った..？",
                        "楽しそうだ"]
        self.feeling_list = ["勝利は目前だ",
                             "このままいけば勝てそうだ",
                             "この調子でいこう",
                             "まだまだ気は抜けない",
                             "強敵だ"]

    def draw(self, screen:pg.Surface):
        if self.is_open == True:
            # タイトル
            title = self.font.render("何をする？", True, WHITE)
            screen.blit(title, (self.command.comment_x, self.command.comment_y))

            # アイテムリスト表示
            for i, action in enumerate(self.commands):
                color = YELLOW if i == self.selected_index else WHITE
                action_text = self.font.render(f"- {action}", True, color)
                if self.command.comment_y + (i + 1) * 50 + 36 < self.command.textbox_start_y + self.command.textbox_height:
                    screen.blit(action_text, (self.command.comment_x + 40, self.command.comment_y + (i + 1) * 50))
                elif self.num != None:
                    screen.blit(action_text, (self.command.comment_x + 40 + self.command.textbox_width // 2, self.command.comment_y + (i + 1 - self.num) * 50))
                else:
                    self.num = i
                    
    def try_talk(self):
        self.escape_p += 0.1
        if self.escape_p >= 0.8:
            self.escape_p = 0.8
                    
    def action_comment(self, screen:pg.Surface):
        self.enemy_state = int((self.enemy.hp * 5 / self.enemy.formal_hp - 0.5) // 1)
        if self.selected_index == 0:
            if self.turn.num < len(self.comments_list):
                self.comment = self.comments_list[self.turn.num]
            else:
                self.comment = self.comments_list[-1]
            self.action_text = self.font.render(self.comment, True, WHITE)
        elif self.selected_index == 1:
            self.action_text = self.font.render(f"HP:{self.enemy.hp} ATK:{self.enemy.atk}", True, WHITE)
            self.feeling_text = self.font.render(self.feeling_list[self.enemy_state], True, WHITE)
            screen.blit(self.feeling_text, (self.command.comment_x, self.command.comment_y + 50))
        elif self.selected_index == 2:
            self.action_text = self.font.render("静寂に包まれた...", True, WHITE)
        screen.blit(self.action_text, (self.command.comment_x, self.command.comment_y))

def main():
    """
    メインゲームループ
    """
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("コマンド選択画面 + HPバー + HP表示")
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)

    turn = TurnManager()
    player = Player(50, 5, turn)
    command_manager = CommandBoxManager(player, turn, font)
    enemy = Enemy(50, 5, command_manager, turn, small_font)
    enemy_manager = EnemyBoxManager(player, turn, command_manager, enemy, enemy_font, font)
    heart = Heart(command_manager, enemy_manager, turn)
    bombs_num = 15 + turn.num * 5
    bombs = Bomb.generate_bombs(bombs_num, enemy, enemy_manager, turn)
    selected_index = 0
    show_comment = False
    tmr = 0
    cnt = None
    item = ItemMenu(small_font, command_manager)
    escape = Escape(turn, command_manager)
    attack = Attack(command_manager, player, enemy, small_font)
    action = Action(command_manager, enemy, turn, escape, small_font)
    command_check = False
    show_item = False
    show_escape = False
    show_attack = False
    show_action = False

    while True:
        screen.fill(BLACK)
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if turn.turn == "player":
                if event.type == pg.QUIT:
                    return
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        item.is_open = False
                        attack.is_open = False
                        action.is_open = False
                        command_check = False
                    elif event.key == pg.K_DOWN:
                        if command_check == True:
                            if item.is_open == True:
                                item.selected_index = (item.selected_index + 1) % len(item.items)
                            elif attack.is_open == True:
                                attack.selected_index = (attack.selected_index + 1) % len(attack.targets)
                            elif action.is_open == True:
                                action.selected_index = (action.selected_index + 1) % len(action.commands)
                    elif event.key == pg.K_UP:
                        if command_check == True:
                            if item.is_open == True:
                                item.selected_index = (item.selected_index - 1) % len(item.items)
                            elif attack.is_open == True:
                                attack.selected_index = (attack.selected_index - 1) % len(attack.targets)
                            elif action.is_open == True:
                                action.selected_index = (action.selected_index - 1) % len(action.commands)
                    elif event.key == pg.K_LEFT:
                        if command_check == False:
                            selected_index = (selected_index - 1) % len(command_manager.commands)
                    elif event.key == pg.K_RIGHT:
                        if command_check == False:
                            selected_index = (selected_index + 1) % len(command_manager.commands)
                    elif event.key == pg.K_RETURN:
                        if show_comment == True and command_check == True:
                            command_check = False
                            show_comment = False
                            turn.turn_change()
                        elif command_manager.commands[selected_index] == "こうげき":
                            if command_check == False and attack.is_open == False:
                                attack.is_open = True
                                command_check = True
                                attack.draw(screen)
                            elif attack.is_open == True:
                                attack.is_open = False
                                attack.attack_enemy()
                                show_attack = True
                            elif attack.is_open == False and command_check == True:
                                show_attack = False
                                show_comment = True
                        elif command_manager.commands[selected_index] == "アクション":
                            if command_check == False and action.is_open == False:
                                action.is_open = True
                                command_check = True
                            elif action.is_open == True:
                                if action.commands[action.selected_index] == "はなしかける":
                                    action.try_talk()
                                action.is_open = False
                                show_action = True
                            elif action.is_open == False and command_check == True:
                                show_action = False
                                show_comment = True
                        elif command_manager.commands[selected_index] == "アイテム":
                            if command_check == False and item.is_open == False:
                                item.is_open = True
                                command_check = True
                                item.draw(screen)
                            elif item.is_open == True:
                                item.is_open = False
                                item.use_item()
                                show_item = True
                            elif item.is_open == False and command_check == True:
                                show_item = False
                                show_comment = True
                        elif command_manager.commands[selected_index] == "にげる":
                            if show_escape == True:
                                if escape.last_result:
                                    return
                                else:
                                    show_escape = False
                                    show_comment = True
                            else:
                                show_escape = True
                                command_check = True
                                escape.try_escape()
                        
                
        if (command_manager.hp == 0 or enemy.hp == 0) and cnt is None:
            cnt = tmr
            
        if cnt is not None and tmr - cnt >= 60:
            turn.turn = "player"
            show_comment = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    return
                
        if item.is_open == True and command_check == True:
            item.draw(screen)
            
        if attack.is_open == True and command_check == True:
            attack.draw(screen)
            
        if action.is_open == True and command_check == True:
            action.draw(screen)
            
        if show_escape == True:
            escape.show_result(screen, small_font) 
                
        if show_comment == True:
            enemy_manager.comments(screen)
            
        if show_item == True:
            item.item_comment(screen)
            
        if show_attack == True:
            attack.attack_comment(screen)
            
        if show_action == True:
            action.action_comment(screen)
        
        for bomb in bombs:
            if bomb.rect.bottom >= enemy_manager.enemybox_y + enemy_manager.enemybox_height:
                bombs.remove(bomb)
            elif heart.rect.colliderect(bomb.rect):
                bombs.remove(bomb)
                command_manager.hp -= enemy.atk
            else:
                bomb.update(screen)

        if command_manager.hp > 0:
            command_manager.draw(screen, selected_index)
            
        command_manager.text_box(screen)
        enemy_manager.drawbox(screen)
        enemy.update(screen)
        command_manager.update(screen) # HPバーの描画と更新
        heart.update(key_lst, screen)
        for bomb in bombs:
            if heart.rect.colliderect(bomb.rect):
                bombs.remove(bomb)
                command_manager.hp -= enemy.atk
            else:
                bomb.update(screen)
                
        if turn.turn == "enemy" and all(bomb.life <= 0 for bomb in bombs):
            turn.turn_change()
            bombs_num = 15 + turn.num * 5
            bombs = Bomb.generate_bombs(bombs_num, enemy, enemy_manager, turn)

        pg.display.update()
        clock.tick(60)
        tmr += 1

if __name__ == "__main__":
    WIDTH, HEIGHT = 1920, 1080

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)

    pg.init()
    main()
    pg.quit()
    sys.exit()