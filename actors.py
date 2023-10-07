import copy

class Player:
    def __init__(self, aType):
        self.x = 460
        self.y = 460
        self.aType = aType # 0 = Marine, 1 = Athelete, 2 = Survivalist
        self.name = ["Mike", "Brooke", "Liam"][aType]
        self.cClass = ["Marine", "Athelete", "Survivalist"][aType]

        self.maxHealth = [120, 80, 200][self.aType]
        self.health = self.maxHealth

        self.maxStamina = [100, 150, 110][self.aType]
        self.stamina = self.maxStamina
        
        self.speed = [3, 5, 4][self.aType]

        self.chargeSpeed = [1, 0.4, 0.65][self.aType]

        self.charge = 100
        self.stunTime = 0

        self.power = 1 if aType != 0 else 2

class Enemy:
    def __init__(self, x, y, eType):
        self.x = x
        self.y = y
        
        self.eType = eType
        """
        0 = Walker
        1 = Dread Walker
        2 = Knight Walker
        3 = Thorn Walker
        4 = Toxic Walker
        5 = Titan Walker
        6 = Hunt Walker

        7 = Shadow Walker (Boss)
        8 = Blade Walker (Boss)
        9 = Terror Walker (Boss)
        
        10 = Night Demon (Final Boss)

        11 = Mirage
        """

        self.health = [2, 1, 5, 3, 4, 10, 15, 20, 15, 30, 20, 999][eType]
        self.maxHealth = copy.deepcopy(self.health)
        self.speed = [3, 4, 2, 2.5, 2.8, 1.5, 2, 3.5, 4, 1, 0, 3][eType]
        self.contactDamage = [20, 15, 30, 20, 35, 50, 35, 30, 45, 75, 40, 20][eType]

        self.colour = [(200, 0, 0), (191, 65, 46), (125, 125, 125), (204, 51, 0), (15, 138, 23), (115, 41, 41), (30, 30, 30), (90, 90, 90), (166, 21, 2), (161, 2, 25), (50, 50, 50), (70, 70, 70)][eType]
        self.stunColour = [(150, 0, 0), (135, 45, 31), (50, 50, 50), (102, 26, 0), (10, 82, 15), (87, 31, 31), (20, 20, 20), (20, 20, 20), (87, 10, 0), (79, 0, 12), (30, 30, 30), (10, 10, 10)][eType]
        self.size = [30, 20, 30, 30, 35, 50, 30, 25, 30, 120, 80, 30][eType]

        self.sightRange = [300, 260, 400, 600, 250, 800, 400, 1500, 1500, 1500, 1500, 1500][eType]
        self.seesPlayer = False

        self.hitStun = [10, 6, 12, 8, 11, 10, 8, 10, 5, 15, 4, 9999999][eType]
        self.cStun = 0

        self.nextShot = [0, 0, 0, 75, 0, 0, 0, 0, 40, 0, 0, 0][eType]

        self.isBoss = False
        self.bossAggro = False

        self.moveTarget = [0, 0]

    def getStunned(self, amount):
        if self.cStun < amount:
            self.cStun = amount

class stunProjectile:
    def __init__(self, x, y, xSpeed, ySpeed, size, speed):
        self.x = x
        self.y = y
        self.xSpeed = xSpeed
        self.ySpeed = ySpeed
        self.size = size
        self.speed = speed

class enemyProjectile:
    def __init__(self, x, y, xSpeed, ySpeed, size, speed, damage):
        self.x = x
        self.y = y
        self.xSpeed = xSpeed
        self.ySpeed = ySpeed
        self.size = size
        self.speed = speed
        self.damage = damage

class enemyShockwave:
    def __init__(self, x, y, colour, fSize, growSpeed, stunTime):
        self.x = x
        self.y = y
        self.colour = colour
        self.fSize = fSize
        self.growSpeed = growSpeed
        self.stunTime = stunTime

        self.size = 0

class Room:
    def __init__(self, x, y, walls, enemies, rType):
        self.x = x
        self.y = y
        self.walls = walls
        self.enemies = enemies
        self.rType = rType

        self.fallenPlayers = []
        self.resources = []

        """
        Types:
        0 - Home Base
        1 - Normal Room
        2 - Scrap Room
        3 - Boss Chamber
        4 - Final Boss Chamber
        """
