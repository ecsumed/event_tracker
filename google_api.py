import cStringIO
from PIL import Image
from itertools import cycle
import urllib

from models import Event
from models import Event_Type
from models import events_to_dict
import local
import settings

google_api_key = cycle(local.GOOGLE_API_KEYS)


class Static_Map_API(object):

    def __init__(self, ):
        self.image_size = (settings.IMAGE_SIZE[0], settings.IMAGE_SIZE[1])
        self.zoom_level = settings.ZOOM_LEVEL
        self.scale = settings.SCALE
        self.format_ = settings.FORMAT

        self.line_weight = settings.LINE_WEIGHT
        self.line_color = settings.LINE_COLOR

        self.area_weight = settings.AREA_WEIGHT
        self.area_color = settings.AREA_COLOR
        self.area_fill_color = settings.AREA_FILL_COLOR

    def build_url(self, url_data):
        """
            Builds a static map url to get the image.

            INPUT:
                A dict of the form:
                {
                    'Event_Name1': [Point(), Point()],
                    'Event_Name2': [Point(), Point()]
                }

            OUTPUT:
                A valid Google static image url
        """

        # add image size
        params = 'size={}x{}&'.format(self.image_size[0],
                                      self.image_size[1],
                                      )
        # add zoom level
        params += 'zoom={}&'.format(self.zoom_level)

        # add scale
        params += 'scale={}&'.format(self.scale)

        # add image_type
        params += 'format={}&'.format(self.format_)

        for event_type, coords in url_data.iteritems():
            event_info = Event_Type.\
                get(Event_Type.name == event_type)

            if not event_info.isSinglePoint:
                if event_info.name == 'Rally':
                    for e in coords:
                        params += 'path=color:{}|weight:{}'.\
                            format(self.line_color, self.line_weight)
                        params += self.add_coordinates(e, True)

                if event_info.name == 'Protest':
                    for e in coords:
                        params += 'path=color:{}|weight:{}|fillcolor:{}'.\
                            format(self.area_color,
                                   self.area_weight,
                                   self.area_fill_color,
                                   )
                        params += self.add_coordinates(e, True)
            else:
                if event_info.icon_url:
                    params += 'markers=icon:{}'.format(event_info.icon_url)
                else:
                    params += 'markers=color:{}|label:{}'.format('red',
                                                                 event_type[0],
                                                                 )
                params += self.add_coordinates(coords, False)
            params += '&'

        url = settings.GOOGLE_BASE_URL.format(parameters=params,
                                              api_key=next(google_api_key),
                                              )
        # handle 2000 character limit url
        # print len(url)
        return url

    def add_coordinates(self, coordinates, addAnd):
        """
            Adds a list of coordinates to a string to be appended to the static
            image url. Also, appends an '&' if addAnd is True.
            INPUT:
                [{'x': <number>, 'y': <number>}], addAnd
            OUTPUT:
                String, ex. '27.456456,58.65248|54.5246,58.695223&'
        """
        coord_params = ''
        for coord in coordinates:
            coord_params += '|{x},{y}'.format(x=coord.x, y=coord.y)

        if addAnd:
            coord_params += '&'

        return coord_params

    def fetch_image(self, url):
        """
            Given a url, will fetch the image and save to memory
        """
        img_file = cStringIO.StringIO(urllib.urlopen(url).read())
        return Image.open(img_file)

    def get_image(self, ):
        """
            Fetches the google static image using the latest 10 events.
        """
        events_by_time = Event.\
            select().\
            order_by(Event.report_time.desc()).\
            limit(10)

        events = events_by_time.order_by(Event.event_type)

        url = self.build_url(events_to_dict(events))
        image = self.fetch_image(url)

        return image
