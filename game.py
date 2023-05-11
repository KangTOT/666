import pygame
from game_items import *
from game_hub import *
from game_music import *
import random


class Game(object):
    def __init__(self):
        self.main_window = pygame.display.set_mode(SCREEN_RECT.size)
        pygame.display.set_caption("飞机大战")
        self.is_game_over = False
        self.is_pause = False
        self.all_group = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()
        self.supplies_group = pygame.sprite.Group()
        # GameSprite("background.png", 1, self.all_group)
        self.all_group.add(Background(False), Background(True))
        # hero = GameSprite("me1.png", 0, self.all_group)
        # hero.rect.center = SCREEN_RECT.center
        # self.hero = Plane(1000, 5, 0, "me_down.wav", ["me%d.png" % i for i in range(1, 3)],
        #                   "me1.png", ["me_destroy_%d.png" % i for i in range(1, 5)], self.all_group)
        # self.hero.rect.center = SCREEN_RECT.center

        self.hud_panel = HudPanel(self.all_group)
        self.create_enemies()
        self.hero = Hero(self.all_group)
        self.hud_panel.show_bomb(self.hero.bomb_count)

        self.create_supplies()

        # for enemy in self.enemies_group.sprites():
        #     enemy.speed = 0
        #     enemy.rect.y += 400
        # self.hero.speed=1
        self.player = MusicPlayer("game_music.ogg")
        self.player.play_music()


    def reset_game(self):
        self.is_game_over = False
        self.is_pause = False
        self.hud_panel.reset_panel()
        self.hero.rect.midbottom = HERO_DEFAULT_MID_BOTTOM
        # 清空所有敌机
        for enemy in self.enemies_group:
            enemy.kill()

        # 清空残留子弹
        for bullet in self.hero.bullets_group:
            bullet.kill()

        # 重新创建敌机
        self.create_enemies()

    def event_handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.is_game_over:
                    self.reset_game()
                else:
                    self.is_pause = not self.is_pause
                    self.player.pause_music(self.is_pause)

            if not self.is_game_over and not self.is_pause:
                if event.type == BULLET_ENHANCED_OFF_EVENT:
                    self.hero.bullets_kind = 0

                    pygame.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 0)
                # 监听投放道具事件
                if event.type == THROW_SUPPLY_EVENT:
                    self.player.play_sound("supply.wav")
                    supply = random.choice(self.supplies_group.sprites())

                    supply.throw_supply()
                # 监听发射子弹事件
                if event.type == HERO_FIRE_EVENT:
                    self.player.play_sound("bullet.wav")
                    self.hero.fire(self.all_group)
                # 监听取消英雄无敌事件
                if event.type == HERO_POWER_OFF_EVENT:
                    print("取消无敌状态...")

                    # 设置英雄属性
                    self.hero.is_power = False

                    # 取消定时器
                    pygame.time.set_timer(HERO_POWER_OFF_EVENT, 0)
                # 监听英雄牺牲事件
                if event.type == HERO_DEAD_EVENT:
                    print("英雄牺牲了...")

                    # 生命计数 -1
                    self.hud_panel.lives_count -= 1

                    # 更新生命计数显示
                    self.hud_panel.show_lives()
                    # 更新炸弹显示
                    self.hud_panel.show_bomb(self.hero.bomb_count)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                    if self.hero.hp > 0 and self.hero.bomb_count >0:
                        self.player.play_sound("use_bomb.wav")

                    score = self.hero.blowup(self.enemies_group)
                    # for enemy in self.enemies_group.sprites():
                    #     enemy.hp = 0
                    self.hud_panel.show_bomb(self.hero.bomb_count)
                    # self.hud_panel.lives_count = random.randint(0, 10)
                    # self.hud_panel.show_lives()
                    if self.hud_panel.increase_score(score):
                        self.create_enemies()

        return False

    def create_enemies(self):
        """根据游戏级别创建不同数量的敌机"""

        # 敌机精灵组中的精灵数量
        count = len(self.enemies_group.sprites())
        # 要添加到的精灵组
        groups = (self.all_group, self.enemies_group)

        # 判断游戏级别及已有的敌机数量
        if self.hud_panel.level == 1 and count == 0:  # 关卡 1
            for i in range(16):
                Enemy(0, 3, *groups)
        elif self.hud_panel.level == 2 and count == 16:  # 关卡 2
            # 1> 增加敌机的最大速度
            for enemy in self.enemies_group.sprites():
                enemy.max_speed = 5
            # 2> 创建敌机
            for i in range(8):
                Enemy(0, 5, *groups)
            for i in range(2):
                Enemy(1, 1, *groups)
        elif self.hud_panel.level == 3 and count == 26:  # 关卡 3
            # 1> 增加敌机的最大速度
            for enemy in self.enemies_group.sprites():
                enemy.max_speed = 7 if enemy.kind == 0 else 3
            # 2> 创建敌机
            for i in range(8):
                Enemy(0, 7, *groups)
            for i in range(2):
                Enemy(1, 3, *groups)
            for i in range(2):
                Enemy(2, 1, *groups)

    def start(self):
        clock = pygame.time.Clock()
        frame_counter = 0
        while True:
            self.is_game_over = self.hud_panel.lives_count == 0
            if self.event_handle():
                self.hud_panel.save_best_score()
                return
            if self.is_game_over:
                # print("游戏结束了，按空格键重新开始...")
                self.hud_panel.panel_pause(True, self.all_group)
            elif self.is_pause:
                # print("暂停了，按空格继续...")
                self.hud_panel.panel_pause(False, self.all_group)
            else:
                self.hud_panel.panel_resume(self.all_group)
                self.check_collide()
                keys = pygame.key.get_pressed()

                # 水平移动基数
                move_hor = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                # 垂直移动基数
                move_ver = keys[pygame.K_DOWN] - keys[pygame.K_UP]

                # if keys[pygame.K_RIGHT]:
                #     self.hero.rect.x += 10
                # self.hero.hp -= 30
                # if self.hud_panel.increase_score(100):
                #     print("升级到 %d " % self.hud_panel.level)
                #     self.create_enemies()
                frame_counter = (frame_counter + 1) % FRAME_INTERVAL
                self.all_group.update(frame_counter == 0, move_hor, move_ver)

            self.all_group.draw(self.main_window)
            pygame.display.update()
            clock.tick(60)

    def check_collide(self):
        if not self.hero.is_power:
            enemies = pygame.sprite.spritecollide(self.hero,
                                                  self.enemies_group,
                                                  False,
                                                  pygame.sprite.collide_mask)
            # 过滤掉已经被摧毁的敌机
            enemies = list(filter(lambda x: x.hp > 0, enemies))
            # 是否撞到敌机
            if enemies:
                self.player.play_sound(self.hero.wav_name)
                self.hero.hp = 0  # 英雄被撞毁

            for enemy in enemies:
                enemy.hp = 0  # 敌机同样被撞毁

            # 2. 检测敌机被子弹击中
            hit_enemies = pygame.sprite.groupcollide(self.enemies_group,
                                                     self.hero.bullets_group,
                                                     False,
                                                     False,
                                                     pygame.sprite.collide_mask)

            # 遍历字典
            for enemy in hit_enemies:

                # 已经被摧毁的敌机不需要浪费子弹
                if enemy.hp <= 0:
                    continue

                # 遍历击中敌机的子弹列表
                for bullet in hit_enemies[enemy]:

                    # 1> 将子弹从所有精灵组中清除
                    bullet.kill()

                    # 2> 修改敌机的生命值
                    enemy.hp -= bullet.damage

                    # 3> 如果敌机没有被摧毁，继续下一颗子弹
                    if enemy.hp > 0:
                        continue

                    # 4> 修改游戏得分并判断是否升级
                    if self.hud_panel.increase_score(enemy.value):
                        self.player.play_sound("upgrade.wav")
                        self.create_enemies()

                    self.player.play_sound(enemy.wav_name)
                    # 5> 退出遍历子弹列表循环
                    break

                    # 3. 英雄拾取道具
                supplies = pygame.sprite.spritecollide(self.hero,
                                                       self.supplies_group,
                                                       False,
                                                       pygame.sprite.collide_mask)
                if supplies:
                    supply = supplies[0]
                    self.player.play_sound(supply.wav_name)

                    # 将道具设置到游戏窗口下方
                    supply.rect.y = SCREEN_RECT.h

                    # 判断道具类型
                    if supply.kind == 0:  # 炸弹补给
                        self.hero.bomb_count += 1
                        self.hud_panel.show_bomb(self.hero.bomb_count)
                    else:  # 设置子弹增强
                        self.hero.bullets_kind = 1

                        # 设置关闭子弹增强的定时器事件
                        pygame.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 8000)

    def create_supplies(self):
        """创建道具"""
        Supply(0, self.supplies_group, self.all_group)
        Supply(1, self.supplies_group, self.all_group)

        # 设置 30s 投放道具定时器事件
        pygame.time.set_timer(THROW_SUPPLY_EVENT,30000)


if __name__ == '__main__':
    pygame.init()
    Game().start()
    pygame.quit()
