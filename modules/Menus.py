import pygame, math

current_scene = 0

#Classe des scÃ¨nes pour gÃ©rer les menus
class Scene:
    def __init__(self, image, screen, sound):
        #Variables de classe
        self.image = image
        self.screen = screen
        self.buttons = []
        self.sound = sound
        #Pour Ã©viter d'activer plein de fois la fonction
        self.lastMouseState = 0

    #Permet d'ajouter un bouton Ã  la scÃ¨ne.
    def addButton(self, image, command, pos, dims = None):
        self.buttons.append(Button(image, command, pos, dims))

    #Permet d'afficher les boutons ET l'image de fond
    def displayUI(self):
        #Permet d'afficher l'image de fond de la scÃ¨ne
        if self.image != None:
            self.screen.blit(self.image, (0, 0))
        #Permet d'afficher les boutons de la scÃ¨ne
        for button in self.buttons:
            if button.image != None:
                self.screen.blit(button.image, button.rect)
            #else:
                #pygame.draw.rect(self.screen, (255,0,0), button.rect, 2)




    #VÃ©rifie si les boutons de la scÃ¨nes sont appuyÃ©s
    def checkButtons(self, mouse, playSound = True):
        pos, state = mouse.get_pos(), mouse.get_pressed()
        for button in self.buttons:
            if button.rect.collidepoint(pos) and state[0] and state != self.lastMouseState:
                button.command() #Si appui, active la commande du bouton
                if playSound and self.sound:
                    self.sound.play() #et joue un son
        self.lastMouseState = state

    #Pour certaines scenes il y a besoin de verifier plus d'evenements que les boutons
    def checkEvents(self, event):
        pass

    def cycle(self):
        pass



#Classe des boutons Ã  placer sur les scÃ¨nes
class Button:
    def __init__(self, image, command, pos, dims):
        #Variables de classe
        self.image = image
        self.rect = self.image.get_rect() if image != None else pygame.Rect(pos, dims)
        if self.image != None:
            self.rect.move_ip(pos)
        self.command = command #Commande Ã executer Ã  l'appui du boutton



class Transition:
    def __init__(self, images, app):
        #Variables de classes
        self.images = images
        self.current_image = self.images[0]
        self.rect = self.images[0].get_rect()
        self.app = app

    def start(self, duration, scene, reverse = False):
        #Initialisation des variables
        self.reverse = reverse
        self.duration = duration #DurÃ©e voulue en secondes
        self.counter = 0
        self.scene = scene
        self.app.transition = self
        if self.reverse:
            self.images.reverse()
        #Calcul du nombre d'images par secondes en fonction de la durÃ©e donnÃ©e
        self.delay = (duration*self.app.fps)/len(self.images)
        self.end = math.floor(self.duration*self.app.fps)
        self.half = math.floor((self.duration*self.app.fps)/2)


    def cycle(self):
        global current_scene
        #Affichage de la frame actuelle
        current_scene.displayUI()
        self.app.screen.blit(self.current_image, (0, 0))
        #Changement de l'image aprÃ¨s un dÃ©lai
        if math.floor(self.counter%self.delay) == 0:
            self.current_image = self.images[math.floor((self.counter)//self.delay)]
        self.counter += 1
        #Changement de la scÃ¨ne Ã  la moitiÃ© de la transition
        if self.counter == self.half:
            current_scene = self.scene
        #Fin de la transition
        if self.counter == self.end:
            self.stop()

    def stop(self):
        self.app.transition = 0
        if self.reverse:
            self.images.reverse()
        current_scene.displayUI()
