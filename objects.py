from library import *
import math, random
from abc import ABC, abstractmethod

FPS = 60
WINDOWHEIGHT = 1250//2
WINDOWWIDTH = 2560//2
PSIZE = int(WINDOWHEIGHT/12)
BGCOLOR = WHITE #(200, 200, 200)
SPEED = int(WINDOWHEIGHT/3)
JUMPVEL = -WINDOWHEIGHT*1.2
MAXVEL = WINDOWHEIGHT
G = WINDOWHEIGHT*3.6

#images
spikes_image = pygame.image.load(r'Images\Spikes.png')
shooter_image = pygame.image.load(r'Images\Shooter.png')
bullet_image = pygame.image.load(r'Images\Bullet.png')
pike_image = pygame.image.load(r'Images\Pike.png')

player_image = pygame.image.load(r'Images\Player.png')
player_image = pygame.transform.scale(player_image, (PSIZE, PSIZE))
player_left_image = pygame.image.load(r'Images\Player_left.png')
player_left_image = pygame.transform.scale(player_left_image, (PSIZE, PSIZE))
player_right_image = pygame.transform.flip(player_left_image, True, False)
spikes_image = pygame.transform.scale(spikes_image, (PSIZE, PSIZE))
player_dead_image = pygame.image.load(r'Images\Dead_player.png')
player_dead_image = pygame.transform.scale(player_dead_image, (PSIZE, PSIZE))
background_image = pygame.image.load(r'Images\Background.jpg')
background_image = pygame.transform.scale(background_image, (WINDOWWIDTH, WINDOWHEIGHT))
player_facing_image = {'' : player_image, 'left' : player_left_image, 'right' : player_right_image}


#---------------------------------------------------------------------------------------------------------------------------------------------------------

class Sprite(ABC, pygame.sprite.Sprite):
    
    def set_pos(self, x, y):
        #Makes the position divisible by five
        x = round(x / 5) * 5
        y = round(y / 5) * 5
        self.rect.centerx = max(min(x, WINDOWWIDTH - self.rect.width/2), self.rect.width/2)
        self.rect.centery = max(min(y, WINDOWHEIGHT - self.rect.height/2), self.rect.height/2)

    @abstractmethod
    def resize(self):
        pass
    
    @abstractmethod
    def scale(self):
        pass

    @abstractmethod
    def rotate(self, rotation):
        pass

    @abstractmethod
    def wheel(self, direction):
        pass

    @abstractmethod
    def copy(self):
        pass

    @abstractmethod
    def state(self):
        pass

#Parent classes--------------------------------------------------------------------------------------------------------------------------------------------
class Rectangle(Sprite):
    def __init__(self, x, y, width, height, color, border_color, border_width=9):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        pygame.draw.rect(self.image, border_color, self.image.get_rect(), width=border_width)
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.color = color
        self.border_color = border_color

    def scale(self, width, height):
        width = max(min(width, WINDOWWIDTH), 5)
        height = max(min(height, WINDOWHEIGHT), 5)
        width = min(width, WINDOWWIDTH - self.rect.left)
        height = min(height, WINDOWHEIGHT - self.rect.top)
        self.image = pygame.Surface((width, height))
        self.image.fill(self.color)
        pygame.draw.rect(self.image, self.border_color, self.image.get_rect(), width=9)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

    def resize(self, x, y):
        self.scale(self.rect.width + x, self.rect.height + y)
        
    def rotate(self, rotation):
        center = self.rect.center
        self.resize(self.rect.height - self.rect.width, self.rect.width - self.rect.height)
        self.rect = self.image.get_rect()
        self.set_pos(center[0], center[1])

    def wheel(self, direction):
        if pygame.key.get_pressed()[K_LSHIFT]:
            self.resize(20 * direction, 0)
        else:
            self.resize(0, 20 * direction)
        

    def copy(self):
        return self.__class__(0, 0, self.rect.width, self.rect.height)

    def state(self):
        return f'x={self.rect.x}  y={self.rect.y}  width={self.rect.width}  height={self.rect.height}'


