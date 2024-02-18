from utils import *
import random

bullet_group = pygame.sprite.Group()
kunai_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

def reset_level():
    bullet_group.empty()
    kunai_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_group.empty()
    enemy_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    data = []
    for row in range(LEVEL_ROWS):
        r = [-1] * LEVEL_COLUMNS
        data.append(r)

    return data

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        self.group = enemy_group
        pygame.sprite.Sprite.__init__(self, self.group)
        self.cycles = {
            'idle': [transform_image(f"images/enemy/Idle/{i}.png", scale) for i in range(0, 5)],
            'jump': [transform_image(f"images/enemy/Jump/{i}.png", scale) for i in range(0, 1)],
            'run': [transform_image(f"images/enemy/Run/{i}.png", scale) for i in range(0, 6)],
            'dead': [transform_image(f"images/enemy/Death/{i}.png", scale) for i in range(0, 8)],
        }

        self.animation_indices = {
            "idle": 0,
            "jump": 0,
            "run": 0,
            "dead": 0,
        }

        self.alive = True
        self.image = self.cycles['idle'][self.animation_indices['idle']]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.update_time = pygame.time.get_ticks()
        self.action_key = 'idle'
        self.moving_left = False
        self.moving_right = False
        self.move_counter = 0
        self.direction = 1
        self.jump = False
        self.in_air = False
        self.y_vel = 0
        self.flip = False
        self.speed = 3
        self.shoot = False
        self.shoot_cooldown = 0
        self.bullet_group = pygame.sprite.Group()
        self.health = 100
        self.idle = False
        self.idle_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.shooting_counter = 40

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.speed = 0
            self.update_action('dead')

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    def update_animation(self):
        self.image = self.cycles[self.action_key][self.animation_indices[self.action_key]]
        if self.animation_indices[self.action_key] < len(self.cycles[self.action_key])-1:
            if pygame.time.get_ticks() - self.update_time > ENEMY_COOLDOWN:
                self.update_time = pygame.time.get_ticks()
                self.animation_indices[self.action_key] += 1
        else:
            if self.action_key == 'dead':
                self.animation_indices[self.action_key] = len(self.cycles[self.action_key])-1
            else:
                self.animation_indices[self.action_key] = 0

    def update_action(self, new_action):
        if new_action != self.action_key:
            self.action_key = new_action
            self.animation_indices[self.action_key] = 0
            self.update_time = pygame.time.get_ticks()

    def update_action_control(self, kunai_group):
        if self.shoot:
            self.shoot_bullet()
        elif self.in_air:
            self.update_action('jump')
        elif self.moving_left or self.moving_right:
            self.update_action('run')
        else:
            self.update_action('idle')

    def shoot_bullet(self, bullet_group, shot_fx):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 60
            bullet = Bullet(self.rect.centerx + (self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            shot_fx.play()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, obstacle_list, level_length):
        screen_scroll = 0
        dx = 0
        dy = 0

        if self.moving_left:
            dx -= self.speed
            self.direction = -1
            self.flip = True
        if self.moving_right:
            dx += self.speed
            self.direction = 1
            self.flip = False

        if self.jump and not self.in_air:
            self.y_vel = -12
            self.jump = False
            self.in_air = True

        self.y_vel += GRAVITY
        if self.y_vel > 10:
            self.y_vel = 10
        dy += self.y_vel

        # Check Collisions with World
        for tile in obstacle_list:
            if(tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height)):
                dx = 0
                self.direction *= -1
                self.move_counter = 0

            if(tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height)):
                if self.y_vel < 0:
                    self.y_vel = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.y_vel >= 0:
                    self.y_vel = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # Update Player Position
        self.rect.x += dx
        self.rect.y += dy

        if (self.rect.right > WIDTH-SCROLL_THRESH and scrolls[1] < (level_length * TILE_SIZE) - WIDTH)\
				or (self.rect.left < SCROLL_THRESH and scrolls[1] > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll

    def ai(self, player, obstacle_list, level_length, shot_fx):
        if self.alive and player.alive:
            if random.randint(1,200) == 1 and not self.idle:
                self.update_action('idle')
                self.idle = True
                self.idle_counter = 50

            # IF AI enemy is near the player
            if self.vision.colliderect(player.rect):
                self.update_action('idle')
                # self.shoot_bullet(bullet_group)
                if self.shooting_counter > 0:
                    self.shooting_counter -= 1
                else:
                    self.shoot_bullet(bullet_group, shot_fx)
                    self.shooting_counter = 20
            else:
                if not self.idle:
                    if self.direction == 1:
                        self.moving_right = True
                    else:
                        self.moving_right = False
                    self.moving_left = not self.moving_right
                    self.move(obstacle_list, level_length)
                    self.update_action('run')
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idle_counter -= 1
                    if self.idle_counter <= 0:
                        self.idle = False

        self.rect.x += scrolls[0]

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        self.group = bullet_group
        pygame.sprite.Sprite.__init__(self, self.group)
        self.image = transform_image("images/icons/bullet.png", 1.2)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.direction = direction
        self.speed = 3

    def update(self, player, obstacle_list):
        self.rect.x += (self.direction * self.speed) + scrolls[0]
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

        for tile in obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 15
                self.kill()

class Kunai(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        self.group = kunai_group
        pygame.sprite.Sprite.__init__(self, self.group)
        self.image = transform_image("images/player/Kunai.png", 0.2)
        if direction == -1:
            self.image = pygame.transform.rotate(self.image, 90)
        else:
            self.image = pygame.transform.rotate(self.image, -90)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.direction = direction
        self.speed = 9

    def update(self, enemy_group, obstacle_list):
        self.rect.x += (self.direction * self.speed) + scrolls[0]
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

        for tile in obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, kunai_group, False):
                if enemy.alive:
                    enemy.health -= 40
                    self.kill()

class ExplodingStar(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        self.group = grenade_group
        pygame.sprite.Sprite.__init__(self, self.group)
        self.image = transform_image("images/icons/grenade.png", 1)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self, player, enemy_group, obstacle_list, grenade_fx):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        self.vel_y += GRAVITY

        for tile in obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed

            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        self.rect.x += dx + scrolls[0]
        self.rect.y += dy

        self.timer -= 1.5
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 1)

            if abs(self.rect.x - player.rect.x) < TILE_SIZE*1.5 and abs(self.rect.y - player.rect.y) < TILE_SIZE*1.5:
                player.health -= 70
            elif abs(self.rect.x - player.rect.x) < TILE_SIZE * 2.5 and abs(self.rect.y - player.rect.y) < TILE_SIZE * 2.5:
                player.health -= 35

            for enemy in enemy_group:
                if abs(self.rect.x - enemy.rect.x) < TILE_SIZE*2 and abs(self.rect.y - enemy.rect.y) < TILE_SIZE*2:
                    enemy.health -= 100
                elif abs(self.rect.x - enemy.rect.x) < TILE_SIZE * 3 and abs(self.rect.y - enemy.rect.y) < TILE_SIZE * 3:
                    enemy.health -= 50


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        self.group = explosion_group
        pygame.sprite.Sprite.__init__(self, self.group)
        self.images = [transform_image(f"images/explosion/exp{i}.png", scale) for i in range(1, 6)]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        self.rect.x += scrolls[0]
        explosion_speed = 4
        self.counter += 1

        if self.counter >= explosion_speed:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]

