import pyglet
from network import Network, Node
import menu as menuUI
import pickle
import pyglet.window.key as key


pyglet.resource.path = ['../Sprites']
pyglet.resource.reindex()

window = pyglet.window.Window(1690, 950, resizable=True)
window.set_minimum_size(640, 360)


# First item in the list is the one on top (aka last one moved)
# Create list of modules
bank_modules = []
network_modules = []
lines = []

network = None

hovering_line = None
hovering_line_coords = None
hovering_line_type = None
hovering_line_root_node_id = None

selected_object = None
selected_object_index = None
selected_object_position = None

hovering_for_text = None


class Module(pyglet.sprite.Sprite):
    def __init__(self, x, y, operation, moveable=True, node_id=None):
        self.node_id = node_id
        self.num_in, self.num_out = 0, 0
        if type(operation) == int or operation == 'const' or operation == 'in':
            image = pyglet.resource.image('UI/module_input.png')
            if type(operation) == int:
                label = str(operation)
            elif operation in {'const', 'in'}:
                label = operation
            self.num_out = 1
        
        if operation == 'out':
            image = pyglet.resource.image('UI/module_output.png')
            label = 'out'
            self.num_out = 1
            
        elif operation in {'-', '*', '/', '<', '<=', '>', '>=', '==', '!=', '+', 'and', 'or', }:
            image = pyglet.resource.image('UI/module.png')
            label = operation
            self.num_in = 2
            self.num_out = 1
            
        elif operation in {'abs', 'neg'}:
            image = pyglet.resource.image('UI/module-1-1.png')
            if operation == 'abs':
                label = '|x|'
            elif operation == 'neg':
                label = '-x'
            self.num_in = 1
            self.num_out = 1
        
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        super().__init__(image, x=x, y=y)
        self.moveable = moveable
        self.operation = operation
        self.label = label
        
        self.label = pyglet.text.Label(self.label,
                          font_name='Times New Roman',
                          font_size=12,
                          x=self.x, y=self.y,
                          anchor_x='center', anchor_y='center')
    
    def update(self, dt):
        self.label.x = self.x
        self.label.y = self.y


def is_hovering_over(obj, x, y):
    # Hovering over the module somewhere
    hovering = obj.x - obj.width / 2 <= x <= obj.x + obj.width / 2 and obj.y - obj.height / 2 <= y <= obj.y + obj.height / 2
    connector_hover = None
    
    if (hovering):
        if obj.x - obj.width / 2 <= x <= obj.x - (obj.width / 2) + 10:
            if obj.y - obj.height / 2 <= y <= obj.y - obj.height / 6:
                connector_hover = 'input 0'
            if obj.y - obj.height / 6 <= y <= obj.y + obj.height / 6:
                connector_hover = 'input 1'
            if obj.y + obj.height / 6 <= y <= obj.y + obj.height / 2:
                connector_hover = 'input 2'
        if (obj.x + (obj.width / 2) - 10 <= x <= obj.x + obj.width / 2):
            connector_hover = 'output'

    return hovering, connector_hover


def drawLine(startX, startY, endX, endY):
    global hovering_line
    hovering_line = pyglet.shapes.Line(startX, startY, endX, endY, 5, color = (50, 225, 30))
    hovering_line.opacity = 250
    

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global selected_object, selected_object_index, selected_object_position, hovering_line, hovering_line_coords, hovering_line_type, hovering_line_root_node_id
    
    if buttons & pyglet.window.mouse.LEFT:
        if selected_object is None:
            # Determine which object we're moving
            selected_object = None
            for obj in bank_modules:
                hovering, _ = is_hovering_over(obj, x, y)
                if hovering:
                    selected_object = obj
                    selected_object_index = bank_modules.index(obj)
                    if selected_object_position is None:
                        selected_object_position = (obj.x, obj.y)
                    break
            
            for obj in network_modules:
                hovering, connector_hovering = is_hovering_over(obj, x, y)
                if hovering and connector_hovering is None:
                    selected_object = obj
                    selected_object_index = network_modules.index(obj)
                    if selected_object_position is None:
                        selected_object_position = (obj.x, obj.y)
                    break
                elif hovering and connector_hovering is not None:
                    if (connector_hovering == 'input 2'):
                        pass
                        # print("top")
                    if (connector_hovering == 'input 1'):
                        pass
                        # print("middle")
                    if (connector_hovering == 'input 0'):
                        pass
                        # print("bottom")
                    if (connector_hovering == 'output'):
                        # print("output stuff")
                        hovering_line_coords = (obj.x + obj.width / 2 - 5, obj.y)
                    if hovering_line_type is None:
                        hovering_line_type = connector_hovering
                    if hovering_line_root_node_id is None:
                        hovering_line_root_node_id = obj.node_id
                
                hovering, connector_hovering = is_hovering_over(obj, x, y)
                if hovering and connector_hovering is None:
                    selected_object = obj
                    hovering_line_root_node_id = obj.node_id
                    break

        if selected_object is not None and selected_object.moveable:
            # Move object
            selected_object.x += dx
            selected_object.y += dy
        
    # If we're dragging a line
    if hovering_line_coords is not None:
        drawLine(hovering_line_coords[0], hovering_line_coords[1], x, y)
    
    # Move object to top of list
    if selected_object in network_modules:
        network_modules.insert(0, network_modules.pop(network_modules.index(selected_object)))


