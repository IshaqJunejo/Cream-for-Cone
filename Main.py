import pygame
import sys
import random
import csv
import time

pygame.init()

clock = pygame.time.Clock()

WIDTH = 600
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Cream for the Cone')
pygame.display.set_icon(pygame.image.load('Assets/logo.xcf').convert_alpha())

tile_size = int(HEIGHT*2 // 16)
tiles = []

for num in range(15):
    
    img = pygame.image.load(f'Assets/tiles/tile{num}.png').convert_alpha()
    img = pygame.transform.scale(img, (tile_size, tile_size))
    
    tiles.append(img)

img = pygame.image.load('Assets/tiles/tile15.png').convert_alpha()
img = pygame.transform.scale(img, (tile_size, tile_size*2))

tiles.append(img)

lev = 0

jump = pygame.mixer.Sound('Assets/jump.wav')
win = pygame.mixer.Sound('Assets/win.wav')
blip = pygame.mixer.Sound('Assets/blip.wav')
die = pygame.mixer.Sound('Assets/splash.wav')

pygame.mixer.music.load('Assets/lowTempo.wav')

font = pygame.font.Font('freesansbold.ttf', 16)

tutorial = font.render('Find Ice Cream Machine to fill your cone with Cream!', True, (255, 255, 255))


class particles:

    def __init__(self):
        self.list = []
        
    def add(self, x, y):
        pos_x = x
        pos_y = y
        
        vel_x = random.randint(-2, 2)
        vel_y = random.randint(-4, -1)
        
        radius = 5
        
        particle = [[pos_x, pos_y], [vel_x, vel_y], radius]
        
        self.list.append(particle)
        
    def update(self):
        for particle in self.list:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            
            particle[2] -= 0.1
            
            pygame.draw.circle(screen, (125, 125, 125), (particle[0][0], particle[0][1]), particle[2])
            
    def remove(self):
        particle_list = [particle for particle in self.list if particle[2] > 0]
        
        self.list = particle_list


class play:
    
    def __init__(self):
        self.idle = []
        self.run = []
        
        for num in range(4):
            img = pygame.image.load(f'Assets/run{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (img.get_width()*4, img.get_height()*4))
            
            self.run.append(img)
        for num in range(4):
            img = pygame.image.load(f'Assets/idle{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (img.get_width()*4, img.get_height()*4))
            
            self.idle.append(img)

        self.list = self.idle
        
        self.num = 0
        self.count = 0
        self.jump = 1
        self.space = False
        self.flipped = False
        
        self.vel_y = 0
        self.dx = 0
        self.dy = 0
        
        self.image = self.idle[self.num]
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 300
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
    def update(self, dt):
        global game_active, playing
        
        self.dx = 0
        self.dy = 0
        
        dx = 0
        dy = 0
        
        self.count += 1
        
        if self.count >= 6:
            self.count = 0
            self.num += 1
            
        if self.num >= len(self.list):
            self.num = 0
            
        self.vel_y += 1
        
        if self.vel_y >= 20:
            self.vel_y = 20
        
        dy += self.vel_y
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            dx -= 5
            self.flipped = True
            
        if keys[pygame.K_RIGHT]:
            dx += 5
            self.flipped = False
            
        if keys[pygame.K_SPACE] and self.jump > 0 and self.space == False:
            self.vel_y = -20
            self.jump -= 1
            self.space = True
            jump.play()
            
            for num in range(15):
                polish.add(self.rect.centerx, self.rect.bottom)
                
        elif keys[pygame.K_SPACE] == False:
            self.space = False
            
        if keys[pygame.K_LEFT] == False and keys[pygame.K_RIGHT] == False:
            self.list = self.idle
            
        else:
            self.list = self.run
            
        if self.rect.x >= 450 and dx >= 0:
            self.rect.x = 450
            self.dx += dx
            
        elif self.rect.x <= 150 and dx < 0:
            self.rect.x = 150
            self.dx += dx
            
        for tile in world.tile_list:
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height) and dy >= 0:
                self.jump = 1
                dy = tile[1].top - self.rect.bottom
                    
            elif tile[1].colliderect(self.rect.x, self.rect.y + dy - 36, self.width, self.height) and dy < 0:
                    dy = tile[1].bottom - self.rect.top
                    
            elif tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                self.dx = 0
                
        if world.tile_list[len(world.tile_list)-1][1].bottom <= 0:
            game_active = False
            
        for tile in world.water:
            if tile[1].colliderect(self.rect):
                game_active = False
                
                die.play()
                
        if self.rect.bottom >= HEIGHT - tile_size and dy > 0:
            self.rect.bottom = HEIGHT - tile_size
            self.dy += dy
            
        if self.rect.y <= 0 and dy < 0:
            self.rect.y = 0
            self.dy += dy
            
        self.image = self.list[self.num]
        
        if self.rect.colliderect(world.machine[1]):
            win.play()
            
            self.image = pygame.image.load('Assets/ice cream2.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            
            self.rect.centerx = world.machine[1].centerx
            self.rect.bottom = world.machine[1].bottom
            
            playing = False
            
        self.rect.x += dx * dt
        self.rect.y += dy * dt
        
        screen.blit(pygame.transform.flip(self.image, self.flipped, False), self.rect)


class level:
    
    def __init__(self, data):
        self.tile_list = []
        self.water = []
        self.tutorial = []
        
        self.machine = 0
        
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if 0 <= tile <= 12:
                    img = tiles[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size
                    tile_data = (img, img_rect)
                    self.tile_list.append(tile_data)
                    
                elif tile > 12 and tile < 15:
                    img = tiles[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size
                    tile_data = (img, img_rect)
                    self.water.append(tile_data)
                    
                elif tile == 15:
                    img = tiles[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = (y * tile_size) - tile_size
                    tile_data = (img, img_rect)
                    self.machine = tile_data

                elif tile == 16:
                    img_rect = pygame.Rect(x * tile_size, y*tile_size - tile_size, 10, 10)
                    self.tutorial.append(img_rect)
                    
    def update(self):
        global r1, r2, r3
        
        for tile in self.tile_list:
            tile[1].x -= player.dx
            tile[1].y -= player.dy
            
        for tile in self.water:
            tile[1].x -= player.dx
            tile[1].y -= player.dy

        for tile in self.tutorial:
            tile.x -= player.dx
            tile.y -= player.dy
            
        r1.x -= player.dx * 0.2
        r2.x -= player.dx * 0.5
        r3.x -= player.dx * 1
        
        if r2.y <= 300:
            pass
        
        else:
            r3.y -= player.dy * 0.4
            r2.y -= player.dy * 0.2
            
        self.machine[1].x -= player.dx
        self.machine[1].y -= player.dy
        
        for particle in polish.list:
            particle[0][0] -= player.dx
            particle[0][1] -= player.dy
        
        if r1.x >= 1200:
            r1.x = 0
            
        elif r1.x <= -1200:
            r1.x = 0
            
        if r2.x >= 900:
            r2.x = 0
            
        elif r2.x <= -900:
            r2.x = 0
            
        if r3.x >= 900:
            r3.x = 0
            
        elif r3.x <= -900:
            r3.x = 0
            
    def draw(self):
        screen.blit(self.machine[0], self.machine[1])
        
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            
        for tile in self.water:
            screen.blit(tile[0], tile[1])

        for tile in self.tutorial:
            screen.blit(tutorial, tile)
            

player = play()

polish = particles()

then = time.time()

r1 = pygame.Rect(0, 0, 10, 10)
r2 = pygame.Rect(0, 250, 10, 10)
r3 = pygame.Rect(0, 300, 10, 10)

game_active = True
playing = True

transition = pygame.image.load('Assets/fall.png').convert_alpha()

counter = 0

def background():
    bg1 = pygame.image.load('Assets/bg1.png').convert_alpha()
    bg1 = pygame.transform.scale(bg1, (bg1.get_width()*4, bg1.get_height()*4))
    
    bg2 = pygame.image.load('Assets/tree2.png').convert_alpha()
    bg2 = pygame.transform.scale(bg2, (bg2.get_width()*3, bg2.get_height()*3))
    
    bg3 = pygame.image.load('Assets/tree1.png').convert_alpha()
    bg3 = pygame.transform.scale(bg3, (bg3.get_width()*3, bg3.get_height()*3))
    
    screen.blit(bg1, r1)
    screen.blit(bg1, (r1.x+1200, r1.y))
    screen.blit(bg1, (r1.x-1200, r1.y))
    
    screen.blit(bg2, r2)
    screen.blit(bg2, (r2.x+900, r2.y))
    screen.blit(bg2, (r2.x-900, r2.y))
    
    screen.blit(bg3, r3)
    screen.blit(bg3, (r3.x+900, r3.y))
    screen.blit(bg3, (r3.x-900, r3.y))


def menu():
    UI = pygame.image.load('Assets/ui.png').convert_alpha()
    UI = pygame.transform.scale(UI, (int(UI.get_width()*3), int(UI.get_height()*3)))
    
    btn1 = pygame.image.load('Assets/start.png').convert_alpha()
    btn1 = pygame.transform.scale(btn1, (int(btn1.get_width()*2.5), int(btn1.get_height()*2.5)))
    
    btn2 = pygame.image.load('Assets/quit.png').convert_alpha()
    btn2 = pygame.transform.scale(btn2, (int(btn2.get_width()*2.5), int(btn2.get_height()*2.5)))

    title = pygame.image.load('Assets/title.png').convert_alpha()
    title = pygame.transform.scale2x(title)
    
    button1 = btn1.get_rect(center = (300, 300))
    button2 = btn2.get_rect(center = (300, 400))

    sfx = True
    
    while True:
        clock.tick(60)
        
        px, py = pygame.mouse.get_pos()
        click = False
        
        screen.fill((135, 206, 235))
        background()
        
        screen.blit(UI, (300-UI.get_width()/2, (300-UI.get_height()/2)+50))
        screen.blit(title, (300-title.get_width()/2, 30))
        screen.blit(btn1, button1)
        screen.blit(btn2, button2)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                    
        if button1.collidepoint((px, py)) and click == False:
            btn1 = pygame.image.load('Assets/start.png').convert_alpha()
            btn1 = pygame.transform.scale(btn1, (int(btn1.get_width()*3), int(btn1.get_height()*3)))
            button1 = btn1.get_rect(center = (300, 300))
            
            if sfx:
                blip.play()
                sfx = False
            
        elif button2.collidepoint((px, py)) and click == False:
            btn2 = pygame.image.load('Assets/quit.png').convert_alpha()
            btn2 = pygame.transform.scale(btn2, (int(btn2.get_width()*3), int(btn2.get_height()*3)))
            button2 = btn2.get_rect(center = (300, 400))
            
            if sfx:
                blip.play()
                sfx = False
            
        else:
            btn1 = pygame.image.load('Assets/start.png').convert_alpha()
            btn1 = pygame.transform.scale(btn1, (int(btn1.get_width()*2.5), int(btn1.get_height()*2.5)))
            button1 = btn1.get_rect(center = (300, 300))
            btn2 = pygame.image.load('Assets/quit.png').convert_alpha()
            btn2 = pygame.transform.scale(btn2, (int(btn2.get_width()*2.5), int(btn2.get_height()*2.5)))
            button2 = btn2.get_rect(center = (300, 400))
            sfx = True

        if button1.collidepoint((px, py)) and click:
            levels()
            
        elif button2.collidepoint((px, py)) and click:
            pygame.quit()
            sys.exit()

        pygame.display.update()


def levels():
    global lev
    
    UI = pygame.image.load('Assets/ui.png').convert_alpha()
    UI = pygame.transform.scale(UI, (int(UI.get_width()*3), int(UI.get_height()*3)))
    title = pygame.image.load('Assets/levels.png').convert_alpha()
    title = pygame.transform.scale2x(title)
    
    icon = pygame.image.load('Assets/icon.png').convert_alpha()
    home = icon.get_rect(topleft = (10, 10))
    
    levs = []
    
    for num in range(0, 6):
        img = pygame.image.load(f'Assets/{num+1}.png').convert_alpha()
        img = pygame.transform.scale2x(img)
        val = num // 3
        img_rect = img.get_rect()
        img_rect.x = (num * img.get_width()* 1.5 - (val*img.get_width()*4.5)) + 168
        img_rect.y = (num//3 * img.get_height()*2) + 208 + 32
        hover = False
        data = [img, img_rect, hover]
        
        levs.append(data)
        
    while True:
        clock.tick(60)
        
        px, py = pygame.mouse.get_pos()
        click = False
        
        screen.fill((135, 206, 235))
        background()
        
        screen.blit(UI, (300 - UI.get_width()/2, (300 - UI.get_height()/2) + 50))
        screen.blit(title, (300 - title.get_width()/2, 20))
        screen.blit(icon, home)
        
        for level in levs:
            screen.blit(level[0], level[1])
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                    
        for level in levs:
            if level[1].collidepoint((px, py)) and click:
                lev = levs.index(level)
                main()
                
            if level[1].collidepoint((px, py)) and click == False:
                level[0] = pygame.image.load(f'Assets/{levs.index(level)+1}.png').convert_alpha()
                level[0] = pygame.transform.scale(level[0], (int(level[0].get_width()*2.5), int(level[0].get_height()*2.5)))
                level[1] = level[0].get_rect(center = (level[1].center))
                
                if level[2] == False:
                    blip.play()
                    level[2] = True
            else:
                level[0] = pygame.image.load(f'Assets/{levs.index(level)+1}.png').convert_alpha()
                level[0] = pygame.transform.scale2x(level[0])
                level[1] = level[0].get_rect(center = (level[1].center))
                level[2] = False
                
        if home.collidepoint((px, py)) and click:
            menu()
            
        pygame.display.update()
        

def main():
    global then, game_active, world, player, counter, lev, playing
    
    world_data = []
    
    for num in range(16):
        r = [-1]*150
        world_data.append(r)
    
    with open(f'Maps/level{lev}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)

    world = level(world_data)
        
    icon = pygame.image.load('Assets/icon.png').convert_alpha()
    home = icon.get_rect(topleft = (10, 10))
    
    pygame.mixer.music.play(-1)
    
    while True:
        clock.tick(60)
        
        now = time.time()
        dt = (now-then) * 60
        then = now
        
        click = False
        px, py = pygame.mouse.get_pos()
        
        if game_active and playing:
            screen.fill((135, 206, 235))
            background()
            
            world.update()
            world.draw()
            
            player.update(dt)
            
            polish.update()
            
            screen.blit(icon, home)
            
        elif playing and game_active == False:
            pygame.mixer.music.stop()
            
            if counter < 100//3:
                counter += 1
                
                world.update()
                world.draw()
                
                for num in range(counter-1):
                    screen.blit(pygame.transform.scale(transition, (WIDTH, HEIGHT)), (0,0))
                    
                screen.blit(icon, home)
                    
            else:
                player = play()
                
                world = level(world_data)
                
                r1 = pygame.Rect(0, 0, 10, 10)
                r2 = pygame.Rect(0, 250, 10, 10)
                r3 = pygame.Rect(0, 300, 10, 10)
                
                counter = 0
                
                game_active = True
                pygame.mixer.music.play(-1)
                
        elif game_active and playing == False:
            if counter < 100//3:
                counter += 1
                screen.blit(pygame.transform.scale(transition, (WIDTH, HEIGHT)), (0,0))
                
            else:
                lev += 1
                world_data = []
                
                for num in range(16):
                    r = [-1]*150
                    world_data.append(r)
                    
                with open(f'Maps/level{lev}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                            
                player = play()
                
                world = level(world_data)
                
                r1 = pygame.Rect(0, 0, 10, 10)
                r2 = pygame.Rect(0, 250, 10, 10)
                r3 = pygame.Rect(0, 300, 10, 10)
                
                playing = True
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                    
        if home.collidepoint((px, py)) and click:
            pygame.mixer.music.stop()
            menu()
                
        pygame.display.update()

menu()
