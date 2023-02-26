import pyglet
from pyglet import shapes
from random import randint
import copy

pyglet.resource.path = ['../Sprites']
pyglet.resource.reindex()

window = pyglet.window.Window(1280, 720, resizable=True)
window.set_minimum_size(640, 360)


# First item in the list is the one on top (aka last one moved)
# Create list of modules
bank_modules = []
network_modules = []
selected_object = None
selected_object_index = None
selected_object_position = None

class Module(shapes.Rectangle):
    def __init__(self, x, y, color=None, moveable=True):
        if color is None:
            color = (randint(50,255), randint(50,255), randint(50,255))
        self.moveable = moveable
        
        super().__init__(x=x, y=y, width=75, height=75, color=color)


def is_hovering_over(obj, x, y):
    hovering = False
    if type(obj) == Module:
        #print(f'Checking if {x}x{y} is in {obj.x}x{obj.y} to {obj.x + obj.width}x{obj.y + obj.height}')
        hovering = obj.x <= x <= obj.x + obj.width and obj.y <= y <= obj.y + obj.height
        #print(f'Hovering: {hovering}')
    return hovering


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global selected_object, selected_object_index, selected_object_position
    
    if buttons & pyglet.window.mouse.LEFT:
        # Determine which object we're moving
        selected_object = None
        for obj in bank_modules:
            if is_hovering_over(obj, x, y):
                selected_object = obj
                selected_object_index = bank_modules.index(obj)
                if selected_object_position is None:
                    selected_object_position = (obj.x, obj.y)
                break
        for obj in network_modules:
            if is_hovering_over(obj, x, y):
                selected_object = obj
                break

        if selected_object is not None and selected_object.moveable:
            # Move object
            selected_object.x += dx
            selected_object.y += dy
        
    # Move object to top of list
    if selected_object in network_modules:
        network_modules.insert(0, network_modules.pop(network_modules.index(selected_object)))


@window.event
def on_mouse_release(x, y, button, modifiers):
    global selected_object, selected_object_index, selected_object_position

    # Move dragged module to the work list
    if selected_object in bank_modules:
        network_modules.append(bank_modules.pop(bank_modules.index(selected_object)))

        # Spawn a new module in the bank to replace the dragged one
        bank_modules.insert(selected_object_index, Module(x=selected_object_position[0], y=selected_object_position[1]))

    # Reset vars
    selected_object_index = None
    selected_object_position = None
    selected_object = None


@window.event
def on_draw():
    window.clear()
    
    print(len(network_modules), len(bank_modules))
    
    for obj in bank_modules:
        obj.draw()
    for obj in network_modules[::-1]:
        obj.draw()

if __name__ == '__main__':
    moduleCount = 14
    inputs = 2
    outputs = 4
    for i in range(moduleCount):
        bank_modules.append(Module(x=100 * i + 25, y=25))
    original_bank_modules = bank_modules.copy()
    
    for i in range(inputs):
        network_modules.append(Module(25, y=100 * i + (window.height // 2), color=(0, 255, 0), moveable=False))
    for i in range(outputs):
        network_modules.append(Module(window.width - 100, y=100 * i + (window.height // 2) - 100, color=(255, 0, 0), moveable=False))

    pyglet.app.run()