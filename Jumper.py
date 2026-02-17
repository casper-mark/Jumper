from objects import *
import time
import csv

#BORDER = 150

class Player(Square_image):
    def __init__(self, cords):
        super().__init__(0, 0, PSIZE, 0, player_image)
        self.rect.bottomleft = (cords[0], cords[1])

        self.pos = vec(cords)
        self.old_pos = vec(cords)
        self.vel = vec(0, 0)
        self.new_vel = vec(0, 0)

        self.sliding_vel = 0

        self.sliding = False
        self.can_jump = False
        self.by_wall = False
        self.standing = False
        self.is_alive = True

        self.facing = ''

    def update(self, sprites, *args):
        
        pressed_keys = pygame.key.get_pressed()

        #If the player holds the up key his momentum will be preserved when pushing against a wall unless its sticky (glide=0)
        if self.sliding and (not pressed_keys[K_UP] or self.sliding_vel == 0):
            self.vel.y = self.sliding_vel
        else:
            self.vel.y += G/FPS
            if self.vel.y > MAXVEL:
                self.vel.y = MAXVEL
            if self.sliding and self.vel.y > self.sliding_vel:
                self.vel.y = self.sliding_vel
                

        self.vel.x = 0
        if pressed_keys[K_LEFT]:
            self.vel.x -= SPEED
            self.by_wall = False
        if pressed_keys[K_RIGHT]:
            self.vel.x += SPEED
            self.by_wall = False
            
        self.old_pos = vec(self.pos)
        self.pos += self.vel/FPS

        self.rect.bottomleft = self.pos
        
        #The player is always assumed to not be standing or sliding. If the player continuously presses against a wall he is sliding
        #Gravity will always press the player downwards and if the player hits a sprite he is standing
        self.sliding = False
        self.standing = False
        
        collisions = pygame.sprite.spritecollide(self, sprites.objects(), False)
        if collisions:
            
            #Since self.vel is used for collision detection the sprites changes this value instead
            self.new_vel = vec(self.vel)
            
            for sprite in collisions:
                #Checks that you are above a platform before colliding with it
                if isinstance(sprite, Jumpable) and not self.old_pos.y <= sprite.rect.top + 1:
                    continue

                face = ''
                    
                if self.vel.x == 0:
                    if self.vel.y > 0:
                        face = 'top'
                    if self.vel.y < 0:
                        face = 'bottom'
                elif self.vel.y == 0:
                    if self.vel.x > 0:
                        face = 'left'
                    if self.vel.x < 0:
                        face = 'right'
                elif self.vel.x > 0 and self.vel.y > 0:
                    if (abs((self.rect.right - sprite.rect.left) / self.vel.x) <
                       abs((self.rect.bottom - sprite.rect.top) / self.vel.y)):
                        face = 'left'
                    else:
                        face = 'top'
                elif self.vel.x > 0 and self.vel.y < 0:
                    if (abs((self.rect.right - sprite.rect.left) / self.vel.x) <
                       abs((self.rect.top - sprite.rect.bottom) / self.vel.y)):
                        face = 'left'
                    else:
                        face = 'bottom'
                elif self.vel.x < 0 and self.vel.y > 0:
                    if (abs((self.rect.left - sprite.rect.right) / self.vel.x) <
                       abs((self.rect.bottom - sprite.rect.top) / self.vel.y)):
                        face = 'right'
                    else:
                        face = 'top'
                elif self.vel.x < 0 and self.vel.y < 0:
                    if (abs((self.rect.left - sprite.rect.right) / self.vel.x) <
                       abs((self.rect.top - sprite.rect.bottom) / self.vel.y)):
                        face = 'right'
                    else:
                        face = 'bottom'
                    
                sprite.interaction(self, face)

            self.vel = vec(self.new_vel)
            self.rect.bottomleft = self.pos

    def jump(self):
        
        #The player can not jump while sliding or while being against a wall in the air
        if self.can_jump and not self.sliding and not (self.by_wall and not self.standing):
            self.vel.y = JUMPVEL
            self.can_jump = False

    def cancel_jump(self):
        if self.vel.y < -400:
            self.vel.y = -400

    def dash(self):
        pass

    def shoot(self, sprites):
        if not self.by_wall:
            if self.facing == 'left':
                pike = Pike((self.rect.left - 25, self.rect.centery), 180, -15)
            else:
                pike = Pike((self.rect.right - 25, self.rect.centery), 0, 15)
                    
            sprites.all_sprites.add(pike)
            sprites.pikes.add(pike)
            sprites.all_sprites.add(pike.hitbox)
            
            #Manages how many sticks can exist at the same time
            if len(sprites.pikes) == 3:
                pike_out = sprites.pikes.sprites()[0]
                sprites.remove(pike_out.hitbox)
                sprites.remove(pike_out)
                del pike_out
                

