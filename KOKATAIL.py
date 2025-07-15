import os
import pygame as pg
import sys
from typing import List

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

# フォントの定義（PCにインストールされているフォントを指定）
font = pg.font.SysFont("meiryo", 50)
small_font = pg.font.SysFont("meiryo", 36)

# --- ゲームデータ ---
# クラスの外で定義し、クラス内のメソッドから参照するデータ
commands = ["こうげき", "アクション", "アイテム", "にげる"]
enemies = [{"name": "サンズとん"}]
player_status = {"max_hp": 50, "current_hp": 50}

# --- クラス定義 ---
class Player():
    """
    プレイヤーのHPと攻撃力を管理するクラス
    """
    def __init__(self, HP: int, ATK: int):
        self.former_hp = HP
        self.hp = self.former_hp
        self.former_atk = ATK
        self.atk = self.former_atk

class Enemy():
    """
    敵の名前、HP、攻撃力を管理するクラス
    """
    def __init__(self, name: str, HP: int, ATK: int):
        self.name = name
        self.former_hp = HP
        self.hp = self.former_hp
        self.former_atk = ATK
        self.atk = self.former_atk

    def update(self, screen: pg.Surface):
        """
        敵の表示（ここでは名前とHPだけ簡易表示）
        """
        enemy_text = font.render(f"{self.name}", True, WHITE)
        screen.blit(enemy_text, (WIDTH//2 - enemy_text.get_width()//2, 200))
        hp_text = small_font.render(f"HP: {self.hp} / {self.former_hp}", True, YELLOW)
        screen.blit(hp_text, (WIDTH//2 - hp_text.get_width()//2, 270))

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

    def __init__(self, player: Player, font: pg.font.Font) -> None:
        self.commands = __class__.commands
        self.box_width = __class__.box_width
        self.box_height = __class__.box_height
        self.box_y = __class__.box_y
        self.font = font
        self.player = player

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
        self.boxes = self.get_command_boxes()
        for i, rect in enumerate(self.boxes):
            color = YELLOW if i == selected_index else WHITE
            pg.draw.rect(screen, color, rect, 4)
            text = self.font.render(self.commands[i], True, WHITE)
            text_x = rect.x + (rect.width - text.get_width()) // 2
            text_y = rect.y + (rect.height - text.get_height()) // 2
            screen.blit(text, (text_x, text_y))

    def draw_hp_bar(self, screen: pg.Surface):
        boxes = self.get_command_boxes()
        center_x = (boxes[1].centerx + boxes[2].centerx) // 2
        # HPバー背景（黒）
        pg.draw.rect(screen, BLACK, (center_x - __class__.hp_bar_width // 2, __class__.hp_bar_y, __class__.hp_bar_width, __class__.hp_bar_height))
        # HPバー黄色部分（HPの割合に応じた幅）
        hp_ratio = self.player.hp / self.player.former_hp
        pg.draw.rect(screen, YELLOW, (center_x - __class__.hp_bar_width // 2, __class__.hp_bar_y, int(__class__.hp_bar_width * hp_ratio), __class__.hp_bar_height))
        # HPバー枠（白）
        pg.draw.rect(screen, WHITE, (center_x - __class__.hp_bar_width // 2, __class__.hp_bar_y, __class__.hp_bar_width, __class__.hp_bar_height), 2)
        # HPバー横にHP数値表示
        hp_text = font.render(f"{self.player.hp} / {self.player.former_hp}", True, WHITE)
        text_x = center_x - __class__.hp_bar_width // 2 + __class__.hp_bar_width + 10
        text_y = __class__.hp_bar_y + (__class__.hp_bar_height - hp_text.get_height()) // 2
        screen.blit(hp_text, (text_x, text_y))

class TurnManager:
    """
    ゲームのターン進行（状態）を管理するクラス
    """
    def __init__(self, player: Player, enemy: Enemy, command_manager: CommandBoxManager):
        self.state = "SELECTING"         # 現在のゲーム状態
        self.selected_index = 0          # コマンドの選択カーソル位置
        self.target_index = 0            # ターゲットの選択カーソル位置
        self.display_text = ""           # 表示するメッセージ
        self.player = player
        self.enemy = enemy
        self.command_manager = command_manager

    def handle_event(self, event):
        """
        キー入力などのイベントを処理するメソッド
        """
        # KEYDOWNイベント（キーが押された時）以外は処理しない
        if event.type != pg.KEYDOWN:
            return

        key = event.key # 押されたキーの種類を取得

        # 【Enterキーが押された時の処理】
        # 現在のstateに応じて、次のstateに遷移させる
        if key == pg.K_RETURN:
            if self.state == "SELECTING":
                if self.command_manager.commands[self.selected_index] == "こうげき":
                    self.state = "TARGET_SELECT_IN_BOX" # ターゲット選択へ
                    self.target_index = 0 # ターゲットカーソルをリセット
            elif self.state == "TARGET_SELECT_IN_BOX":
                self.display_text = f"＊{self.enemy.name}に攻撃！"
                # 攻撃処理
                self.enemy.hp = max(0, self.enemy.hp - self.player.atk)
                self.state = "ATTACK_MESSAGE" # 攻撃メッセージ表示へ
            elif self.state == "ATTACK_MESSAGE":
                self.display_text = f"＊{self.enemy.name}のターン。"
                self.state = "ENEMY_TURN" # 敵のターンへ
            elif self.state == "ENEMY_TURN":
                # 敵の攻撃処理
                self.player.hp = max(0, self.player.hp - self.enemy.atk)
                self.state = "SELECTING" # プレイヤーのコマンド選択へ戻る
        
        # 【各stateでの左右・上下キーの処理】
        if self.state == "SELECTING":
            if key == pg.K_LEFT: self.selected_index = (self.selected_index - 1 + len(self.command_manager.commands)) % len(self.command_manager.commands)
            elif key == pg.K_RIGHT: self.selected_index = (self.selected_index + 1) % len(self.command_manager.commands)
        elif self.state == "TARGET_SELECT_IN_BOX":
            # 今は敵1体なので上下キーは未使用
            if key == pg.K_x: self.state = "SELECTING" # Xキーでキャンセル

    def draw(self, screen):
        """
        現在のstateに応じて、適切なUIを描画するメソッド
        """
        self.command_manager.draw_hp_bar(screen)

        if self.state == "SELECTING":
            self.command_manager.draw(screen, self.selected_index)
        elif self.state == "TARGET_SELECT_IN_BOX":
            self._draw_selection_box(screen, "だれを こうげきする？", [self.enemy.name], self.target_index)
        elif self.state == "ATTACK_MESSAGE" or self.state == "ENEMY_TURN":
            self._draw_message_box(screen, self.display_text)

    # 以降の「_」で始まるメソッドは、このクラス内部でのみ使われる補助的な描画関数
    def _draw_selection_box(self, screen, title, item_list, selected_index):
        # 項目リストを持つテキストボックスを描画する
        box_rect = pg.Rect(400, HEIGHT - 550, WIDTH - 800, 150)
        pg.draw.rect(screen, BLACK, box_rect)
        pg.draw.rect(screen, WHITE, box_rect, 4)
        title_surf = small_font.render(title, True, WHITE)
        screen.blit(title_surf, (box_rect.x + 20, box_rect.y + 5))
        for i, item_name in enumerate(item_list):
            color = YELLOW if i == selected_index else WHITE
            surf = small_font.render(f"＊ {item_name}", True, color)
            screen.blit(surf, (box_rect.x + 40, box_rect.y + 45 + i * 45))

    def _draw_message_box(self, screen, text):
        # 1行のメッセージを持つテキストボックスを描画する
        box_rect = pg.Rect(400, HEIGHT - 550, WIDTH - 800, 150)
        pg.draw.rect(screen, BLACK, box_rect)
        pg.draw.rect(screen, WHITE, box_rect, 4)
        surf = small_font.render(text, True, WHITE)
        screen.blit(surf, (box_rect.x + 40, box_rect.y + 30))

# --- メイン処理 ---
# TurnManagerクラスから、実際に操作するインスタンス（実体）を1つ生成
def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("コマンド選択画面 + HPバー + HP表示 + ターン管理")
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)

    player = Player(50, 5)
    enemy = Enemy("サンズとん", 30, 3)
    command_manager = CommandBoxManager(player, font)
    turn_manager = TurnManager(player, enemy, command_manager)

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            else:
                turn_manager.handle_event(event)
        screen.fill(BLACK)
        enemy.update(screen)
        turn_manager.draw(screen)
        pg.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pg.quit()
    sys.exit()