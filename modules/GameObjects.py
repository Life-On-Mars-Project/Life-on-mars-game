import pygame, random
from pygame.locals import *
import pygame.sprite as sprite

GRAVITY = 2.7



class Player(sprite.Sprite):
    def __init__(self, images, skin):
        #Init
        sprite.Sprite.__init__(self)
        self.walk_frames = [str(skin)+'Walk'+str(x) for x in range(3)]
        self.jump_frames = [str(skin)+'Jump'+str(x) for x in range(12)]
        self.crouch_frames = [str(skin)+'Crouch'+str(x) for x in range(11)]
        self.image = self.walk_frames[0]
        self.rect = images[self.image].get_rect()
        self.rect.inflate_ip(-25, 0)
        self.rect.move_ip(150, 630)
            #hitbox
        self.generateHitbox()

        #Movement variables
        self.vel = 0
        self.landed = False
        self.in_hole = False
        self.crouching = False
        self.cd_crouch = 10
        self.duration_crouch = 45
        self.count_crouch = self.cd_crouch + self.duration_crouch

        #Animation variables
        self.animation_count = 0
        self.animation_queue = []
        self.curr_frame_count = 0

    def update(self, screen, ia):
        self.rect.move_ip(0, self.vel)
        self.hitbox.move_ip(0, self.vel)
        #Gravity
        if not self.landed and self.vel < 25:
            self.vel += GRAVITY
        #Colision test
        self.collide()
        #Walk animation
        if not ia:
            self.animate()
        #cooldown
        self.count_crouch += 1
        if self.crouching and self.count_crouch > self.duration_crouch:
            self.endCrouch()

            #Pourmontrer la hitbox
        #pygame.draw.rect(screen, (0,255,255), self.hitbox, 2)
        #pygame.draw.rect(screen, (0,255,0), self.rect, 2)

    def animate(self):
        self.animation_count += 1
        if not self.animation_queue:
            #Walking cycle
            if self.animation_count > 1:
                self.animation_count = 0
                self.walk_frames.append(self.walk_frames.pop(0))
                self.image = self.walk_frames[0]
        else:
            #Rolls through the queue once when frames are added
            if self.animation_count > 2:
                self.animation_count = 0
                self.image = self.animation_queue[0]
                self.animation_queue.pop(0)


    def jump(self):
        if self.landed:
            self.endCrouch()
            self.vel -= 35
            self.landed = False
            self.animation_queue = []
            self.animation_queue += self.jump_frames

    def endCrouch(self):
        self.crouching = False
        self.generateHitbox()

    def startCrouch(self):
        if self.count_crouch > self.duration_crouch + self.cd_crouch and not self.crouching:
            self.count_crouch = 0
            self.crouching = True
            self.hitbox.inflate_ip(0, -(self.hitbox.h//2))
            self.hitbox.move_ip(0, self.hitbox.h//2)
            self.animation_queue = []
            self.animation_queue += self.crouch_frames

    def collide(self):
        if self.rect.bottom >= 480 and not self.in_hole:
            self.land(480)
        else:
            self.in_hole = False

    def land(self, top):
        self.rect.bottom = top
        self.hitbox.bottom = top-30
        self.landed = True
        self.vel = 0

    def generateHitbox(self):
        self.hitbox = self.rect.inflate(-110,-100)
        self.hitbox.move_ip(0,-30)

class Obstacle():
    def __init__(self, ob_type, image, surface):
        self.ob_type = ob_type
            #CrÃƒÆ’Ã‚Â©ation image et hit box
        self.image = image
        self.rect = surface.get_rect(left=(1370-(surface.get_width()//2)))

            #DifÃƒÆ’Ã‚Â©renciation des obstacles
        if self.ob_type == 'spike':
            self.rect.move_ip(0, 440-self.rect.h)
            self.hitbox = self.rect.inflate(-15, -10)
            self.hitbox.move_ip(10, 5)
            self.type_val = 50

        if self.ob_type == 'pit':
            self.rect.move_ip(0, 440)
            self.hitbox = self.rect.inflate(-100, 0)
            self.hitbox.move_ip(10, 0)
            self.type_val = 25

        if self.ob_type == 'arch':
            self.rect.move_ip(0,470-self.rect.h)
            self.hitbox = self.rect.inflate(-50, -160)
            self.hitbox.move_ip(30, -80)
            self.type_val = -10


    def update(self, screen, speed, showHB = True):
        self.rect.move_ip(speed,0)
        self.hitbox.move_ip(speed,0)
        if showHB: #Vérifie si l'on veut ou non afficher les hitbox
            pygame.draw.rect(screen, (40,40,40), self.hitbox)



class Coin():
    def __init__(self, image, surface, X, Y):
            #CrÃ©ation image et get_rect
        self.image = image
        self.rect = surface.get_rect(left=X, top=Y)

    def update(self, speed):
        self.rect.move_ip(speed,0)



class Background :
    def __init__(self, image_name, image, speed_coef):
        self.image = image_name
        self.rects = [image.get_rect(left=0),image.get_rect(left=3307)]
        self.speed_coef = speed_coef

    def update(self, speed):
        for rect in self.rects:
            rect.move_ip(speed*self.speed_coef,0)
            if rect.right <= 0:
                rect.move_ip(6614,0)


class Particule:
    def __init__(self, pos, life_span, Rxmin,Rxmax, Rymin,Rymax, Modx,Mody, Divx,Divy):
        self.rect = pygame.Rect((pos[0]+10, pos[1]-60),(1,1))

        self.velx = (random.uniform(Rxmin,Rxmax)+Modx)
        if Divx != 0:
            self.velx = self.velx//Divx

        self.vely = (random.uniform(Rymin,Rymax)+Modx)
        if Divy != 0:
            self.vely = self.vely//Divy

        self.life = 0
        self.life_span = life_span


    def update(self, pos, dico):
        self.life += 1
        if self.life == self.life_span:
            self.life = False
            self.__init__(pos, **dico)
        self.rect.move_ip(self.velx, self.vely)
