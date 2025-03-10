from multi_actions import BaseAction


class example(BaseAction):
    def __init__(self):
        super().__init__()

    def execute(self):
        print("example Work!!")
