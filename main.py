import pygame
import time
import copy
import random
import sys
import math

from actors import *
from data import *

pygame.init()

# Game properties
screenWidth = 950
screenHeight = 950
tickDelay = 0.01  # Time between updates. Lower time = faster game.
gameTitle = "Silent Night"

screen = pygame.display.set_mode([screenWidth, screenHeight])
pygame.display.set_caption(gameTitle)

# Game class
class Game:
    def __init__(self):
        # Global Game Variables
        self.gameState = 0 # 0 = Main Menu, 1 = Help, 2 = Story Mode, 3 = Home Base, 4 = Game Done

        # UI Interaction
        self.textButtons = []

        self.leftClicked = False

        # Base
        self.heldPlayers = [Player(0), Player(1), Player(2)]
        self.resources = 5
        self.abandonCount = 5

        # Main Menu
        self.blinkIntensity = 0
        self.nextBlink = 0
        self.blinkDirection = 1
        self.blinkMax = 0

        # Game Done
        self.victory = False

        # Base Gameplay
        self.player = Player(0)
        self.walls = []
        self.prevPlayerPos = [0, 0]

        self.cRoom = Room(0, 0, [], [], 0)
        self.rooms = []
        
        self.cMidWalls = [
            pygame.Rect(300, 400, 300, 20),
            pygame.Rect(600, 100, 20, 200)
        ]
        self.enemies = []

        self.stunBullets = []
        
        self.enemyBullets = []
        self.enemyShockwaves = []

        self.baseZone = pygame.Rect(0, 0, 0, 0)

        self.hLevel = 0
        
        """
        20+: Projectiles move at twice the speed.
        40+: Shockwaves are twice the size.
        60+: Thorn Walkers fire at twice the rate.
        80+: Enemy sight range increased by 100%.
        100+: Night Demon --> True Nightmare, Regular Walkers are replaced with Hunt Walkers.
        """

        self.defeatedBosses = [False, False, False]
        
        self.finalBossSpawned = False
        self.nightDemonSpawns = 0
        self.ringShotCount = 0

        self.carryObject = 0
        self.carriedPlayer = Player(0)

        # Debug
        self.boxTraces = []

        # Fonts
        self.statFont = pygame.font.SysFont('Arial Black', 15)
        self.titleFont = pygame.font.SysFont('Arial Black', 40)
        self.subTitleFont = pygame.font.SysFont('Arial Black', 30)

        self.characterHeaderFont = pygame.font.SysFont('Arial Black', 25)
        self.characterBodyFont = pygame.font.SysFont('Arial Black', 20)

        self.generateRooms()

    # In-built functions
    def roomSwitch(self):
        self.stunBullets = []

    def reset(self):
         # Game Done
        self.victory = False

        # Base Gameplay
        self.player = Player(0)
        self.walls = []
        self.prevPlayerPos = [0, 0]

        self.cRoom = Room(0, 0, [], [], 0)
        self.rooms = []
        
        self.cMidWalls = [
            pygame.Rect(300, 400, 300, 20),
            pygame.Rect(600, 100, 20, 200)
        ]
        self.enemies = []

        self.stunBullets = []
        
        self.enemyBullets = []
        self.enemyShockwaves = []

        self.baseZone = pygame.Rect(0, 0, 0, 0)

        self.defeatedBosses = [False, False, False]
        
        self.finalBossSpawned = False
        self.nightDemonSpawns = 0
        self.ringShotCount = 0

        self.carryObject = 0
        self.carriedPlayer = Player(0)

        self.heldPlayers = [Player(0), Player(1), Player(2)]
        self.resources = 5
        self.abandonCount = 5
    
    def nearbyRoom(self, x, y):
        gotRoom = False
        selectedRoom = Room(self.cRoom.x, self.cRoom.y, [], [], -1)

        for room in self.rooms:
            if room.x == x and room.y == y:
                gotRoom = True
                selectedRoom = room
                break

        return gotRoom, selectedRoom
    
    def generateRooms(self):
        self.rooms = []
        availableBosses = [7, 8, 9]

        roomsToPlace = [3, 3, 3, 4]

        recoveryRoomCount = random.choice(range(3, 7))
        for i in range(0, recoveryRoomCount):
            roomsToPlace.append(2)

        numberOfRooms = random.choice(range(20, 50))
        while len(roomsToPlace) < numberOfRooms:
            roomsToPlace.append(1)
            
        random.shuffle(roomsToPlace)

        for i in range(0, 7):
            roomsToPlace.insert(0, 1)

        roomsToPlace.insert(0, 0)
    
        for rType in roomsToPlace:
            room = Room(0, 0, [], [], rType)
            
            if len(self.rooms) > 0:
                xPlace = 0
                yPlace = 0

                foundSpot = False
                while not foundSpot:
                    foundSpot = True

                    for room in self.rooms:
                        if xPlace == room.x and yPlace == room.y:
                            foundSpot = False
                            break

                    if not foundSpot:
                        if random.choice([0, 1]) == 0:
                            xPlace += random.choice([1, -1])
                        else:
                            yPlace += random.choice([1, -1])

                room = Room(xPlace, yPlace, [], [], rType)

                match room.rType:
                    case 0:
                        pass
                    
                    case 1:
                        wallCount = random.choice(range(2, 7))
                        for wall in range(0, wallCount):
                            select = random.choice([0, 1])
                            lowRoll = random.choice(range(20, 101))
                            highRoll = random.choice(range(101, 401))
                            wallDimensions = [random.choice(range(30, 931)), random.choice(range(30, 931)), lowRoll if select == 0 else highRoll, lowRoll if select == 1 else highRoll]

                            if wallDimensions[0] + wallDimensions[2] > 930:
                                wallDimensions[0] = 930 - wallDimensions[2]

                            if wallDimensions[1] + wallDimensions[3] > 930:
                                wallDimensions[1] = 930 - wallDimensions[3]

                            room.walls.append(pygame.Rect(wallDimensions[0], wallDimensions[1], wallDimensions[2], wallDimensions[3]))

                        enemyCount = random.choice(range(1, 4)) + min(math.floor(self.hLevel / 20), 5)
                        for enemy in range(0, enemyCount):
                            enemyTypes = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5]
                            if self.hLevel >= 100:
                                enemyTypes = [ 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 6, 6, 6]

                            gotLocation = False
                            newEnemy = Enemy(0, 0, 0)

                            while not gotLocation:
                                gotLocation = True

                                newEnemy = Enemy(random.choice(range(50, 901)), random.choice(range(50, 901)), random.choice(enemyTypes))
                                enemyRect = pygame.Rect(newEnemy.x, newEnemy.y, newEnemy.size, newEnemy.size)

                                sideWalls = [
                                    pygame.Rect(0, 0, 100, 950),
                                    pygame.Rect(900, 0, 100, 950),
                                    pygame.Rect(0, 0, 950, 100),
                                    pygame.Rect(0, 900, 950, 100)
                                ]
                                
                                for wall in room.walls:
                                    if pygame.Rect.colliderect(enemyRect, wall):
                                        gotLocation = False
                                        break

                                for wall in sideWalls:
                                    if pygame.Rect.colliderect(enemyRect, wall):
                                        gotLocation = False
                                        break

                            newEnemy.contactDamage *= 1 + (0.02 * self.hLevel)
                            newEnemy.speed += 0.1 * math.floor(self.hLevel / 5)
                            newEnemy.sightRange *= (2 if self.hLevel >= 80 else 1)
                            
                            room.enemies.append(newEnemy)

                        if random.choice([0, 0, 0, 1]) == 1:
                            resourceCount = random.choice(range(1, 3))
                            for i in range(0, resourceCount):
                                rLoc = [0, 0]
                                canPlace = False

                                while not canPlace:
                                    canPlace = True

                                    rLoc = [random.choice(range(0, 910)), random.choice(range(0, 930))]
                                    resourceRect = pygame.Rect(rLoc[0], rLoc[1], 40, 20)

                                    sideWalls = [
                                        pygame.Rect(0, 0, 50, 950),
                                        pygame.Rect(900, 0, 50, 950),
                                        pygame.Rect(0, 0, 950, 50),
                                        pygame.Rect(0, 900, 950, 50)
                                    ]

                                    for wall in room.walls:
                                        if pygame.Rect.colliderect(resourceRect, wall):
                                            canPlace = False
                                            break
                                    
                                    for wall in sideWalls:
                                        if pygame.Rect.colliderect(resourceRect, wall):
                                            canPlace = False
                                            break

                            room.resources.append(pygame.Rect(rLoc[0], rLoc[1], 40, 20))
                            
                    case 2:
                        resourceCount = random.choice(range(4, 8))
                        for i in range(0, resourceCount):
                            rLoc = [0, 0]
                            canPlace = False

                            while not canPlace:
                                canPlace = True

                                rLoc = [random.choice(range(0, 910)), random.choice(range(0, 930))]
                                resourceRect = pygame.Rect(rLoc[0], rLoc[1], 40, 20)

                                sideWalls = [
                                    pygame.Rect(0, 0, 50, 950),
                                    pygame.Rect(900, 0, 50, 950),
                                    pygame.Rect(0, 0, 950, 50),
                                    pygame.Rect(0, 900, 950, 50)
                                ]

                                for wall in sideWalls:
                                    if pygame.Rect.colliderect(resourceRect, wall):
                                        canPlace = False
                                        break

                            room.resources.append(pygame.Rect(rLoc[0], rLoc[1], 40, 20))
                            
                    case 3:
                        chosenBoss = random.choice(availableBosses)
                        newEnemy = Enemy(0, 0, chosenBoss)

                        newEnemy.x = 475 - math.floor(newEnemy.size / 2)
                        newEnemy.y = 475 - math.floor(newEnemy.size / 2)
                        newEnemy.isBoss = True

                        newEnemy.contactDamage *= 1 + (0.02 * self.hLevel)
                        newEnemy.speed += 0.1 * math.floor(self.hLevel / 5)
                        newEnemy.sightRange *= (2 if self.hLevel >= 80 else 1)

                        room.enemies.append(newEnemy)
                        availableBosses.remove(chosenBoss)
                    case 4:
                        pass

            self.rooms.append(room)
                
            if room.rType == 0:
                self.cRoom = room
    
    def drawText(self, text, colour, font, x, y, style): # For style: 0 = Left Anchor, 1 = Middle Anchor, 2 = Right Anchor
        global screen
        
        text = font.render(text, True, colour)

        text_rect = text.get_rect(center=(x, y))
        
        if style == 0:
            text_rect.left = x
        elif style == 2:
            text_rect = text.get_rect(center=(x, y))
            text_rect.right = x
        screen.blit(text, text_rect)

        return text_rect

    def playerCollision(self):
        playerRect = pygame.Rect(self.player.x, self.player.y, 30, 30)
        for wall in self.walls:
            if pygame.Rect.colliderect(playerRect, wall):
                self.player.x = self.prevPlayerPos[0]
                self.player.y = self.prevPlayerPos[1]
                break

        self.prevPlayerPos[0] = self.player.x
        self.prevPlayerPos[1] = self.player.y
    
    def baseGameLogic(self):
        # Setup
        self.enemies = self.cRoom.enemies
        self.player.stunTime -= 1
        
        # Player Stats
        self.player.charge = min(100, self.player.charge + self.player.chargeSpeed)

        # DEBUG
        self.boxTraces = []

        # Grabbing Stuff
        if self.carryObject == 0:
            for character in self.cRoom.fallenPlayers:
                fallenRect = pygame.Rect(character.x, character.y, 30, 30)
                playerRect = pygame.Rect(self.player.x, self.player.y, 30, 30)
                if pygame.Rect.colliderect(fallenRect, playerRect):
                    self.carryObject = character.aType + 2
                    self.carriedPlayer = copy.deepcopy(character)
                    self.cRoom.fallenPlayers.remove(character)
                    break

        if self.carryObject == 0:
            for resource in self.cRoom.resources:
                playerRect = pygame.Rect(self.player.x, self.player.y, 30, 30)
                if pygame.Rect.colliderect(resource, playerRect):
                    self.carryObject = 1
                    self.cRoom.resources.remove(resource)
                    break
                

        # Enemy Sight
        for enemy in self.enemies:
            hitWall = False
            
            xDist = self.player.x - enemy.x
            yDist = self.player.y - enemy.y

            lineTraceCoords = [enemy.x + (enemy.size / 2), enemy.y + (enemy.size / 2)]

            for i in range(0, enemy.sightRange):
                cTrace = pygame.Rect(lineTraceCoords[0], lineTraceCoords[1], 5, 5)
                self.boxTraces.append(cTrace)

                for wall in self.walls:
                    if pygame.Rect.colliderect(wall, cTrace):
                        hitWall = True
                        enemy.seesPlayer = False
                        break

                if hitWall:
                    break
                else:
                    playerRect = pygame.Rect(self.player.x, self.player.y, 30, 30)
                    
                    if pygame.Rect.colliderect(playerRect, cTrace):
                        enemy.seesPlayer = True
                        break
                    else:
                        if abs(xDist) > abs(yDist):
                            lineTraceCoords[0] += 1 if xDist >= 0 else -1
                            lineTraceCoords[1] += (yDist / abs(xDist)) if xDist != 0 else 1
                        else:
                            lineTraceCoords[1] += 1 if yDist >= 0 else -1
                            lineTraceCoords[0] += (xDist / abs(yDist)) if yDist != 0 else 1

                if i == enemy.sightRange - 1:
                    enemy.seesPlayer = False

        # Enemy Deletion
        for enemy in self.cRoom.enemies:
            if enemy.eType > 10 and enemy.x <= -50:
                self.cRoom.enemies.remove(enemy)

            elif enemy.health <= 0 and 7 <= enemy.eType <= 10:
                self.defeatedBosses[enemy.eType - 7] = True

                if enemy.eType == 9:
                    for enemy2 in self.cRoom.enemies:
                        if enemy2 != enemy:
                            self.cRoom.enemies.remove(enemy2)
                
                self.cRoom.enemies.remove(enemy)
        
        # Enemy Behaviour
        for enemy in self.enemies:
            if enemy.seesPlayer and enemy.cStun <= 0 and not enemy.isBoss:
                ogX = enemy.x
                enemy.x += min(enemy.speed, abs(enemy.x - self.player.x)) * (1 if enemy.x < self.player.x else -1)

                for wall in self.walls:
                    enemyRect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
                    if pygame.Rect.colliderect(enemyRect, wall):
                        enemy.x = ogX
                        break

                ogY = enemy.y
                enemy.y += min(enemy.speed, abs(enemy.y - self.player.y)) * (1 if enemy.y < self.player.y else -1)

                for wall in self.walls:
                    enemyRect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
                    if pygame.Rect.colliderect(enemyRect, wall):
                        enemy.y = ogY
                        break

                playerRect = pygame.Rect(self.player.x, self.player.y, 30, 30)
                enemyRect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)

                if pygame.Rect.colliderect(playerRect, enemyRect):
                    if self.player.aType == 2 and enemy.contactDamage > self.player.maxHealth * 0.25:
                        self.player.health -= self.player.maxHealth * 0.25
                    else:
                        self.player.health -= enemy.contactDamage
                    enemy.getStunned(enemy.hitStun * 5)

                if enemy.eType == 3:  # Thorn Walker Shots
                    enemy.nextShot -= 1 * (2 if self.hLevel >= 60 else 1)
                    if enemy.nextShot <= 0:
                        enemy.nextShot = 75

                        newBullet = enemyProjectile(enemy.x + int(enemy.size / 2), enemy.y + int(enemy.size / 2), 0, 0, 7, 3, int(enemy.contactDamage / 2))
                    
                        xDiff = ((self.player.x + 15) - (enemy.x + int(enemy.size / 2)))
                        yDiff = ((self.player.y + 15) - (enemy.y + int(enemy.size / 2)))
                        fullDist = math.sqrt(xDiff**2 + yDiff**2)
                        ratio = 6 / fullDist

                        newBullet.xSpeed = ratio * xDiff
                        newBullet.ySpeed = ratio * yDiff

                        self.enemyBullets.append(newBullet)

                elif enemy.eType == 4: # Toxic Walker Shockwave
                    enemy.nextShot -= 1
                    if enemy.nextShot <= 0:
                        enemy.nextShot = 400

                        self.enemyShockwaves.append(enemyShockwave(enemy.x + int(enemy.size / 2), enemy.y + int(enemy.size / 2), (0, 74, 10), 250, 4, 1))

            enemy.cStun -= 1

            if enemy.isBoss and enemy.bossAggro: # Boss Fight
                if enemy.eType == 7:
                    enemy.moveTarget = [self.player.x, self.player.y]

                if enemy.cStun <= 0:
                    ogX = enemy.x
                    enemy.x += min(enemy.speed, abs(enemy.x - enemy.moveTarget[0])) * (1 if enemy.x < enemy.moveTarget[0] else -1)

                    for wall in self.walls:
                        enemyRect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
                        if pygame.Rect.colliderect(enemyRect, wall):
                            enemy.x = ogX
                            break

                    ogY = enemy.y
                    enemy.y += min(enemy.speed, abs(enemy.y - enemy.moveTarget[1])) * (1 if enemy.y < enemy.moveTarget[1] else -1)

                    for wall in self.walls:
                        enemyRect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
                        if pygame.Rect.colliderect(enemyRect, wall):
                            enemy.y = ogY
                            break

                    playerRect = pygame.Rect(self.player.x, self.player.y, 30, 30)
                    enemyRect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)

                    if pygame.Rect.colliderect(playerRect, enemyRect):
                        if self.player.aType == 2 and enemy.contactDamage > self.player.maxHealth * 0.25:
                            self.player.health -= self.player.maxHealth * 0.25
                        else:
                            self.player.health -= enemy.contactDamage
                        enemy.getStunned(enemy.hitStun * 5)

                # Shadow Walker
                if enemy.eType == 7 and enemy.x <= -1000:
                    enemy.nextShot -= 1
                    if enemy.nextShot <= 0:
                        gotSpot = False

                        while not gotSpot:
                            gotSpot = True
                            enemy.x = random.choice(range(50, 900))
                            enemy.y = random.choice(range(50, 900))

                            if (enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2 <= 200**2:
                                gotSpot = False
                        enemy.cStun = 0

                        if enemy.health <= 10:
                            directions = [[1, 0], [1, 0.5], [1, 1], [0.5, 1], [0, 1], [-0.5, 1], [-1, 1], [-1, 0.5], [-1, 0], [-1, -0.5], [-1, -1], [-0.5, -1], [0, -1], [0.5, -1], [1, -1], [1, -0.5]]

                            for direction in directions:
                                newBullet = enemyProjectile(enemy.x + int(enemy.size / 2), enemy.y + int(enemy.size / 2), 0, 0, 7, 3, int(enemy.contactDamage / 2))
                                
                                newBullet.xSpeed = direction[0] * 0.75
                                newBullet.ySpeed = direction[1] * 0.75

                                self.enemyBullets.append(newBullet)

                        if enemy.health <= 15:
                            spawns = 1 + math.floor((20 - enemy.health) / 5)
                            for i in range(0, spawns):
                                gotSpot = False
                                while not gotSpot:
                                    gotSpot = True
                                    newEnemy = Enemy(random.choice(range(50, 900)), random.choice(range(50, 900)), 11)
                                    newEnemy.contactDamage *= 1 + (0.02 * self.hLevel)
                                    newEnemy.speed += 0.1 * math.floor(self.hLevel / 5)
                                    newEnemy.sightRange *= (2 if self.hLevel >= 80 else 1)

                                    if (newEnemy.x - self.player.x)**2 + (newEnemy.y - self.player.y)**2 <= 150**2:
                                        gotSpot = False

                                    if gotSpot:
                                        self.cRoom.enemies.append(newEnemy)

                # Blade Walker
                if enemy.eType == 8:
                    #enemy.size += 0.1
                    if (enemy.x == enemy.moveTarget[0] and enemy.y == enemy.moveTarget[1]) or enemy.moveTarget == [0, 0]:
                        if random.choice([0, 0, 1]) == 1:
                            enemy.moveTarget = [self.player.x, self.player.y]
                        else:
                            gotSpot = False
                            while not gotSpot:
                                gotSpot = True
                                enemy.moveTarget = [random.choice(range(20, 901)), random.choice(range(20, 901))]

                                if (enemy.moveTarget[0] - self.player.x)**2 + (enemy.moveTarget[1] - self.player.y)**2 >= 50**2:
                                    gotSpot = False

                    enemy.nextShot -= 1
                    if enemy.nextShot <= 0 and enemy.health <= 12:
                        enemy.nextShot = 40 - (2 * (15 - enemy.health))

                        newBullet = enemyProjectile(enemy.x + int(enemy.size / 2), enemy.y + int(enemy.size / 2), 0, 0, 7, 3, int(enemy.contactDamage / 2))
                    
                        xDiff = ((self.player.x + 15) - (enemy.x + int(enemy.size / 2)))
                        yDiff = ((self.player.y + 15) - (enemy.y + int(enemy.size / 2)))
                        fullDist = math.sqrt(xDiff**2 + yDiff**2)
                        ratio = 10 / fullDist

                        newBullet.xSpeed = ratio * xDiff
                        newBullet.ySpeed = ratio * yDiff

                        self.enemyBullets.append(newBullet)

                    if enemy.health <= 5:
                        enemy.speed = 5

                # Terror Walker
                if enemy.eType == 9:
                    enemy.moveTarget = [self.player.x - 45, self.player.y - 45]

                    barriers = [28, 26, 18, 12, 5]
                    for barrier in barriers:
                        if enemy.health <= barrier and len(self.cRoom.enemies) < barriers.index(barrier) + 2:
                            gotSpot = False
                            while not gotSpot:
                                gotSpot = True
                                newEnemy = Enemy(random.choice(range(50, 900)), random.choice(range(50, 900)), 0)
                                newEnemy.contactDamage *= 1 + (0.02 * self.hLevel)
                                newEnemy.speed = 2
                                newEnemy.speed += 0.1 * math.floor(self.hLevel / 5) + barriers.index(barrier) * 0.2
                                newEnemy.sightRange = 1500

                                if (newEnemy.x - self.player.x)**2 + (newEnemy.y - self.player.y)**2 <= 300**2:
                                    gotSpot = False

                                if gotSpot:
                                    self.cRoom.enemies.append(newEnemy)

                        if enemy.health <= 15:
                            if len(self.enemyShockwaves) <= 0:
                                enemy.nextShot -= 1
                            
                            if enemy.nextShot <= 0:
                                enemy.nextShot = 500
                                
                                self.enemyShockwaves.append(enemyShockwave(enemy.x + int(enemy.size / 2), enemy.y + int(enemy.size / 2), (120, 0, 0), 400, 3, 1))

                # Night Demon
                if enemy.eType == 10 and self.hLevel < 100:
                    enemy.moveTarget = [self.player.x - 25, self.player.y - 25]
                    enemy.nextShot -= 1
                    enemy.speed = 0

                    if len(self.cRoom.enemies) <= 1:
                        spawns = 2 + math.floor((20 - enemy.health) / 3)
                        for i in range(0, spawns):
                            gotSpot = False
                            while not gotSpot:
                                gotSpot = True
                                newEnemy = Enemy(random.choice(range(50, 900)), random.choice(range(50, 900)), 11)
                                newEnemy.speed = 2
                                newEnemy.contactDamage *= 1 + (0.02 * self.hLevel)
                                newEnemy.speed += 0.1 * math.floor(self.hLevel / 5)
                                newEnemy.sightRange *= (2 if self.hLevel >= 80 else 1)

                                if (newEnemy.x - self.player.x)**2 + (newEnemy.y - self.player.y)**2 <= 400**2:
                                    gotSpot = False

                                if gotSpot:
                                    self.cRoom.enemies.append(newEnemy)

                    if enemy.nextShot <= 0 and enemy.health <= 18:
                        enemy.nextShot = 100 - ((20 - enemy.health) * 3)

                        newBullet = enemyProjectile(enemy.x + int(enemy.size / 2), enemy.y + int(enemy.size / 2), 0, 0, 7, 3, int(enemy.contactDamage / 2))
                    
                        xDiff = ((self.player.x + 15) - (enemy.x + int(enemy.size / 2)))
                        yDiff = ((self.player.y + 15) - (enemy.y + int(enemy.size / 2)))
                        fullDist = math.sqrt(xDiff**2 + yDiff**2)
                        ratio = 10 / fullDist

                        newBullet.xSpeed = ratio * xDiff
                        newBullet.ySpeed = ratio * yDiff

                        self.enemyBullets.append(newBullet)

                        self.ringShotCount -= 1
                        if enemy.health <= 12 and self.ringShotCount <= 0:
                            self.ringShotCount = 5
                            directions = [[1, 0], [1, 0.5], [1, 1], [0.5, 1], [0, 1], [-0.5, 1], [-1, 1], [-1, 0.5], [-1, 0], [-1, -0.5], [-1, -1], [-0.5, -1], [0, -1], [0.5, -1], [1, -1], [1, -0.5]]

                            for direction in directions:
                                newBullet = enemyProjectile(enemy.x + int(enemy.size / 2), enemy.y + int(enemy.size / 2), 0, 0, 7, 3, int(enemy.contactDamage / 2))
                                
                                newBullet.xSpeed = direction[0] * 0.75
                                newBullet.ySpeed = direction[1] * 0.75

                                self.enemyBullets.append(newBullet)

                            if enemy.health <= 6:
                                self.enemyShockwaves.append(enemyShockwave(enemy.x + int(enemy.size / 2), enemy.y + int(enemy.size / 2), (60, 60, 60), 350 if self.hLevel < 80 else 200, 4, 1))

                # Walking Nightmare
                if enemy.eType == 10 and self.hLevel >= 100:
                    enemy.moveTarget = [self.player.x - 25, self.player.y - 25]
                    enemy.nextShot -= 1
                    enemy.colour = (163, 11, 0)
                    enemy.speed = 0 if enemy.health > 10 else 0.5

                    if len(self.cRoom.enemies) <= 1:
                        spawns = 3 + math.floor((30 - enemy.health) / 3)
                        for i in range(0, spawns):
                            gotSpot = False
                            while not gotSpot:
                                gotSpot = True
                                newEnemy = Enemy(random.choice(range(50, 900)), random.choice(range(50, 900)), 11)
                                newEnemy.speed = 1.5
                                newEnemy.contactDamage *= 1 + (0.02 * self.hLevel)
                                newEnemy.speed += 0.1 * math.floor(self.hLevel / 5)
                                newEnemy.sightRange *= (2 if self.hLevel >= 80 else 1)

                                if (newEnemy.x - self.player.x)**2 + (newEnemy.y - self.player.y)**2 <= 400**2:
                                    gotSpot = False

                                if gotSpot:
                                    self.cRoom.enemies.append(newEnemy)

                    if enemy.nextShot <= 0:
                        enemy.nextShot = 100 - ((20 - enemy.health) * 3)

                        newBullet = enemyProjectile(enemy.x + int(enemy.size / 2), enemy.y + int(enemy.size / 2), 0, 0, 7, 3, int(enemy.contactDamage / 2))
                    
                        xDiff = ((self.player.x + 15) - (enemy.x + int(enemy.size / 2)))
                        yDiff = ((self.player.y + 15) - (enemy.y + int(enemy.size / 2)))
                        fullDist = math.sqrt(xDiff**2 + yDiff**2)
                        ratio = 10 / fullDist

                        newBullet.xSpeed = ratio * xDiff
                        newBullet.ySpeed = ratio * yDiff

                        self.enemyBullets.append(newBullet)

                        self.ringShotCount -= 1
                        if enemy.health <= 25 and self.ringShotCount <= 0:
                            self.ringShotCount = 3
                            directions = [[1, 0], [1, 0.5], [1, 1], [0.5, 1], [0, 1], [-0.5, 1], [-1, 1], [-1, 0.5], [-1, 0], [-1, -0.5], [-1, -1], [-0.5, -1], [0, -1], [0.5, -1], [1, -1], [1, -0.5]]

                            for direction in directions:
                                newBullet = enemyProjectile(enemy.x + int(enemy.size / 2), enemy.y + int(enemy.size / 2), 0, 0, 7, 3, int(enemy.contactDamage / 2))
                                
                                newBullet.xSpeed = direction[0] * 0.75
                                newBullet.ySpeed = direction[1] * 0.75

                                self.enemyBullets.append(newBullet)

                            if enemy.health <= 20:
                                self.enemyShockwaves.append(enemyShockwave(enemy.x + int(enemy.size / 2), enemy.y + int(enemy.size / 2), (60, 60, 60), 200, 4, 1))
                    

        # Stun Projectiles
        for projectile in self.stunBullets:
            projectile.x += projectile.xSpeed
            projectile.y += projectile.ySpeed

            for wall in self.walls:
                if wall.collidepoint((projectile.x, projectile.y)):
                    projectile.x = -1000
                    break

            for enemy in self.cRoom.enemies:
                enemyRect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
                if enemyRect.collidepoint((projectile.x, projectile.y)):
                    if enemy.eType != 2: # Knight Walker Immunity
                        enemy.getStunned(enemy.hitStun * 8)

                    if enemy.isBoss:
                        enemy.health -= self.player.power
                        enemy.cStun = 0

                        if not enemy.bossAggro:
                            enemy.bossAggro = True
                            enemy.health += self.player.power

                            if self.player.x < 20:
                                self.player.x = 21
                            elif self.player.x > 900:
                                self.player.x = 899

                            if self.player.y < 20:
                                self.player.y = 21
                            elif self.player.y > 900:
                                self.player.y = 899

                        if enemy.eType == 7:
                            enemy.x = -10000
                            enemy.nextShot = random.choice(range(200, 301)) - (10 * (20 - enemy.health))

                            for enemy in self.cRoom.enemies:
                                if enemy.eType == 11:
                                    enemy.x = -10000

                        elif enemy.eType == 10:
                            damageBoss = True
                            for enemy2 in self.cRoom.enemies:
                                if enemy2.eType == 11 and enemy2.cStun <= 0:
                                    damageBoss = False

                            if damageBoss:
                                for enemy2 in self.cRoom.enemies:
                                    if enemy2.eType == 11:
                                        enemy2.x = -10000
                            else:
                                enemy.health += self.player.power

                        if enemy.health <= 0:
                            if enemy.eType == 9:
                                for enemy2 in self.cRoom.enemies:
                                    if enemy2 != enemy:
                                        enemy2.x = -100000
                                        enemy2.eType = 11
                                        enemy2.cStun = 99999999999

                            elif enemy.eType == 10:
                                self.victory = True
                                self.gameState = 4

                            print(enemy.eType)
                            if 7 <= enemy.eType <= 9:
                                self.defeatedBosses[enemy.eType - 7] = True

                            self.cRoom.enemies.remove(enemy)

                    projectile.x = -10000
                    break

        for projectile in self.stunBullets:
            if not -50 <= projectile.x <= 1000 or not -50 <= projectile.y <= 1000:
                self.stunBullets.remove(projectile)

        # Enemy Projectiles
        for projectile in self.enemyBullets:
            projectile.x += projectile.xSpeed * (1.5 if self.hLevel >= 20 else 1)
            projectile.y += projectile.ySpeed * (1.5 if self.hLevel >= 20 else 1)

            for wall in self.walls:
                if wall.collidepoint((projectile.x, projectile.y)):
                    projectile.x = -1000
                    break
            
            playerRect = pygame.Rect(self.player.x, self.player.y, 30, 30)

            if playerRect.collidepoint(projectile.x, projectile.y):
                projectile.x = -1000

                damageToDeal = projectile.damage * (1 + (0.01 * self.hLevel))

                if self.player.aType == 2 and damageToDeal > self.player.maxHealth * 0.25:
                    self.player.health -= self.player.maxHealth * 0.25
                else:
                    self.player.health -= damageToDeal

        for projectile in self.enemyBullets:
            if not -50 <= projectile.x <= 1000 or not -50 <= projectile.y <= 1000:
                self.enemyBullets.remove(projectile)

        # Enemy Shockwaves
        for shockwave in self.enemyShockwaves:
            shockwave.size += shockwave.growSpeed
            if shockwave.size >= shockwave.fSize * (2 if self.hLevel >= 40 else 1):
                self.enemyShockwaves.remove(shockwave)
            else:
                if (((self.player.x + 15) - shockwave.x)**2 + ((self.player.y + 15) - shockwave.y)**2) <= shockwave.size**2:
                    self.player.stunTime = shockwave.stunTime

        # Final Boss Spawning
        if not self.finalBossSpawned:
            doSpawn = True
            for defeat in self.defeatedBosses:
                if not defeat:
                    doSpawn = False
                    break

            if doSpawn:
                targetRoom = Room(0, 0, [], [], 0)
                for room in self.rooms:
                    if room.rType == 4:
                        targetRoom = room
                        break

                newEnemy = Enemy(435, 435, 10)
                newEnemy.x = 475 - math.floor(newEnemy.size / 2)
                newEnemy.y = 475 - math.floor(newEnemy.size / 2)
                newEnemy.isBoss = True

                newEnemy.contactDamage *= 1 + (0.02 * self.hLevel)
                newEnemy.speed += 0.1 * math.floor(self.hLevel / 5)
                newEnemy.sightRange *= (2 if self.hLevel >= 80 else 1)

                if self.hLevel >= 100:
                    newEnemy.maxHealth = 30
                    newEnemy.health = 30

                targetRoom.enemies.append(newEnemy)
                self.finalBossSpawned = True
        
        # Player Changing Rooms
        directions = [
            [0, 1],
            [1, 0],
            [0, -1],
            [-1, 0]
        ]

        selectedDirection = -1
        
        if self.player.x <= -30:
            selectedDirection = 3
        
        elif self.player.x >= 950:
            selectedDirection = 1

        elif self.player.y <= -30:
            selectedDirection = 0

        elif self.player.y >= 950:
            selectedDirection = 2
            
        if selectedDirection != -1:
            nextRoom = self.nearbyRoom(self.cRoom.x + directions[selectedDirection][0], self.cRoom.y + directions[selectedDirection][1])[1]

            for room in self.rooms:
                if room.x == self.cRoom.x and room.y == self.cRoom.y:
                    room = self.cRoom
                    break

            self.cRoom = nextRoom

            if directions[selectedDirection][0] == 0:
                self.player.y = 949 if selectedDirection == 0 else -29
                self.prevPlayerPos[1] = self.player.y
                self.prevPlayerPos[0] = 460
                
            else:
                self.player.x = 949 if selectedDirection == 3 else -29
                self.prevPlayerPos[0] = self.player.x
                self.prevPlayerPos[1] = 460

            self.stunBullets = []
            self.enemyBullets = []
            self.enemyShockwaves = []
                    
    def inputs(self):
        global gameRunning
        
        match self.gameState:
            case 0:
                # Button Input
                if pygame.mouse.get_pressed()[0] and not self.leftClicked:
                    self.leftClicked = True
                    
                    mouseX, mouseY = pygame.mouse.get_pos()

                    for button in self.textButtons:
                        if button[1].collidepoint(mouseX, mouseY):
                            if button[0] == 0:
                                self.gameState = 3
                                self.abandonCount = 5
                                self.reset()
                                self.generateRooms()

                            elif button[0] == 1:
                                self.gameState = 1

                            elif button[0] == 2:
                                gameRunning = False

                            elif button[0] == 3:
                                self.hLevel = max(0, self.hLevel - 1)

                            elif button[0] == 4:
                                self.hLevel = min(100, self.hLevel + 1)

                            elif button[0] == 5:
                                self.hLevel = max(0, self.hLevel - 10)

                            elif button[0] == 6:
                                self.hLevel = min(100, self.hLevel + 10)

                            elif button[0] == 7:
                                self.hLevel = 0

                            elif button[0] == 8:
                                self.hLevel = 100
                
                elif not pygame.mouse.get_pressed()[0]:
                    self.leftClicked = False

            case 1:
                # Button Input
                if pygame.mouse.get_pressed()[0] and not self.leftClicked:
                    self.leftClicked = True
                    
                    mouseX, mouseY = pygame.mouse.get_pos()

                    for button in self.textButtons:
                        if button[1].collidepoint(mouseX, mouseY):
                            self.gameState = 0

                elif not pygame.mouse.get_pressed()[0]:
                    self.leftClicked = False

            case 2:
                keys = pygame.key.get_pressed()

                # Player Movement
                if keys[pygame.K_w] and self.player.stunTime <= 0:
                    self.player.y -= self.player.speed + (2 if (keys[pygame.K_LSHIFT] and self.player.stamina > 0) else 0)
                elif keys[pygame.K_s] and self.player.stunTime <= 0:
                    self.player.y += self.player.speed + (2 if (keys[pygame.K_LSHIFT] and self.player.stamina > 0) else 0)

                self.playerCollision()

                if keys[pygame.K_a] and self.player.stunTime <= 0:
                    self.player.x -= self.player.speed + (2 if (keys[pygame.K_LSHIFT] and self.player.stamina > 0) else 0)
                elif keys[pygame.K_d] and self.player.stunTime <= 0:
                    self.player.x += self.player.speed + (2 if (keys[pygame.K_LSHIFT] and self.player.stamina > 0) else 0)

                self.playerCollision()

                # Stamina Drain
                if keys[pygame.K_LSHIFT]:
                    self.player.stamina = max(0, self.player.stamina - 1)
                else:
                    self.player.stamina = min(self.player.maxStamina, self.player.stamina + (0.2 if self.player.aType != 1 else 0.4))

                # Firing
                if pygame.mouse.get_pressed()[0] and self.player.charge >= 100:
                    self.player.charge = 0

                    newBullet = stunProjectile(self.player.x + 15, self.player.y + 15, 0, 0, 5, 5)
                    
                    mouseX, mouseY = pygame.mouse.get_pos()
                    
                    xDiff = (mouseX - (self.player.x + 15))
                    yDiff = (mouseY - (self.player.y + 15))
                    fullDist = math.sqrt(xDiff**2 + yDiff**2)
                    ratio = 12 / fullDist

                    newBullet.xSpeed = ratio * xDiff
                    newBullet.ySpeed = ratio * yDiff

                    self.stunBullets.append(newBullet)

                # Dropping Stuff
                if keys[pygame.K_q] and self.carryObject != 0:
                    shimmyBases = [[20, 20], [20, -20], [-20, 20], [-20, -20]]
                    
                    newResource = [0, 0]
                    for i in range(1, 4):
                        successfulShimmy = False
                        done = False
                        resourceRect = pygame.Rect(0, 0, 40, 20)
                        
                        for shimmy in shimmyBases:
                            successfulShimmy = True
                            
                            newResource = [self.player.x + (shimmy[0] * i), self.player.y + (shimmy[1] * i)]

                            resourceRect = pygame.Rect(newResource[0], newResource[1], 40, 20) if self.carryObject == 1 else pygame.Rect(newResource[0], newResource[1], 30, 30)

                            sideWalls = [
                                pygame.Rect(0, 0, 50, 950),
                                pygame.Rect(900, 0, 50, 950),
                                pygame.Rect(0, 0, 950, 50),
                                pygame.Rect(0, 900, 950, 50)
                            ]

                            if not (0 <= resourceRect[0] <= 950) or not (0 <= resourceRect[1] <= 950):
                                successfulShimmy = False

                            for wall in self.cRoom.walls:
                                if pygame.Rect.colliderect(resourceRect, wall):
                                    successfulShimmy = False
                            
                            for wall in sideWalls:
                                if pygame.Rect.colliderect(resourceRect, wall):
                                    successfulShimmy = False

                            playerRect = pygame.Rect(self.player.x, self.player.y, 30, 30)
                            if pygame.Rect.colliderect(resourceRect, playerRect):
                                successfulShimmy = False

                            if successfulShimmy:
                                if self.carryObject == 1:
                                    self.cRoom.resources.append(resourceRect)
                                else:
                                    self.carriedPlayer.x = newResource[0]
                                    self.carriedPlayer.y = newResource[1]

                                    self.cRoom.fallenPlayers.append(self.carriedPlayer)
                                
                                done = True
                                break
                            elif i == 3:
                                if self.carryObject == 1:
                                    self.cRoom.resources.append(resourceRect)
                                    resourceRect = pygame.Rect(self.player.x, self.player.y, 40, 20)
                                else:
                                    self.carriedPlayer.x = self.player.x
                                    self.carriedPlayer.y =  self.player.y

                                    self.cRoom.fallenPlayers.append(self.carriedPlayer)
                                done = True
                                break
                        if done:
                            break

                    self.carryObject = 0
                                
            case 3:
                # Button Input
                if pygame.mouse.get_pressed()[0] and not self.leftClicked:
                    self.leftClicked = True
                    
                    mouseX, mouseY = pygame.mouse.get_pos()

                    for button in self.textButtons:
                        if button[1].collidepoint(mouseX, mouseY):
                            if button[0] == 15:
                                self.abandonCount -= 1
                                if self.abandonCount <= 0:
                                    self.gameState = 0

                            elif (button[0] == 0 or button[0] == 5 or button[0] == 10) and self.resources >= 1:
                                self.resources -= 1
                                targetChar = [0, 5, 10]

                                selectedIndex = targetChar.index(button[0])
                                if self.heldPlayers[selectedIndex].health == self.heldPlayers[selectedIndex].maxHealth:
                                    self.resources += 1
                                else:
                                    self.heldPlayers[selectedIndex].health = min(self.heldPlayers[selectedIndex].health + int(self.heldPlayers[selectedIndex].maxHealth * 0.6), self.heldPlayers[selectedIndex].maxHealth)

                            elif (button[0] == 1 or button[0] == 6 or button[0] == 11) and self.resources >= 3:
                                self.resources -= 3
                                targetChar = [1, 6, 11]

                                selectedIndex = targetChar.index(button[0])
                                self.heldPlayers[selectedIndex].speed += 0.5
                                self.heldPlayers[selectedIndex].speed = float(format(self.heldPlayers[selectedIndex].speed, ".1f"))

                            elif (button[0] == 2 or button[0] == 7 or button[0] == 12) and self.resources >= 2:
                                self.resources -= 2
                                targetChar = [2, 7, 12]

                                selectedIndex = targetChar.index(button[0])
                                self.heldPlayers[selectedIndex].maxStamina += 10

                            elif (button[0] == 3 or button[0] == 8 or button[0] == 13) and self.resources >= 3:
                                self.resources -= 3
                                targetChar = [3, 8, 13]

                                selectedIndex = targetChar.index(button[0])
                                self.heldPlayers[selectedIndex].chargeSpeed += 0.2
                                self.heldPlayers[selectedIndex].chargeSpeed = float(format(self.heldPlayers[selectedIndex].chargeSpeed, ".2f"))

                            elif button[0] == 4 or button[0] == 9 or button[0] == 14:
                                targetChar = [4, 9, 14]

                                selectedIndex = targetChar.index(button[0])
                                character = self.heldPlayers[selectedIndex]

                                self.player = character
                                self.player.x = 460
                                self.player.y = 460
                                self.player.charge = 0
                                self.player.stamina = self.player.maxStamina

                                self.stunBullets = []
                                self.enemyBullets = []
                                self.enemyShockwaves = []

                                for room in self.rooms:
                                    if room.rType == 0:
                                        self.cRoom = room

                                self.gameState = 2
                
                elif not pygame.mouse.get_pressed()[0]:
                    self.leftClicked = False

            case 4:
                # Button Input
                if pygame.mouse.get_pressed()[0] and not self.leftClicked:
                    self.leftClicked = True
                    
                    mouseX, mouseY = pygame.mouse.get_pos()

                    for button in self.textButtons:
                        if button[1].collidepoint(mouseX, mouseY):
                            if button[0] == 0:
                                self.gameState = 0
                
                elif not pygame.mouse.get_pressed()[0]:
                    self.leftClicked = False
    
    def logic(self):
        match self.gameState:
            case 0:
                self.nextBlink -= 1
                if self.nextBlink <= 0 and self.blinkMax == 0:
                    self.blinkMax = random.choice(range(20, 41))
                    self.blinkDirection = 1

                if self.blinkMax > 0:
                    self.blinkIntensity += self.blinkDirection

                    if self.blinkDirection == 1 and self.blinkIntensity >= self.blinkMax:
                        self.blinkDirection = -1
                    elif self.blinkDirection == -1 and self.blinkIntensity <= 0:
                        self.blinkIntensity = 0
                        self.blinkMax = 0
                        self.nextBlink = random.choice(range(150, 200))
                pass

            case 1:
                self.nextBlink -= 1
                if self.nextBlink <= 0 and self.blinkMax == 0:
                    self.blinkMax = random.choice(range(20, 41))
                    self.blinkDirection = 1

                if self.blinkMax > 0:
                    self.blinkIntensity += self.blinkDirection

                    if self.blinkDirection == 1 and self.blinkIntensity >= self.blinkMax:
                        self.blinkDirection = -1
                    elif self.blinkDirection == -1 and self.blinkIntensity <= 0:
                        self.blinkIntensity = 0
                        self.blinkMax = 0
                        self.nextBlink = random.choice(range(150, 200))

            case 2:
                self.baseGameLogic()

                playerRect = pygame.Rect(self.player.x, self.player.y, 30, 30)
                if pygame.Rect.colliderect(playerRect, self.baseZone):
                    self.abandonCount = 5
                    self.gameState = 3

                    for enemy in self.cRoom.enemies:
                        if enemy.eType == 11:
                            enemy.x = -10000

                    if self.carryObject >= 2:
                        self.carriedPlayer.health = 1
                        self.heldPlayers[self.carryObject - 2] = self.carriedPlayer
                        self.carryObject = 0
                    elif self.carryObject == 1:
                        self.carryObject = 0
                        self.resources += 1

                if self.player.health <= 0:
                    self.cRoom.fallenPlayers.append(self.player)
                    self.carryObject = 0
                    self.carriedPlayer = Player(0)

                    for enemy in self.cRoom.enemies:
                        if enemy.isBoss:
                            enemy.bossAggro = False
                    
                    for room in self.rooms:
                        if room.x == self.cRoom.x and room.y == self.cRoom.y:
                            room = self.cRoom
                            break

                    self.gameState = 3

            case 3:
                hasLost = True
                for character in self.heldPlayers:
                    if character.health > 0:
                        hasLost = False
                        break

                if hasLost:
                    self.gameState = 4

    def draw(self):
        global screen

        match self.gameState:
            case 0:
                screen.fill((self.blinkIntensity, 0, 0))

                self.textButtons = []

                self.drawText("--- SILENT NIGHT ---", (255, 255, 255), self.titleFont, 475, 30, 1)
                self.drawText("You know your orders.", (200, 200, 200), self.characterHeaderFont, 475, 70, 1)

                button = self.drawText("> Play <", (255, 255, 255), self.characterHeaderFont, 475, 435, 1)
                self.textButtons.append([0, button])

                button = self.drawText("> Help <", (255, 255, 255), self.characterHeaderFont, 475, 475, 1)
                self.textButtons.append([1, button])
                
                button = self.drawText("> Quit <", (255, 255, 255), self.characterHeaderFont, 475, 515, 1)
                self.textButtons.append([2, button])

                self.drawText("Hazard Level: " + str(self.hLevel), (255, 255, 255), self.characterHeaderFont, 475, 650, 1)

                button = self.drawText("<", (255, 255, 255), self.characterHeaderFont, 330, 650, 1)
                self.textButtons.append([3, button])

                button = self.drawText(">", (255, 255, 255), self.characterHeaderFont, 620, 650, 1)
                self.textButtons.append([4, button])

                button = self.drawText("<<", (255, 255, 255), self.characterHeaderFont, 280, 650, 1)
                self.textButtons.append([5, button])

                button = self.drawText(">>", (255, 255, 255), self.characterHeaderFont, 670, 650, 1)
                self.textButtons.append([6, button])

                button = self.drawText("0", (255, 255, 255), self.characterHeaderFont, 230, 650, 1)
                self.textButtons.append([7, button])

                button = self.drawText("100", (255, 255, 255), self.characterHeaderFont, 730, 650, 1)
                self.textButtons.append([8, button])

            case 1:
                screen.fill((self.blinkIntensity, 0, 0))
                
                self.drawText("--- SILENT NIGHT ---", (255, 255, 255), self.titleFont, 475, 30, 1)
                self.drawText("Here are your orders.", (200, 200, 200), self.characterHeaderFont, 475, 70, 1)

                self.drawText("You lead a military operation against a horde of demons named 'walkers'.", (255, 255, 255), self.characterBodyFont, 475, 200, 1)
                self.drawText("Your objective is to find and eliminate the Night Demon.", (255, 255, 255), self.characterBodyFont, 475, 230, 1)
                self.drawText("There is no intel on where it is or what it can do. It is up to you to find that out.", (255, 255, 255), self.characterBodyFont, 475, 260, 1)

                self.drawText("You have been given command of three brave mercenaries - Only the best we have.", (255, 255, 255), self.characterBodyFont, 475, 320, 1)
                self.drawText("Only one is allowed out on the field at a time to minimise casualties.", (255, 255, 255), self.characterBodyFont, 475, 350, 1)
                self.drawText("Each has been given a stun gun. It is only capable of killing specific walkers.", (255, 255, 255), self.characterBodyFont, 475, 380, 1)
                self.drawText("Evade walkers by running from them or stunning them with the stun gun.", (255, 255, 255), self.characterBodyFont, 475, 440, 1)
                self.drawText("Collect resources and bring them back to base to improve your mercenaries.", (255, 255, 255), self.characterBodyFont, 475, 470, 1)
                self.drawText("Our base is situated in one of the few safe areas, marked by the blue square.", (255, 255, 255), self.characterBodyFont, 475, 500, 1)
                
                self.drawText("WASD: Move.", (255, 255, 255), self.characterBodyFont, 475, 560, 1)
                self.drawText("Shift: Run (requires stamina).", (255, 255, 255), self.characterBodyFont, 475, 590, 1)
                self.drawText("Left Click: Fire a stun projectile (requires 100% charge).", (255, 255, 255), self.characterBodyFont, 475, 620, 1)

                button = self.drawText("> Back <", (255, 255, 255), self.characterHeaderFont, 475, 920, 1)
                self.textButtons.append([0, button])

            case 2:
                screen.fill((20, 20, 20))

                # Base
                self.baseZone = pygame.Rect(0, 0, 0, 0) if self.cRoom.rType != 0 else pygame.Rect(20, 830, 100, 100)
                pygame.draw.rect(screen, (0, 0, 200), self.baseZone)

                if self.cRoom.rType == 4 and not self.finalBossSpawned:
                    trianglePoints = [(475, 450), (400, 300), (550, 300)]
                    pygame.draw.circle(screen, (255, 255, 255), (475, 475), 10)
                    
                    if not self.defeatedBosses[0]:
                        pygame.draw.polygon(screen, (90, 90, 90), (trianglePoints[0],trianglePoints[1], trianglePoints[2]))

                    if not self.defeatedBosses[1]:
                        newPoints = []
                        for point in trianglePoints:
                            newPoint = [0, 0]
                            newPoint[0] = ((point[0] - 475) * math.cos(math.radians(120)) + (point[1] - 475) * -math.sin(math.radians(120))) + 475
                            newPoint[1] = ((point[0] - 475) * math.sin(math.radians(120)) + (point[1] - 475) * math.cos(math.radians(120))) + 475
                            newPoints.append((newPoint[0], newPoint[1]))
                        pygame.draw.polygon(screen, (166, 21, 2), (newPoints[0], newPoints[1], newPoints[2]))

                    if not self.defeatedBosses[2]:
                        newPoints = []
                        for point in trianglePoints:
                            newPoint = [0, 0]
                            newPoint[0] = ((point[0] - 475) * math.cos(math.radians(240)) + (point[1] - 475) * -math.sin(math.radians(240))) + 475
                            newPoint[1] = ((point[0] - 475) * math.sin(math.radians(240)) + (point[1] - 475) * math.cos(math.radians(240))) + 475
                            newPoints.append((newPoint[0], newPoint[1]))
                        pygame.draw.polygon(screen, (161, 2, 25), (newPoints[0], newPoints[1], newPoints[2]))

                # Enemy Shockwaves
                for shockwave in self.enemyShockwaves:
                    pygame.draw.circle(screen, shockwave.colour, (math.floor(shockwave.x), math.floor(shockwave.y)), shockwave.size)

                # Resource Packs
                for resource in self.cRoom.resources:
                    pygame.draw.rect(screen, (117, 60, 4), resource)
                
                # Fallen Players
                for character in self.cRoom.fallenPlayers:
                    pygame.draw.rect(screen, (0, 80, 0), pygame.Rect(character.x, character.y, 30, 30))
                
                # Player
                pygame.draw.rect(screen, (0, 255, 0) if self.player.stunTime <= 0 else (0, 160, 0), pygame.Rect(self.player.x, self.player.y, 30, 30))

                # Walls
                self.walls = [
                    pygame.Rect(0, 0, 20, 445),
                    pygame.Rect(0, 505, 20, 445),
                    pygame.Rect(930, 0, 20, 445),
                    pygame.Rect(930, 505, 20, 445),
                    pygame.Rect(0, 0, 445, 20),
                    pygame.Rect(505, 0, 445, 20),
                    pygame.Rect(0, 930, 445, 20),
                    pygame.Rect(505, 930, 445, 20)
                ]

                bossGoing = False
                for enemy in self.cRoom.enemies:
                    if enemy.isBoss and enemy.bossAggro:
                        bossGoing = True

                        self.walls = [
                            pygame.Rect(0, 0, 20, 950),
                            pygame.Rect(930, 0, 20, 950),
                            pygame.Rect(0, 0, 950, 20),
                            pygame.Rect(0, 930, 950, 20)
                        ]

                if not self.nearbyRoom(self.cRoom.x - 1, self.cRoom.y)[0]:
                    self.walls.append(pygame.Rect(0, 445, 20, 60))

                if not self.nearbyRoom(self.cRoom.x + 1, self.cRoom.y)[0]:
                    self.walls.append(pygame.Rect(930, 445, 20, 60))

                if not self.nearbyRoom(self.cRoom.x, self.cRoom.y + 1)[0]:
                    self.walls.append(pygame.Rect(445, 0, 60, 20))

                if not self.nearbyRoom(self.cRoom.x, self.cRoom.y - 1)[0]:
                    self.walls.append(pygame.Rect(445, 930, 60, 20))

                for wall in self.cRoom.walls:
                    self.walls.append(wall)

                for wall in self.walls:
                    pygame.draw.rect(screen, (150, 150, 150), wall)

                # Enemies
                for enemy in self.cRoom.enemies:
                    pygame.draw.rect(screen, enemy.colour if enemy.cStun <= 0 else enemy.stunColour, pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size))

                # DEBUG - View
                #for trace in self.boxTraces:
                    #pygame.draw.rect(screen, (255, 255, 255), trace)

                # Enemy Projectiles
                for bullet in self.enemyBullets:
                    pygame.draw.circle(screen, (200, 0, 0), (math.floor(bullet.x), math.floor(bullet.y)), bullet.size)
                
                # Stun Projectiles
                for stunBullet in self.stunBullets:
                    pygame.draw.circle(screen, (0, 0, 255), (math.floor(stunBullet.x), math.floor(stunBullet.y)), stunBullet.size)

                # Player Statistic Text
                self.drawText("Health: " + str(math.ceil(self.player.health)) + " / " + str(self.player.maxHealth), (255, 255, 255), self.statFont, 25, 30, 0)
                self.drawText("Stun Gun: " + str(math.floor(self.player.charge)) + "%", (255, 255, 255), self.statFont, 25, 45, 0)
                self.drawText("Stamina: " + str(math.floor(self.player.stamina)) + " / " + str(self.player.maxStamina), (255, 255, 255), self.statFont, 25, 60, 0)
                self.drawText("Carrying: " + ["Nothing", "Resource", "Mike", "Brooke", "Liam"][self.carryObject], (255, 255, 255), self.statFont, 25, 75, 0)

                # Health Text
                if bossGoing:
                    targetEnemy = self.cRoom.enemies[0]
                    enemyName = ["Shadow Walker", "Blade Walker", "Terror Walker", ("Night Demon" if self.hLevel < 100 else "Walking Nightmare")][targetEnemy.eType - 7]

                    healthText = ""
                    for i in range(0, targetEnemy.health):
                        healthText += "|"

                    self.drawText(enemyName + ": " + healthText, (255, 0, 0), self.characterBodyFont, 25, 910, 0)

            case 3:
                screen.fill((80, 80, 80))

                self.textButtons = []

                self.drawText("Welcome to base camp.", (255, 255, 255), self.subTitleFont, 475, 30, 1)
                self.drawText("You know your orders.", (200, 200, 200), self.characterHeaderFont, 475, 60, 1)

                centeredLocations = [200, 475, 750]
                buttonOffsets = [0, 5, 10]
                
                for character in self.heldPlayers:
                    self.drawText(character.name + " (" + character.cClass + ")", (255, 255, 255), self.characterHeaderFont, centeredLocations[self.heldPlayers.index(character)], 150, 1)
                    if character.health <= 0:
                        self.drawText("FALLEN", (200, 0, 0), self.characterBodyFont, centeredLocations[self.heldPlayers.index(character)], 180, 1)
                    else:
                        self.drawText("HP: " + str(math.ceil(character.health)) + " / " + str(character.maxHealth), (255, 255, 255), self.characterBodyFont, centeredLocations[self.heldPlayers.index(character)], 180, 1)
                        button = self.drawText("> Heal (1 resource) <", (255, 255, 255), self.statFont, centeredLocations[self.heldPlayers.index(character)], 200, 1)

                        self.textButtons.append([0 + buttonOffsets[self.heldPlayers.index(character)], button])
                        
                        self.drawText("Speed: " + str(character.speed), (255, 255, 255), self.characterBodyFont, centeredLocations[self.heldPlayers.index(character)], 240, 1)
                        button = self.drawText("> Upgrade (3 resources) <", (255, 255, 255), self.statFont, centeredLocations[self.heldPlayers.index(character)], 260, 1)

                        self.textButtons.append([1 + buttonOffsets[self.heldPlayers.index(character)], button])

                        self.drawText("Stamina: " + str(character.maxStamina), (255, 255, 255), self.characterBodyFont, centeredLocations[self.heldPlayers.index(character)], 300, 1)
                        button = self.drawText("> Upgrade (2 resources) <", (255, 255, 255), self.statFont, centeredLocations[self.heldPlayers.index(character)], 320, 1)

                        self.textButtons.append([2 + buttonOffsets[self.heldPlayers.index(character)], button])

                        self.drawText("Charge Speed: " + str(character.chargeSpeed), (255, 255, 255), self.characterBodyFont, centeredLocations[self.heldPlayers.index(character)], 360, 1)
                        button = self.drawText("> Upgrade (3 resources) <", (255, 255, 255), self.statFont, centeredLocations[self.heldPlayers.index(character)], 380, 1)

                        self.textButtons.append([3 + buttonOffsets[self.heldPlayers.index(character)], button])

                        self.drawText("Ability:", (255, 255, 255), self.characterBodyFont, centeredLocations[self.heldPlayers.index(character)], 420, 1)
                        self.drawText(["Powerful shots", "Conditioning", "Endurance"][self.heldPlayers.index(character)], (255, 255, 255), self.characterBodyFont, centeredLocations[self.heldPlayers.index(character)], 440, 1)

                        button = self.drawText("> Send Out <", (255, 255, 255), self.characterHeaderFont, centeredLocations[self.heldPlayers.index(character)], 500, 1)
                        self.textButtons.append([4 + buttonOffsets[self.heldPlayers.index(character)], button])


                self.drawText("Resoureces: " + str(self.resources), (255, 255, 255), self.characterHeaderFont, 475, 600, 1)
                self.drawText("Hazard Level: " + str(self.hLevel), (255, 0, 0), self.characterHeaderFont, 475, 650, 1)

                button = self.drawText("> Abandon Operation (" + str(self.abandonCount) + ") <", (255, 255, 255), self.characterHeaderFont, 475, 925, 1)

                self.textButtons.append([15, button])

            case 4:
                screen.fill((150, 0, 0) if not self.victory else (0, 200, 0))
                self.drawText("You failed." if not self.victory else "You succeeded.", (255, 255, 255), self.subTitleFont, 475, 30, 1)
                self.drawText("All agents have fallen. The world remains in terror." if not self.victory else "The world may breath a sigh of relief once again.", (255, 255, 255), self.characterHeaderFont, 475, 60, 1)
                self.drawText("Hazard Level: " + str(self.hLevel), (255, 255, 255), self.characterHeaderFont, 475, 100, 1)

                if self.victory and self.hLevel >= 100:
                    self.drawText("https://www.youtube.com/watch?v=iik25wqIuFo", (255, 255, 255), self.characterHeaderFont, 475, 860, 1)

                button = self.drawText("> Finish <", (255, 255, 255), self.characterHeaderFont, 475, 925, 1)
                self.textButtons.append([0, button])

        pygame.display.flip() # Display drawn objects on screen

# Run the actual game
game = Game() # Game object

gameRunning = True
while gameRunning:
    ev = pygame.event.get()

    # Handing player pressing the "X" button. Put any player input into the "game.logic" function to keep this section clutter-free.
    for event in ev:
        if event.type == pygame.QUIT:
            gameRunning = False
    
    # Run game functions
    game.inputs()
    game.logic()
    game.draw()

    time.sleep(tickDelay)

pygame.quit()
