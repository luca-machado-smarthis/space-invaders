from PPlay import sprite, mouse, window, keyboard
import math
import random
import operator

gamestate = 0
difficulty = 2

score_entries = []

with open("ranking.txt") as file:
    for line in file:
        line = line.strip()
        entry = list(map(str, line.split(',')))
        entry[0] = int(entry[0])
        score_entries.append(entry)
        score_entries.sort(key=operator.itemgetter(0), reverse=True)

frames = 0
frame_time = 0

mouse = mouse.Mouse()
keyboard = keyboard.Keyboard()

width = 1200
height = 600

janela = window.Window(width, height)

background = sprite.Sprite("galaxy.jpeg")

play = sprite.Sprite("play.png")
play.set_position(width/2-play.width/2, 25)
difficulty_img = sprite.Sprite("difficulty.png")
difficulty_img.set_position(width/2-difficulty_img.width/2, (50+play.height) + 25)
ranking = sprite.Sprite("ranking.png")
ranking.set_position(width/2-ranking.width/2, (50+play.height)*2 + 25)
quit_img = sprite.Sprite("quit.png")
quit_img.set_position(width/2-quit_img.width/2, (50+play.height)*3 + 25)

ship = sprite.Sprite("ship.png")

projectiles_player = []
projectiles_enemy = []
player_lives = []

enemies = []
enemy_direction = 1

easy = sprite.Sprite("play.png")
easy.set_position(width/2-easy.width/2, 25)
normal = sprite.Sprite("play.png")
normal.set_position(width/2-normal.width/2, (50+play.height) + 25)
hard = sprite.Sprite("play.png")
hard.set_position(width/2-hard.width/2, (50+play.height)*2 + 25)

player_shot_cooldown = 0
enemy_shot_cooldown = 0

LU_collision_point = [0, 0]
RB_collision_point = [0, 0]
score = 0

player_invincibility = False
player_invincibility_cooldown = -2000

def generate_enemy_wave(enemies, row, column, v_spread=50, h_spread=50):
    x_pos = 0
    ship.set_position(width / 2 - ship.width / 2, height - 16 - ship.height)
    for i in range(row*column):
        enemy_sprite = sprite.Sprite("enemy.png")
        enemy_sprite.y = h_spread * math.ceil((i + 1) / row)
        enemy_sprite.x = width / 4 + x_pos
        if (i + 1) % row != 0:
            x_pos += v_spread
        else:
            x_pos = 0
        enemies.append(enemy_sprite)
    LU_collision_point[0], LU_collision_point[1] = enemies[0].x-32, enemies[0].y+32
    RB_collision_point[0], RB_collision_point[1] = enemies[-1].x+32, enemies[-1].y+32

    return enemies


