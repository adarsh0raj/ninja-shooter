from utils import *
from classes import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)

        self.cycles = {
            'idle': [transform_image(f"images/player/Idle__00{i}.png", scale) for i in range(0, 10)],
            'jump': [transform_image(f"images/player/Jump__00{i}.png", scale) for i in range(0, 10)],
            'attack': [transform_image(f"images/player/Attack__00{i}.png", scale) for i in range(0, 10)],
            'climb': [transform_image(f"images/player/Climb_00{i}.png", scale) for i in range(0, 10)],
            'dead': [transform_image(f"images/player/Dead__00{i}.png", scale) for i in range(0, 10)],
            'glide': [transform_image(f"images/player/Glide_00{i}.png", scale) for i in range(0, 10)],
            'jump_attack': [transform_image(f"images/player/Jump_Attack__00{i}.png", scale) for i in range(0, 10)],
            'jump_throw': [transform_image(f"images/player/Jump_Throw__00{i}.png", scale) for i in range(0, 10)],
            'run': [transform_image(f"images/player/Run__00{i}.png", scale) for i in range(0, 10)],
            'slide': [transform_image(f"images/player/Slide__00{i}.png", scale) for i in range(0, 10)],
            'throw': [transform_image(f"images/player/Throw__00{i}.png", scale) for i in range(0, 10)],
        }

        self.animation_indices = {
            "idle": 0,
            "jump": 0,
            "attack": 0,
            "climb": 0,
            "dead": 0,
            "glide": 0,
            "jump_attack": 0,
            "jump_throw": 0,
            "run": 0,
            "slide": 0,
            "throw": 0
        }
        self.alive = True
        self.image = self.cycles['idle'][self.animation_indices['idle']]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.update_time = pygame.time.get_ticks()
        self.action_key = 'idle'
        self.moving_left = False
        self.moving_right = False
        self.direction = 1
        self.jump = False
        self.in_air = False
        self.y_vel = 0
        self.x_vel = 0
        self.flip = False
        self.speed = 5
        self.shoot = False
        self.ammo = 10
        self.start_ammo = self.ammo
        self.health = 100
        self.max_health = self.health
        self.grenade = False
        self.grenades_no = 5
        self.grenade_thrown = False
        self.slide = False
        self.sliding = False

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.speed = 0
            self.update_action('dead')

    def draw(self, screen):
        if self.action_key == 'slide':
            rect_copy = self.rect.copy()
            rect_copy.y += 10
            screen.blit(pygame.transform.flip(self.image, self.flip, False), rect_copy)
        else:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    def update_animation(self):
        self.image = self.cycles[self.action_key][self.animation_indices[self.action_key]]
        if self.animation_indices[self.action_key] < len(self.cycles[self.action_key])-1:

            if self.action_key == 'throw' or self.action_key == 'jump_throw':
                if pygame.time.get_ticks() - self.update_time > PLAYER_COOLDOWN/4:
                    self.update_time = pygame.time.get_ticks()
                    self.animation_indices[self.action_key] += 1
            else:
                if pygame.time.get_ticks() - self.update_time > PLAYER_COOLDOWN:
                    self.update_time = pygame.time.get_ticks()
                    self.animation_indices[self.action_key] += 1
        else:
            if self.action_key == 'dead':
                self.animation_indices[self.action_key] = len(self.cycles[self.action_key])-1
            elif self.action_key == 'slide':
                self.x_vel = 0
                self.sliding = False
            else:
                self.animation_indices[self.action_key] = 0

    def update_action(self, new_action):
        if new_action != self.action_key:
            self.action_key = new_action
            self.animation_indices[self.action_key] = 0
            self.update_time = pygame.time.get_ticks()

    def update_action_control(self, kunai_group, shot_fx):
        if self.shoot and self.ammo > 0:
            if self.in_air:
                self.update_action('jump_throw')
                if self.image == self.cycles['jump_throw'][9]:
                    self.update_action('jump')
                    self.shoot_kunai(kunai_group, shot_fx)
                    self.shoot = False
            else:
                self.update_action('throw')
                if self.image == self.cycles['throw'][9]:
                    self.update_action('idle')
                    self.shoot_kunai(kunai_group, shot_fx)
                    self.shoot = False

        elif self.grenade and not self.grenade_thrown and self.grenades_no > 0:
            if self.in_air:
                self.update_action('jump_throw')
                if self.image == self.cycles['jump_throw'][9]:
                    self.update_action('jump')
                    grenade = ExplodingStar(self.rect.centerx + (self.rect.size[0] * self.direction), self.rect.top, self.direction)
                    grenade_group.add(grenade)
                    self.grenades_no -= 1
                    self.grenade_thrown = True
            else:
                self.update_action('throw')
                if self.image == self.cycles['throw'][9]:
                    self.update_action('idle')
                    grenade = ExplodingStar(self.rect.centerx + (self.rect.size[0] * self.direction), self.rect.top, self.direction)
                    grenade_group.add(grenade)
                    self.grenades_no -= 1
                    self.grenade_thrown = True

        elif self.in_air:
            self.update_action('jump')
        elif self.sliding and not self.in_air:
            self.update_action('slide')
        elif self.moving_left or self.moving_right:
            self.update_action('run')
        else:
            self.update_action('idle')

    def shoot_kunai(self, kunai_group, shot_fx):
        if self.ammo > 0:
            self.ammo -= 1
            kunai = Kunai(self.rect.centerx + (self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            kunai_group.add(kunai)
            shot_fx.play()

    def update(self):
        self.update_animation()
        self.check_alive()

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

        if self.slide and not self.in_air and not self.sliding:
            self.x_vel = 6 * self.direction
            self.slide = False
            self.sliding = True

        if self.jump and not self.in_air:
            self.y_vel = -12
            self.jump = False
            self.in_air = True

        self.y_vel += GRAVITY
        if self.y_vel > 10:
            self.y_vel = 10

        dx += self.x_vel
        dy += self.y_vel

        # Check Collisions with World
        for tile in obstacle_list:
            if(tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height)):
                dx = 0

            if(tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height)):
                if self.y_vel < 0:
                    self.y_vel = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.y_vel >= 0:
                    self.y_vel = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for water collision
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # Check for exit collision
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        if self.rect.bottom > HEIGHT:
            self.health = 0

        # Edges of screen check
        if self.rect.left + dx < 0 or self.rect.right + dx > WIDTH:
            dx = 0

        # Update Player Position
        self.rect.x += dx
        self.rect.y += dy

        if (self.rect.right > WIDTH-SCROLL_THRESH and scrolls[1] < (level_length * TILE_SIZE) - WIDTH)\
				or (self.rect.left < SCROLL_THRESH and scrolls[1] > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete