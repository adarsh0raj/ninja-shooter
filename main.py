from classes import *
from player import *
import csv
from pygame import mixer

class World():
    def __init__(self):
        self.obstacle_list = []
        self.images = []
        for x in range(TILE_TYPES):
            img = pygame.image.load(f"images/tile/{x}.png")
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            self.images.append(img)

    def process(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = self.images[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)

                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(x * TILE_SIZE, y * TILE_SIZE, img)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(x * TILE_SIZE, y * TILE_SIZE, img)
                    elif tile == 15:
                        player = Player(x * TILE_SIZE, y * TILE_SIZE,  0.12)
                        healthbar = HealthBar(10, 10, player.health, player.max_health)
                    elif tile == 16:
                        enemy = Enemy(x*TILE_SIZE, y*TILE_SIZE, 1.65)
                    elif tile == 17:
                        item = Item(x*TILE_SIZE, y*TILE_SIZE, 1)
                    elif tile == 18:
                        item = Item(x*TILE_SIZE, y*TILE_SIZE, 2)
                    elif tile == 19:
                        item = Item(x*TILE_SIZE, y*TILE_SIZE, 0)
                    elif tile == 20:
                        exit = Exit(x*TILE_SIZE, y*TILE_SIZE, img)
                    else:
                        pass

        return player, healthbar

    def draw(self, screen):
        for tile in self.obstacle_list:
            tile[1][0] += scrolls[0]
            screen.blit(tile[0], tile[1])


############################
## Main Program
## Pygame Init and Variables
############################

pygame.init()
mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ninja Shooter")
clock = pygame.time.Clock()
level = 1

# Load Sounds and set volumes
pygame.mixer.music.load("audio/music2.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound("audio/jump.wav")
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound("audio/shot.wav")
shot_fx.set_volume(0.5)
slash_fx = pygame.mixer.Sound("audio/slash.mp3")
slash_fx.set_volume(0.8)
grenade_fx = pygame.mixer.Sound("audio/grenade.wav")
grenade_fx.set_volume(0.5)

# Load Background World Images
pine1_img = pygame.image.load('images/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('images/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('images/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('images/background/sky_cloud.png').convert_alpha()

# Load Button Images
start_img = transform_image("images/start_btn.png", 1)
exit_img = transform_image("images/exit_btn.png", 1)
restart_img = transform_image("images/restart_btn.png", 1.5)

# Load World Data of level 1
data = [[-1]*LEVEL_COLUMNS for i in range(LEVEL_ROWS)]
with open(f"levels/level{level}.csv", newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            data[x][y] = int(tile)

# Create World and Player
world = World()
player, healthbar = world.process(data)

# Initialize Different Menu Buttons
start_button = Button(WIDTH//2 - 130, HEIGHT//2 - 150, start_img)
exit_button = Button(WIDTH//2 - 110, HEIGHT//2 + 50, exit_img)
restart_button = Button(WIDTH//2 - 100, HEIGHT//2 - 50, restart_img)

#create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, RED, 4)
win_fade = ScreenFade(2, YELLOW, 4)

# Game State Variables
start_game = False
start_intro = False
run = True

# Main Game Loop
while run:
    clock.tick(60)

    # Main Menu
    if start_game == False:
        screen.fill(BACKGROUND)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
        draw_controls_text(screen)

    # Game Started
    else:
        # Draw Background, Intro, World, HealthBar and Ammo
        intro_fade.fade(screen)
        draw_background(screen, sky_img, mountain_img, pine1_img, pine2_img)
        world.draw(screen)
        draw_text(screen, "LEVEL: {}".format(level), WIDTH//2 - 50, 20, 40, WHITE)
        healthbar.draw(screen, player.health)
        draw_ammo(screen, player)

        # Player Screen Updates
        player.update()
        player.draw(screen)

        # Enemies Screen Updates
        for enemy in enemy_group:
            enemy.ai(player, world.obstacle_list, world.level_length, shot_fx)
            enemy.update()
            enemy.draw(screen)

        # Groups Screen Updates
        item_group.update(player)
        item_group.draw(screen)
        decoration_group.update()
        decoration_group.draw(screen)
        water_group.update()
        water_group.draw(screen)
        exit_group.update()
        exit_group.draw(screen)
        kunai_group.update(enemy_group, world.obstacle_list)
        kunai_group.draw(screen)
        bullet_group.update(player, world.obstacle_list)
        bullet_group.draw(screen)
        grenade_group.update(player, enemy_group, world.obstacle_list, grenade_fx)
        grenade_group.draw(screen)
        explosion_group.update()
        explosion_group.draw(screen)

        # Screen Updates
        if start_intro:
            if intro_fade.fade(screen):
                start_intro = False
                intro_fade.fade_counter = 0

        # Player Controls and Level Updates
        if player.alive:
            player.update_action_control(kunai_group, shot_fx, slash_fx)
            scrolls[0], level_complete = player.move(world.obstacle_list, world.level_length)
            scrolls[1] -= scrolls[0]

            # If player has reached the end of the level
            if level_complete:
                level += 1
                start_intro = True
                if level <= 2:
                    scrolls[1] = 0
                    world_data = reset_level()
                    with open(f"levels/level{level}.csv", newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, healthbar = world.process(world_data)
                else:
                    scrolls[0] = 0
                    scrolls[1] = 0
                    start_game = False
                    start_intro = False
                    level_complete = False
                    level = 1
                    world_data = reset_level()
                    with open(f"levels/level{level}.csv", newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, healthbar = world.process(world_data)
                    continue

        # If player is dead
        else:
            scrolls[0] = 0
            if death_fade.fade(screen):
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    scrolls[1] = 0
                    world_data = reset_level()
                    with open(f"levels/level{level}.csv", newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, healthbar = world.process(world_data)

    # Player Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                player.moving_left = True
            if event.key == pygame.K_d:
                player.moving_right = True
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_RETURN:
                player.shoot = True
            if event.key == pygame.K_e:
                player.sword_attack = True
            if event.key == pygame.K_q:
                player.grenade = True
            if event.key == pygame.K_LCTRL:
                player.slide = True
            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                player.moving_left = False
            if event.key == pygame.K_d:
                player.moving_right = False
            if event.key == pygame.K_q:
                player.grenade = False
                player.grenade_thrown = False

    pygame.display.update()