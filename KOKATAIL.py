import pygame as pg
import sys

# --- 初期設定 ---
# Pygameライブラリの初期化
pg.init()

# 画面のサイズを設定
WIDTH, HEIGHT = 1920, 1080
screen = pg.display.set_mode((WIDTH, HEIGHT))

# ウィンドウのタイトルを設定
pg.display.set_caption("クラスによるターン管理（コメント付き）")

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
small_font = pg.font.SysFont("meiryo", 40)

# --- ゲームデータ ---
# クラスの外で定義し、クラス内のメソッドから参照するデータ
commands = ["こうげき", "アクション", "アイテム", "にげる"]
enemies = [{"name": "サンズとん"}]
player_status = {"max_hp": 50, "current_hp": 50}

# --- クラス定義 ---
class TurnManager:
    """
    ゲームのターン進行（状態）を管理するクラス
    """
    def __init__(self):
        """
        クラスが作られた時に最初に呼ばれる関数（初期化）
        """
        self.state = "SELECTING"         # 現在のゲーム状態
        self.selected_index = 0          # コマンドの選択カーソル位置
        self.target_index = 0            # ターゲットの選択カーソル位置
        self.display_text = ""           # 表示するメッセージ

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
                if commands[self.selected_index] == "こうげき":
                    self.state = "TARGET_SELECT_IN_BOX" # ターゲット選択へ
                    self.target_index = 0 # ターゲットカーソルをリセット
            elif self.state == "TARGET_SELECT_IN_BOX":
                target_enemy = enemies[self.target_index]
                self.display_text = f"＊{target_enemy['name']}に攻撃！"
                self.state = "ATTACK_MESSAGE" # 攻撃メッセージ表示へ
            elif self.state == "ATTACK_MESSAGE":
                self.display_text = f"＊{enemies[0]['name']}のターン。"
                self.state = "ENEMY_TURN" # 敵のターンへ
            elif self.state == "ENEMY_TURN":
                self.state = "SELECTING" # プレイヤーのコマンド選択へ戻る
        
        # 【各stateでの左右・上下キーの処理】
        if self.state == "SELECTING":
            if key == pg.K_LEFT: self.selected_index = (self.selected_index - 1 + len(commands)) % len(commands)
            elif key == pg.K_RIGHT: self.selected_index = (self.selected_index + 1) % len(commands)
        elif self.state == "TARGET_SELECT_IN_BOX":
            if key == pg.K_UP: self.target_index = (self.target_index - 1 + len(enemies)) % len(enemies)
            elif key == pg.K_DOWN: self.target_index = (self.target_index + 1) % len(enemies)
            elif key == pg.K_x: self.state = "SELECTING" # Xキーでキャンセル

    def draw(self, screen):
        """
        現在のstateに応じて、適切なUIを描画するメソッド
        """
        self._draw_player_status(screen) # HPバーは常に描画

        if self.state == "SELECTING":
            self._draw_commands(screen)
        elif self.state == "TARGET_SELECT_IN_BOX":
            enemy_names = [e['name'] for e in enemies]
            self._draw_selection_box(screen, "だれを こうげきする？", enemy_names, self.target_index)
        elif self.state == "ATTACK_MESSAGE" or self.state == "ENEMY_TURN":
            self._draw_message_box(screen, self.display_text)

    # 以降の「_」で始まるメソッドは、このクラス内部でのみ使われる補助的な描画関数
    def _draw_player_status(self, screen):
        # HPバーやHP数値を描画する
        hp_bar_width, hp_bar_height = 160, 20
        status_y, center_x = HEIGHT - 350, WIDTH // 2
        hp_ratio = player_status["current_hp"] / player_status["max_hp"]
        pg.draw.rect(screen, WHITE, (center_x - hp_bar_width // 2, status_y, hp_bar_width, hp_bar_height), 2)
        pg.draw.rect(screen, YELLOW, (center_x - hp_bar_width // 2, status_y, int(hp_bar_width * hp_ratio), hp_bar_height))
        hp_text = font.render(f"{player_status['current_hp']} / {player_status['max_hp']}", True, WHITE)
        screen.blit(hp_text, (center_x + hp_bar_width // 2 + 10, status_y + (hp_bar_height - hp_text.get_height()) // 2))

    def _draw_commands(self, screen):
        # 4つのコマンドボックスを描画する
        box_width, box_height, spacing = 265, 80, 40
        total_width = len(commands) * box_width + (len(commands) - 1) * spacing
        start_x = (WIDTH - total_width) // 2
        for i, command in enumerate(commands):
            rect = pg.Rect(start_x + i * (box_width + spacing), HEIGHT - 300, box_width, box_height)
            color = YELLOW if i == self.selected_index else WHITE
            pg.draw.rect(screen, color, rect, 4)
            text = font.render(command, True, WHITE)
            screen.blit(text, text.get_rect(center=rect.center))

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
turn_manager = TurnManager()

# メインループ (このループが回り続けることでゲームが進行する)
while True:
    # イベント処理 (キー入力、閉じるボタンなど)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        # イベント処理はTurnManagerにお任せ
        turn_manager.handle_event(event)

    # 描画処理
    # 画面を一度真っ黒に塗りつぶす
    screen.fill(BLACK)
    
    # 敵など、常に表示するものをここに描画
    # (現在は何も描画していない)

    # ターンに応じたUIの描画はTurnManagerにお任せ
    turn_manager.draw(screen)

    # 画面全体を更新して、描画を反映させる
    pg.display.update()

    # フレームレートを60FPSに固定
    clock.tick(60)