# -*- coding: utf-8 -*-
###############################################
#Game based on a maze. Experimenting with     #
#different algoritms to create the maze       #
#Arthur Guillaumin                            #
###############################################
import pygame, sys, socket, threading
#import jsonpickle     #We will use json to transmit large objects via sockets
from random import choice, shuffle
from Cemra import Camera
from Animate import Animate

#Definition of the class Maze. It shall represent a maze of
#m lines and n columns (mxn).

MAZE_SIZE = 60

class Application:
    def __init__(self):
        pygame.init()
        #Graphical parameters
        self.width = 800
        self.height = 600

        #Application surface
        self.main_surface = pygame.display.set_mode((self.width, self.height))

        #Creating the maze
        self.maze = Maze(MAZE_SIZE, MAZE_SIZE)
        self.maze.generateAtRandom2()

        #Creating the player
        self.human = Player(self.maze)
        self.opponent = Player(self.maze)

        #Create the camera.
        #The camera width and height defines the size of the image
        #that the camera gives. 
        cameraWitdh = self.width
        cameraHeight = self.height
        self.camera = Camera(cameraWitdh, cameraHeight, 100, self.maze, self.human, self.opponent)

        #Create the starting animation
        self.zoom_animate = Animate(200, 10, 5.0)
        self.camera.add_animation(self.zoom_animate)
        
        #Defines the period that is used to send a keydown event when a key
        #is kept down.
        pygame.key.set_repeat(200, 150)
        
        #We ask the player if they want to play on the network
        self.multiplayer = self.ask_multiplayer()

        if self.multiplayer:
            #We ask if this is the server
            is_serveur = raw_input('<S>erveur or <C>lient?')
            if str(is_serveur).upper() == 'S':
                HOST = socket.gethostname()
                PORT = 3000
                self.start_server(HOST, PORT)
                
                #Sending the maze to the other player
                print("Sending game data... Please wait.")
                encoded_maze = jsonpickle.encode(self.maze)
                print("Size of data is " + str(sys.getsizeof(encoded_maze)/1000) + "k.")
                self.connection.send(encoded_maze)
                #Creation des deux joueurs
                self.human = PlayerReseau(self.maze, self.connection)
                self.opponent = OpponentReseau(self.maze, self.connection)
                self.opponent.start()
            elif ask_multiplayer == 'C':
                HOST = input('Host?')
                PORT = 3000
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    self.connection.connect((HOST, PORT))
                except socket.error:
                    print("Connection has failed.")
                    sys.exit()
                print("Connection has been established with the server.")
                #Receiving the maze
                msg = self.connection.recv(200*1024)
                self.maze = jsonpickle.decode(msg)
                self.human = PlayerReseau(self.maze, self.connection)
                self.opponent = OpponentReseau(self.maze, self.connection)
                self.opponent.start()
        
#        self.human = Player(self.maze);
        
        
        
        #Start the main loop
        self.main_loop()

    def ask_multiplayer(self):
        s = input('Partie réseau?(Y/N)').upper()
        return s == 'Y'

    def start_server(self, host, port):
        """This function starts the server, by create a socket, listening
        and then accepting connections."""
        print('Adresse serveur: ' + HOST + ", PORT " + str(PORT))
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            mySocket.bind((HOST, PORT))
        except socket.error:
            print("Connection failed.")
            sys.exit()
        print("Server is ready")
        mySocket.listen(1)
        connection, address = mySocket.accept()
        return connection

    def main_loop(self):
        #We start a zoom animation for the camera.
        self.zoom_animate.start_animation()
        while True:
            #Gestion des évènements
            for evt in pygame.event.get():
                self.handle_event(evt)
            #Màj de l'affichage
            #Get the maze drawing
            self.camera.updateCamera()
            maze_surface = self.camera.getCameraView()
            self.main_surface.blit(maze_surface, (0,0))
            pygame.display.update()
            
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.connection.close()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if self.human is not None:
                if event.key == pygame.K_RIGHT:
                    self.human.move('E')
                elif event.key == pygame.K_DOWN:
                    self.human.move('S')
                elif event.key == pygame.K_LEFT:
                    self.human.move('O')
                elif event.key == pygame.K_UP:
                    self.human.move('N')
            if event.key == pygame.K_s:
                self.camera.setShowSolution(True)

