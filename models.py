from datetime import datetime
import peewee as pw

import local


db = pw.MySQLDatabase(local.DATABASE,
                      host=local.HOST,
                      port=local.PORT,
                      user=local.USER,
                      passwd=local.PASSWD)


class MySQLModel(pw.Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = db


class Event_Type(MySQLModel):
    id = pw.IntegerField(primary_key=True)
    name = pw.CharField()


class Event(MySQLModel):
    id = pw.IntegerField(primary_key=True)
    coord = pw.CharField()
    event_time = pw.DateTimeField(default=datetime.now())
    report_time = pw.DateTimeField(default=datetime.now())
    event_type = pw.ForeignKeyField(Event_Type, related_name='id')




def create_tables(db):
    db.connect()
    db.create_tables([Event, Event_Type], safe=True)


create_tables(db)