#Gives a preview of how the level looks over time
def demo(sprites):
    
    #corrects sprites.pos and self.start to the rects positions
    for sprite in sprites.all_sprites:
        if isinstance(sprite, Moving_platform):
            sprite.pos = vec(sprite.rect.topleft)
            sprite.start = vec(sprite.rect.topleft)

    demo = True
                        
    while demo:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_RETURN:
                demo = False

        #The new rectangle is put in place of the player to avoid hit detection
        sprites.all_sprites.update(sprites, Rectangle(-10, -10, 5, 5, BLACK, BLACK))
                                
        dispSurface.blit(background_image, background_image.get_rect())
        sprites.all_sprites.draw(dispSurface)

        pygame.display.update()
        Clock.tick(FPS)

    #Moves the moving platforms back to their start positions corrects their direction
    for sprite in sprites.all_sprites:
        if isinstance(sprite, Moving_platform):
            sprite.rect.topleft = sprite.start
            sprite.direction = vec(math.cos(math.radians(sprite.angle)), math.sin(math.radians(sprite.angle)))

    for sprite in sprites.bullets:
        sprites.remove(sprite)

def load(filename):

    all_templates = []
    import os

    with open(filename, newline='') as file:
        reader = csv.reader(file)
        templates = []
        for row in reader:
            if row == ['end']:
                all_templates.append(templates)
                templates = []
            else:
                templates.append(list(map(int, row)))
    
    sprites = Sprites()
    
    if all_templates:
        player_cords = all_templates[0][0]

        for x, y, width, height in all_templates[1]:
            block = Block(x, y, width, height)
            sprites.all_sprites.add(block)

        for x, y, width, height in all_templates[2]:
            ice = Ice(x, y, width, height)
            sprites.all_sprites.add(ice)
    
        for x, y, width, height in all_templates[3]:
            lava = Lava(x, y, width, height)
            sprites.all_sprites.add(lava)
            sprites.hazards.add(lava)

        for x, y, width, rotation in all_templates[4]:
            spike = Spikes(x, y, width, rotation)
            sprites.all_sprites.add(spike)
            sprites.hazards.add(spike)

        for x, y, width, distance, angle, vel in all_templates[5]:
            moving_platform = Moving_platform(x, y, width, distance, angle, vel)
            sprites.all_sprites.add(moving_platform)

        for x, y, width, height in all_templates[6]:
            sticky = Sticky(x, y, width, height)
            sprites.all_sprites.add(sticky)

        for x, y, width in all_templates[7]:
            platform = Platform(x, y, width)
            sprites.all_sprites.add(platform)

        for x, y, width, rotation, intervall, vel in all_templates[8]:
            shooter = Shooter(x, y, width, rotation, intervall, vel)
            sprites.all_sprites.add(shooter)
    else:
        #Happens if the file is completely empty
        player_cords = (100, WINDOWHEIGHT - 200)

    return sprites, player_cords


