import sys  #用于退出游戏
import pygame
import json  #存储数据
from time import sleep  #用于游戏暂停
from bullet import Bullet
from alien import Alien
from music import *

def check_keydown_events(event,ai_settings,screen,ship,bullets):
    """响应按键"""
    if event.key == pygame.K_RIGHT:  #➡键向右移动
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:  #⬅键向左移动
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:  #空格键发射子弹
        fire_bullet(ai_settings,screen,ship,bullets)
        laugh_sound()  #发射音效
    elif event.key == pygame.K_q:  #q键退出游戏
        sys.exit()
    elif event.key == pygame.K_y:  #y键暂停背景音乐
        pygame.mixer.music.pause()
    elif event.key == pygame.K_u:  #u键继续背景音乐
        pygame.mixer.music.unpause()

def check_keyup_events(event,ship):
    """响应松开"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False

def check_events(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets):
    """响应按键和鼠标事件"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event,ai_settings,screen,ship,bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event,ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x,mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets,mouse_x,mouse_y)

def check_play_button(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets,mouse_x,mouse_y):
    """在玩家单击play按钮时开始游戏"""
    button_clicked = play_button.rect.collidepoint(mouse_x,mouse_y)
    if button_clicked and not stats.game_active:
        ai_settings.initialize_dynamic_settings()  #重置游戏设置
        pygame.mouse.set_visible(False)  #隐藏光标
        
        stats.reset_stats()  #重置游戏统计信息
        stats.game_active = True

        sb.prep_score()  #重置记分牌图像
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()

        aliens.empty()  #清空外星人
        bullets.empty()  #清空子弹

        create_fleet(ai_settings,screen,ship,aliens)  #创建一群新的外星人
        ship.center_ship()  #让飞船居中
        

def update_screen(ai_settings,screen,stats,sb,ship,aliens,bullets,play_button):
    """更新屏幕上的图像，并切换到新屏幕"""
    #每次循环时都重绘屏幕
    screen.fill(ai_settings.bg_color)  #使用ai_settings访问背景色

    #在飞船和外星人后面重绘所有子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    ship.blitme()  #将飞船绘制到屏幕上
    aliens.draw(screen)  #将外星人绘制到屏幕上
    sb.show_score()  #显示得分

    if not stats.game_active:
        play_button.draw_button()  #如果游戏处于非活动状态，就绘制play按钮

    pygame.display.flip()  #让最近的绘制屏幕可见

def fire_bullet(ai_settings,screen,ship,bullets):
    """如果还没有达到限制，就发射一颗子弹"""
    #创建一颗子弹，并将其加入到编组bullets中
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings,screen,ship)
        bullets.add(new_bullet)

def update_bullets(ai_settings,screen,stats,sb,ship,aliens,bullets):
    """更新子弹的位置，并删除已消失的子弹"""
    bullets.update()  #更新子弹的位置
    for bullet in bullets.copy():  #删除已消失的子弹
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collisions(ai_settings,screen,stats,sb,ship,aliens,bullets)

def check_bullet_alien_collisions(ai_settings,screen,stats,sb,ship,aliens,bullets):
    """响应子弹和外星人的碰撞，删除相应的子弹和外星人"""
    collisions = pygame.sprite.groupcollide(bullets,aliens,True,True)
    if collisions :
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats,sb)  #检测是否为最高分
        boom_sound()  #爆炸音效

    if len(aliens) == 0:
        bullets.empty()  #删除现有子弹
        ai_settings.increase_speed()  #加快游戏速度

        stats.level += 1  #提高等级
        sb.prep_level()  #显示新等级
        if stats.level < 10:
            create_fleet(ai_settings,screen,ship,aliens)  #新建一群外星人
        elif stats.level >= 10:
            n_create_fleet(ai_settings,screen,ship,aliens)  #新建一群高级外星人

def create_alien(ai_settings,screen,aliens,alien_number,row_number):
    """创建一个外星人并将其放在当前行"""
    alien = Alien(ai_settings,screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)

def create_fleet(ai_settings,screen,ship,aliens):
    """创建外星人群"""
    #创建一个外星人，并计算每行可以容纳多少个外星人
    alien = Alien(ai_settings,screen)
    number_aliens_x = get_number_aliens_x(ai_settings,alien.rect.width)
    number_rows = get_number_rows(ai_settings,ship.rect.height,alien.rect.height)

    #创建外星人群
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings,screen,aliens,alien_number,row_number)
       
def get_number_aliens_x(ai_settings,alien_width):
    """计算每行可容纳多少个外星人"""
    available_space_x = ai_settings.screen_width - 3 * alien_width
    number_aliens_x = int(available_space_x / (3 * alien_width))
    return number_aliens_x

def get_number_rows(ai_settings,ship_height,alien_height):
    """计算屏幕可容纳多少行外星人"""
    available_space_y = (ai_settings.screen_height -(4 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows

def check_fleet_edges(ai_settings,aliens):
    """有外星人到达边缘时采取相应的措施"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings,aliens)
            break
    
def change_fleet_direction(ai_settings,aliens):
    """"将整群外星人下移，并改变它们的方向"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

def check_aliens_bottom(ai_settings,screen,stats,sb,ship,aliens,bullets):
    """检测是否有外星人到达屏幕底端"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            ship_hit(ai_settings,screen,stats,sb,ship,aliens,bullets)
            break

def update_aliens(ai_settings,screen,stats,sb,ship,aliens,bullets):
    """检查是否有外星人位于屏幕边缘，并更新整群外星人的位置"""
    check_fleet_edges(ai_settings,aliens)
    aliens.update()

    if pygame.sprite.spritecollideany(ship,aliens):  #检测外星人和飞船之间的碰撞
        ship_hit(ai_settings,screen,stats,sb,ship,aliens,bullets)

    check_aliens_bottom(ai_settings,screen,stats,sb,ship,aliens,bullets)

def ship_hit(ai_settings,screen,stats,sb,ship,aliens,bullets):
    """响应被外星人撞到的飞船"""
    if stats.ships_left > 0:
        stats.ships_left -= 1  #将ships_left减1
        sb.prep_ships()
        aliens.empty()  #清空外星人列表
        bullets.empty()  #清空子弹列表
        create_fleet(ai_settings,screen,ship,aliens)  #创建一群新的外星人
        ship.center_ship  #将飞船放到屏幕底端中央
        sleep(0.5)  #暂停
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)  #显示光标

def check_high_score(stats,sb):
    """检测是否诞生了新的最高分"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()

    if pygame.K_q:
        #将最高分写入文件
        high = 'high_score.json'
        high_score = stats.high_score
        with open(high,'w') as f_obj:
            json.dump(high_score,f_obj)

def n_create_fleet(ai_settings,screen,ship,aliens):
    """创建高级外星人群"""
    #创建一个外星人，并计算每行可以容纳多少个外星人
    alien = Alien(ai_settings,screen)
    number_aliens_x = n_get_number_aliens_x(ai_settings,alien.rect.width)
    number_rows = n_get_number_rows(ai_settings,ship.rect.height,alien.rect.height)

    #创建外星人群
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings,screen,aliens,alien_number,row_number)
       
def n_get_number_aliens_x(ai_settings,alien_width):
    """计算每行可容纳多少个高级外星人"""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x

def n_get_number_rows(ai_settings,ship_height,alien_height):
    """计算屏幕可容纳多少行高级外星人"""
    available_space_y = (ai_settings.screen_height -(3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows