class GlobalState:
    user = None

    @classmethod
    def set_user(cls, user_data):
        cls.user = user_data

    @classmethod
    def get_user(cls):
        return cls.user

    @staticmethod
    def clear_token():
        GlobalState.user_token = None