def write(filename, sprites, P):
    
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(P.rect.bottomleft)
        writer.writerow(['end'])
        
        #Sorts the sprites by their type
        blocks = pygame.sprite.Group()
        ices = pygame.sprite.Group()
        lavas = pygame.sprite.Group()
        spikes = pygame.sprite.Group()
        moving_platforms = pygame.sprite.Group()
        stickys = pygame.sprite.Group()
        platforms = pygame.sprite.Group()
        shooters = pygame.sprite.Group()

        for sprite in sprites.all_sprites:
            if isinstance(sprite, Block):
                blocks.add(sprite)
            if isinstance(sprite, Ice):
                ices.add(sprite)
            if isinstance(sprite, Lava):
                lavas.add(sprite)
            if isinstance(sprite, Spikes):
                spikes.add(sprite)
            if isinstance(sprite, Moving_platform):
                moving_platforms.add(sprite)
            if isinstance(sprite, Sticky):
                stickys.add(sprite)
            if isinstance(sprite, Platform):
                platforms.add(sprite)
            if isinstance(sprite, Shooter):
                shooters.add(sprite)
        
        for sprite in blocks.sprites():
            writer.writerow([sprite.rect.x, sprite.rect.y, sprite.rect.width, sprite.rect.height])
        writer.writerow(['end'])
        for sprite in ices.sprites():
            writer.writerow([sprite.rect.x, sprite.rect.y, sprite.rect.width, sprite.rect.height])
        writer.writerow(['end'])
        for sprite in lavas.sprites():
            writer.writerow([sprite.rect.x, sprite.rect.y, sprite.rect.width, sprite.rect.height])
        writer.writerow(['end'])
        for sprite in spikes.sprites():
            writer.writerow([sprite.rect.x, sprite.rect.y, sprite.rect.width, sprite.rotation])
        writer.writerow(['end'])
        for sprite in moving_platforms.sprites():
            writer.writerow([sprite.rect.x, sprite.rect.y, sprite.rect.width,
                             sprite.distance, sprite.angle, sprite.vel])
        writer.writerow(['end'])
        for sprite in stickys.sprites():
            writer.writerow([sprite.rect.x, sprite.rect.y, sprite.rect.width, sprite.rect.height])
        writer.writerow(['end'])
        for sprite in platforms.sprites():
            writer.writerow([sprite.rect.x, sprite.rect.y, sprite.rect.width])
        writer.writerow(['end'])
        for sprite in shooters.sprites():
            writer.writerow([sprite.rect.x, sprite.rect.y, sprite.rect.width,
                             sprite.rotation, sprite.intervall, sprite.vel])
        writer.writerow(['end'])   

        
def play(filename):

    deaths = 0
    completed = False

    while not completed:

        sprites, player_cords = load(filename)

        P = Player(player_cords)

        #play_background = pygame.Surface((2560, 1440))
        #play_background.blit(background_image, background_image.get_rect())
        
    
        #Game loop
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return True
                    if event.key == K_UP:
                        P.jump()
                    if event.key == K_LEFT:
                        P.facing = 'left'
                    if event.key == K_RIGHT:
                        P.facing = 'right'
                    if event.key == K_SPACE:
                        P.shoot(sprites)
                if event.type == KEYUP:
                    if event.key == K_UP:
                        P.cancel_jump()

            sprites.all_sprites.update(sprites, P)
            P.update(sprites)
            
            #checks if the player touches deadly objects like spikes and lava
            if pygame.sprite.spritecollide(P, sprites.hazards, False):
                break
            
            #if the player reaches the end he completes the level
            if P.rect.top >= WINDOWHEIGHT:
                break
            
            #if the player falls off the map he dies
            if P.pos.x >= WINDOWWIDTH:
                completed = True
                break
            
            #dispSurface.blit(staticSurface, staticSurface.get_rect())
            dispSurface.fill(BLACK)
            dispSurface.blit(background_image, background_image.get_rect())
            sprites.all_sprites.draw(dispSurface)
            dispSurface.blit(player_facing_image[P.facing], P.rect)

            drawText(50, 1300, f'Deaths: {deaths}', 100, dispSurface, color=WHITE)
            
            pygame.display.update()
            Clock.tick(FPS)

        if not completed:
            #death animation
            dispSurface.fill(BLACK)
            dispSurface.blit(background_image, background_image.get_rect())
            sprites.all_sprites.draw(dispSurface)
            dispSurface.blit(player_dead_image, P.rect)
 
            pygame.display.update()
            time.sleep(0.7)
            
            deaths += 1