class Maze:
    def __init__(self, m, n):
        #Tuple pour stoquer la taille. m lines, n columns
        self.size = (m,n)
        self.start_pos = (0,0)
        self.end_pos = (m-1,n-1)
        self.end_cell = None

        #Ajouts des cellules
        self.cells = []
        for i in range(m):
            for j in range(n):
                new_cell = Cell(i, j)
                if (i,j) == self.end_pos:
                    self.end_cell = new_cell
                self.cells.append(new_cell)

        #Define the end position at random
        self.end_cell = choice(self.cells)
        self.end_pos = (self.end_cell.getI(), self.end_cell.getJ())

        #To store the solution
        self.solution = []

        self.directions = ['N', 'O', 'S', 'E']

    def generateAtRandom(self):
        m = self.size[0]
        n = self.size[1]
        nb_open = 0
        i=0
        for cell in self.cells:
            cell.setColor(i)
            i += 1
        walls = []
        for cell in self.cells:
            for direction in self.directions:
                walls.append((cell, direction))
        shuffle(walls)
        print(len(walls))
        it = walls.__iter__()
        while nb_open < m*n-1:
            if nb_open % 100 == 0:
                print(nb_open)
            while True:
                (cell, wall) = it.next()
                neighbour_cell = self.getCellNeighbour(cell, wall)
                if neighbour_cell is not None and cell.getColor() != neighbour_cell.getColor():
                    walls.remove((cell, wall))
                    break
            self.joinCells(cell, wall)
            nb_open += 1

    def generateAtRandom2(self):
        """Implémentation de la méthode exhaustive. Renvoie la solution sous forme de liste de cellules."""
        #We initialize visited to False for all cells
        for cell in self.cells:
            cell.setVisited(False)
        path = []
        solutionPath = []   #List where the solution will be stored
        #Initial cell
        c = choice(self.cells)

        path_start = []
        path_end = []
        start_found = False
        end_found = False
        solved = False

        while True:
            path.append(c)
            c.setVisited(True)
            if not start_found: path_start.append(c)
            if not end_found: path_end.append(c)
            pos = (c.getI(), c.getJ())
            if not start_found and pos == self.start_pos:
                start_found = True
            if not end_found and pos == self.end_pos:
                end_found = True
            n = self.get_a_neighbour(c)
            if n is None:
                if len(path)>1:
                    path.pop()
                    nextCell = path.pop()
                    if not start_found:
                        path_start.pop()
                        path_start.pop()
                    if not end_found:
                        path_end.pop()
                        path_end.pop()
                else:
                    break
            else:
                (nextCell, d) = n
                self.joinCells(c, d)
            c = nextCell
        for c1, c2 in zip(path_start, path_end):
            if c1 is not c2:
                i = path_start.index(c1)
                r = path_start[i:]
                r.reverse()
                self.solution = r + path_end[i:]
                solved = True
                break
        if not solved:
            len_end = len(path_end)
            len_start = len(path_start)
            print("situation 2")
            if len_end > len_start:
                self.solution = path_end[len_start-1:]
            else:
                self.solution = path_start[len_end-1:]
        
            

    def get_a_neighbour(self, c):
        possibilities = []
        for d in self.directions:
            neighbour = self.getCellNeighbour(c, d) 
            if  neighbour != None and not neighbour.getVisited():
                possibilities.append((neighbour, d))
        if len(possibilities) > 0:
            return choice(possibilities)
        else:
            return None
                
            
            

    def getCellNeighbour(self, c, orientation):
        m = self.size[0]
        n = self.size[1]
        if orientation == 'N':
            if c.getI()>0:
                neighbour = self.cells[(c.getI()-1)*n+c.getJ()]
            else:
                return None
        elif orientation == 'S':
            if c.getI() < m-1:
                neighbour = self.cells[(c.getI()+1)*n+c.getJ()]
            else:
                return None
        elif orientation == 'E':
            if c.getJ()<n-1:
                neighbour = self.cells[c.getI()*n+c.getJ()+1]
            else:
                return None
        elif orientation == 'O':
            if c.getJ()>0:
                neighbour = self.cells[c.getI()*n+c.getJ()-1]
            else:
                return None
        else:
            raise Exception("Orientation non conventionelle: " + str(orientation))
        return neighbour

    def joinCells(self, c, orientation):
        c.destroyWall(orientation)
        neighbour = self.getCellNeighbour(c, orientation)
        opposite = self.getOppositeOrientation(orientation)
        neighbour.destroyWall(opposite)
        color = c.getColor()
        colorNeighbour = neighbour.getColor()
        for cell in self.cells:
            if cell.getColor() == color:
                cell.setColor(colorNeighbour)
        
                
    def getOppositeOrientation(self, orientation):
        orientation = self.directions.index(orientation)
        return self.directions[(orientation+2)%4]

    def isPositionValid(self, i, j):
        return i>=0 and j>=0 and i<self.size[0] and j<self.size[1]

    def checkMove(self, pos, direction):
        m = self.size[0]
        n = self.size[1]
        cell = self.cells[pos[0]*n+pos[1]]
        if not cell.getWall(direction):
            dest_cell = self.getCellNeighbour(cell, direction)
            if dest_cell is not None:
                return [dest_cell.getI(), dest_cell.getJ()]
            else:
                return None

    def getSize(self):
        return self.size

    def getCells(self):
        return self.cells

    def getSolution(self):
        return self.solution

    def getEnd_cell(self):
        return self.end_cell

        

