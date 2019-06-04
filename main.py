import sys, pygame, os, time, random
from pygame.locals import *
import tkinter.filedialog as filedialog
import pygame.sprite as sprite
import tkinter as tk
import modules.GameObjects as go
import modules.ia as ia
import modules.Menus as Menus
import modules.Tools as Tools

pygame.init()
pygame.mixer.init()

class App:
    def __init__(self):
        #Initialisation de la fenètre pygame
        self.screen = pygame.display.set_mode((1120, 630))
        pygame.display.set_caption('Life On Mars')

        #Initialisation de l'horloge
        self.clock = pygame.time.Clock()
        self.statswin = 0
        #Initialisation de la police d'écriture
        self.font = pygame.font.SysFont(None, 48)
        self.fontB = pygame.font.SysFont(None, 100)
        #Nombre d'images affichées par secondes
        self.fps = 40
        self.transition = 0

        #Chargement des ressources et des scènes
        self.loadingScreenSetup()
        self.preloadImages()
        self.preloadSounds()
        self.setupScenes()
        self.preloadTransitions()

        #Initialisation de la boucle
        self.eventsLoop()


    def preloadImages(self):
        self.images = {}
        #Chargement des images
        for file in os.listdir("assets/images"):
            #Récupération des tailles dans un fichier texte
            sizes = {}
            if not file.endswith(".txt"):
                with open("assets/images/"+file+".txt") as sizesheet:
                    lines = sizesheet.readlines()
                    for line in lines:
                        temp = line.split(":")
                        sizes[temp[0]] = temp[1].rstrip("\n").split(",")
                #Chargement des images utilisant une fonction personnalisée
                for _file in os.listdir("assets/images/"+file):
                    filename = "assets/images/{}/{}".format(file, _file)
                    name = _file.replace(".png", "")
                    w, h = (int(sizes[name][0]), int(sizes[name][1])) if name in sizes else (0,0)
                    self.images[name] = Tools.load_image(filename, w, h, True)
        self.loadingScreenUpdate()

    def preloadSounds(self):
        self.sounds = {}
        #Chargement des sons
        for file in os.listdir("assets/sounds"):
            name = file.replace(".wav", "")
            self.sounds[name] = pygame.mixer.Sound("assets/sounds/"+file)
        self.sounds['Flute'].play()

    def preloadTransitions(self):
        self.transitions = {}
        #Chargement des sons
        for file in os.listdir("assets/transitions"):
            images = []
            for _file in sorted(os.listdir("assets/transitions/"+file)):
                filename = "assets/transitions/{}/{}".format(file, _file)
                img = Tools.load_image(filename, 1120, 630)
                images.append(img)
            self.transitions[file] = Menus.Transition(images, self)
            self.loadingScreenUpdate()
        self.transitions["loading"].start(1, self.mainMenu)

    def loadingScreenSetup(self):
        self.load_progress = 0
        self.increment = 700/(len(os.listdir("assets/transitions"))+1)
        self.loadingScreen = Tools.load_image("assets/loadingScreen.png", 1120, 630)

    def loadingScreenUpdate(self):
        #Affichage du chargement
        self.load_progress += self.increment
        pygame.draw.rect(self.screen, (0,0,0), (0,0,1120,630))
        pygame.draw.rect(self.screen, (78,192,192), (250,230,self.load_progress,120))
        self.screen.blit(self.loadingScreen, (0, 0))
        pygame.display.update()

    def setupScenes(self):

        #Menu Principal
        self.mainMenu = Menus.Scene(self.images["mainMenu"], self.screen, self.sounds['Boutton'])
        self.mainMenu.addButton(None, self.goToModes, (360, 470), (460, 180))
        self.mainMenu.addButton(None, self.goToOptions, (1020, 0), (100, 100))
        self.mainMenu.addButton(None, self.goToBoard, (920, 430), (200,200))
        self.mainMenu.addButton(None, self.goToMainShop, (0,450), (230,180))
        #Menu des différents modes de jeu
        self.modesMenu = Menus.Scene(self.images["gameModeMenu"], self.screen, self.sounds['Boutton'])
        self.modesMenu.addButton(None, self.goToCountDown, (300, 170), (540, 150))
        self.modesMenu.addButton(None, self.StartTraining, (370, 350), (370, 130))
        self.modesMenu.addButton(None, self.loadIAFile, (300, 500), (540, 150))
        self.modesMenu.addButton(None, lambda: self.goToMainMenu("transition-2", 0.3, True), (1020, 0), (100, 100))

        #Menu des Options
        self.optionsMenu = OptionsScene(self.images["optionsMenu"], self.screen, self, self.sounds['Boutton'])
        self.optionsMenu.addButton(None, self.goToMainMenu, (975,0), (150,125))
        self.optionsMenu.addButton(None, self.optionsMenu.newUpBind, (0, 275), (488,88))
        self.optionsMenu.addButton(None, self.optionsMenu.newCrouchBind, (0, 415), (488,88))
        self.optionsMenu.addButton(None, self.optionsMenu.turnOffSounds, (735, 300), (185,150))

        #Menu LeaderBoard
        self.boardMenu = LeaderBoard(self.images["boardMenu"], self.screen, self, self.sounds['Boutton'])
        self.boardMenu.addButton(None, self.goToMainMenu, (975,0), (150,125))

        #Scene du jeu
        self.gameScene = GameScene(self.images["gameUI"], self.screen, self)
        self.gameScene.addButton(None, self.gameScene.pause, (990, 10), (125, 100))

        #Menu pause mode de jeu de base
        self.pauseMenu = Menus.Scene(self.images["pauseMenu"], self.screen, self.sounds['Boutton'])
        self.pauseMenu.addButton(None, self.gameScene.pause, (360, 280), (470, 125))
        self.pauseMenu.addButton(None, self.gameScene.returnToMain, (410, 435), (365, 105))

        #Menu pause mode de jeu IA
        self.pauseMenuIA = Menus.Scene(self.images["pauseMenu"], self.screen, self.sounds['Boutton'])
        self.pauseMenuIA.addButton(None, self.gameScene.pause, (360, 280), (470, 125))
        self.pauseMenuIA.addButton(None, self.gameScene.returnToMain, (410, 435), (365, 105))
        self.pauseMenuIA.addButton(self.images["saveIABtn"], self.gameScene.saveIA, (965, 400))

        #Menu Défaite
        self.loseScreen = Menus.Scene(self.images["gameOver"], self.screen, self.sounds['Boutton'])
        self.loseScreen.addButton(None, self.gameScene.endScreen, (0, 0), (1120,630))

        #Menu Victoire
        self.winScreen = Menus.Scene(self.images["winScreen"], self.screen, self.sounds['Boutton'])
        self.winScreen.addButton(None, self.gameScene.endScreen, (0, 0), (1120,630))

        #Menu Score apres Gameover
        self.endScore = Menus.Scene(self.images['endScore'], self.screen, self.sounds['Boutton'])
        self.endScore.addButton(None, self.gameScene.returnToMain, (860,410), (260,220))
        self.endScore.addButton(None, self.goToCountDown, (0, 400), (260,230))

        #Menu du compte ÃƒÆ’Ã‚Â  rebours
        self.cdMenu = Menus.Scene(self.images["cdMenu3"], self.screen, self.sounds['Boutton'])

        #Menu shop
        self.shop = Menus.Scene(self.images['MainShop'], self.screen, self.sounds['Boutton'])
        self.shop.addButton(None, self.goToMainMenu, (1000,0),(120,120))
        self.shop.addButton(None, self.goToShop0, (120,200),(220,250))
        self.shop.addButton(None, self.goToShop1, (439,207),(220,250))
        self.shop.addButton(None, self.goToShop2, (750,207),(220,250))
        self.shop.addButton(None, self.resetSkin, (0,0),(165,125))

        #Menu goToShop0
        self.shop0 = Shop(self.images['Shop0'], self.screen, self, 0, 200, self.sounds['Boutton'])
        #Menu goToShop1
        self.shop1 = Shop(self.images['Shop1'], self.screen, self, 1, 200, self.sounds['Boutton'])
        #Menu goToShop
        self.shop2 = Shop(self.images['Shop2'], self.screen, self, 2, 500, self.sounds['Boutton'])

        Menus.current_scene = self.mainMenu
        Menus.current_scene.displayUI()

    def goToBoard(self):
        self.transitions["transition-1"].start(1.2, self.boardMenu)

    def goToDifficulties(self):
        self.transitions["transition-1"].start(1.2, self.mainMenu)

    def goToModes(self):
        #Affiche le menu des modes de jeu
        self.transitions["transition-2"].start(0.3, self.modesMenu)

    def goToCountDown(self):
        #Affiche le compte ÃƒÆ’Ã‚Â  rebours avant la partie
        Menus.current_scene = self.cdMenu
        for i in range(3,-1,-1):
            Menus.current_scene.image = self.images["cdMenu{}".format(i)]
            Menus.current_scene.displayUI()
            pygame.display.update()
            self.clock.tick(1)
        self.StartGame()

    def goToOptions(self):
        #Affiche le menu des options
        self.transitions["transition-1"].start(1.2, self.optionsMenu)
        Menus.current_scene.displayUI()

    def goToMainShop(self):
        self.transitions["transition-1"].start(1.2, self.shop)
        Menus.current_scene.displayUI()

    def goToShop0(self):
        self.transitions["transition-1"].start(1.2, self.shop0)

    def goToShop1(self):
        self.transitions["transition-1"].start(1.2, self.shop1)

    def goToShop2(self):
        self.transitions["transition-1"].start(1.2, self.shop2)

    def resetSkin(self):
        with open('txt_files/Save.txt', 'r') as save:
            save = save.read().split('\n')
        save[5] = 0
        with open('txt_files/Save.txt', 'w') as new_save:
            for line in save:
                if line != '':
                    new_save.write(str(line)+'\n')
        self.gameScene.current_skin = 0

    def goToMainMenu(self, transition = "transition-1", duration = 1.2, reverse = 0):
        #Affiche le menu principal
        self.transitions[transition].start(duration, self.mainMenu, reverse)
        if self.statswin:
            self.statswin.root.destroy()
            self.statswin = 0

    def StartGame(self, forIa = False):
        #Commence la partie
        self.gameScene.gameSetup()
        Menus.current_scene = self.gameScene
        Menus.current_scene.displayUI()

    def StartTraining(self):
        #Ouvre la fenetre de statistiques
        self.statswin = ia.StatsWindow(self)
        self.statswin.root.mainloop()

    def StartIA(self, n, lr):
        self.gameScene.gameSetup()
        self.gameScene.setupIA(n, lr)
        Menus.current_scene = self.gameScene
        Menus.current_scene.displayUI()

    def loadIAFile(self):
        #Fenetre pour choisir une IA contre laquelle jouer
        self.temproot = tk.Tk()
        #Chargement des IA
        path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("TXT (*.txt)","*.txt")])
        if path == "":
            return 0
        with open(path, "r") as file:
            self.loadedIA = file.readlines()
            self.loadedIA =  [el.split(":") for el in self.loadedIA]
        self.loadIAwindow = tk.Toplevel()
        self.loadIAwindow.geometry("600x450+0+0")
        #Création des labels et boutons de la fenetre
        title = tk.Label(self.loadIAwindow, font = ("Arial", 20), bg="#F9F9F9", text="Choisis une IA")
        title.place(relx = 0, rely = 0, relwidth = 1, relheight = 0.1)

        if len(self.loadedIA) > 10:
            cols = (len(self.loadedIA)-1)//10 + 1
            height, split, width = 0.09, True, 1/cols
            xoffset = -1/cols
        else:
            height = 0.9/(len(self.loadedIA))
            split, width, cols = False, 1, 1
            xoffset = 0
        yoffset = 0.1
        for i, e in enumerate(self.loadedIA):
            if split and i%10 == 0:
                xoffset += 1/cols
                yoffset = 0.1
            temp = tk.Button(self.loadIAwindow, font = ("Arial", 20), bg="#F9F9F9", text=self.loadedIA[i][0], command = (lambda x=i: self.startVSIA(x)))
            temp.place(relx = xoffset, rely = yoffset, relwidth = width, relheight = height)
            yoffset += height
        self.loadIAwindow.mainloop()

    def startVSIA(self, i):
        self.temproot.destroy()
        brain = ia.NeuralNetwork.fromText(self.loadedIA[i][1])
        self.gameScene.gameSetup()
        self.gameScene.setupIA(2, 0, brain)
        Menus.current_scene = self.gameScene
        Menus.current_scene.displayUI()

    def eventsLoop(self):
        while True:
            #Récupération des évenements et de la souris
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                Menus.current_scene.checkEvents(event)
            mouse = pygame.mouse

            #Affichage de la scène
            if not self.transition:
                Menus.current_scene.checkButtons(mouse, self.optionsMenu.toggleSound)
                Menus.current_scene.cycle()

            # Affichage de la transition
            if self.transition:
                self.transition.cycle()

            # Raffraichissement du canvas
            pygame.display.update()
            self.clock.tick(self.fps)


