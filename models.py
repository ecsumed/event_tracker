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


def point_list_toJson(point_list):
    return [pt.toJson() for pt in point_list]


def point_list_fromJson(point_list, isSinglePoint):
    """
        Converts a list of dicts to a list of Points.
    """
    if isSinglePoint:
        point = point_list[0]
        return Point(float(point['x']), float(point['y']))
    else:
        return [Point(float(pt['x']), float(pt['y'])) for pt in point_list]


def events_to_dict(events):
    """
        Converts rows of events returned from the db query to a manageable dict.

        INPUT:
            List of Event objects.

        OUTPUT:
            {
                u'Pickpocket': [Point(), Point()],
                u'Robbery': [Point(), Point()]
            }
    """
    data = {}
    for event in events:
        # Get event_type info
        event_type = Event_Type.get(Event_Type.id == event.event_type_id)

        # Convert coord's to a list of dicts
        event.coord = json.loads(event.coord)

        if event_type.name not in data:
            data[event_type.name] = []

        data[event_type.name].\
            append(point_list_fromJson(event.coord, event_type.isSinglePoint))
    return data


class MySQLModel(pw.Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = db


class Event_Type(MySQLModel):
    id = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    isSinglePoint = pw.BooleanField()

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
        Creates a new event with the required paramets.

        INPUT:
            ex.
            coord = '[{"x": "24.891352", "y": "67.03474"}]' (json object)
            event_time = 2012-11-16 01:09:34 (datetime object)
            report_time = 2012-11-16 01:09:34 (datetime object)
            event_type_id = 4 (int) (foreign key id)

        OUTPUT:
            Newly created Event object
        """

        event = Event(coord=coord,
                      event_time=event_time,
                      report_time=report_time,
                      event_type=event_type_id)

        event.save()
        return (True, event)


def create_tables(db):
    db.connect()
    db.create_tables([Event, Event_Type], safe=True)


create_tables(db)
