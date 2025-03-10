from dataclasses import dataclass


@dataclass
class ActionState:
    pending = "pending"
    completed = "completed"
    failed = "failed"


class BaseAction:
    """Базовый класс для представления отдельного действия."""

    def __init__(self, *args, **kwargs):
        self.state = ActionState.pending
        self.input_params = {}
        self.output_params = {}
        for name, value in kwargs.items():
            if isinstance(value, str) and value.startswith("$"):
                self.input_params[name] = value
            else:
                setattr(self, name, value)
        self.error_info = None

    def execute(self):
        # Метод для выполнения конкретного действия
        raise NotImplementedError("Метод execute должен быть реализован в подклассах")

    def get_output_params(self):
        return self.output_params

    def fail(self, error_message):
        self.state = ActionState.failed
        self.error_info = error_message

    def complete(self):
        self.state = ActionState.completed
