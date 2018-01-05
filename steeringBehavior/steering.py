import cv2
import numpy as np
from copy import deepcopy
import math
import random as r

class Position:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.radius = 0
		self.health = None
		self.owner = None
		self.id = None

class Ship:
	def __init__(self,x,y, color):
		self.x = x
		self.y = y
		self.vx = r.random()
		self.vy = r.random()
		self.color = color

	def calculate_distance_between(self, target):
		return math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2)

	def calculate_angle_between(self, target):
		return math.degrees(math.atan2(target.y - self.y, target.x - self.x)) % 360

	def closest_point_to(self, target, min_distance=3):
		angle = target.calculate_angle_between(self)
		radius = target.radius + min_distance
		x = target.x + radius * math.cos(math.radians(angle))
		y = target.y + radius * math.sin(math.radians(angle))
		return Position(x, y)

	def move(self, target, ships):
		"""distance = self.calculate_distance_between(target)
		angle = self.calculate_angle_between(target)
		speed = 0.1 if distance > 0.1 else distance
		self.vx = math.cos(math.radians(angle))*speed
		self.vy = math.sin(math.radians(angle))*speed
		self.x, self.y = self.x + self.vx, self.y + self.vy"""
		cptShip, alignX, alignY = 0, 0, 0
		for ship in ships:
			if ship != self:
				alignX += ship.vx
				alignY += ship.vy
				cptShip += 1
		alignX /= cptShip
		alignY /= cptShip
		norme = math.sqrt(alignX**2 + alignY**2) + 1e-5
		alignX /= norme
		alignY /= norme

		cptShip, coheX, coheY = 0, 0, 0
		for ship in ships:
			if ship != self:
				coheX += ship.x
				coheY += ship.y
				cptShip += 1
		coheX /= cptShip
		coheY /= cptShip
		coheX -= self.x
		coheY -= self.y
		norme = math.sqrt(coheX**2 + coheY**2) + 1e-5
		coheX /= norme
		coheY /= norme

		cptShip, sepX, sepY = 0, 0, 0
		val = False
		for ship in ships:
			if ship != self:
				if self.calculate_distance_between(ship) < 6:
					sepX += ship.x - self.x
					sepY += ship.y - self.y
					cptShip += 1
					val = True
		if val:
			sepX /= -cptShip
			sepY /= -cptShip
			norme = math.sqrt(sepX**2 + sepY**2) + 1e-5
			sepX /= norme
			sepY /= norme
		
		self.vx, self.vy = self.vx + sepX + coheX + alignX, self.vy + sepY + coheY + alignY
		norme = math.sqrt(self.vx**2 + self.vy**2) + 1e-5
		self.vx /= norme
		self.vy /= norme
		self.x, self.y = self.x + self.vx, self.y + self.vy

def drawShip(image,x,y,c):
	x, y = int(x), int(y)
	image[x*size-5:x*size+5,y*size-5:y*size+5,:] = c
	return image

def drawShips(image, ships):
	image2 = deepcopy(image)
	for ship in ships:
		image2 = drawShip(image2,ship.x,ship.y,ship.color)
	return image2

def updateShips(ships):
	for ship in ships:
		ship.move(Position(150,250), ships)
	return ships

size = 2
image = np.zeros((280*size, 320*size, 3))
print(image.shape)

ship1 = Ship(40,60,[255,0,0])
ship2 = Ship(50,60,[0,255,0])
ship3 = Ship(120,60,[0,0,255])

ships = [ship1, ship2, ship3]

while True:
	image2 = drawShips(image, ships)
	ships = updateShips(ships)
	cv2.imshow('zone',image2)
	k = cv2.waitKey(1) & 0xff
	if k == ord('q'):
		cv2.destroyAllWindows()
		break

