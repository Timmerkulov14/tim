from pygame import *
from random import randint
from time import time as timer
 
import sys 
import os 

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    elif hasattr(sys, "_MEIPASS2"):
        return os.path.join(sys._MEIPASS2, relative_path)
    else:
        return os.path.join(os.path.abspath("."), relative_path)

image_folder = resource_path(".")

mixer.init()
font.init()


WIDTH = 700
HEIGHT = 500
FPS = 60
SCORE = 0
LOST = 0
MAX_LOST = 20
GOAL = 10
LIFE = 3

background = os.path.join(image_folder, "galaxy.jpg")
img_hero = os.path.join(image_folder, "rocket.png")
img_ufo = os.path.join(image_folder, "ufo.png")
img_bullet = os.path.join(image_folder, "bullet.png")
img_asteroid = os.path.join(image_folder, "asteroid.png")
mus_space = os.path.join(image_folder, "space.ogg")
affect = os.path.join(image_folder, "fire.ogg")

WHITE = (255, 255, 255)
RED = (150, 0, 0)
GREEN = (0, 150, 0)
YELLOW = (150, 150, 0)
 
mixer.music.load(mus_space)
mixer.music.play()
mixer.music.set_volume(0.1)
snd_effect = mixer.Sound(affect)

font_text = font.Font(None, 36)
font_dash = font.Font(None, 50)
text_win = font_dash.render("YOU WIN!", True, GREEN)
text_lose = font_dash.render("YOU LOSE!", True, RED)

window = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Шутер")
background = transform.scale(image.load(background), (WIDTH, HEIGHT))
clock = time.Clock()


class GameSprite(sprite.Sprite):
    def __init__(self, p_image: str, x: int, y: int, w: int, h: int, speed: int):
        super().__init__()
        self.image = transform.scale(image.load(p_image), (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed 

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):

    def update(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < WIDTH - 80:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, 15)
        bullets.add(bullet)

class Enemy(GameSprite):
    def update(self):
        global LOST
        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            self.rect.x = randint(80, WIDTH - 80)
            self.rect.y = 0
            LOST += 1

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            self.rect.x = randint(80, WIDTH - 80)
            self.rect.y = 0

player = Player(img_hero, 5, HEIGHT - 100, 80, 100, 10)

bullets = sprite.Group()
asteroids = sprite.Group()
monsters = sprite.Group()

for i in range(6):
    monster = Enemy(img_ufo, randint(80, WIDTH - 80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)

for i in range(3):
    asteroid = Asteroid(img_asteroid, randint(80, WIDTH - 80), 0, 50, 50, randint(1, 2))
    asteroids.add(asteroid)

run = True
finish = False
rel_time = False
current_bullets = 0

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        if e.type == KEYDOWN:
            if e.key == K_w:
                if current_bullets < 5 and not rel_time:
                    current_bullets += 1
                    player.fire()
                    snd_effect.play()
                if current_bullets >= 5 and not rel_time:
                    last_time = timer()
                    rel_time = True   
 
    if not finish:

        window.blit(background, (0,0))
        
        player.reset()
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)
    
        player.update()
        monsters.update()
        asteroids.update()
        bullets.update()
    
        text_lost = font_text.render("Пропущено: " + str(LOST), True, WHITE)
        text_score = font_text.render("Счёт: " + str(SCORE), True, WHITE)
        window.blit(text_score, (10, 20))
        window.blit(text_lost, (10, 50))

        if rel_time: 
            now_time = timer()

            if now_time - last_time < 3:
                reload = font_dash.render("ПЕРЕЗАРЯДКА...", True, RED)
                window.blit(reload, (100, 420))
            else:
                current_bullets = 0
                rel_time = False


        if sprite.spritecollide(player, monsters, False) or sprite.spritecollide(player, asteroids, False):
            sprite.spritecollide(player, monsters, True)
            sprite.spritecollide(player, asteroids, True)
            LIFE -= 1
        
        if LIFE == 0 or LOST >= MAX_LOST:
            finish = True
            window.blit(text_lose, (200,200))
            mixer.music.stop()

        collides = sprite.groupcollide(monsters, bullets, True, True)

        for collide in collides:
            SCORE += 1
            monster = Enemy(img_ufo, randint(80, WIDTH - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        if SCORE >= GOAL:
            finish = True
            window.blit(text_win, (200,200))
            mixer.music.stop()

        if LIFE == 3:
            life_color = GREEN
        if LIFE == 2:
            life_color = YELLOW
        if LIFE == 1:
            life_color = RED    

        text_life = font_text.render("Жизни: " + str(LIFE), True, life_color)
        window.blit(text_life, (570, 10))

    display.update()
    clock.tick(FPS)