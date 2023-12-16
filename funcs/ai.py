# Jerrin Shirks

# custom imports
import openai
from aiohttp import ClientSession
import asyncio
import tiktoken
import pprint

from files.support import *


class AI:
    def __init__(self, bot):
        self.bot = bot
        self.encoding = tiktoken.get_encoding("gpt2")
        self.openai = openai
        self.key_index = 0
        self.token_limit = {
            "gpt-3.5-turbo": 4000,
            "text-davinci-003": 4000,
            "text-davinci-002": 2048,
            "text-davinci-001": 2048,
            "text-curie-001": 2048,
            "text-babbage-001": 2048,
            "text-ada-001": 2048,
            # "code-davinci-002": 8000,
            # "code-davinci-001": 2048,
            "code-cushman-001": 2048,
        }
        self.engines = ["gpt-3.5-turbo",
                        "text-davinci-003",
                        "text-davinci-002",
                        "text-davinci-001",
                        "text-curie-001",
                        "text-babbage-001",
                        "text-ada-001",
                        # "code-davinci-002",
                        # "code-davinci-001",
                        "code-cushman-001"
                        ]

    def getAPIKeys(self):
        return self.bot.settings["openai_api_keys"]

    def loadNextKey(self) -> None:
        self.openai.api_key = self.getAPIKeys()[self.key_index]
        if len(self.getAPIKeys()) == 1:
            self.key_index = 0
        else:
            self.key_index = (self.key_index + 1) % (len(self.getAPIKeys()) - 1)

    def popKey(self) -> None:
        self.bot.settings["openai_api_keys"].pop(self.key_index)
        self.loadNextKey()
        self.bot.saveSettings()

    def getTokenCount(self, text: str, engine: str) -> int:
        _cap = self.token_limit.get(engine, 2048)
        text_tokens = len(text) // 4
        return _cap - text_tokens - 10

    async def getModeration(self, response):
        self.openai.aiosession.set(ClientSession())

        async def getModerationWrapper(message_data):
            try:
                self.loadNextKey()
                _response = await self.bot.ai.openai.Moderation.acreate(input=message_data)

            except openai.error.RateLimitError as e:
                if e.error["type"] == "insufficient_quota":
                    print("(moderation) Popping API Key")
                    self.popKey()   # updates token if quota ends
                else:
                    print("(moderation) openai.error.RateLimitError", e.error)
                return False, "try_again"

            else:
                return True, _response

        for _ in range(3):
            status, resp = await getModerationWrapper(response)
            logging.info("attempt: " + str(status))
            if status:
                await openai.aiosession.get().close()
                return True, resp
            else:
                if resp == "try_again":
                    print("(moderation) trying again")
                    await asyncio.sleep(2)
                    continue
        else:
            await openai.aiosession.get().close()
            return False, "Please try again!\nAn unknown error occurred."

    async def getChat(self, data):
        self.openai.aiosession.set(ClientSession())

        async def getChatResponseWrapper(message_data):

            try:
                self.loadNextKey()
                logging.info("before")
                response = await self.openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=message_data
                )

                finish_reason = response['choices'][0]['finish_reason']
                if finish_reason not in ["stop", "length", "None", None]:
                    print(f"(,chat) Bad Finish Reason: '{finish_reason}'")
                    pprint.pprint(response)
                    return False, "try_again"

                # no response
                if response['choices'][0]['message']['content'] == "":
                    response['choices'][0]['message'][
                        'content'] = "For some reason I do not have a response for that!"
                    return True, response

                return True, response

            except openai.error.RateLimitError as e:
                if e.error["type"] == "insufficient_quota":
                    self.popKey()   # updates token if quota ends
                    print("(,chat) Popping API Key")
                    return False, "try_again"

                print("(,chat) openai.error.RateLimitError")
                return False, "try_again"

            except openai.error.ServiceUnavailableError:
                print("(,chat) openai.error.ServiceUnavailableError")
                return False, "try_again"

            except openai.error.APIError:
                print("(,chat) openai.error.APIError")
                return False, "try_again"

            except Exception as e:
                print("(,chat) Other error:", e, e.args)
                return False, "try_again"

        for _ in range(3):
            status, resp = await getChatResponseWrapper(data)
            logging.info("attempt: " + str(status))
            if status:
                await openai.aiosession.get().close()
                return True, resp
            else:
                if resp == "try_again":
                    print("(,chat) trying again")
                    await asyncio.sleep(2)
                    continue
        else:
            await openai.aiosession.get().close()
            return False, "Please try again!\nAn unknown error occurred."

    async def getResponse(self, engine, text, randomness):
        self.openai.aiosession.set(ClientSession())

        async def getAiResponseWrapper(_engine, _text, _randomness):

            try:
                self.loadNextKey()
                response = await self.openai.Completion.acreate(
                    engine=self.engines[_engine],
                    prompt=_text,
                    temperature=_randomness,
                    max_tokens=self.getTokenCount(_text, _engine),
                    top_p=1.0,
                    frequency_penalty=1.0,
                    presence_penalty=0.0
                )

                # updates token if quota ends
                if "error" in response:
                    if response["error"]["type"] == "insufficient_quota":
                        self.popKey()
                        print("failing popping key")
                        return False, "try_again"

                else:
                    finish_reason = response['choices'][0]['finish_reason']
                    if finish_reason not in ["stop", "length"]:
                        print("finish reason")
                        return False, "try_again"

                    # no response
                    if response['choices'][0]['text'] == "":
                        response['choices'][0]['text'] = "For some reason I do not have a response for that!"

                return True, response

            except openai.error.RateLimitError as e:
                if self.bot.debug:
                    print(e.args, "openai.error.RateLimitError")

                if e.args[0] == 'You exceeded your current quota, please check your plan and billing details.':
                    self.popKey()
                    if self.bot.debug:
                        print("popping ai key")
                return False, "try_again"

            except openai.error.ServiceUnavailableError:
                if self.bot.debug:
                    print("openai.error.ServiceUnavailableError")
                return False, "try_again"

            except openai.error.APIError:
                if self.bot.debug:
                    print("openai.error.APIError")
                return False, "try_again"

            except Exception as e:
                print(e)
                return False, "try_again"

        for _ in range(3):
            status, resp = await getAiResponseWrapper(engine, text, randomness)
            if status:
                await openai.aiosession.get().close()
                return True, resp
            else:
                if resp == "try_again":
                    print("trying again")
                    await asyncio.sleep(2)
                    continue
        else:
            await openai.aiosession.get().close()
            return False, "Please try again! An unknown error occurred."
