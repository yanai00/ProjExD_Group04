import pygame as pg
import sys

# 初期設定
WIDTH, HEIGHT = 1920, 1080
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("黒画面だけ")
clock = pg.time.Clock()
pg.mouse.set_visible(False)

# メインループ
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

    screen.fill((0, 0, 0))  # 真っ黒
    pg.display.update()
    clock.tick(60)
