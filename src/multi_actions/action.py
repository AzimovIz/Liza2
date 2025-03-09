from dataclasses import dataclass


@dataclass
class ActionState:
    pending = "pending"
    completed = "completed"
    failed = "failed"


class Actions:
    """Базовый класс для представления отдельного действия."""

    def __init__(self, action_type):
        self.action_type = action_type
        self.state = ActionState.pending
        self.input_params = {}
        self.output_params = {}
        self.error_info = None

    def get_actions(self):
        return {
            "execute": {
                "description": "",
                "input": [],
                "output": [],
                "func": self.execute
            }
        }

    def execute(self):
        # Метод для выполнения конкретного действия
        raise NotImplementedError("Метод execute должен быть реализован в подклассах")

    def set_input_params(self, params):
        self.input_params.update(params)

    def get_output_params(self):
        return self.output_params

    def fail(self, error_message):
        self.state = ActionState.failed
        self.error_info = error_message

    def complete(self):
        self.state = ActionState.completed
