from dataclasses import dataclass


@dataclass
class Node:
    ID: str
    X: float
    Y: float
    Z: float


@dataclass
class Pipe:
    ID: str
    start_node: str
    end_node: str
    diameter: float
    roughness: float
    length: float
    heat_loss_coefficient: float


@dataclass
class Source:
    ID: str
    Node: str
    P_s: float
    P_r: float
    T_s: float
    T_r: float


@dataclass
class Consumer:
    ID: str
    Node: str
    thermal_power_demand: float


class NetworkModel:
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.pipes: dict[str, Pipe] = {}
        self.sources: dict[str, Source] = {}
        self.consumers: dict[str, Consumer] = {}
        self.node_counter = 0
        self.pipe_counter = 0

    def create_node(self, x, y, z):
        self.node_counter += 1
        node_id = f"N{self.node_counter}"
        node = Node(node_id, x, y, z)
        self.add_node(node)
        return node

    def create_pipe(self, start_node, end_node):
        self.pipe_counter += 1
        pipe = Pipe(
            ID=f"P{self.pipe_counter}",
            start_node=start_node,
            end_node=end_node,
            diameter=0.0,
            roughness=0.0,
            length=0.0,
            heat_loss_coefficient=0.0,
        )
        self.add_pipe(pipe)
        return pipe

    def add_node(self, node):
        self.nodes[node.ID] = node

    def delete_node(self, node_id):
        self.nodes.pop(node_id, None)

    def add_pipe(self, pipe):
        self.pipes[pipe.ID] = pipe

    def delete_pipe(self, pipe_id):
        self.pipes.pop(pipe_id, None)

    def add_source(self, source):
        self.sources[source.ID] = source

    def delete_source(self, source_id):
        self.sources.pop(source_id, None)

    def add_consumer(self, consumer):
        self.consumers[consumer.ID] = consumer

    def delete_consumer(self, consumer_id):
        self.consumers.pop(consumer_id, None)
