import math, random
import pygame.sprite as sprite
import tkinter as tk

class Population:
    def __init__(self, scene, n, ia, lr_mult, cls, *args):
        #Initialisation des variables
        self.forIA = ia
        self.vsIA = False
        self.n = n #Taille de la population
        self.gen = 1
        self.elements = []
        self.deadpop = []
        self.scene = scene
        self.cls = cls
        self.args = args
        self.lr_mult = lr_mult
        #Conteur pour que les objets ne pensent que toutes les X frames
        self.counter = 0
        #Création des éléments de la population
        for i in range (n):
            self.elements.append(cls(*args))
        #Initialisation des scores
        for el in self.elements:
            el.scoreIA = 0
        self.statswin = 0

    def updateElements(self, *args):
        #Update des élements de la population
        for i, el in enumerate(self.elements):
            el.update(*args)

        if self.forIA and self.counter%5 == 0:
            self.think()
            self.counter = 0

        #Vérification de si toute la population est morte
        self.counter += 1
        if len(self.elements) == 0:
            if self.forIA:
                self.nextGen()
            else:
                self.scene.gameOver()

    def upScore(self, n):
        for el in self.elements:
            el.scoreIA += n

    def setElementBrain(self, i, brain):
        self.elements[i].brain = brain
        self.vsIA = True
    def drawElements(self, screen, app, one = False):
        #Affichage des élements de la population
        if one:
            screen.blit(app.images[self.elements[0].image], self.elements[0].rect)
        else:
            for el in self.elements:
                screen.blit(app.images[el.image], el.rect)

    def kill(self, el):
        self.deadpop.append(el)
        if self.vsIA:
            if self.elements.index(el) == 1:
                self.scene.gameOver(True)
            else:
                self.scene.gameOver(False)
        self.elements.remove(el)

    def setInputs(self, *args):
        #La deuxième valeur de chaque tuple est la valeur par laquelle on divise la 1ère pour normaliser les inputs
        self.extInputs = []
        self.classInputs = []
        for _input in args:
            if isinstance(_input[0], str):
                self.classInputs.append(_input)
            else:
                self.extInputs.append(_input)

    def setupBrains(self, geometry):
        #Initialisation des réseaux de neurones de chaque éléments
        for j, e in enumerate(self.elements):
            self.elements[j].brain = NeuralNetwork(geometry)

    def setActions(self, *args):
        #Initialisation des fonctions à executer en fonction du résultat du réseau de neurones
        self.funcs = args
        self.probs = ()
        for list_ in self.funcs:
            self.probs = self.probs + ([(1/len(list_))*(i+1) for i in range(len(list_))],)

    def think(self):
        #Appel de la fonction en fonction du résultat donné par le réseau de neurones
        for i, el in enumerate(self.elements):
            #Récupération des inputs
            if (i == 1 and self.vsIA) or not self.vsIA:
                inputs = []
                for input_ in self.extInputs:
                    inputs.append(input_[0]/input_[1])
                for input_ in self.classInputs:
                    inputs.append(eval(input_[0])/input_[1])
                #Récupération des outputs
                outputs = el.brain.feedForward(inputs)
                #Appel des actions selon la valeur renvoyée par le réseau de neurones
                for k in range(el.brain.o):
                    for i, p in enumerate(self.probs[k]):
                        if outputs[k] < p:
                            if self.funcs[k][i] != None:
                                eval("el.{}()".format(self.funcs[k][i]))
                                el.scoreIA -= 10
                            break

    def nextGen(self):
        new_elements = []
        self.calculateFitness()
        for i in range(self.n):
            #Choix des parents selon leur fitness
            parentA = self.pickOne()
            parentB = self.pickOne()
            #Crossover
            childbrain = (parentA.brain + parentB.brain)/2
            #lr --> learning rate (taux d'apprentissage) calculé en fonction des fitness des parents
            lr = (1/((parentA.scoreIA + parentB.scoreIA)))*self.lr_mult
            #Mutation
            childbrain += ( -1 if random.random() < 0.5 else 1)*random.random()*lr
            child = self.cls(self.args[0], self.args[1])
            child.brain = childbrain
            child.scoreIA = 0
            new_elements.append(child)
        #Calcul du score moyen de la population cette génération
        sum = 0
        for el in self.deadpop:
            sum += el.scoreIA
        avg = sum/len(self.deadpop)
        #Update de la fenetre des stats
        self.gen += 1
        if self.statswin:
            self.statswin.graph.addVal(avg)
            self.statswin.graph.draw()
            self.statswin.genlbl["text"] = str(self.gen)
        #Reset des variables
        self.deadpop = []
        self.elements = new_elements
        self.scene.gameSetup(False)
        self.scene.cycle = self.scene.cycleIA

    def pickOne(self):
        #Choix d'un élément de la population en fonction de sa fitness
        index = 0
        r = random.random()
        while r > 0:
            r = r - self.deadpop[index].fitness
            index += 1
        index -= 1
        return self.deadpop[index]

    def calculateFitness(self):
        #Normalisation des valeurs du score de chaque élement
        total = 0
        for el in self.deadpop:
            total += el.scoreIA
        for el in self.deadpop:
            el.fitness = el.scoreIA/total

    def addStatsWindow(self, window):
        self.statswin = window