while True:
    janela.set_background_color([55,120,160])
    click = mouse.is_button_pressed(1)
    background.draw()
    if gamestate == 0:
        play.draw()
        difficulty_img.draw()
        ranking.draw()
        quit_img.draw()
        if mouse.is_over_object(play) and click:
            enemies = generate_enemy_wave(enemies, 8, 4)
            for i in range (0,3):
                life = sprite.Sprite("ship.png")
                life.set_position(25+i*25, 25)
                player_lives.append(life)
            gamestate = 1
        if mouse.is_over_object(difficulty_img) and click:
            gamestate = 2
        if mouse.is_over_object(ranking) and click:
            gamestate = 3
        if mouse.is_over_object(quit_img) and click:
            janela.close()

    if gamestate == 1:
        player_shot_cooldown += 40000 * janela.delta_time()
        enemy_shot_cooldown += 200 * janela.delta_time()
        if keyboard.key_pressed("esc"):
            gamestate = 0
        ship.draw()
        janela.draw_text(f'score: {score}', width/2, 20)
        ship.move_key_x(250 * janela.delta_time())
        if ship.x < 0 : ship.x = 0
        if ship.x > width-ship.width: ship.x = width-ship.width

        if keyboard.key_pressed("space") and player_shot_cooldown > 100*difficulty:
            player_shot_cooldown = 0
            shot = sprite.Sprite("projectile.png")
            shot.set_position(ship.x, ship.y)
            projectiles_player.append(shot)
        if enemy_shot_cooldown > 200/difficulty and len(enemies) >= 1:
            enemy_shot_cooldown = 0
            shot = sprite.Sprite("projectile.png")
            rnd = random.randint(0, len(enemies)-1)
            shot.set_position(enemies[rnd].x, enemies[rnd].y)
            projectiles_enemy.append(shot)

        for idx, shot in enumerate(projectiles_player):
            shot.move_y(-300 * janela.delta_time())

            if LU_collision_point[0] < shot.x < RB_collision_point[0]:
                for enemy in enemies:
                    if shot.collided(enemy):
                        projectiles_player.remove(shot)
                        enemies.remove(enemy)
                        score += 50
                        break
            shot.draw()
            if shot.y < 0:
                projectiles_player.remove(projectiles_player[idx])

        for idx, shot in enumerate(projectiles_enemy):
            shot.move_y(300 * janela.delta_time())
            if shot.y >= ship.y:
                if shot.collided(ship) and janela.curr_time - player_invincibility_cooldown > 2000:
                    projectiles_enemy.remove(shot)
                    score -= 500
                    player_lives.pop()
                    player_invincibility_cooldown = janela.curr_time
                    ship.x = width/2 - ship.width/2
                    if len(player_lives) == 0:
                        enemies.clear()
                        projectiles_player.clear()
                        player_shot_cooldown = 0
                        enemy_shot_cooldown = 0
                        player_name = input("digite seu nome")
                        with open("ranking.txt", "a") as file:
                            file.write(f'\n{score},{player_name}')
                        score = 0
                        player_invincibility = False
                        player_invincibility_cooldown = 0
                        gamestate = 0
                    break
            shot.draw()
            if shot.y > height:
                projectiles_enemy.remove(projectiles_enemy[idx])

        for enemy in enemies:
            enemy.draw()
            enemy.x += 10 * janela.delta_time() * enemy_direction
            if enemy.x < 0 or enemy.x > width-enemy.width:
                enemy_direction *= -1
                for enemy_ in enemies:
                    enemy_.y += 50
                LU_collision_point[1] += 50
                RB_collision_point[1] += 50
            if enemy.y > ship.y:
                enemies.clear()
                projectiles_player.clear()
                ship.set_position(width/2-ship.width/2, 600)
                player_shot_cooldown = 0
                enemy_shot_cooldown = 0
                score = 0
                player_invincibility = False
                player_invincibility_cooldown = 0
                gamestate = 0
            for life in player_lives:
                life.draw()

        LU_collision_point[0] += 10 * janela.delta_time() * enemy_direction
        RB_collision_point[0] += 10 * janela.delta_time() * enemy_direction
        if len(enemies) <= 0:
            projectiles_player.clear()
            projectiles_enemy.clear()
            player_shot_cooldown = 0
            enemy_shot_cooldown = 0
            player_invincibility = False
            player_invincibility_cooldown = -2000
            difficulty += 0.2
            generate_enemy_wave(enemies, 8, 4)

    if gamestate == 2:
        easy.draw()
        normal.draw()
        hard.draw()
        if mouse.is_over_object(easy) and click:
            difficulty = 1
        if mouse.is_over_object(normal) and click:
            difficulty = 2
        if mouse.is_over_object(hard) and click:
            difficulty = 3
        if keyboard.key_pressed("esc"):
            gamestate = 0

    if janela.delta_time():
        frames += 1
        frame_time += janela.delta_time()
        if frame_time > 1:
            # print(frames)
            frame_time = 0
            frames = 0

    if gamestate == 3:
        for i in range (min(5, len(score_entries))):
            janela.draw_text(f'{i+1} - {score_entries[i][1]} {score_entries[i][0]}', width/2-75, 50, size=24, color=[255,255,0])

        if keyboard.key_pressed("esc"):
            gamestate = 0


    click = False
    janela.update()