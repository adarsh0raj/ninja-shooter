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

def main():
    global scrolls
    pygame.init()
    mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ninja Shooter")
    clock = pygame.time.Clock()
    level = 1

    # Load Sounds
    pygame.mixer.music.load("audio/music2.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, 0.0, 5000)
    jump_fx = pygame.mixer.Sound("audio/jump.wav")
    jump_fx.set_volume(0.5)
    shot_fx = pygame.mixer.Sound("audio/shot.wav")
    shot_fx.set_volume(0.5)
    grenade_fx = pygame.mixer.Sound("audio/grenade.wav")
    grenade_fx.set_volume(0.5)

    # Create World
    pine1_img = pygame.image.load('images/background/pine1.png').convert_alpha()
    pine2_img = pygame.image.load('images/background/pine2.png').convert_alpha()
    mountain_img = pygame.image.load('images/background/mountain.png').convert_alpha()
    sky_img = pygame.image.load('images/background/sky_cloud.png').convert_alpha()

    # Button images
    start_img = transform_image("images/start_btn.png", 1)
    exit_img = transform_image("images/exit_btn.png", 1)
    restart_img = transform_image("images/restart_btn.png", 1.5)

    data = [[-1]*LEVEL_COLUMNS for i in range(LEVEL_ROWS)]
    with open(f"levels/level{level}.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                data[x][y] = int(tile)

    world = World()
    player, healthbar = world.process(data)

    start_button = Button(WIDTH//2 - 130, HEIGHT//2 - 150, start_img)
    exit_button = Button(WIDTH//2 - 110, HEIGHT//2 + 50, exit_img)
    restart_button = Button(WIDTH//2 - 100, HEIGHT//2 - 50, restart_img)

    start_game = False
    run = True

    while run:
        clock.tick(60)

        if start_game == False:
            screen.fill(BACKGROUND)
            if start_button.draw(screen):
                start_game = True
            if exit_button.draw(screen):
                run = False

        else:
            draw_background(screen, sky_img, mountain_img, pine1_img, pine2_img)
            world.draw(screen)

            healthbar.draw(screen, player.health)
            draw_text(screen, "AMMO: ", 10, 35, 25, WHITE)
            for i in range(player.ammo):
                screen.blit(transform_image("images/icons/bullet.png", 1), (75 + (i * 15), 38))
            draw_text(screen, "GRENADES: ", 10, 55, 25, WHITE)
            for i in range(player.grenades_no):
                screen.blit(transform_image("images/icons/grenade.png", 0.8), (115 + (i * 15), 58))

            # Screen Updates
            player.update()
            player.draw(screen)

            for enemy in enemy_group:
                enemy.ai(player, world.obstacle_list, world.level_length, shot_fx)
                enemy.update()
                enemy.draw(screen)

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

            if player.alive:
                player.update_action_control(kunai_group, shot_fx)
                scrolls[0], level_complete = player.move(world.obstacle_list, world.level_length)
                scrolls[1] -= scrolls[0]

                # if player has reached the end of the level
                if level_complete:
                    level += 1
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
                        draw_text(screen, "YOU WIN!", WIDTH//2 - 150, HEIGHT//2 - 150, 100, RED)
                        if restart_button.draw(screen):
                            scrolls[1] = 0
                            level = 1
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
                if restart_button.draw(screen):
                    scrolls[1] = 0
                    world_data = reset_level()
                    with open(f"levels/level{level}.csv", newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, healthbar = world.process(world_data)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    player.moving_left = True
                if event.key == pygame.K_d:
                    player.moving_right = True
                if event.key == pygame.K_w and player.alive:
                    player.jump = True
                    jump_fx.play()
                if event.key == pygame.K_SPACE:
                    player.shoot = True
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

if __name__ == "__main__":
    main()