@window.event
def on_mouse_release(x, y, button, modifiers):
    global selected_object, selected_object_index, selected_object_position
    global hovering_line, hovering_line_coords, hovering_line_type, hovering_line_root_node_id

    # Move dragged module to the network list
    if selected_object in bank_modules:
        new_module = bank_modules.pop(bank_modules.index(selected_object))
        new_module.node_id = len(network_modules)
        new_module.moveable = False
        network_modules.append(new_module)
        network.add_node(Node(selected_object.num_in, selected_object.num_out, selected_object.operation))
        print(network)

        # Spawn a new module in the bank to replace the dragged one
        bank_modules.insert(selected_object_index, Module(x=selected_object_position[0], y=selected_object_position[1], operation=selected_object.operation))

    # If releasing dragged line on valid point
    if hovering_line_coords is not None:
        for obj in network_modules:
            hovering, connector_hovering = is_hovering_over(obj, x, y)
            if hovering and connector_hovering is not None:
                if hovering_line_type == 'output' and 'input' in connector_hovering:
                    #print(f'Adding connection out to in from {hovering_line_root_node_id} to {obj.node_id}')
                    network.add_connection(hovering_line_root_node_id, obj.node_id)
                    
                elif 'input' in hovering_line_type and hovering_line_type == 'output':
                    #print(f'Adding connection in to out from {obj.node_id} to {hovering_line_root_node_id}')
                    network.add_connection(obj.node_id, hovering_line_root_node_id)
                print(network)
                lines.append(pyglet.shapes.Line(hovering_line_coords[0], hovering_line_coords[1], x, y, 5, color = (50, 225, 30)))
                lines[-1].opacity = 250

    # Reset vars
    selected_object_index = None
    selected_object_position = None
    selected_object = None
    hovering_line = None
    hovering_line_coords = None
    hovering_line_type = None
    hovering_line_root_node_id = None

def update(dt):
    for obj in bank_modules:
        obj.update(dt)
    for obj in network_modules:
        obj.update(dt)
        
        
@window.event
def on_mouse_motion(x, y, dx, dy):
    global hovering_for_text
    for obj in network_modules:
        hovering, _ = is_hovering_over(obj, x, y)
        if hovering:
            if obj.operation == 'const' or type(obj.operation) == int or type(obj.operation) == float:
                hovering_for_text = obj
            else:
                hovering_for_text = None
        else:
            hovering_for_text = None

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.BACKSPACE:
        if hovering_for_text is not None:
            hovering_for_text.label.text = 'const'


@window.event
def on_text(text):
    if hovering_for_text is not None:
        if hovering_for_text.label.text == 'const':
            hovering_for_text.label.text = ''
        hovering_for_text.label.text = str(hovering_for_text.label.text) + text
        network.nodes[hovering_for_text.node_id].value = float(hovering_for_text.label.text)
        print(f'Set node {hovering_for_text.node_id} to {float(hovering_for_text.label.text)}')


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == pyglet.window.mouse.LEFT:
        menuButtons = menu.getButtons()
        for button in menuButtons:
            spriteX = button.getX()
            spriteY = button.getY()
            image_width = button.getWidth()
            image_height = button.getHeight()
            if spriteX + image_width > x and spriteY + image_height > y and spriteX - image_width < x and spriteY - image_height < y:
                global inMenu
                inMenu = button.trigger()
        
    elif button == pyglet.window.mouse.RIGHT:
        #print("right click")
        for obj in network_modules:
            hovering, _ = is_hovering_over(obj, x, y)
            if hovering:
                hovering_obj = obj

                #print(hovering_obj)
                if hovering_obj in network_modules:
                    #print(network_modules.index(hovering_obj))
                    network.delete_node(network_modules.index(hovering_obj))
                    network_modules.remove(hovering_obj)


@window.event
def on_draw():
    window.clear()
    menu.redraw()

    for obj in bank_modules:
        obj.draw()
        obj.label.draw()
    for obj in network_modules[::-1]:
        obj.draw()
        obj.label.draw()
    
    if hovering_line is not None:
        hovering_line.draw()
  
    #print('len lines', len(lines))
    for line in lines:
        # line.opacity = 250
        line.draw()


def SaveGraph():
    print("saving")
    with open('graph.pkl', 'wb') as f:
        pickle.dump(network, f)


if __name__ == '__main__':
    inputs = 2
    outputs = 4
    operations = ['<', '>', '==', '<=', '>=', '+', '-', '/', '*', 'and', 'or', 'neg', 'abs', 'const']
    for i in range(len(operations)):
        bank_modules.append(Module(x=100 * i + 50, y=50, operation=operations[i]))
    original_bank_modules = bank_modules.copy()
    
    network = Network(inputs, outputs)
    
    for i in range(inputs):
        network_modules.append(Module(50, y=100 * i + (window.height // 2), operation="const", moveable=False, node_id=len(network_modules)))
        if i == 0:
            network_modules[-1].label.text = 'distance'
        elif i == 1:
            network_modules[-1].label.text = 'angle'
    for i in range(outputs):
        network_modules.append(Module(window.width - 100, y=100 * i + (window.height // 2) - 100, operation='out', moveable=False, node_id=len(network_modules)))
        if i == 0:
            network_modules[-1].label.text = 'left'
        elif i == 1:
            network_modules[-1].label.text = 'right'
        elif i == 2:
            network_modules[-1].label.text = 'forward'
        elif i == 3:
            network_modules[-1].label.text = 'shoot'

    menu = menuUI.Menu(window.width, window.height)
    menu.addButton("SaveButton", pyglet.resource.image("UI/Save.png"), window.width / 2, window.height - 50, SaveGraph)

    pyglet.clock.schedule_interval(update, 1/120.0)
    print(network)

    pyglet.app.run()