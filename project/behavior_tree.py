class Node:
    def run(self):
        raise NotImplementedError


class Action(Node):
    def __init__(self, name, fn):
        self.name = name
        self.fn = fn

    def run(self):
        return self.fn()


class Condition(Node):
    def __init__(self, name, fn):
        self.name = name
        self.fn = fn

    def run(self):
        if self.fn():
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL


class Sequence(Node):
    def __init__(self, name, children):
        self.name = name
        self.children = children
        self.current = 0

    def run(self):
        while self.current < len(self.children):
            status = self.children[self.current].run()
            if status == BehaviorTree.RUNNING:
                return BehaviorTree.RUNNING
            if status == BehaviorTree.FAIL:
                self.current = 0
                return BehaviorTree.FAIL
            self.current += 1
        self.current = 0
        return BehaviorTree.SUCCESS


class Selector(Node):
    def __init__(self, name, children):
        self.name = name
        self.children = children
        self.current = 0

    def run(self):
        while self.current < len(self.children):
            status = self.children[self.current].run()
            if status == BehaviorTree.RUNNING:
                return BehaviorTree.RUNNING
            if status == BehaviorTree.SUCCESS:
                self.current = 0
                return BehaviorTree.SUCCESS
            self.current += 1
        self.current = 0
        return BehaviorTree.FAIL


class BehaviorTree:
    RUNNING = 0
    SUCCESS = 1
    FAIL = 2

    def __init__(self, root):
        self.root = root

    def run(self):
        return self.root.run()
