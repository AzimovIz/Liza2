from multi_actions import BaseAction


class example(BaseAction):
    def get_actions(self):
        return {
            "example_action": {
                "description": "Тестовое действие",
                "input": [],
                "output": [],
                "func": self.example
            }
        }

    def example(self):
        print("example Work!!")
