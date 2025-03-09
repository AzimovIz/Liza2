import asyncio
import json
import logging
import os
import shutil
from importlib import invalidate_caches, reload, import_module
from pathlib import Path

from .classes import Settings

logger = logging.getLogger(__name__)

class Module:
    def __init__(self, name):
        self.name = name
        self.module_path = Path(__file__).absolute().parent / "modules" / name / "main.py"

    def load_actions(self):
        if self.module_path.exists():
            module = __import__(self.name)
            actions = getattr(module, self.name)()
            return actions.get_actions()
        else:
            raise FileNotFoundError(f"Module file not found: {self.module_path}")


class Module:
    def __init__(self, name, mm: 'ModuleManager'):
        self.name = name
        self.path = Path(__file__).absolute().parent / "modules" / name
        self.module = None
        if not os.path.isfile(f"{self.path}/settings.json"):
            if os.path.isfile(f"{self.path}/example.settings.json"):
                shutil.copyfile(
                    src=f"{self.path}/example.settings.json",
                    dst=f"{self.path}/settings.json"
                )
            else:
                logger.error(
                    f"{self.path}/settings.json и "
                    f"{self.path}/example.settings.json не найдены, "
                    f"невозможно инициализировать {self.name}"
                )
                self.settings = Settings(
                    version=0.0,
                    is_active=False,
                    config={},
                    require_modules=[],
                )
                return

        with open(f"{self.path}/settings.json", "r", encoding="utf-8") as file:
            self.settings = Settings.from_dict(json.load(file))

        if not self.settings.is_active:
            logger.debug(f"Модуль {self.name} выключен")

        try:
            if self.name in mm.modules.keys():
                invalidate_caches()
                self.module = reload(module=mm.modules[self.name].module)
            else:
                if not os.path.isfile(f"{self.path}/main.py"):
                    logger.error(f"Файл main.py не найден в модуле {self.name}")
                    raise ModuleNotFoundError(f"{self.path}/main.py")
                self.module: SubModule = import_module(f"{self.path.replace("/", ".")}.main")

        except ModuleNotFoundError:
            self.settings.is_active = False
            logger.error(
                f"Модуль {self.name}.main или его зависимости не найдены, невозможно инициализировать {self.name}",
                exc_info=True
            )
            return

        if not hasattr(self.module, "acceptor"):
            self.module.acceptor = None
        if not hasattr(self.module, "sender"):
            self.module.sender = None
        if not hasattr(self.module, "intents"):
            self.module.intents = []
        if not hasattr(self.module, "extensions"):
            self.module.extensions = []

        self.version = self.settings.version
        self._mm = mm

    async def init(self):
        if not self.settings.is_active:
            return

        if hasattr(self.module, "init"):
            try:
                if asyncio.iscoroutinefunction(self.module.init):
                    await self.module.init(config=self.settings.as_dict)
                else:
                    self.module.init(config=self.settings.as_dict)
            except Exception as e:
                logger.error(f"Error func init() in module {self.name}: {e}", exc_info=True)

    # async def run(self):
    #     if not self.settings.is_active:
    #         return
    #
    #     if self.module.sender:
    #         self.sender_task = asyncio.create_task(
    #             self.module.sender(queue=self.queues.output, config=self.settings.as_dict)
    #         )
    #         self.queues.output.is_active = True
    #
    #     if self.module.acceptor:
    #         self.acceptor_task = asyncio.create_task(
    #             self.module.acceptor(queue=self.queues.input, config=self.settings.as_dict)
    #         )
    #         self.queues.input.is_active = True


    def stop(self):
        self.acceptor_task.cancel()
        self.sender_task.cancel()

        if hasattr(self.module, "stop"):
            try:
                self.module.stop()
            except Exception as e:
                logger.error(f"Error stop() in module {self.name}: {e}", exc_info=True)

    def get_settings(self):
        return self.settings

    # @return_blank_list_if_not_active
    # def get_extensions(self):
    #     return self.module.extensions

    def save_settings(self):
        with open(f"{self.path}/settings.json", "r", encoding="utf-8") as file:
            file_data: dict = json.load(file)

        new_data = {
            "is_active": self.settings.is_active,
            "config": self.settings.config
        }

        file_data.update(new_data)

        with open(f"{self.path}/settings.json", "w", encoding="utf-8") as file:
            json.dump(file_data, file, ensure_ascii=False, indent=2)

    def __bool__(self):
        if hasattr(self, "settings"):
            return self.settings.is_active
        return False
