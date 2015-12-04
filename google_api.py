from itertools import cycle
import urllib
import cStringIO

from models import Event
from models import events_to_dict
import local
import settings

google_api_key = cycle(local.GOOGLE_API_KEYS)


class Static_Map_API(object):

    def __init__(self, ):
        pass

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
        params = 'size={}x{}&'.format(settings.IMAGE_SIZE[0],
                                      settings.IMAGE_SIZE[1],
                                      )
        # add zoom level
        params += 'zoom={}&'.format(settings.ZOOM_LEVEL)

        # add scale
        params += 'scale={}&'.format(settings.SCALE)

        # add image_type
        params += 'format={}&'.format(settings.FORMAT)

        for event_type, coords in url_data.iteritems():
            if event_type is ('Rally' or 'Protest'):
                continue

            else:
                params += 'markers=color:{}|label:{}'.format('red',
                                                             event_type[0],
                                                             )
                for coord in coords:
                    params += '|{x},{y}'.format(x=coord.x, y=coord.y)

            params += '&'

        url = settings.GOOGLE_BASE_URL.format(parameters=params,
                                              api_key=next(google_api_key),
                                              )
        # handle 2000 character limit url
        # print len(url)

        return url

    def fetch_image(self, url):
        """
            Given a url, will fetch the image and save to memory
        """
        file = cStringIO.StringIO(urllib.urlopen(url).read())
        return file

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