class NeuralNetwork:
    def __init__(self, geometry):
        #Nombres de nodes d'input, cachées et d'output
        self.i, self.o = geometry[0], geometry[-1]
        self.geometry = geometry
        self.layers = len(self.geometry)
        #Initialisation des poids et biais
        self.weights = []
        self.biases = []
        for i in range(self.layers-1):
            self.weights.append(Matrix(self.geometry[i+1], self.geometry[i]))
            self.biases.append(Matrix(self.geometry[i+1], 1))
        for matx in self.weights:
            matx.randomize()
        for matx in self.biases:
            matx.randomize()

    def feedForward(self, input_list):
        #Initialisation des inputs
        inputs = Matrix.fromList(input_list)
        inputs = inputs.transpose()
        #Calcul du réseau de neurones
        inputs.map(sigmoid)
        temp = inputs
        for i in range(self.layers-1):
            #Produits matriciels entre poids et inputs
            result = self.weights[i].dot(temp)
            #Ajout du biais
            result += self.biases[i]
            #Fonction d'activation
            result.map(sigmoid)
            temp = result
        #Envoi des outputs sous forme de liste
        return result.toList()

    def toText(self, title):
        text = title +  ":"
        for i, matx in enumerate(self.weights):
            for j in range(matx.rows):
                row = [str(val) for val in matx.vals[j]]
                text += ",".join(row) + ";"
            text += "/"
        text += "_"
        for i, matx in enumerate(self.biases):
            for j in range(matx.rows):
                row = [str(val) for val in matx.vals[j]]
                text += ",".join(row) + ";"
            text += "/"
        text += "~"+",".join([str(el) for el in self.geometry])
        text += "\n"
        return text

    @classmethod
    def fromText(self, text):
        #Récupération des infos du fichier texte
        text, geometry = text.split("~")
        weights, biases = text.split("_")
        weights, biases = weights.split("/"), biases.split("/")
        weights.pop()
        biases.pop()
        geometry = [int(el.rstrip("\n")) for el in geometry.split(",")]
        nn = NeuralNetwork(geometry)
        #Conversion des infos en float
        #Pour les poids
        for i, matx in enumerate(weights):
            rows = matx.split(";")
            rows = [row.split(",") for row in rows]
            rows.pop()
            for j, row in enumerate(rows):
                for k, col in enumerate(row):
                    rows[j][k] = float(rows[j][k])
            weight = Matrix(len(rows), len(rows[0]))
            weight.vals = rows
            nn.weights[i] = weight
        #Pour les biais
        for i, matx in enumerate(biases):
            rows = matx.split(";")
            rows = [row.split(",") for row in rows]
            rows.pop()
            for j, row in enumerate(rows):
                for k, col in enumerate(row):
                    rows[j][k] = float(rows[j][k])
            bias = Matrix(len(rows), len(rows[0]))
            bias.vals = rows
            nn.biases[i] = bias
        return nn

    def __add__(self, nn2):
        result = NeuralNetwork(self.geometry)
        for i, e in enumerate(result.weights):
            result.weights[i] = self.weights[i] + nn2.weights[i]
        for j, e in enumerate(result.biases):
            result.biases[j] = self.biases[j] + nn2.biases[j]
        return result

    def __truediv__(self, k):
        result = NeuralNetwork(self.geometry)
        for i, e in enumerate(result.weights):
            result.weights[i] = self.weights[i] /k
        for j, e in enumerate(result.biases):
            result.biases[j] = self.biases[j] / k
        return result

    def __iadd__(self, k):
        result = NeuralNetwork(self.geometry)
        for i, e in enumerate(result.weights):
            result.weights[i] = self.weights[i] + k
        for j, e in enumerate(result.biases):
            result.biases[j] = self.biases[j] + k
        return result

