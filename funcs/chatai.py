# Jerrin Shirks


import g4f
from undetected_chromedriver import Chrome, ChromeOptions
import tiktoken

import asyncio
from copy import deepcopy
from typing import List, Tuple, Dict


class Memory:
    DEFAULT_PROMPT: str = "DEFAULT PROMPT"
    MAX_MEMORY_SIZE: int = 16834
    __ENCODING: tiktoken.Encoding = tiktoken.get_encoding("gpt2")
    __Message = List[Dict[str, str]]

    def __init__(self, _messages: __Message = None, _prompt: str = "default"):
        if _messages is None:
            _messages = self.__getDefaultMessage(_prompt)
        self.__prompt: str = _prompt
        self.__messages: Memory.__Message = _messages

    @staticmethod
    def __getDefaultMessage(_prompt: str) -> __Message:
        return [{"role": "system", "content": _prompt}]

    @staticmethod
    def countTokens(_content: str):
        return len(Memory.__ENCODING.encode(_content))

    @staticmethod
    def __getPromptSize(_data: __Message) -> int:
        if _data[0]["content"] == "default":
            return Memory.countTokens(Memory.DEFAULT_PROMPT)
        else:
            return Memory.countTokens(_data[0]["content"])

    def getHistoryTokenSize(self, _temp_data: __Message = None) -> int:
        if _temp_data is None:
            _temp_data = self.__messages
        token_count = Memory.__getPromptSize(_temp_data)
        for index, content in enumerate(_temp_data[1:]):
            token_count += self.countTokens(content["content"])
        return token_count

    def isEmpty(self):
        return len(self.__messages) < 2

    def getSize(self):
        return len(self.__messages)

    def getDict(self) -> __Message:
        return deepcopy(self.__messages)

    def getMessages(self) -> __Message:
        _data = deepcopy(self.__messages)
        if _data[0]["content"] == "default":
            _data[0]["content"] = Memory.DEFAULT_PROMPT
        return _data

    def addUser(self, _user: str = "", _content: str = "") -> None:
        if _user == "":
            if _content != "":
                self.__messages.append({"role": "user", "content": f"{_content}"})
        else:
            if _content != "":
                self.__messages.append({"role": "user", "content": f"{_user}: {_content}"})

    def addAssistant(self, _content: str) -> None:
        if _content != "":
            self.__messages.append({"role": "assistant", "content": _content})

    def removeLast(self):
        self.__messages.pop(1)

    def resizeMemory(self, _temp_data: __Message = None):
        reassign = False
        if _temp_data is None:
            _temp_data = deepcopy(self.__messages)
            reassign = True
        else:
            _temp_data = _temp_data
        # count prompt tokens
        prompt_tokens = Memory.__getPromptSize(_temp_data)
        token_count = [self.countTokens(content["content"]) for content in _temp_data[1:]]

        # find how items to remove
        cumulative_sum = prompt_tokens
        start_index = 1
        for count in reversed(token_count):
            cumulative_sum += count
            if cumulative_sum > self.MAX_MEMORY_SIZE:
                break
            start_index += 1

        # create new data
        index = len(_temp_data) - start_index + 1
        new_data = [_temp_data[0]] + _temp_data[index:]
        if reassign:
            self.__messages = new_data
        else:
            return new_data


class CHATAI:
    class InvalidMessageError(Exception):
        def __init__(self, *args):
            super().__init__(*args)

    @staticmethod
    def __collect_providers(both: bool = False, gpt3_5: bool = False, gpt4: bool = False) -> List:
        _providers = []
        for _provider in g4f.Provider.__providers__:
            def testKey(*args):
                return all(_provider.__dict__.get(key, False) for key in args)

            if not _provider.working:
                continue
            if not testKey("supports_message_history"):
                continue
            if testKey("needs_auth"):
                continue
            if not both:
                if gpt3_5 and not testKey("supports_gpt_35_turbo"):
                    continue
                if gpt4 and not testKey("supports_gpt_4"):
                    continue
            else:
                if not testKey("supports_gpt_35_turbo") and not testKey("supports_gpt_4"):
                    continue
            if _provider.__module__ == "g4f.Provider.GptChatly":
                continue
            if _provider.__module__ == "g4f.Provider.Koala":
                continue
            if _provider.__module__ == "g4f.Provider.Liaobots":
                continue
            _providers.append(_provider)
        return _providers

    @staticmethod
    async def __run_provider(_provider, _memory: Memory) -> Tuple[bool, str, str]:
        try:
            if _memory.isEmpty():
                raise CHATAI.InvalidMessageError("AI.InvalidMessageError: Memory object contains no history.")

            _model = None
            if _provider.supports_gpt_35_turbo:
                _model = g4f.models.gpt_35_turbo
            elif _provider.supports_gpt_4:
                _model = g4f.models.gpt_4_turbo

            _response = await g4f.ChatCompletion.create_async(
                provider=_provider,
                model=_model,
                messages=_memory.getMessages(),
                timeout=15
            )
            return True, _provider.__name__, _response
        except Exception as e:
            return False, _provider.__name__, e.args[0]

    @staticmethod
    async def getChat(_memory: Memory) -> Tuple[bool, str, str]:
        _providers = CHATAI.__collect_providers(both=True)
        """
        _providers = [
            g4f.Provider.ChatBase,
            g4f.Provider.FakeGpt,
            g4f.Provider.GPTalk,
            g4f.Provider.GptGo
        ]
        """

        tasks = [asyncio.create_task(CHATAI.__run_provider(_provider, _memory)) for _provider in _providers]
        _message = ""
        while tasks:  # Continue as long as there are tasks pending
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                _success, _name, _message = task.result()
                if _success:
                    # If a task was successful, cancel all other tasks and return the result
                    for t in pending:
                        t.cancel()
                    return True, _name, _message
                else:
                    # If the task was not successful, remove it from the list of tasks
                    tasks.remove(task)

            # If no tasks are left and none were successful, return failure
            if not tasks:
                return False, "", _message


if __name__ == "__main__":

    Memory.MAX_MEMORY_SIZE = 4096
    with open("default", "r") as f:
        Memory.DEFAULT_PROMPT = f.read()

    username = "Jerrin"
    memory = Memory()

    while True:
        message = input(': ')
        memory.addUser(username, message)

        status, name, response = asyncio.run(CHATAI.getChat(memory))
        if status:
            print(f"{name}: {response}")
            memory.addAssistant(response)
            memory.resizeMemory()
        else:
            print(f"{response}")

