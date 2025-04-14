from typing import Dict, Any


class SystemRolePrompt:
    def __init__(self, template: str):
        self.template = template

    def create_message(self, **kwargs) -> Dict[str, str]:
        return {"role": "system", "content": self.template.format(**kwargs)}


class UserRolePrompt:
    def __init__(self, template: str):
        self.template = template

    def create_message(self, **kwargs) -> Dict[str, str]:
        return {"role": "user", "content": self.template.format(**kwargs)}


class AssistantRolePrompt:
    def __init__(self, template: str):
        self.template = template

    def create_message(self, **kwargs) -> Dict[str, str]:
        return {"role": "assistant", "content": self.template.format(**kwargs)} 