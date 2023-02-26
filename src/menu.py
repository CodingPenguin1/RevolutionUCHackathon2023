from pyglet import graphics, sprite, image as pygletImage
import pyglet
pyglet.resource.path = ['../Sprites']
pyglet.resource.reindex()

class Image(object):
    def __init__(self, name, image, xPos, yPos, batch, animation=None):
        self.name = name
        self.image = image
        self.width = self.image.width
        self.height = self.image.height
        self.image.anchor_x = self.width/2
        self.image.anchor_y = self.height/2
        self.sprite = sprite.Sprite(self.image, x=xPos, y=yPos, batch=batch)
        self.animate = animation

    def getName(self):
        return self.name

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def getAnchor_x(self):
        return self.image.anchor_x

    def getAnchor_y(self):
        return self.image.anchor_y

    def getX(self):
        return self.sprite.x

    def getY(self):
        return self.sprite.y

    def deleteSprite(self):
        self.sprite.delete()


class Title(Image):
    def __init__(self, name, image, x, y, batch):
        super().__init__(name, image, x, y, batch)


class Button(Image):
    def __init__(self, name, image, x, y, activation, batch):
        super().__init__(name, image, x, y, batch)
        self.activation = activation

    def ifAbove(self, x, y):
        leftBoundary = self.getX() - self.getAnchor_x()
        rightBoundary = self.getX() + self.getAnchor_x()
        bottomBoundary = self.getY() - self.getAnchor_y()
        topBoundary = self.getY() + self.getAnchor_y()
        return ((leftBoundary <= x <= rightBoundary) and (bottomBoundary <= y <= topBoundary))
    
    def trigger(self):
        self.activation()


def PlayGame():
    return False

def QuitGame():
    print("QUITTING")
    pyglet.app.exit()

class Menu(object):
    def __init__(self, menuWidth, menuHeight, x=0, y=0):
        '''Menu Width: width of menu
           Menu Height: height of menu
           Used as relative positioning for buttons
           x: Position of menu Horizontally inside of the window
           y: Position of menu Vertically inside of the window

           buttonShift: the shift of buttons from mid height'''
        self.batch = graphics.Batch()
        self.title = None
        self.buttons = []
        self.width = menuWidth
        self.height = menuHeight
        self.x = x
        self.y = y
        self.buttonShift = 0

    def addTitle(self, name, image, xPos, yPos):
        self.title = Title(name, image, xPos + self.x, yPos + self.y, self.batch)

    def addButton(self, name, image, xPos, yPos, activation):
        self.buttons.append(Button(name, image, xPos + self.x, yPos + self.y, activation, self.batch))

    def addCenterButton(self, name, image, activation, margine=0):
        self.addButton(name, image, self.width/2 + self.x, self.height/2 + self.y + self.buttonShift, activation)
        self.buttonShift -= self.buttons[-1].getHeight() + margine

    def getButton(self, name):
        for button in self.buttons:
            if button.getName() == name:
                return button
            
    def getButtons(self):
        return self.buttons

    def ifAbove(self, name, x, y):
        return self.getButton(name).ifAbove(x, y)

    def redraw(self):
        self.batch.draw()

    def delete(self):
        if self.title != None:
            self.title.deleteSprite()
        if len(self.buttons) != 0:
            for button in self.buttons:
                button.deleteSprite()


def mainMenu(window):
    menu = Menu(window.width, window.height)

    menu.addTitle("TitleWidget", pyglet.resource.image("UI/Title.png"), window.width / 2, window.height / 1.5)

    menu.addCenterButton("PlayButton", pyglet.resource.image("UI/Play.png"), PlayGame, 15)
    menu.addButton("QuitButton", pyglet.resource.image("UI/Quit.png"), window.width / 2, window.height / 3, QuitGame)

    return menu