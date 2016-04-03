import json
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime
from dateutil import tz


conf ={
    'last_refresh_url': 'http://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json',
    'img_url_pattern': 'http://himawari8-dl.nict.go.jp/himawari8/img/D531106/%id/550/%s_%i_%i.png',    # scale, time, row, col
    'scale': 1,     # 1, 2, 4, 8, 16, 20
}


def utf2local(utc):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)


def download(args):
    scale = args['scale']
    png = Image.new('RGB', (550*scale, 550*scale))
    for row in range(scale):
        for col in range(scale):
            print 'Downloading %i of %i ...' % (row*scale + col + 1, scale*scale)
            strtime = args['time'].strftime("%Y/%m/%d/%H%M%S")
            url = conf['img_url_pattern'] % (args['scale'], strtime, row, col)
            r = requests.get(url)
            tile = Image.open(BytesIO(r.content))
            png.paste(tile, (550 * row, 550 * col, 550 * (row + 1), 550 * (col + 1)))
    fpath = "%s.png" % utf2local(args['time']).strftime("%Y/%m/%d/%H%M%S").replace('/', '')
    print 'Download over, save to file %s' % fpath
    png.save(fpath, "PNG")


def get_last_time():
    r = requests.get(conf['last_refresh_url'])
    resp = json.loads(r.text)
    last_refresh_time = datetime.strptime(resp['date'], '%Y-%m-%d %H:%M:%S')
    return last_refresh_time


def get_last_image():
    last_refresh_time = get_last_time()
    args = {'time': last_refresh_time}
    args['scale'] = conf['scale']
    download(args)


if __name__ == '__main__':
    get_last_image()