class Decoration(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        self.group = decoration_group
        pygame.sprite.Sprite.__init__(self, self.group)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x +TILE_SIZE // 2, y + TILE_SIZE - self.image.get_height())

    def update(self):
        self.rect.x += scrolls[0]

class Water(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        self.group = water_group
        pygame.sprite.Sprite.__init__(self, self.group)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x +TILE_SIZE // 2, y + TILE_SIZE - self.image.get_height())

    def update(self):
        self.rect.x += scrolls[0]

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        self.group = exit_group
        pygame.sprite.Sprite.__init__(self, self.group)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x +TILE_SIZE // 2, y + TILE_SIZE - self.image.get_height())

    def update(self):
        self.rect.x += scrolls[0]

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        self.group = item_group
        pygame.sprite.Sprite.__init__(self, self.group)
        self.item_type = item_type
        if self.item_type == 0:
            self.image = transform_image("images/icons/health_box.png", 1)
        elif self.item_type == 1:
            self.image = transform_image("images/icons/ammo_box.png", 1)
        elif self.item_type == 2:
            self.image = transform_image("images/icons/grenade_box.png", 1)
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self, player):
        self.rect.x += scrolls[0]
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 0:
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            if self.item_type == 1:
                player.ammo += 15
            if self.item_type == 2:
                player.grenades_no += 3
            self.kill()

class HealthBar(pygame.sprite.Sprite):
    def __init__(self, x, y, health, max_health):
        pygame.sprite.Sprite.__init__(self)
        self.health = health
        self.max_health = max_health
        self.x = x
        self.y = y

    def draw(self, screen, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 19))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 15))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150*ratio, 15))


class Button():
    def __init__(self, x, y, image):
        width = image.get_width()
        height = image.get_height()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, screen):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action