def make(filename):

    sprites, player_cords = load(filename)
    
    making = True
    focused_sprite = None
    dragging = False
    
    #rel saves the relative position of the sprite and the mouse which i used when dragging sprites
    #pos tracks the mouses position
    rel = ()
    pos = (WINDOWWIDTH/2, WINDOWHEIGHT/2)
    P = Square_image(player_cords[0], player_cords[1] - PSIZE, PSIZE, 0, player_image)
    
    sprites.all_sprites.add(P)

    while making:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    making = False

                if 49 <= int(ascii(event.key)) <= 56:
                    if event.key == K_1:
                        focused_sprite = Block(0, 0, PSIZE, PSIZE)
                    elif event.key == K_2:
                        focused_sprite = Lava(0, 0, PSIZE, PSIZE)
                    elif event.key == K_3:
                        focused_sprite = Ice(0, 0, PSIZE, PSIZE)
                    elif event.key == K_4:
                        focused_sprite = Spikes(0, 0, PSIZE, 0)
                    elif event.key == K_5:
                        focused_sprite = Platform(0, 0, PSIZE)
                    elif event.key == K_6:
                        focused_sprite = Moving_platform(0, 0, PSIZE, 300, 0, 100)
                    elif event.key == K_7:
                        focused_sprite = Sticky(0, 0, PSIZE, PSIZE)
                    elif event.key == K_8:
                        focused_sprite = Shooter(0, 0, PSIZE, 0, FPS, 200)
                        
                    focused_sprite.set_pos(pos[0], pos[1])
                    rel = (focused_sprite.rect.x - pos[0], focused_sprite.rect.y - pos[1])
                    sprites.all_sprites.add(focused_sprite)

                if event.key == K_RETURN:
                    demo(sprites)

                if focused_sprite:
                    
                    if event.key == K_UP:
                        focused_sprite.set_pos(focused_sprite.rect.centerx, focused_sprite.rect.centery - 5)
                    elif event.key == K_DOWN:
                        focused_sprite.set_pos(focused_sprite.rect.centerx, focused_sprite.rect.centery + 5)
                    elif event.key == K_LEFT:
                        focused_sprite.set_pos(focused_sprite.rect.centerx - 5, focused_sprite.rect.centery)
                    elif event.key == K_RIGHT:
                        focused_sprite.set_pos(focused_sprite.rect.centerx + 5, focused_sprite.rect.centery)

                    if not focused_sprite is P:
                
                        if event.key == K_e:
                            if isinstance(focused_sprite, Moving_platform):
                                focused_sprite.rotate(5)
                            else:
                                focused_sprite.rotate(90)
                        elif event.key == K_q:
                            if isinstance(focused_sprite, Moving_platform):
                                focused_sprite.rotate(-5)
                            else:
                                focused_sprite.rotate(-90)
                    
                        elif event.key == K_a:
                            focused_sprite.resize(-5, 0)
                        elif event.key == K_d:
                            focused_sprite.resize(5, 0)
                        elif event.key == K_s:
                            focused_sprite.resize(0, 5)
                        elif event.key == K_w:
                            focused_sprite.resize(0, -5)

                        elif event.key == K_c:
                            focused_sprite = focused_sprite.copy()
                            sprites.all_sprites.add(focused_sprite)
                            focused_sprite.set_pos(pos[0], pos[1])
                            rel = (focused_sprite.rect.x - pos[0], focused_sprite.rect.y - pos[1])
                        elif event.key == K_SPACE:
                            sprites.remove(focused_sprite)
                            focused_sprite = None

            if event.type == MOUSEWHEEL and focused_sprite and not focused_sprite is P:
                focused_sprite.wheel(event.y)
                    
            if event.type == MOUSEMOTION:
                pos = event.pos
                if dragging and focused_sprite:
                    focused_sprite.set_pos(pos[0] + rel[0], pos[1] + rel[1])

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                for sprite in sprites.all_sprites.sprites():
                    
                    #if the player clicks on a sprite it will become focused and the relative positions is saved
                    if sprite.rect.collidepoint(event.pos):
                        
                        focused_sprite = sprite
                        dragging = True
                        rel = (focused_sprite.rect.centerx - event.pos[0], focused_sprite.rect.centery - event.pos[1])

            if event.type == MOUSEBUTTONUP and event.button == 1:
                dragging = False

        dispSurface.blit(make_background, make_background.get_rect())
        sprites.all_sprites.draw(dispSurface)
        
        #draws the hightlighting and state of the focused sprite
        if focused_sprite:
            drawText(30, WINDOWHEIGHT + 30, focused_sprite.state(), 50, dispSurface, color=WHITE)
            draw_rect(dispSurface, GREEN, focused_sprite.rect, width=1)
            
        #draws the line for the moving platfoms
        for sprite in sprites.all_sprites.sprites():
            if isinstance(sprite, Moving_platform):
                pygame.draw.line(dispSurface, GREEN, sprite.rect.center,
                                 sprite.rect.center + sprite.direction*sprite.distance, width=3)
        pygame.display.update()

    #saves the level
    write(filename, sprites, P)