class Cell:
    def __init__(self, i, j):
        self.visited = False
        self.i = i
        self.j = j
        self.walls = {'N': True, 'S': True, 'O': True, 'E': True}
        self.color = None

    def getColor(self):
        return self.color

    def setColor(self, v):
        self.color = v

    def setVisited(self, v=True):
        self.visited = v

    def getVisited(self):
        return self.visited

    def getI(self):
        return self.i

    def setI(self, v):
        self.i = v

    def getJ(self):
        return self.j

    def setJ(self, v):
        self.j = v
        
    def getWall(self, orientation):
        return self.walls[orientation]

    def destroyWall(self, orientation):
        self.walls[orientation] = False


class Player:
    def __init__(self, maze):
        self.maze = maze
        self.position = (0,0)

    def getPosition(self):
        return self.position

    def setPosition(self, i, j):
        if self.maze.isPositionValid(i,j):
            self.position = [i,j]

    def move(self, direction):
        v= self.maze.checkMove(self.position, direction)
        if v is not None:
            self.position = v
            print(v)


class PlayerReseau(Player):
    def __init__(self, maze, connection):
        Player.__init__(self, maze)
        self.connection = connection

    def move(self, direction):
        Player.move(self, direction)
        self.connection.send(str(self.position[0]) + ' ' + str(self.position[1]))

class OpponentReseau(Player, threading.Thread):
    def __init__(self, maze, connection):
        Player.__init__(self, maze)
        threading.Thread.__init__(self)
        self.connection = connection

    def run(self):
        while 1:
            print("Waiting for communication...")
            #We wait for the updated position of the player
            pos = self.connection.recv(1024)
            print("updated position of oponent is " + str(pos))
            pos = pos.split()
            self.setPosition(int(pos[0]), int(pos[1]))

if __name__ == "__main__":
    app = Application()
