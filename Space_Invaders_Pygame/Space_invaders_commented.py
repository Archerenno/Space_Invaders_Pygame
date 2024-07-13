#Late 2022
#initializing the various modules that are later refered to/used
import pygame
import os
import time
import random
#importing all fonts from pygame so I can write on the screen
pygame.font.init()

#Creating the dimension of the game window at naming it
WIDTH, HEIGHT = 850, 700
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

#Creating constant variables which hold each image
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

Background = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# a class for my lasers, having a class for my objects allows me to make each laser/ship/enemy have its own direction and x,y coords
class Laser:
    #defining the class variables
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    #every frame the laser is redrawn
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    #function that adds velcoity to a lasers y value and thus making it move
    def move(self, vel):
        self.y += vel

    #when the laser touches the edge of the screen it is deleted
    def off_screen(self, height):
        #checking for true or false, whether the laser is still in the window
        return not (self.y <= HEIGHT and self.y >= 0)

    #checks for collision and returns true if detected a collision and false if not
    def collision(self, obj):
        return collide(obj, self)

#A class for both ships, enemy and player share some code here. This means less lines of code for me :)
class Ship():

    #sets the cooldown of lasers to 30, in this context meaning a half second (FPS is 60)
    COOLDOWN = 30

    #setting the variabels for this class, allowing for enemy and player ships to have different health
    def __init__(self, x, y, health = 100):

        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    #individually draws each laser each frame
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))

        for laser in self.lasers:
            laser.draw(window)

    #moves the lasers per frame, 
    def move_lasers(self, vel, obj):
        self.cooldown()
        
        for laser in self.lasers:
            laser.move(vel)
            #but if the laser is of the screen or has collided with the player, the laser is deleted i.e removed from the laser list
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    #Each frame +1 is added to cool_down_counter until it reaches 30 or in real time 1/2 sec when it resets to 0
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    #If space is pressed to shoot a laser and therefore the cooldown is set back to 0,
    #a set of data is sent to the laser class so that it can be drawn and moved from the ships position when it was shot
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    #uses a method to find the eact width of the ship sprite
    def get_width(self):
        return self.ship_img.get_width()

    #uses a method to find the eact height of the ship sprite
    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    # a class for the player which uses some passed down values from the ship class
    def __init__(self, x, y, health = 100):

        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    #deals with the movement of lasers and deletes them if they go offscreen
    def move_lasers(self, vel, objs):
        self.cooldown()
        
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                #objs is a list of all enemy ships basically and therefore this detects collsion between the players laser
                #if collision is deteced the enemy ship and laser are both deleted from the screen
                for obj in objs:

                    if laser.collision(obj):
                        objs.remove(obj)

                        if laser in self.lasers:
                            self.lasers.remove(laser)

    #draws the players health bar, 'super()' is used to give this function access to the other classes variables such as 'self'
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    #the health bar is drawn using 2 overlapping green and red rectangles
    def healthbar(self, window):

        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


# a class for all enemy ships, inherits 
class Enemy(Ship):

    #uses a dictionary to accosciate the colours red, green and blue with their coloured images and laser images
    COLOUR_MAP = {"red" : (RED_SPACE_SHIP, RED_LASER),
                  "green" : (GREEN_SPACE_SHIP, GREEN_LASER),
                  "blue" : (BLUE_SPACE_SHIP, BLUE_LASER)}

    def __init__(self, x, y, colour, health = 100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOUR_MAP[colour]
        #this self.mask essentially creates a hitbox for the ship img which is pixel perfect
        self.mask = pygame.mask.from_surface(self.ship_img)

    #movement of enemy lasers
    def move(self, vel):
        self.y += vel

    #the enemy can shoot aswell, with a similiar cooldown except they have a randomised chance they shoot every sec.
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

#returns a True or False value on whether two objects, likely lasers and ships or ships and ships have collided, i.e their masks/pixels are overlaping
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None



def main():

    #defining my main variables 
    run = True
    FPS = 60
    level = 0
    lives = 5
    #associating a variable with these fonts so its easier to render them in later
    main_font = pygame.font.SysFont("comicsans", 40)
    lost_font = pygame.font.SysFont("comicsans", 50)

    enemies = []
    wave_length = 5
    enemy_vel = 1
    
    player_vel = 5
    laser_vel = 7

    #spawns in the player ship at 370, 550 (x, y) coords
    player = Player(370, 550)
    
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

#redraws the game window every frame, it basically erases everthing and then draws it back in in case it has changed position
    def redraw_window():

        #this is the 'eraser'
        window.blit(Background, (0,0))

        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        window.blit(lives_label, (10, 10))
        window.blit(level_label, (WIDTH - level_label.get_width()- 10, 10))

        for enemy in enemies:
            enemy.draw(window)

        player.draw(window)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            window.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
            
        
        pygame.display.update()
        
    #the main loop which the game runs on,
    #this is a while loop which means the loop will continue to repeat itself until a condition is met, in this case the loop will loop or repeat until run no longer equals false
    while run:
        clock.tick(FPS)
        redraw_window()

    #the following couple if/else conditions determine if the player has lost and then display the lost screen for 3 seconds
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            #FPS * 3 = 180 frames or 3 seconds (at 60fps)
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        #This 'if' condition detects if all the enemies in the level have been killed which tells us that the player is ready for the next wave
        #It then increases the level count, resests the health to max and increase the number of spaceships spawned
        #If conditions are sections of code that only excute if a requirement is met, without being inside a while loop a 'if' condition will only be check for once
        #but because it sits within a 'while run' loop the if condition is checked for every frame
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            player.health = player.max_health

            #This basically spawns in a enemy and then sets it a random colour
            #To get the spaceships to not all come in at the same time they randomly spawn in a large area 'above' and outside the display and slowly make their way down
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        #This quit loop means that if someone presses the exit button it sends them back to the main menu
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        #All these conditiosns detect for when a designated key is pressed and the second requirement ensures the player cannot move off the screen
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel

        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel

        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel

        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 20 < HEIGHT:
            player.y += player_vel

        if keys[pygame.K_SPACE]:
            player.shoot()

        #goes through the list of all enemies and makes them randomly shoot, do damage if collided with the player
        #(ship to ship collision) and makes them remove a life if they reach the bottom of the screen
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 3*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        #moves the players lasers
        player.move_lasers(-laser_vel, enemies)


def main_menu():

    #This is the main menu fucntiona and these are the functions variables
    run = True
    title_font = pygame.font.SysFont("comicsans", 60)
    
    while run:

        #draws up the press mouse to begin label
        window.blit(Background, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        window.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                run = False
            #If the mouse is pressed, start the main loop
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()
        

main_menu()