def main():
    dispSurface.fill(BLACK)
    
    #creates all the buttons
    level_buttons = pygame.sprite.Group()
    mode_buttons = pygame.sprite.Group()
    
    for i in range(2):
        for j in range(5):
            button = Button(WINDOWWIDTH/2 - 250 + j*100, WINDOWHEIGHT/2 + 50*i, 100, 50, f'Level {i*5 + j + 1}', i*5 + j + 1)
            level_buttons.add(button)
    mode_buttons.add(Button(WINDOWWIDTH/2 - 200 - 100, 500, 200, 100, 'Play', 1))
    mode_buttons.add(Button(WINDOWWIDTH/2 + 100, 500, 200, 100, 'Edit', 2))
    
    #mode represents the gamemode where 1 is make and 2 is play
    mode = 0
    level = 1
    choosing = True
    
    #has the player choose mode and level
    while choosing:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                for button in level_buttons:
                    if mode != 0:
                        if button.rect.collidepoint(event.pos):
                            level = button.num
                            choosing = False
        
                for button in mode_buttons:
                    if button.rect.collidepoint(event.pos):
                        mode = button.num

        dispSurface.blit(background_image, background_image.get_rect())
        if mode != 0:
            level_buttons.draw(dispSurface)
        mode_buttons.draw(dispSurface)
        if mode == 1:
            drawText((WINDOWWIDTH-200)/2, 100, 'Play', 200, dispSurface)
        if mode == 2:
            drawText((WINDOWWIDTH-200)/2, 100, 'Edit', 200, dispSurface)
        pygame.display.update()

    pygame.display.set_caption('Level ' + str(level))

    filename = r'Levels/level_' + str(level) + '.csv'
    print(filename)
    
    if mode == 2:
        make(filename)
    else:
        play(filename)


