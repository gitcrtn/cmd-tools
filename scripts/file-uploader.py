import os
import sys
import codecs

import click
from bottle import Bottle, request


sys.stdout = codecs.getwriter("utf-8")(sys.stdout)


class Server(object):
    def __init__(self, host, port, save_dir):
        self._host = host
        self._port = port
        self._save_dir = save_dir
        self._app = Bottle()
        self._init_route()
    
    def _init_route(self):
        self._app.route('/', callback=self.upload)
        self._app.post('/uploader', callback=self.do_upload)

    def upload(self):
        existing_file_list = os.listdir(self._save_dir)
        scrollable_style = 'overflow:auto; height:250px; line-height:1.5; padding:10px 0;'
        list_style = 'list-style: none; background: #888; color: #fff; padding: 0 0.5em; width: 30em; height: 2em; line-height: 2em; margin: 2px 0;'
        file_list_dom = ''.join(['<li style="%s">%s</li>' % (list_style, fname) for fname in existing_file_list])
        return '''
            <form action="/uploader" method="post" enctype="multipart/form-data">
                <input type="submit" value="Upload"></br>
                <input type="file" name="upload"></br>
            </form>
            <hr>
            <span>File List</span>
            <div style="%s">
                <ul>%s</ul>
            </div>
        ''' % (scrollable_style, file_list_dom)

    def do_upload(self):
        upload = request.files.get('upload', '')
        saving_file = os.path.join(self._save_dir, upload.filename)
        if os.path.exists(saving_file):
            return 'File exists. Canceled uploading.'
        upload.save(self._save_dir)
        return 'Upload OK. FilePath: %s' % saving_file
    
    def start(self):
        self._app.run(host=self._host, port=self._port, debug=True, reloader=True)


@click.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default='8080')
@click.option('--dir', 'save_dir', default=os.getcwd())
def main(host, port, save_dir):
    Server(host, port, save_dir).start()


if __name__ == '__main__':
    main()