class Square_image(Sprite):
    def __init__(self, x, y, width, rotation, image):
        super().__init__()
        self._image = image
        self.image = pygame.transform.scale(image, (width, width))
        self.image = pygame.transform.rotate(self.image, 360-rotation)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.rotation = rotation
        
    def rotate(self, rotate):
        self.rotation += rotate
        self.rotation = self.rotation % 360
        self.image = pygame.transform.rotate(self.image, -rotate)

    def resize(self, x, y):
        self.scale(self.rect.width + x + y, self.rect.height)

    def scale(self, width, height):
        width = max(min(width, WINDOWHEIGHT), 5)
        width = min(min(width, WINDOWWIDTH - self.rect.left), WINDOWHEIGHT - self.rect.top)
        self.image = pygame.transform.scale(self._image, (width, width))
        self.image = pygame.transform.rotate(self.image, 360-self.rotation)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

    def wheel(self, direction):
        if pygame.key.get_pressed()[K_LSHIFT]:
            self.resize(20 * direction, 0)
        else:
            self.resize(0, 20 * direction)

    def copy(self):
        return self.__class__(0, 0, self.rect.width, self.rotation)

    def state(self):
        return f'x={self.rect.x}  y={self.rect.y}  width={self.rect.width}  rotation={self.rotation}'

#Attributes----------------------------------------------------------------------------------------------------------------------------------------------
class Physical():
    def interaction(self, player, face):
        if face == 'right' or face == 'left':
            player.sliding = True
            player.by_wall = True
            player.sliding_vel = self.glide
            if self.jumpable:
                player.can_jump = True
        if face == 'right':
            player.pos.x = self.rect.right
        if face == 'left':
            player.pos.x = self.rect.left - player.rect.width
        if face == 'top':
            player.pos.y = self.rect.top
            player.can_jump = True
            player.standing = True
            player.new_vel.y = 0
        if face == 'bottom':
            player.pos.y = self.rect.bottom + player.rect.height
            player.new_vel.y = 0


class Jumpable():
    
    def interaction(self, player, face):
        if face == 'top' and not pygame.key.get_pressed()[K_DOWN]:
            player.pos.y = self.rect.top
            player.can_jump = True
            player.standing = True
            player.new_vel.y = 0


#Objects------------------------------------------------------------------------------------------------------------------------------------------------
class Block(Rectangle, Physical):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, GREY, DARK_GREY)
        self.glide = 150
        self.jumpable = True
        

class Ice(Rectangle, Physical):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, LIGHT_BLUE, BLUE)
        self.glide = 900
        self.jumpable = True

        
class Lava(Rectangle):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, RED, RED)
        

class Sticky(Rectangle, Physical):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, YELLOW, DARK_YELLOW)
        self.glide = 0
        self.jumpable = True


class Platform(Rectangle, Jumpable):
    def __init__(self, x, y, width):
        super().__init__(x, y, width, 20, BROWN, DARK_BROWN)

    def resize(self, x, y):
        self.scale(self.rect.width + x, self.rect.height)

    def wheel(self, direction):
        if pygame.key.get_pressed()[K_LSHIFT]:
            pass
        else:
            self.resize(20 * direction, 0)

    def rotate(self, rotation):
        pass

    def copy(self):
        return Platform(0, 0, self.rect.width)