class Matrix:
    def __init__(self, rows, cols):
        self.vals = []
        self.rows, self.cols = rows, cols
        for i in range(rows):
            temp = []
            for j in range(cols):
                temp.append(0)
            self.vals.append(temp)

    def randomize(self):
        #Mise en place de valeurs aléatoires
        for i in range(self.rows):
            for j in range(self.cols):
                sign = -1 if random.random() < 0.5 else 1
                self.vals[i][j] = random.random() * sign

    def __iadd__(self, k):
        #Ajout incrémentiel --> +=
        constBool = True if isinstance(k, int) or isinstance(k, float) else False
        result = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                num = k if constBool else k.vals[i][j]
                self.vals[i][j] += num
        return self

    def __isub__(self, k):
        #Soustraction incrémentielle --> -=
        constBool = True if isinstance(k, int) or isinstance(k, float) else False
        result = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                num = k if constBool else k.vals[i][j]
                self.vals[i][j] -= num
        return self

    def __add__(self, k):
        #Addition de matrice élement par élement ou avec une constante k
        constBool = True if isinstance(k, int) or isinstance(k, float) else False
        result = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                num = k if constBool else k.vals[i][j]
                result.vals[i][j] = self.vals[i][j] + num
        return result

    def __sub__(self, k):
        #Soustraction de matrice élement par élement ou avec une constante k
        constBool = True if isinstance(k, int) or isinstance(k, float) else False
        result = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                num = k if constBool else k.vals[i][j]
                result.vals[i][j] = self.vals[i][j] - num
        return result

    def __truediv__(self, k):
        #Division de matrice élement par élement ou avec une constante k
        constBool = True if isinstance(k, int) or isinstance(k, float) else False
        result = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                num = k if constBool else k.vals[i][j]
                result.vals[i][j] = self.vals[i][j] / num
        return result

    def __mul__(self, k):
        #Multiplication de matrice élement par élement ou avec une constante k
        constBool = True if isinstance(k, int) or isinstance(k, float) else False
        result = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                num = k if constBool else k.vals[i][j]
                result.vals[i][j] = self.vals[i][j] * num
        return result

    def __neg__(self):
        #Signe négatif appliqué à tous les élements de la matrice
        result = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                result.vals[i][j] = self.vals[i][j] * -1
        return result

    def dot(self, m2):
        #Produit matriciel ou "dot product"
        if self.cols != m2.rows:
            raise Exception("Les matrices ne sont pas de bonnes dimensions.")
        result = Matrix(self.rows, m2.cols)
        for i in range(result.rows):
            for j in range(result.cols):
                sum_ = 0
                for k in range(self.cols):
                    sum_ += self.vals[i][k] * m2.vals[k][j]
                result.vals[i][j] = sum_
        return result

    def transpose(self):
        #Rotation de la matrice
        result = Matrix(self.cols, self.rows)
        for i in range(self.rows):
            for j in range(self.cols):
                result.vals[j][i] = self.vals[i][j]
        return result

    @classmethod
    def fromList(self, list_):
        #Création d'une matrice à partir d'un objet liste
        matx = Matrix(1, len(list_))
        matx.vals[0] = list_
        return matx

    def toList(self):
        #Création d'une liste à partir d'un objet Matrice
        list_ = []
        for row in self.vals:
            list_ += row
        return list_

    def map(self, func):
        #Applique une fonction à tous les élements de la matrice
        for i in range(self.rows):
            for j in range(self.cols):
                self.vals[i][j] = func(self.vals[i][j])

    def display(self, name = "Matrix"):
        #Affichage de la matrice, utile pour le débug et les tests
        print("="*4 + name + "="*4)
        for row in self.vals:
            print(row)
        print("="*(8+len(name)))

#Fonction sigmoid d'activation --> Renvoie un nombre entre 0 et 1 peut importe le nombre en entrée
def sigmoid(x):
    if x < -100:
        return sigmoid(-100)
    return (1 / (1 + math.exp(-x)))

title_font = ("Arial", 20)
medium_text_font = ("Arial", 14)
small_text_font = ("Arial", 12)

