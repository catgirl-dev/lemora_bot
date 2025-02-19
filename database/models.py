from peewee import SqliteDatabase, Model, IntegerField, CharField, TextField

db: SqliteDatabase = SqliteDatabase('userdata.db')


class User(Model):
    chat_id: IntegerField  = IntegerField()
    user_id: IntegerField = IntegerField()
    message_id: IntegerField = IntegerField()
    captcha: CharField = CharField()
    answer: CharField = CharField()
    attempt_counter: IntegerField = IntegerField()
    bot_message_id: IntegerField = IntegerField()

    class Meta:
        database = db


class CaptchaConfig(Model):
    chat_id: IntegerField = IntegerField()
    captcha_ban_time: IntegerField = IntegerField(default=35) # минуты
    captcha_time: IntegerField = IntegerField(default=20) # часы

    class Meta:
        database: SqliteDatabase = db


class Rules(Model):
    chat_id: IntegerField = IntegerField()
    rules: CharField = CharField()

    class Meta:
        database: SqliteDatabase = db


class WelcomeMessage(Model):
    chat_id: IntegerField = IntegerField()
    welcome_message: TextField = TextField(
        default='Вы прошли капчу! Добро пожаловать!'
    )

    class Meta:
        database: SqliteDatabase = db
