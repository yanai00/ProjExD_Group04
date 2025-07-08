import pygame as pg
import sys
import os
import random
import time
# 初期設定
WIDTH, HEIGHT = 1920, 1080
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("コマンド選択画面 + HPバー + HP表示")
clock = pg.time.Clock()
pg.mouse.set_visible(False)

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# フォント
font = pg.font.SysFont("meiryo", 50)

# コマンド
commands = ["こうげき", "アクション", "アイテム", "にげる"]
selected_index = 0

# コマンドボックスサイズ
box_width = 265
box_height = 80
box_y = HEIGHT - 300

# HPバーサイズ
hp_bar_width = 160
hp_bar_height = 20
hp_bar_margin_top = 10  # コマンドボックスとHPバーの間の隙間

# HP値
max_hp = 50
current_hp = 50  # 0～max_hpで変更可能

class Escape:
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
        result = random.random() < 0.1 
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
        


def get_command_boxes():
    """
    コマンド選択用の矩形リストを作成する。
    各コマンドは等間隔に横並びされ、中央揃えされる。
    Returns:
        list[pg.Rect]: コマンドボックスのリスト
    """
    spacing = 40
    total_width = len(commands) * box_width + (len(commands) - 1) * spacing
    start_x = (WIDTH - total_width) // 2
    boxes = []
    for i in range(len(commands)):
        x = start_x + i * (box_width + spacing)
        boxes.append(pg.Rect(x, box_y, box_width, box_height))
    return boxes

def main():
    selected_index = 0
    escape = Escape()
    global current_hp  # HPをグローバルで使う場合

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
                elif event.key == pg.K_RETURN:
                    if commands[selected_index] == "にげる":
                        if escape.try_escape():
                            escape.show_result(screen, font)
                            pg.quit()
                            sys.exit()
                        else:
                            escape.show_result(screen, font)

        screen.fill(BLACK)

        boxes = get_command_boxes()

        # コマンドボックス描画
        for i, rect in enumerate(boxes):
            color = YELLOW if i == selected_index else WHITE
            pg.draw.rect(screen, color, rect, 4)

            text = font.render(commands[i], True, WHITE)
            text_x = rect.x + (rect.width - text.get_width()) // 2
            text_y = rect.y + (rect.height - text.get_height()) // 2
            screen.blit(text, (text_x, text_y))

        # 真ん中2つのコマンドボックスの中心の真ん中を計算
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

if __name__ == "__main__":
    main()