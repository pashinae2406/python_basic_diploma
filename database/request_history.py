from peewee import SqliteDatabase, Model, CharField, IntegerField


db = SqliteDatabase('people.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    command = CharField()
    telegram_id = IntegerField()
    date_time = CharField()
    city = CharField()
    hotels = CharField()


user = User()