class Moving_platform(Rectangle, Jumpable):
    def __init__(self, x, y, width, distance, angle, vel):
        super().__init__(x, y, width, 20, BROWN, DARK_BROWN)
        self.angle = angle
        self.vel = vel
        self.start = vec(x, y)
        self.pos = vec(x, y)
        self.distance = distance
        self.direction = vec(math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle)))

        self.attachments = pygame.sprite.Group()

    def update(self, sprites, player):
        
        is_inside_player = self.rect.colliderect(player.rect)

        x = self.rect.x
        
        self.pos += self.vel*self.direction/FPS
        self.rect.topleft = self.pos

        xmov = self.rect.x - x

        for sprite in self.attachments:
            sprite.pos.x += xmov
            sprite.pos.y = self.rect.top
            sprite.rect.bottomleft = sprite.pos

        self.attachments.remove(player)

        
        #checks if the platform hits the player after moving upwards and calls self.interaction() if true 
        if self.direction.y < 0 and self.rect.colliderect(player.rect) and not is_inside_player:
            
            face = ''
                    
            if self.direction.x == 0:
                face = 'top'
            elif self.direction.x > 0:
                if (abs((self.rect.right - player.rect.left) / (self.direction.x*self.vel)) >
                    abs((self.rect.bottom - player.rect.top) / (self.direction.y*self.vel))):
                    face = 'top'
            elif self.direction.x < 0:
                if (abs((self.rect.left - player.rect.right) / (self.direction.x*self.vel)) >
                    abs((self.rect.bottom - player.rect.top) / (self.direction.y*self.vel))):
                    face = 'top'
                    
            self.interaction(player, face)
        
        if (self.pos - self.start).length_squared() >= self.distance ** 2 or round((self.pos - self.start).length_squared()) == 0:
            self.direction = -self.direction

    def interaction(self, player, face):
        super().interaction(player, face)
        if face == 'top' and not pygame.key.get_pressed()[K_DOWN]:
            self.attachments.add(player)
            

    def resize(self, x, y):
        self.scale(self.rect.width + x, self.rect.height)
        self.distance -= y
        if self.distance < 10:
            self.distance = 10

    def rotate(self, rotation):
        self.angle += rotation
        self.angle = self.angle % 360
        self.direction = vec(math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle)))

    def wheel(self, direction):
        if pygame.key.get_pressed()[K_LSHIFT]:
            self.vel += direction * 10
            if self.vel < 10:
                self.vel = 10
        else:
            self.resize(0, -20 * direction)

    def copy(self):
        return Moving_platform(0, 0, self.rect.width, self.distance, self.angle, self.vel)

    def state(self):
        return f'x={self.rect.x}  y={self.rect.y}  width={self.rect.width}  distance={self.distance}  angle={self.angle}  vel={self.vel}'


class Pike(pygame.sprite.Sprite):
    def __init__(self, cords, rotation, vel):
        super().__init__()
        self.image = pygame.transform.rotate(pike_image, 360-rotation)
        self.rect = self.image.get_rect(topleft=cords)

        self.pos = vec(cords)
        self.vel = vel
        self.moving = True

        self.hitbox = Hitbox(cords[0], cords[1] + 20, 50, 10)
        
    def update(self, sprites, *args):
        if self.moving:
            self.pos.x += self.vel
            self.rect.topleft = self.pos
            self.hitbox.rect.left = self.rect.left

            collision = pygame.sprite.spritecollide(self, sprites.objects(), False)
            if collision and isinstance(collision[0], Physical):
                self.moving = False
                if self.vel > 0:
                    self.rect.right = self.hitbox.rect.right = collision[0].rect.left + 5
                if self.vel < 0:
                    self.rect.left = self.hitbox.rect.left = collision[0].rect.right - 5

            if pygame.sprite.spritecollide(self, sprites.hazards, False):
                sprites.remove(self.hitbox)
                sprites.remove(self)
                del self


class Hitbox(pygame.sprite.Sprite, Jumpable):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.image = pygame.Surface((0, 0))
    
                

class Spikes(Square_image):
    def __init__(self, x, y, width, rotation):
        super().__init__(x, y, width, rotation, spikes_image)


