from peewee import SqliteDatabase, Model, TextField, DateField, AutoField

db = SqliteDatabase('cafe_bot.db')


class BaseModel(Model):
    class Meta:
        database = db


class Compra(BaseModel):
    id = AutoField()
    name = TextField()
    date = DateField()


def load_compra_table():
    if not Compra.table_exists():
        Compra.create_table(True)
