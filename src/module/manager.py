from typing import List


class ModuleManager:
    def __init__(self):
        pass

    def get_actions(self) -> List:
        pass

    def prepare_actions(self, data: dict):
        # TODO: валидация наличия переменных в выходе действий для следующих действий
        acts = []
        for action_name in data.keys():
            inputs = data[action_name]["input"]
            act = self.get_actions()[action_name](**inputs)
            acts.append(act)

        return acts
