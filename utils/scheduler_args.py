class SchedulerArgs:
    def __init__(self, chat_id: int, user_id: int, message_id: int, link: str):
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_id = message_id
        self.link = link
