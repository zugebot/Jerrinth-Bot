# Jerrin Shirks

# custom imports
import openai
from transformers import GPT2TokenizerFast
from aiohttp import ClientSession
import random
import asyncio


class AI:
    def __init__(self, bot):
        self.bot = bot
        self.tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        self.openai = openai
        self.token_limit = {
            "text-davinci-003": 4000,
            "text-davinci-002": 2048,
            "text-davinci-001": 2048,
            "text-curie-001": 2048,
            "text-babbage-001": 2048,
            "text-ada-001": 2048,
            "code-davinci-002": 8000,
            "code-davinci-001": 2048,
            "code-cushman-001": 2048,
        }
        self.engines = ["text-davinci-003",
                        "text-davinci-002",
                        "text-davinci-001",
                        "text-curie-001",
                        "text-babbage-001",
                        "text-ada-001",
                        "code-davinci-002",
                        "code-davinci-001",
                        "code-cushman-001"
                        ]

    def loadRandomAIKey(self) -> None:
        self.openai.api_key = random.choice(self.bot.settings["openai_api_keys"])

    def popOpenAIKey(self) -> None:
        self.bot.settings["openai_api_keys"].pop(openai.api_key)
        self.loadRandomAIKey()
        self.bot.saveSettings()

    def getTokenCount(self, text: str, engine: str) -> int:
        cap = self.token_limit.get(engine, 2048)
        text_tokens = len(text) // 4
        return cap - text_tokens - 10



    async def getModeration(self, response):
        self.openai.aiosession.set(ClientSession())
        metrics = await self.bot.ai.openai.Moderation.acreate(input=response)
        await openai.aiosession.get().close()
        return metrics


    async def getResponse(self, engine, text, randomness):

        self.openai.aiosession.set(ClientSession())

        async def getResponseWrapper(_engine, _text, _randomness):

            try:
                self.loadRandomAIKey()
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
                        self.popOpenAIKey()
                        return False, "try_again"

                else:
                    finish_reason = response['choices'][0]['finish_reason']
                    if finish_reason not in ["stop", "length"]:
                        return False, "try_again"

                    # no response
                    if response['choices'][0]['text'] == "":
                        response['choices'][0]['text'] = "For some reason I do not have a response for that!"
                        return True, response

                return True, response

            except openai.error.RateLimitError:
                if self.bot.debug:
                    print("openai.error.RateLimitError")
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
                if self.bot.debug:
                    print(e)
                return False, "try_again"



        for _ in range(3):
            status, resp = await getResponseWrapper(engine, text, randomness)
            if status:
                await openai.aiosession.get().close()
                return True, resp
            else:
                if resp == "try_again":
                    await asyncio.sleep(3)
                    continue
        else:
            await openai.aiosession.get().close()
            return False, "Please try again!\nAn unknown error occurred."
