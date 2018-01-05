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

class Obstacle:
	def __init__(self, x, y, r, c):
		self.x = x
		self.y = y
		self.radius = r
		self.color = c

class Ship:
	def __init__(self,x,y, color):
		self.x = x
		self.y = y
		self.vx = r.random()
		self.vy = r.random()
		self.vvx = 0
		self.vvy = 0
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

	def move(self, target, ships, obstacles):
		distance = self.calculate_distance_between(target)
		angle = self.calculate_angle_between(target)
		speed = 7 if distance > 7 else distance
		self.vvx = math.cos(math.radians(angle))
		self.vvy = math.sin(math.radians(angle))
		norme = math.sqrt((speed*self.vvx)**2 + (speed*self.vvy)**2) + 1e-5
		headX = self.vvx*speed/norme
		headY = self.vvy*speed/norme

		fact = 1
		avoidX, avoidY = 0, 0
		for obstacle in obstacles:
			if math.sqrt((obstacle.x - self.x - fact*headX) ** 2 + (obstacle.y - self.y - fact*headY) ** 2) < obstacle.radius + 5:
				avoidX = self.x + fact*headX - obstacle.x
				avoidY = self.y + fact*headY - obstacle.y
				norme = math.sqrt(avoidX**2 + avoidY**2) + 1e-5
				avoidX /= norme
				avoidY /= norme
				print('eerer')
			if math.sqrt((obstacle.x - self.x - 0.5*headX) ** 2 + (obstacle.y - self.y - 0.5*headY) ** 2) < obstacle.radius + 5:
				avoidX = self.x + 0.5*headX - obstacle.x
				avoidY = self.y + 0.5*headY - obstacle.y
				norme = math.sqrt(avoidX**2 + avoidY**2) + 1e-5
				avoidX /= norme
				avoidY /= norme
				print('dmlfmdfldslfdlf')

		#self.x, self.y = self.x + self.vvx*speed, self.y + self.vvy*speed
		cptShip, alignX, alignY = 0, 0, 0
		val = False
		for ship in ships:
			if ship != self:
				if self.calculate_distance_between(ship) < 50:
					alignX += ship.vvx
					alignY += ship.vvy
					cptShip += 1
					val = True
		if val:
			alignX /= cptShip
			alignY /= cptShip
			norme = math.sqrt(alignX**2 + alignY**2) + 1e-5
			alignX /= norme
			alignY /= norme

		val = False
		cptShip, coheX, coheY = 0, 0, 0
		for ship in ships:
			if ship != self:
				coheX += ship.x
				coheY += ship.y
				cptShip += 1
				val = True
		if val:
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
				if self.calculate_distance_between(ship) < 15:
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
		
		self.vx, self.vy = self.vvx + sepX + 2*avoidX + alignX + 0.1*coheX, self.vvy + sepY + 2*avoidY + alignY + 0.1*coheY
		norme = math.sqrt(self.vx**2 + self.vy**2) + 1e-5
		self.vx /= norme
		self.vy /= norme
		self.x, self.y = self.x + self.vx*speed, self.y + self.vy*speed

def drawShip(image,x,y,c):
	x, y = int(x), int(y)
	image[x*size-5:x*size+5,y*size-5:y*size+5,:] = c
	return image

def drawObstacles(image, obstacles):
	for obs in obstacles:
		r, x, y = obs.radius, obs.x, obs.y
		r2 = r**2
		for i in range(-r,r+1):
			for j in range(-r,r+1):
				if i**2 + j**2 < r2:
					image[x+i,y+j,:] = [255,255,255]
	return image

def drawShips(image, ships):
	image2 = deepcopy(image)
	for ship in ships:
		image2 = drawShip(image2,ship.x,ship.y,ship.color)
	return image2

def updateShips(ships, obstacles):
	for ship in ships:
		ship.move(Position(15,25), ships, obstacles)
	return ships

size = 1
image = np.zeros((280*size, 320*size, 3))
print(image.shape)

ship1 = Ship(40,60,[255,0,0])
ship2 = Ship(50,60,[0,255,0])
ship3 = Ship(120,60,[0,0,255])

obstacle1 = Obstacle(125,175,20,[255,255,255])
obstacle2 = Obstacle(225,175,20,[255,255,255])

ships = [ship1, ship2, ship3]
obstacles = [obstacle1,obstacle2]

"""ships = []
for x in range(1):
	ships.append(Ship(r.randint(0,280*size-1),r.randint(0,320*size-1),[0,0,255]))"""

image = drawObstacles(image, obstacles)
while True:
	image2 = drawShips(image, ships)
	ships = updateShips(ships, obstacles)
	cv2.imshow('zone',image2)
	print(ship1.x, ship1.y)
	k = cv2.waitKey(5) & 0xff
	if k == ord('q'):
		cv2.destroyAllWindows()
		break

