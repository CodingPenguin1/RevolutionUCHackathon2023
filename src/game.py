import pyglet
from objects import Ship
import menu as menuUI

pyglet.resource.path = ['../Sprites']
pyglet.resource.reindex()

window = pyglet.window.Window(1280, 720, resizable=True)
window.set_minimum_size(640, 360)
#window.set_maximum_size(1000, 1000)

game_objects = []
to_add = []
ship_batch = pyglet.graphics.Batch()

menu = menuUI.mainMenu(window)
inMenu = True
# started = False
# ship = None

# def startGame():
#     ship_image = pyglet.resource.image("ship2.png")
#     bullet_image = pyglet.resource.image("ShotRegular/blueShot.png")  # TODO: Load all sprites at launch
#     exhaust_image = pyglet.resource.image("Exhaust/exhaust4.png")

#     exhaust_image.anchor_x = exhaust_image.width * 1.5
#     exhaust_image.anchor_y = exhaust_image.height / 2

#     global ship
#     ship = Ship(image=ship_image, batch=ship_batch, team=0)
#     ship2 = Ship(image=ship_image, batch=ship_batch, x=200, y=200, team=1)    
    
#     game_objects = [ship, ship2]

#     window.push_handlers(ship)

#     # pyglet.clock.schedule_interval(update(), 1/120.0)

@window.event
def on_draw():
    if (inMenu):
        window.clear()
        menu.redraw()
    else:
        window.clear()
        ship_batch.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    menuButtons = menu.getButtons()
    for button in menuButtons:
        spriteX = button.getX()
        spriteY = button.getY()
        image_width = button.getWidth()
        image_height = button.getHeight()
        if spriteX + image_width > x and spriteY + image_height > y and spriteX - image_width < x and spriteY - image_height < y:
            global inMenu
            inMenu = button.trigger()

# @window.event
# def on_draw():
#     window.clear()
#     ship_batch.draw()

def update(dt):
    global inMenu #, started
    # if (not started and not inMenu):
    #     print('s')
    #     #startGame()
    #     started = True

    if (not inMenu):
        # Remove dead objects
        for to_remove in [obj for obj in game_objects if obj.dead]:
            to_remove.delete()
            game_objects.remove(to_remove)
        
        # Physics update and adds new objects
        object_positions = []
        for obj in game_objects:
            obj.update(dt)
            to_add.extend(obj.new_objects)
            obj.new_objects = []

            # Retrieves all object locations
            obj_info = {'type': type(obj),
                        'x': obj.x,
                        'y': obj.y,
                        'angle': obj.rotation,
                        'velocity': obj.velocity
                        }
            object_positions.append(obj_info)
        
        # Broadcast all object locations to all ships
        for obj in game_objects:
            if type(obj) == Ship:
                obj.object_locations = object_positions
        
        # Collision checks
        for i in range(len(game_objects)):
            for j in range(i + 1, len(game_objects)):
                obj_1 = game_objects[i]
                obj_2 = game_objects[j]

                if not obj_1.dead and not obj_2.dead:
                    if obj_1.collides_with(obj_2):
                        obj_1.handle_collision_with(obj_2)
                        obj_2.handle_collision_with(obj_1)

        # TODO: If player ship dies, display death UI and disable input
        if (ship.dead):
            print("YOU DIED")
            pyglet.app.exit()

        # Last
        game_objects.extend(to_add)
        to_add.clear()
    

if __name__ == '__main__':
    ship_image = pyglet.resource.image("ship2.png")
    bullet_image = pyglet.resource.image("ShotRegular/blueShot.png")  # TODO: Load all sprites at launch
    exhaust_image = pyglet.resource.image("Exhaust/exhaust4.png")

    exhaust_image.anchor_x = exhaust_image.width * 1.5
    exhaust_image.anchor_y = exhaust_image.height / 2

    ship = Ship(name='billy bob', image=ship_image, batch=ship_batch, x=1, y=1, team=0)
    ship2 = Ship(name='wallhacks', image=ship_image, batch=ship_batch, x=200, y=200, team=1)
    
    game_objects = [ship, ship2]

    window.push_handlers(ship)

    # background = pyglet.image.load('../Sprites/UI/background.png')
    # background.blit(0,0,0)

    # if (not started and not inMenu):
    #     print('s')
    #     startGame()

    pyglet.clock.schedule_interval(update, 1/120.0)
    
    pyglet.app.run()

# def manualRun(window):
#     ship_image = pyglet.resource.image("ship2.png")
#     bullet_image = pyglet.resource.image("ShotRegular/blueShot.png")  # TODO: Load all sprites at launch
#     exhaust_image = pyglet.resource.image("Exhaust/exhaust4.png")

#     exhaust_image.anchor_x = exhaust_image.width * 1.5
#     exhaust_image.anchor_y = exhaust_image.height / 2

#     global ship
#     ship = Ship(image=ship_image, batch=ship_batch, team=0)
#     ship2 = Ship(image=ship_image, batch=ship_batch, x=200, y=200, team=1)
    
#     game_objects = [ship, ship2]

#     window.push_handlers(ship)

#     pyglet.clock.schedule_interval(update, 1/120.0)