# Jerrin Shirks

# normal imports

# custom imports
from files.jerrinth import JerrinthBot


class Memory:
    def __init__(self, bot: JerrinthBot):
        self.bot = bot

    def count_tokens(self, text):
        return len(self.bot.ai.encoding.encode(text))

    def get_chat_prompt(self, ctx):
        return self.bot.getChannel(ctx).get("chatgpt-system-message", self.bot.ai_prompt_dict["normal"])

    def set_person_chat_prompt(self, ctx, name):
        with open(self.bot.directory + f"data/prompts/{name}.txt", "r", encoding='utf-8') as f:
            self.bot.getChannel(ctx)["chatgpt-system-message"] = f.read()

    def get_chat_history(self, ctx) -> list:
        data = self.bot.getChannel(ctx).get("chatgpt-content", [None])
        data[0] = {"role": "system", "content": self.get_chat_prompt(ctx)}
        return data

    def add_chat_user(self, ctx, content):
        data = self.get_chat_history(ctx)
        data.append({"role": "user", "content": content})
        self.bot.getChannel(ctx)["chatgpt-content"] = data

    def add_chat_assistant(self, ctx, content):
        data = self.get_chat_history(ctx)
        data.append({"role": "assistant", "content": content})
        self.bot.getChannel(ctx)["chatgpt-content"] = data

    def get_history_token_size(self, ctx, data=None):
        if data is None:
            data = self.get_chat_history(ctx)
        token_count = [0] * len(data)

        for index, content in enumerate(data):
            token_count[index] = self.count_tokens(content["content"])

        total = sum(token_count)
        print("History Tokens:", total, token_count)

        return total

    def reset_chat_history(self, ctx):
        if "chatgpt-content" in self.bot.getChannel(ctx):
            del self.bot.getChannel(ctx)["chatgpt-content"]

    def handle_resizing_memory(self, ctx, temp_data=None):
        if temp_data is None:
            data = self.get_chat_history(ctx)
        else:
            data = temp_data

        token_count = [0] * len(data)
        for index, content in enumerate(data):
            token_count[index] = self.count_tokens(content["content"])

        to_remove = 0
        while sum(token_count) > 3900:
            to_remove += 1
            token_count.pop(0)

        while to_remove > 0:
            to_remove -= 1
            data.pop(1)

        if temp_data is None:
            self.bot.getChannel(ctx)["chatgpt-content"] = data
            self.bot.saveData()
        else:
            return data