class Shooter(Square_image, Physical):
    def __init__(self, x, y, width, rotation, intervall, vel):
        super().__init__(x, y, width, rotation, shooter_image)
        self.intervall = intervall
        self.rotation = rotation
        self.vel = vel
        self.glide = 150
        self.jumpable = True
        self.counter = random.randint(0, self.intervall)

    def update(self, sprites, *args):
        self.counter += 1
        if self.counter >= self.intervall:
            self.shoot(sprites)
            self.counter = 0

    def shoot(self, sprites):
        bullet = Bullet(self.rotation, self.vel)
        
        if self.rotation == 0:
            bullet.rect.midleft = self.rect.midright
        if self.rotation == 90:
            bullet.rect.midtop = self.rect.midbottom
        if self.rotation == 180:
            bullet.rect.midright = self.rect.midleft
        if self.rotation == 270:
            bullet.rect.midbottom = self.rect.midtop
        bullet.pos = vec(bullet.rect.topleft)
            
        sprites.all_sprites.add(bullet)
        sprites.bullets.add(bullet)
        sprites.hazards.add(bullet)

    def wheel(self, direction):
        if pygame.key.get_pressed()[K_LSHIFT]:
            self.vel += 10*direction
            if self.vel < 10:
                self.vel = 10
        else:
            self.intervall += direction * 6
            if self.intervall < 6:
                self.intervall = 6

    def copy(self):
        return Shooter(0, 0, self.rect.width, self.rotation, self.intervall, self.vel)

    def state(self):
        return super().state() + f'  vel={self.vel}  intervall={self.intervall/FPS}s'

#Sprites that are not apart of the level-------------------------------------------------------------------------------------------------------------------        

class Bullet(pygame.sprite.Sprite):
    def __init__(self, rotation, vel):
        super().__init__()
        self.image = pygame.transform.smoothscale(bullet_image, (15, 15))
        self.rect = self.image.get_rect()
        self.direction = vec(math.cos(math.radians(rotation)), math.sin(math.radians(rotation)))
        self.vel = vel
        self.pos = vec(0, 0)

    def update(self, sprites, *args):
        self.pos += self.vel*self.direction/FPS
        self.rect.topleft = self.pos

        if WINDOWWIDTH < self.pos.x or self.pos.x < 0 or self.pos.y < 0 or self.pos.y > WINDOWHEIGHT:
            sprites.remove(self)
            del self

#Other-----------------------------------------------------------------------------------------------------------------------------------------------------
class Sprites():
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        self.pikes = pygame.sprite.Group()    
        self.bullets = pygame.sprite.Group()

    def remove(self, sprite):
        self.all_sprites.remove(sprite)
        self.hazards.remove(sprite)
        self.pikes.remove(sprite)   
        self.bullets.remove(sprite)

    def objects(self):
        group = pygame.sprite.Group()
        for sprite in self.all_sprites:
            if isinstance(sprite, Physical) or isinstance(sprite, Jumpable):
                group.add(sprite)
        return group

        
class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, text, num):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image = self.image.convert_alpha()
        pygame.draw.rect(self.image, RED, self.image.get_rect())
        self.rect = self.image.get_rect(topleft=(x, y))

        pygame.draw.rect(self.image, DARK_RED, self.image.get_rect(), width=9)
        font = pygame.font.Font(None, width//3)
        textobj = font.render(text, 1, BLACK)
        textrect = textobj.get_rect()
        textrect.center = self.image.get_rect().center
        self.image.blit(textobj, textrect)

        self.num = num

def Key(width, height, key):
    surface = pygame.Surface((width, height))
    rect = surface.get_rect()
    surface.fill(WHITE)
    pygame.draw.rect(surface, GREY, rect, width=5)
    if key:
        font = pygame.font.Font(None, round(width/math.sqrt(len(key))))
        textobj = font.render(key, 1, BLACK)
        textrect = textobj.get_rect()
        textrect.center = rect.center
        surface.blit(textobj, textrect)
    return surface

def Arrow_key(width):
    surface = pygame.Surface((width, width))
    rect = surface.get_rect()
    surface.fill(WHITE)
    pygame.draw.rect(surface, GREY, rect, width=5)
    pygame.draw.line(surface, BLACK, (rect.width // 4, rect.centery), (rect.width // 4 * 3, rect.centery), width=5)
    pygame.draw.line(surface, BLACK, (rect.width // 2, rect.height // 4), (rect.width // 4 * 3, rect.centery), width=5)
    pygame.draw.line(surface, BLACK, (rect.width // 2, rect.height // 4 * 3), (rect.width // 4 * 3, rect.centery), width=5)
    return surface
    
