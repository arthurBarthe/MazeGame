# -*- coding: utf-8 -*-
###############################################
#Application graphique de résolution de sudoku#
#Arthur Guillaumin                            #
###############################################
import pygame, sys
from random import choice
from math import exp

class Camera:
    def __init__(self, width, height, zoom, maze, player=None, player2=None):
        self.pos = [0.0,0.0]        #Position of the camera on the map
        self.width = width          #Size of the surface which we draw
        self.height = height
        self.zoom = zoom            #Number of cells seen
        self.maze = maze
        self.player = player
        self.player2 = player2
        self.showSolution = False
        self.surface = pygame.Surface((self.width,self.height))
        self.camera_speed = 0.01    #between 0 (not moving) and 1 (moves immediately to the new position of the player
        self.animations = []

    def setPos(self, i, j):
        self.pos = [i,j]

    def getPos(self):
        return self.pos

    def setZoom(self, v):
        self.zoom = v

    def getZoom(self):
        return self.zoom

    def updateCamera(self):
        #Update position according to player's position
        if self.player is not None:
            pos = self.player.getPosition()
            speed = self.camera_speed
            pos = (self.pos[0] + speed*(pos[0]-self.pos[0]), self.pos[1] + speed*(pos[1]-self.pos[1]))
            self.setPos(pos[0], pos[1])
        #Update zoom in case of animation
        binAnimations = []
        for anim in self.animations:
            if anim.getAlive():
                self.setZoom(anim.getCurrentZoom())
            else:
                binAnimations.append(anim)
        #We remove dead animations
        for anim in binAnimations:
            self.animations.remove(anim)

    def setShowSolution(self,v):
        self.showSolution = v

    def getShowSolution(self):
        return self.showSolution

    def add_animation(self, anim):
        self.animations.append(anim)

    def convertPosition(self, i, j):
        pxCentre = int(((j-self.pos[1])/self.zoom+0.5)*self.width)
        pyCentre = int(((i-self.pos[0])/self.zoom+0.5)*self.height)
        return (pxCentre, pyCentre)

    def getCameraView(self):
        #Returns a pygameSurface
        self.surface.fill(pygame.Color(255, 255, 255))
        (m,n) = self.maze.getSize()
        deltaV = int(self.height/self.zoom)
        deltaH = int(self.width/self.zoom)

        #On trace le joueur
        #Draw the human position
        deltaVp = self.height/self.zoom/2.0;
        deltaHp = self.width/self.zoom/2.0;
        [i,j] = self.player.getPosition()
        pxCentre, pyCentre = self.convertPosition(i, j)
        pygame.draw.rect(self.surface, pygame.Color(0,0,255), pygame.Rect(int(pxCentre-deltaHp/2), int(pyCentre-deltaVp/2), int(deltaHp), int(deltaVp)), 0)
#
#        #On trace le joueur2
#        #Draw the human position
#        [i,j] = self.player2.getPosition()
#        pxCentre, pyCentre = self.convertPosition(i, j)
#        pygame.draw.rect(self.surface, pygame.Color(255,0,0), pygame.Rect(int(pxCentre-deltaHp/2), int(pyCentre-deltaVp/2), int(deltaHp), int(deltaVp)), 0)


        #On trace les murs des cellules
        cells = self.maze.getCells()
        for cell in cells:
            i = cell.getI()
            j = cell.getJ()
            if abs(i-self.pos[0]) <= self.zoom +2 and abs(j-self.pos[1]) <= self.zoom +2:
                pxCentre, pyCentre = self.convertPosition(i, j)
                xTopLeft = max(0, pxCentre-deltaH/2)
                yTopLeft = max(0, pyCentre-deltaV/2)
                xBottomRight = min(self.width, pxCentre+deltaH/2)
                yBottomRight = min(self.height, pyCentre+deltaV/2)
                """if cell.getWall('N') and pyCentre-deltaV/2 >= 0:
                    pygame.draw.line(self.surface, pygame.Color(0,0,0), (xTopLeft, yTopLeft), (xBottomRight, yTopLeft), 1)"""
                if cell.getWall('S') and pyCentre+deltaV/2 <= self.height:
                    pygame.draw.line(self.surface, pygame.Color(0,0,0), (xTopLeft, yBottomRight), (xBottomRight, yBottomRight), 1)
                """if cell.getWall('O') and pxCentre-deltaH/2 >= 0:
                    pygame.draw.line(self.surface, pygame.Color(0,0,0), (xTopLeft, yTopLeft), (xTopLeft, yBottomRight), 1)"""
                if cell.getWall('E') and pxCentre+deltaH/2 < self.width:
                    pygame.draw.line(self.surface, pygame.Color(0,0,0), (xBottomRight, yTopLeft), (xBottomRight, yBottomRight), 1)
                #On colorie la case d'arrivée
                if cell == self.maze.getEnd_cell():
                    pygame.draw.rect(self.surface, pygame.Color(0,150,0), pygame.Rect(xTopLeft, yTopLeft, deltaH, deltaV), 0)
                        
        #On trace la solution
        if self.showSolution:
            last_i = None
            last_j = None
            for cell in self.maze.getSolution():
                i = cell.getI()
                j = cell.getJ()
                if last_i is not None:
                    last_pxCentre = ((last_j-self.pos[1])/self.zoom+0.5)*self.width
                    last_pyCentre = ((last_i-self.pos[0])/self.zoom+0.5)*self.height
                    pxCentre = ((j-self.pos[1])/self.zoom+0.5)*self.width
                    pyCentre = ((i-self.pos[0])/self.zoom+0.5)*self.height
                    pygame.draw.line(self.surface, pygame.Color(0, 255, 0), (last_pxCentre, last_pyCentre), (pxCentre, pyCentre), 2)
                last_i = i
                last_j = j
            
        return self.surface

    
