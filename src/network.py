class Node:
    def __init__(self, num_inputs, num_outputs, operation):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self._in = []
        self._out = []
        self.operation = operation
        
