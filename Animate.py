# -*- coding: utf-8 -*-
###############################################
#Application graphique de résolution de sudoku#
#Arthur Guillaumin                            #
###############################################
import pygame, sys
from random import choice, shuffle
from Cemra import Camera
from time import time

class Animate:
    def __init__(self, i_zoom, f_zoom, duration, method='linear'):
        self.initial_zoom = i_zoom
        self.final_zoom = f_zoom
        self.method = method
        self.time_start = 0
        self.duration = duration       #duration must be in seconds
        self.alive = True

    def setInitial_zoom(self, v):
        self.initial_zoom = v

    def getInitial_zoom(self):
        return self.initial_zoom

    def setFinal_zoom(self, v):
        self.final_zoom = v

    def getFinal_zoom(self):
        return self.final_zoom

    def start_animation(self):
        self.time_start = pygame.time.get_ticks()
        self.alive = True

    def getCurrentZoom(self):
        if self.method == 'linear' and self.alive:
            p = (pygame.time.get_ticks()-self.time_start)/(self.duration*1000)
            if p <= 1:
                diff = self.final_zoom - self.initial_zoom
                return self.initial_zoom + p*diff
            else:
                self.alive = False
                return self.final_zoom
        elif not self.alive:
            return None

    def getAlive(self):
        return self.alive
