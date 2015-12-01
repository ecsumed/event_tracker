from datetime import datetime
import json

import peewee as pw

import local


db = pw.MySQLDatabase(local.DATABASE,
                      host=local.HOST,
                      port=local.PORT,
                      user=local.USER,
                      passwd=local.PASSWD)


class Point(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def toJson(self, ):
        return json.dumps({'x': self.x,
                           'y': self.y,
                           })

    def fromJson(self, json_pt):
        dict_pt = json.loads(json_pt)
        self.x = dict_pt['x']
        self.y = dict_pt['y']

        return self


class MySQLModel(pw.Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = db


class Event_Type(MySQLModel):
    id = pw.IntegerField(primary_key=True)
    name = pw.CharField()

    @classmethod
    def get_id(cls, event_type_name):
        """
        Returns id of event type specified.
        """
        try:
            type_ = cls.get(cls.name == event_type_name)
        except pw.DoesNotExist:
            type_ = None

        if type_:
            return type_.id
        else:
            return None


class Event(MySQLModel):
    id = pw.IntegerField(primary_key=True)
    coord = pw.CharField()
    event_time = pw.DateTimeField(default=datetime.now())
    report_time = pw.DateTimeField(default=datetime.now())
    event_type = pw.ForeignKeyField(Event_Type)

    @classmethod
    def addEvent(cls, coord, event_time, report_time, event_type_id):
        """
        Creates a new event.
        """

        event = Event(coord=coord.toJson(),
                      event_time=event_time,
                      report_time=report_time,
                      event_type=event_type_id)

        event.save()
        return (True, event)


def create_tables(db):
    db.connect()
    db.create_tables([Event, Event_Type], safe=True)


create_tables(db)
