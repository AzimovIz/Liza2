import asyncio
from typing import List, Dict
from .action import BaseAction


def validate_action(func: callable):
    async def wrapper(cls, action: callable):
        if action.__class__ == cls:
            if asyncio.iscoroutinefunction(func):
                await func(action)
            else:
                func(action)
        else:
            pass

    return wrapper


class DependencyManager:
    """Класс для управления зависимостями между действиями."""

    def __init__(self, actions: List[BaseAction]):
        self.actions = actions
        self._data_store = {}  # Хранилище промежуточных результатов

    def run_actions(self):
        for action in self.actions:
            if action.state == 'pending':
                input_params = self._get_input_params(action)
                action.set_input_params(input_params)

                try:
                    action.execute()
                except Exception as e:
                    action.fail(str(e))

            if action.state == 'completed':
                output_params = action.get_output_params()
                self._data_store.update(output_params)

    def _get_input_params(self, action):
        required_inputs = []
        inputs = {}
        for key, value in action.input_params.items():
            if isinstance(value, str) and value.startswith('$'):
                param_name = value[1:]  # Убираем символ '$' перед именем параметра
                required_inputs.append(param_name)

            for param_name in required_inputs:
                inputs[key] = self._data_store.get(param_name)

        return inputs