class StatsWindow:
    def __init__(self, app):
        #Setup de la fenètre
        self.root = tk.Tk()
        self.root.geometry("600x450+0+0")
        self.root.resizable(width=False, height=False)
        #Setup des élements
        self.app = app
        self.setup()

    def setup(self):
        #Dictionnaire pour garder une reference de tous les widgets
        #Titre
        lbl1 = tk.Label(self.root, bg="#F9F9F9", relief="groove", font = title_font, text="Statistiques IA")
        lbl1.place(relx=0, rely=0, relwidth = 1, relheight = 0.2)
        #Choix de la vitesse
        self.speedVar = tk.IntVar()
        self.speedVar.set(5)
        speedSlider = tk.Scale(self.root, orient='horizontal', from_=1, to=5, resolution=1, tickinterval=5, label='Vitesse du Jeu :', showvalue=0, variable=self.speedVar)
        speedSlider.place(relx=0, rely=0.2, relwidth = 0.3, relheight = 0.2)
        entry1 = tk.Entry(self.root, bg="#F9F9F9", relief="groove", font = small_text_font, textvariable=self.speedVar)
        entry1.place(relx=0.3, rely=0.25, relwidth = 0.05, relheight = 0.05)
        #Choix du nombre d'élements dans la population
        self.nVar = tk.IntVar()
        self.nVar.set(5)
        lbl2 = tk.Label(self.root, bg="#F9F9F9", relief="groove", font = small_text_font, text="N(Taille de la population):")
        lbl2.place(relx=0, rely=0.35, relwidth = 0.30, relheight = 0.05)
        self.n_entry = tk.Entry(self.root, bg="#F9F9F9", relief="groove", font = small_text_font, textvariable=self.nVar)
        self.n_entry.place(relx=0.30, rely=0.35, relwidth = 0.05, relheight = 0.05)
        #Choix du multiplicateur pour le learning rate
        self.lrVar = tk.IntVar()
        self.lrVar.set(0.1)
        lbl5 = tk.Label(self.root, bg="#F9F9F9", relief="groove", font = small_text_font, text="Learning rate --> X")
        lbl5.place(relx=0, rely=0.45, relwidth = 0.30, relheight = 0.05)
        self.lr_entry = tk.Entry(self.root, bg="#F9F9F9", relief="groove", font = small_text_font, textvariable=self.lrVar)
        self.lr_entry.place(relx=0.30, rely=0.45, relwidth = 0.05, relheight = 0.05)
        #Bouton de démarage
        self.startbtn = tk.Button(self.root, bg="#F9F9F9", relief="groove", font = medium_text_font, text="Lancer l'expérience", command=self.start)
        self.startbtn.place(relx=0, rely=0.9, relwidth = 0.5, relheight = 0.1)
        self.quitbtn = tk.Button(self.root, bg="#F9F9F9", relief="groove", font = medium_text_font, text="Quitter", command=self.quit)
        self.quitbtn.place(relx=0.5, rely=0.9, relwidth = 0.5, relheight = 0.1)
        #Graphique du score moyen
        lbl4 = tk.Label(self.root, bg="#F1F1F1", relief="flat", font = small_text_font, text="Score moyen IA :")
        lbl4.place(relx=0.35, rely=0.20, relwidth = 0.3, relheight = 0.05)
        self.graph = GraphList(self.root, [],  0.40, 0.25, 350, 100)
        self.graph.draw()
        #Affichage du nombre de la génération
        lbl6 = tk.Label(self.root, bg="#F9F9F9", relief="groove", font = small_text_font, text="Génération:")
        lbl6.place(relx=0, rely=0.55, relwidth = 0.30, relheight = 0.05)
        self.genlbl = tk.Label(self.root, bg="#F9F9F9", relief="groove", font = small_text_font, text = "0")
        self.genlbl.place(relx=0.30, rely=0.55, relwidth = 0.05, relheight = 0.05)

    def start(self):
        self.startbtn.destroy()
        self.quitbtn.destroy()
        self.app.StartIA(self.nVar.get(), self.lrVar.get())
        self.root.quit()

    def quit(self):
        self.root.destroy()


class GraphList:
    def __init__(self, parent, list_, x, y, w, h):
        #Initialisation des variables
        self.canv = tk.Canvas(parent, bg = "#FFFFFF")
        self.canv.place(relx = x, rely = y, width = w, height = h)
        self.vals = list_
        self.x, self.y = x, y
        self.w, self.h = w, h

    def draw(self):
        self.canv.delete("all")
        if self.vals:
            max_val = max(self.vals)
            grid = self.w/(len(self.vals)+1)
            for i, val in enumerate(self.vals):
                height = self.h - (val/max_val)*(self.h*0.85)
                self.canv.create_oval((i+1)*grid, height, (i+1)*grid + 2, height + 2)
                if len(self.vals) < 10:
                    self.canv.create_text((i+1)*grid, height-5, text = str(val))
        self.canv.update()

    def updateVals(self, list_):
        self.vals = list_

    def addVal(self, val):
        self.vals.append(val)


if __name__ == "__main__":
    nn = NeuralNetwork([1, 3, 1])
    nn.toText("nn1")