if __name__ == '__main__':

    pygame.init()

    Clock = pygame.time.Clock()

    #The static background in make gamemode
    make_background = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT + 100))
    make_background.fill(BLACK)
    make_background.blit(background_image, background_image.get_rect())
    
    arrow_key = Arrow_key(40)


    #draws the numbers with the corresponding sprite
    size = 50//2
    for i in range(8):
        drawText((30 + i*150)/2, WINDOWHEIGHT + 130//2, str(i + 1), size, make_background, color=WHITE)
    draw_rect(make_background, GREY, Rect(90/2, WINDOWHEIGHT + 120/2, size, size))
    draw_rect(make_background, RED, Rect(240/2, WINDOWHEIGHT + 120/2, size, size))
    draw_rect(make_background, LIGHT_BLUE, Rect(390/2, WINDOWHEIGHT + 120/2, size, size))
    make_background.blit(pygame.transform.scale(spikes_image, (size, size)), Rect(540/2, WINDOWHEIGHT + 120/2, size, size))
    draw_rect(make_background, BROWN, Rect(690/2, WINDOWHEIGHT + 140/2, size, 10))
    draw_rect(make_background, BROWN, Rect(840/2, WINDOWHEIGHT + 140/2, size, 10))
    pygame.draw.line(make_background, GREEN, (864/2, WINDOWHEIGHT + 144/2), (904/2, WINDOWHEIGHT + 144/2))
    draw_rect(make_background, YELLOW, Rect(990/2, WINDOWHEIGHT + 120/2, size, size))
    make_background.blit(pygame.transform.scale(shooter_image, (size, size)), Rect(1140/2, WINDOWHEIGHT + 120/2, size, size))

    #draws the arrow keys     
    make_background.blit(arrow_key, arrow_key.get_rect(topleft=(int(WINDOWWIDTH/2)+60, WINDOWHEIGHT + 50)))
    make_background.blit(pygame.transform.rotate(arrow_key, 90), arrow_key.get_rect(topleft=(int(WINDOWWIDTH/2)+60, WINDOWHEIGHT+10)))
    make_background.blit(pygame.transform.rotate(arrow_key, 180), arrow_key.get_rect(topleft=(int(WINDOWWIDTH/2)+20, WINDOWHEIGHT + 50)))
    make_background.blit(pygame.transform.rotate(arrow_key, 270), arrow_key.get_rect(topleft=(int(WINDOWWIDTH/2)+60, WINDOWHEIGHT+50)))
    drawText(WINDOWWIDTH/2+170, WINDOWHEIGHT+50, 'Move', size , make_background, color=WHITE)

    keysize=40/2
    #draws the keys
    make_background.blit(Key(keysize, keysize, 'a'), Rect(int(WINDOWWIDTH*0.625), int(WINDOWHEIGHT*1.04), keysize, keysize))
    make_background.blit(Key(keysize, keysize, 's'), Rect(int(WINDOWWIDTH*0.64), int(WINDOWHEIGHT*1.04), keysize, keysize))
    make_background.blit(Key(keysize, keysize, 'd'), Rect(int(WINDOWWIDTH*0.66), int(WINDOWHEIGHT*1.04), keysize, keysize))
    make_background.blit(Key(keysize, keysize, 'w'), Rect(int(WINDOWWIDTH*0.64), int(WINDOWHEIGHT*1.01), keysize, keysize))
    drawText(int(WINDOWWIDTH*0.684), int(WINDOWHEIGHT*1.04), 'Scale', size , make_background, color=WHITE)

    make_background.blit(Key(keysize, keysize, 'q'), Rect(int(WINDOWWIDTH*0.74), int(WINDOWHEIGHT*1.04), keysize, keysize))
    make_background.blit(Key(keysize, keysize, 'e'), Rect(int(WINDOWWIDTH*0.76), int(WINDOWHEIGHT*1.04), keysize, keysize))
    drawText(int(WINDOWWIDTH*0.785), int(WINDOWHEIGHT*1.04), 'Rotate', size , make_background, color=WHITE)

    make_background.blit(Key(keysize, keysize, 'c'), Rect(int(WINDOWWIDTH*0.84), int(WINDOWHEIGHT*1.04), keysize, keysize))
    drawText(int(WINDOWWIDTH*0.867), int(WINDOWHEIGHT*1.04), 'Copy', size , make_background, color=WHITE)

    make_background.blit(Key(60/2, 80/2, 'Ent'), Rect(int(WINDOWWIDTH*0.918), int(WINDOWHEIGHT*1.008), 70/2, 100/2))
    drawText(int(WINDOWWIDTH*0.953), int(WINDOWHEIGHT*1.04), 'Demo', size , make_background, color=WHITE)

    make_background.blit(Key(keysize, 30/2, 'Esc'), Rect(int(WINDOWWIDTH*0.508), int(WINDOWHEIGHT*1.10), size, 30/2))
    drawText(int(WINDOWWIDTH*0.53), int(WINDOWHEIGHT*1.10), 'Exit', size , make_background, color=WHITE)

    make_background.blit(Key(100/2, 30/2, ''), Rect(int(WINDOWWIDTH*0.586), int(WINDOWHEIGHT*1.10), 100/2, 30/2))
    drawText(int(WINDOWWIDTH*0.637), int(WINDOWHEIGHT*1.10), 'Del', size , make_background, color=WHITE)

    make_background.blit(Key(80/2, keysize, 'Shift'), Rect(int(WINDOWWIDTH*0.664), int(WINDOWHEIGHT*1.10), 100/2, 30/2))

    #mousewheel, mousewheel shift

    dispSurface = pygame.display.set_mode()
    
    #draws the title screen
    dispSurface.fill(BLACK)
    dispSurface.blit(background_image, background_image.get_rect())
    drawText((WINDOWWIDTH - 1000)/2, (WINDOWHEIGHT-300)/2, 'Jumper', 400, dispSurface, color=PURPLE)
    pygame.display.update()

    wait()

    while True:
        main()

    