class GameScene(Menus.Scene):
    def __init__(self, image, screen, app):
        self.image = image
        self.screen = screen
        self.app = app
        self.buttons = []
        self.counter = 119
        self.speed = -10
        self.paused = False
        self.sound = 0
            #Coins
        self.coin_count = 0
        self.schemas = self.init_coins()
            #Initialisation des groupes de sprites et de l'horloge
        self.obstacles = []
        self.coins = []
        self.clock = pygame.time.Clock()
        self.speed_mult = 1
        self.dico_particules = {'Rxmin':-10 ,'Rxmax':-6 ,'Rymin':-2 ,'Rymax':2,
                       'Modx':0 ,'Mody':0 ,'Divx':0 ,'Divy':0,'life_span':20}
        #Variables pour test
        self.secondObstacle = "spike"
        self.lastObstacle = self.secondObstacle

    #Cycle avec les animations (utilisé pour le classique et le vs IA)
    def cycleBase(self):
        if not self.paused:
            if self.players.vsIA:
                self.refreshInputs()
                #Update et affichage des backgrounds
            for bg in self.backgrounds:
                bg.update(self.speed)
                self.screen.blit(self.app.images[bg.image], bg.rects[0])
                self.screen.blit(self.app.images[bg.image], bg.rects[1])
                #Affichage de l'UI
            self.displayUI()
                #Update et affichage des obstacles
            to_delete = []
            for obstacle in self.obstacles:
                obstacle.update(self.screen, self.speed, False)
                self.screen.blit(self.app.images[obstacle.image], obstacle.rect)
                if obstacle.rect.right <=0:
                    to_delete.append(obstacle)
                for el in self.players.elements:
                    if obstacle.hitbox.colliderect(el.hitbox):
                        if obstacle.ob_type == 'pit':
                            el.in_hole = True
                            el.vel += 3
                        else:
                            self.players.kill(el)
            for ob in to_delete:
                self.obstacles.remove(ob)

                #Update et affichage des pieces
            to_delete = []
            for coin in self.coins:
                coin.update(self.speed)
                self.screen.blit(self.app.images[coin.image], coin.rect)
                if coin.rect.right <=0:
                    to_delete.append(coin)
                elif self.players.elements:
                    if coin.rect.colliderect(self.players.elements[0].hitbox):
                        to_delete.append(coin)
                        self.coin_count += 1
                        self.score += 1
                    #print('line 235 in #update et affichage des pièces, ajout de score')
            for ob in to_delete:
                self.coins.remove(ob)

            #Spawn des obstacles et des pièces
            self.counter += 1
            if self.counter% (1200//(-self.speed)) == 0:
                self.counter = 1
                temp = random.randint(0,5)
                if temp > 0:
                    arg = "vsIA" if self.players.vsIA else "classic"
                    self.spawnObstacle(True if temp > 3 else False, arg)
                else:
                    self.spawnCoins()

                #Update et affichage du/des joueur(s)
            self.players.updateElements(self.screen, False)
            self.players.drawElements(self.screen, self.app)
                #Verification rover en dehors de l'écran
            for el in self.players.elements:
                if el.rect.bottom > 730:
                    self.players.kill(el)

                #dessine les particules
            if len(self.particules) < 20:
                self.particules.append(go.Particule(self.players.elements[0].hitbox.bottomleft,
                            **self.dico_particules))
            need2del = []
            for part in self.particules:
                if self.players.elements:
                    part.update(self.players.elements[0].hitbox.bottomleft, self.dico_particules)
                    self.screen.blit(self.app.images['particule1'], part.rect)


                #Augmentation de la vitesse
            if self.counter%40 == 0 and self.speed > -23:
                self.speed -= 1

                #Augmentation du score
            self.score += 1

    #Cycle sans les animations (utilisé pour l'IA)
    def cycleIA(self):
        #Loop pour la vitesse
        for i in range(self.speed_mult):
            if not self.paused:
                    #Affichage de l'UI
                pygame.draw.rect(self.screen, (150,150,150), (0,0,1120,630), 0)
                pygame.draw.rect(self.screen, (90,90,90), (0,440,1120,210), 0)
                self.displayUI()
                    #Update et affichage des obstacles
                to_delete = []
                for obstacle in self.obstacles:
                    obstacle.update(self.screen, self.speed, True)
                    if obstacle.rect.right <=0:
                        to_delete.append(obstacle)
                    for el in self.players.elements:
                        if obstacle.hitbox.colliderect(el.hitbox):
                            if obstacle.ob_type == 'pit':
                                el.in_hole = True
                                el.vel += 3
                            else:
                                self.players.kill(el)
                for ob in to_delete:
                    self.obstacles.remove(ob)
                    self.players.upScore(200)

                #Spawn des obstacles et des pièces
                self.counter += 1
                if self.counter% (1200//(-self.speed)) == 0:
                    self.counter = 1
                    self.spawnObstacle(False, "ia")

                    #Actualisation des inputs du réseau de neurones
                self.refreshInputs()
                if self.app.statswin:
                    self.speed_mult = self.app.statswin.speedVar.get()

                    #Update et affichage du/des joueur(s)
                self.players.updateElements(self.screen, True)
                self.players.drawElements(self.screen, self.app)
                    #Verification rover en dehors de l'écran
                for el in self.players.elements:
                    if el.rect.bottom > 630:
                        self.players.kill(el)

                    #Augmentation de la vitesse
                if self.counter%40 == 0 and self.speed > -23:
                    self.speed -= 1
                self.players.upScore(1)



    def checkEvents(self, event):
        #Vérifie si le bouton pour sauter est activé
        if event.type == KEYDOWN and not self.paused:
            if event.key == self.app.optionsMenu.upbind:
                self.players.elements[0].jump()
            if event.key == self.app.optionsMenu.crouchbind:
                self.players.elements[0].startCrouch()

    def refreshInputs(self):
        closest_pos, closest_type, closest_width = 1000, 0, 0
        #Récupération des valeurs de l'obstacle le plus proche
        if len(self.obstacles) > 1:
            closest = sorted(self.obstacles, key=lambda ob: ob.rect.left - 200)
            closest = list(filter(lambda x: x.rect.left > 0, closest))
        else:
            closest = self.obstacles
        if self.obstacles:
            closest_pos = self.obstacles[0].rect.left
            closest_width = self.obstacles[0].rect.width
        self.players.setInputs((closest_pos, 112), (closest_width, 1120), ("el.rect.bottom", 630), ("el.vel", 10))
        #self.players.setInputs((1,1), (1,1), (1,1), (1,1))

    def spawnObstacle(self, with_coin, mode = "classic"):
        if mode == "classic":
            _type = random.choice(["spike", "arch", "pit"])
        elif mode == "ia":
            _type = "spike" if self.lastObstacle == "pit" else "pit"
        else:
            _type = random.choice(["spike", "pit"])
        self.lastObstacle = _type
        variant = random.randint(0,1)
        obstacle = _type + str(variant)
        self.obstacles.append(go.Obstacle(_type, obstacle, self.app.images[obstacle]))
        if with_coin:
            self.spawnCoins(_type)

    def spawnCoins(self, key_word=''):
        x = 1100    #bord de l'ecran (par defaut)
        y = 170     #heuteur de spawn (par defaut)
        if key_word == '':
            key_word, schema = random.choice(list(self.schemas.items()))
        else:
            schema = self.schemas[key_word]
        for ligne in schema:
            for caractere in ligne:
                if caractere == "0":
                    self.coins.append(go.Coin('coin', self.app.images['coin'], x, y))
                x += 80
            x = 1100
            y += 60

    def init_backgrounds(self,biome):
        coefs = []
        temp = []
        for x in range(3,-1,-1):
            bg_name = f'B{biome}_{x}'
            temp.append(go.Background(bg_name, self.app.images[bg_name],1/(x+1)))
        return temp

    def init_coins(self):
        with open('txt_files/maquette.txt', 'r') as file:
            schemas = {}
            temp = file.read().split('*\n')
            #rentre le couple clef - schema dans dico schemas
            for schema in temp:
                schemas[schema.split('-\n')[0]] = schema.split('-\n')[1].split('\n')
            #retire les objets vides des schema dans schemas
            for x in schemas:
                schemas[x].remove('')
        return schemas

    def pause(self):
        #Affiche le menu de pause
        scene = self.app.pauseMenuIA if (self.players.forIA and not self.players.vsIA) else self.app.pauseMenu
        Menus.current_scene = scene if not self.paused else self
        Menus.current_scene.displayUI()
        self.paused = False if self.paused else True

    def saveIA(self):
        text = ""
        for i, el in enumerate(self.players.elements):
            text += el.brain.toText("IA-"+str(i))
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT (*.txt)","*.txt")])
        if path == "":
            return 0
        with open(path, "w+") as file:
            file.write(text)

    def returnToMain(self):
        if self.paused:
            self.pause()
        self.app.goToMainMenu()

    def gameSetup(self, resetPlayers = True):
        #Reset ou set des variables de jeu
        with open('txt_files/Save.txt', 'r') as save:
            save = save.read().split('\n')
        self.current_skin = save[5]
        if resetPlayers:
            self.players = ia.Population(self, 1, False, 1, go.Player, self.app.images, self.current_skin)
        self.speed = -10
        self.score = 0
        self.coin_count = 0
        self.obstacles = []
        self.coins = []
        self.backgrounds = self.init_backgrounds('3')
        self.counter = 119
        self.cycle = self.cycleBase
        self.particules = []

    def setupIA(self, n, lr, brain = 0):
        self.players = ia.Population(self, n, True, lr, go.Player, self.app.images, self.current_skin)
        self.players.setupBrains([4, 5, 5, 1])
        self.players.setActions(["jump", None])
        self.players.addStatsWindow(self.app.statswin)
        if brain:
            self.players.setElementBrain(1, brain)
        else:
            self.cycle = self.cycleIA

    def gameOver(self, win = False):
        pygame.draw.rect(self.screen, (0,0,0), (0,0,1120,630), 0)
        Menus.current_scene = self.app.loseScreen if not win else self.app.winScreen
        Menus.current_scene.displayUI()

    def endScreen(self):
        #Enregistre les scores et le nbr de pieces dans "score.txt"
        if self.players.vsIA:
            self.returnToMain()
        else:
            Menus.current_scene = self.app.endScore
            Menus.current_scene.displayUI()
            with open("txt_files/score.txt", "r") as score_file:
                file = score_file.read().split("\n")
                old_coins = file[0]
                old_scores = file[1]
                self.coin_count += int(old_coins)
            with open("txt_files/score.txt", "w") as score_file:
                score_line = file[1].split(",")
                score_line.append(str(self.score))
                score_line = sorted(list(map(int, score_line)))
                while len(score_line) > 5 :
                    score_line.pop(0)
                    score_line = list(reversed(list(map(str, score_line))))
                    score_file.write(str(self.coin_count) + "\n" + ",".join(score_line))
            # blit le score + le classement
            with open("txt_files/score.txt", "r") as score_file:
                file = score_file.read().split("\n")
                coins = self.app.fontB.render(str(file[0]), True, (230,230,230))
                self.screen.blit(coins, (480,515))
                score = self.app.fontB.render(str(self.score), True, (230,230,230))
                self.screen.blit(score, (480,225))


class OptionsScene(Menus.Scene):
    def __init__(self, image, screen, app, sound):
        #Variables de l'objet
        self.image = image
        self.screen = screen
        self.app = app
        self.buttons = []
        self.sound = sound
        self.toggleSound = True
        #Variable vraie si l'utilisateur souhaite changer de controles de jeu
        self.upbindcheck = False
        self.crouchbindcheck = False
        self.need2save = False
        #Lecture des controles enregistrés
        with open('txt_files/Save.txt', 'r') as save:
            save = save.read().split('\n')
            self.upbind = int(save[0].split(':')[1])
            self.crouchbind = int(save[1].split(':')[1])
            self.toggleSound = int(save[6].split(':')[1])
        if not self.toggleSound:
            self.app.sounds['Flute'].stop()
            self.image = self.app.images["optionsMenuSoundOff"]

    def cycle(self):
        self.displayUI()
        text1 = self.app.font.render(pygame.key.name(self.upbind), True, (255,255,255))
        self.screen.blit(text1, (300,310))
        text2 = self.app.font.render(pygame.key.name(self.crouchbind), True, (255,255,255))
        self.screen.blit(text2, (300,450))

    def turnOffSounds(self):
        self.toggleSound = True if self.toggleSound == False else False
        name = "optionsMenu" if self.toggleSound == True else "optionsMenuSoundOff"
        self.image = self.app.images[name]
        if self.toggleSound:
            self.app.sounds['Flute'].play()
        else:
            self.app.sounds['Flute'].stop()
        self.need2save = True

    def newUpBind(self):
        #Active la recherche d'un nouveau controle de jeu
        self.upbindcheck = True

    def newCrouchBind(self):
        #Active la recherche d'un nouveau controle de jeu
        self.crouchbindcheck = True

    def checkEvents(self, event):
        #Change les controles de jeu selon la touche appuyée
        if self.upbindcheck and event.type == KEYDOWN:
            self.upbind = event.key
            self.upbindcheck = False
            self.need2save = True
        if self.crouchbindcheck and event.type == KEYDOWN:
            self.crouchbind = event.key
            self.crouchbindcheck = False
            self.need2save = True

        if self.need2save:
            with open('txt_files/Save.txt', 'r') as save:
                save = save.read().split('\n')
                save[0] = 'BindJump:'+str(self.upbind)
                save[1] = 'BindCrouch:'+str(self.crouchbind)
                save[6] = 'Sound:'+str(int(self.toggleSound))
            with open('txt_files/Save.txt', 'w') as new:
                for line in save:
                    if  line != '':
                        new.write(line+'\n')


class LeaderBoard(Menus.Scene):
    def __init__(self, image, screen, app, sound):
        #Variables de l'objet
        self.app = app
        self.image = image
        self.screen = screen
        self.buttons = []
        self.sound = sound


    def checkEvents(self, event):
        pass

    def cycle(self):
        with open("txt_files/score.txt", "r") as score_file:
            file = score_file.read().split("\n")
        for i in range(5):
            classement_value = int(file[1].split(",")[i])
            classement = self.app.font.render("({}) : {:20d}".format(i+1, classement_value), True, (200,200,200))
            self.screen.blit(classement, (200,160+i*98))


class Shop(Menus.Scene):
    def __init__(self, image, screen, app, shop_id, price, sound):
        #Variables de l'objet
        self.image = image
        self.screen = screen
        self.app = app
        self.buttons = []
        self.shop_id = shop_id
        self.price = price
        self.sound = sound
        with open('txt_files/score.txt', 'r') as save:
            save = save.read().split('\n')
        self.balance = int(save[0])

        self.addButton(None, app.goToMainShop, (895,425),(130,100))

        with open('txt_files/Save.txt', 'r') as file:
            skin = file.read().split('\n')[shop_id+2].split(':')[1]
        if skin == 'True':
            self.addButton(app.images['grisage140'], self.boutton_gris, (680,30),(345,140))
            self.addButton(None, self.equip, (685,210),(345,85))

        else:
            self.addButton(None, self.buy, (680,30),(345,140))
            self.addButton(app.images['grisage85'], self.boutton_gris, (685,210),(345,85))


    def cycle(self):
        self.displayUI()
        with open('txt_files/score.txt', 'r') as save:
            save = save.read().split('\n')
        self.balance = int(save[0])
        coins = self.app.font.render(str(self.balance), True, (255,255,255))
        self.screen.blit(coins, (425,580))

    def buy(self):
        if self.balance >= self.price:
            with open('txt_files/score.txt', 'r') as save:
                save = save.read().split('\n')
            save[0] = self.balance - self.price
            with open('txt_files/score.txt', 'w') as new_save:
                for line in save:
                    if line != '':
                        new_save.write(str(line)+'\n')
            with open('txt_files/Save.txt', 'r') as save:
                save = save.read().split('\n')
            save[self.shop_id + 2] = f'Skin{self.shop_id}:True'
            with open('txt_files/Save.txt', 'w') as new_save:
                for line in save:
                    if line != '':
                        new_save.write(str(line)+'\n')
            self.__init__(self.image, self.screen, self.app, self.shop_id, self.price, self.sound)
        else:
            print('aps assez de thunasses')


    def equip(self):
        with open('txt_files/Save.txt', 'r') as save:
            save = save.read().split('\n')
        save[5] = self.shop_id + 1
        with open('txt_files/Save.txt', 'w') as new_save:
            for line in save:
                if line != '':
                    new_save.write(str(line)+'\n')
        self.app.gameScene.current_skin = self.shop_id

    def boutton_gris(self):
        pass

    def checkEvents(self, event):
        pass

a = App()
