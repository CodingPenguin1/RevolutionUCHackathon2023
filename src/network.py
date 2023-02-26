class Network:
    def __init__(self, num_in, num_out):
        self.num_in = num_in
        self.num_out = num_out
        
        self.nodes = []
        self.graph = {}
        
        for _ in range(num_in):
            self.nodes.append(Node(0, 1, None))
            self.graph[str(len(self.nodes) - 1)] = []
        for _ in range(num_out):
            self.nodes.append(Node(1, 0, None))
            self.graph[str(len(self.nodes) - 1)] = []

    def reset(self):
        for node in self.nodes:
            node.reset()

    def add_node(self, node, input_idxs=None, output_idxs=None, add_connections=True):
        if input_idxs is None:
            input_idxs = []
        if output_idxs is None:
            output_idxs = []
        
        # Generate new node key and add to node list
        new_node_idx = len(self.nodes)
        self.nodes.append(node)
        
        if add_connections:
            # Add edges for all nodes that point to the new node
            for i in input_idxs:
                self.graph[str(i)].append(new_node_idx)
            # Add edges for all nodes that the new node points to
            self.graph[str(new_node_idx)] = output_idxs

    def delete_node(self, idx):
        # Remove the node itself
        self.nodes.pop(idx)
        
        # Remove edges for all nodes that point to the deleted node
        for i in range(len(self.nodes)):
            if idx in self.graph[str(i)]:
                self.graph[str(i)].remove(idx)
        
        # Remove edges for all nodes that the deleted node points to
        self.graph.pop(str(idx))
    
    def add_connection(self, input_idx, output_idx):
        self.graph[str(input_idx)].append(output_idx)
    
    def delete_connection(self, input_idx, output_idx):
        self.graph[str(input_idx)].remove(output_idx)

    def parse_network(self, inputs):
        # Set input node values
        for i in range(len(inputs)):
            self.nodes[i].value = inputs[i]
        
        for node in self.nodes:
            if node.num_outputs == 0:
                # print(f'[START] Parsing node {self.nodes.index(node)}...')
                self._parse_network_helper(self.nodes.index(node))
        # self._parse_network_helper(0)
        
        # Get output node values
        output_values = []
        for i in range(len(self.nodes)):
            if self.nodes[i].num_outputs == 0:
                output_values.append(self.nodes[i].value)
        return output_values
        
    def _parse_network_helper(self, node_idx):
        # print(f'Parsing node {node_idx}...')
        # If input node, go down to the next node
        if self.nodes[node_idx].num_inputs == 0:
            # print(f'Node {node_idx} is an input node. Going down to node {self.graph[str(node_idx)][0]}...')
            self._parse_network_helper(self.graph[str(node_idx)][0])
        
        # If output node, grab value from inbound node and break out
        if self.nodes[node_idx].num_outputs == 0:
            # print(f'Node {node_idx} is an output node. Grabbing value from node UNKNOWN...')
            for i in range(len(self.nodes)):
                if node_idx in self.graph[str(i)]:
                    self.nodes[node_idx].value = self.nodes[i].value
                    break
        
        # If node already parsed, break out
        if self.nodes[node_idx].value is not None:
            # print(f'Node {node_idx} already parsed. Breaking out...')
            return

        # If not input or output node, perform operation
        # Find all nodes that point to this node and get their values to pass to the operation
        inbound_nodes = []
        for i in range(len(self.nodes)):
            if node_idx in self.graph[str(i)]:
                # If the node has a None value, parse it first
                if self.nodes[i].value is None:
                    self._parse_network_helper(i)
                inbound_nodes.append(i)
                
        # if node_idx == 9:
        #     print(f'NODES INBOUND TO 9: {inbound_nodes}')
        inputs = [self.nodes[i].value for i in inbound_nodes]
        
        # if len(inputs) == 2:
        #     print(f'{node_idx}: {inputs[0]} {self.nodes[node_idx].operation} {inputs[1]} = {self.nodes[node_idx].perform_operation(inputs)}')
        # elif len(inputs) == 1:
        #     print(f'{node_idx}: {inputs[0]} {self.nodes[node_idx].operation} = {self.nodes[node_idx].perform_operation(inputs)}')
        
        if len(inputs) > 0:
            self.nodes[node_idx].value = self.nodes[node_idx].perform_operation(inputs)
        
        # Parse all nodes that this node points to
        for i in self.graph[str(node_idx)]:
            self._parse_network_helper(i)
        
    def __str__(self):
        s = ''
        for i, node in enumerate(self.nodes):
            s += f'({i}){node}, '
        s += '\n'
        for k in self.graph.keys():
            s += f'{k}: {self.graph[k]}\n'
        return s


class Node:
    def __init__(self, num_inputs, num_outputs, operation):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.operation = operation
        self.value = None
        if type(self.operation) == int:
            self.value = self.operation
            self.operation = 'const'
    
    def reset(self):
        if self.operation != 'const':
            self.value = None
    
    def perform_operation(self, inputs):
        if self.operation is None:
            return inputs[0]
        elif self.operation == '+':
            return inputs[0] + inputs[1]
        elif self.operation == '-':
            return inputs[0] - inputs[1]
        elif self.operation == '*':
            return inputs[0] * inputs[1]
        elif self.operation == '/':
            return inputs[0] / inputs[1]
        elif self.operation == 'abs':
            return abs(inputs[0])
        elif self.operation == '<':
            return int(inputs[0] < inputs[1])
        elif self.operation == '<=':
            return int(inputs[0] <= inputs[1])
        elif self.operation == '>':
            return int(inputs[0] > inputs[1])
        elif self.operation == '>=':
            return int(inputs[0] >= inputs[1])
        elif self.operation == '==':
            return int(inputs[0] == inputs[1])
        elif self.operation == '!=':
            return int(inputs[0] != inputs[1])
        elif self.operation == 'neg':
            return -inputs[0]
        elif self.operation == 'and':
            return int(bool(inputs[0]) and bool(inputs[1]))
        elif self.operation == 'or':
            return int(bool(inputs[0]) or bool(inputs[1]))
    
    def __str__(self):
        if self.num_inputs == 0 and self.operation is None:
            return f'[IN]: {self.value}'
        if self.num_outputs == 0 and self.operation is None:
            return f'[OUT]: {self.value}'
        return f'[{self.operation}]: {self.value}'


if __name__ == '__main__':
    # network = Network(2, 1)
    # network.add_node(Node(2, 1, '+'), [0, 1], [2])
    
    network = Network(2, 4)
    network.add_node(Node(0, 1, 5))
    network.add_node(Node(0, 1, 10))
    network.add_node(Node(1, 1, 'abs'), [1])
    network.add_node(Node(2, 1, '>'), [8, 7])
    network.add_node(Node(2, 1, '<='), [6, 0])
    network.add_node(Node(2, 1, 'and'), [9, 10], [5])
    network.add_node(Node(0, 1, -10))
    network.add_node(Node(2, 1, '<'), [1, 12], [3])
    network.add_node(Node(2, 1, '>'), [1, 7], [2])
    
    print(network)
    # print(network.parse_network([10, 5]))
    # # print(network)