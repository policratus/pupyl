"""
interface Module.

Create a web interface to query images and see results
based on indexed images on database.
"""
import lzma
import webbrowser
from http.server import SimpleHTTPRequestHandler
import socketserver
from urllib.parse import urlparse, parse_qs

import termcolor

from pupyl.duplex.file_io import FileIO
from pupyl.search import PupylImageSearch


TEMPLATE = lzma.decompress(
    b'\xfd7zXZ\x00\x00\x04\xe6\xd6\xb4F\x02\x00!\x01\x0c\x00\x00\x00'
    b'\x8f\x98A\x9c\xe0\x04T\x02=]\x00\x1e\x08E\x06\xd0\xef\xa8(\x17'
    b'Y\xd9\xa9\xf5\xea\xa7%@j6\\\xeb\x9c\xe5Q9\xfb__\x00W\xfe\x9c\xbd'
    b"\xbc\xb7\x81T\x95\xde\xe59\xdbd[\x8aWP'\xa1\xde\xdf\xb3fV\x05\x00T"
    b' \x84>8\xf1_y\xe1\xa50\xeb\x87\x91\xc0\x9c\x91\xf7\xaa%}\xfa\x98Ju'
    b'\x1f\xbb\x1fva\xdcW\xc9\x94&\xe8\xeb\x1et\xe7m\xa5\xd2\xdc\x0c'
    b'\xe5\x85@\xbc`\xb8\x80\x8b\xb7\t\x1e\x1e\xd71\xa7\xf4'
    b"\x01\xf6\xf4\xb6\xb7\xb3\xbe\r\xef\x01\xb7\xe8\x13\xcd'I"
    b'o\x8f\xde\xc2\xa9\xc8\x8a\xbd\x8e:\x00\xd3\x96\xfe\x9c?\xe3\xd2U#'
    b'\x88\x11\x9c\xfd3g\x8c\xfb\xd4\xb9\xd0\xc9"\xfd\xf5Nob\xd8\x12'
    b'\xa7\x91\x16&\x85\x9e\xe9\xc3sZ6\xb2\n\xc2\xdb$\xab\xe9\xf6}'
    b'l\xed\x06\xd1\x8f\x92\xd3\x82\xed\x91#|\xa2{\x7f\xfa'
    b"\xe6\xae\xfb\x05\xaeI\xa8\xa0\x1b\xca?\x06\xca%P\xea\x9c'\xd7\xce"
    b'\x7f\x8b`zB(|\xe0n\xfb\xdb\xdb\x84\xf3\x1e\xa7\xff\x0f7\x83'
    b'\xcd\xcc\xe39\xef\xe4A\xf50\\\xe9>\x18\xa61P\xce\x98>\x16'
    b'\xc9s\xb3\xa3\xb5\xb6\x84Nv\xaf\x07\x1d\x0b\xe0\xb2\x82\x06C`K'
    b'\x08/TC\xbfr\xb9\xda"\xff\xc9\xa9!=?\xd9`\xfaN,\x01\'t\xc0:m\r1'
    b'\xfa)\x88\xf9\xb6\x15\xaa\x04\x85\xa4\xec\xa8\xb5\x06a}'
    b'=\xb5\xca\x8c>\x0e\x18\x04\xec\xbe\xea1\x9c?\xf5\x8c\xe7\xe36k'
    b'm\n\xb2\xadu\n\xb7\xab sD\x98\xb3\x8fJ\xa5\x0c\x06\xeb5'
    b'\xf6b\xcc\xd0\xbd\x8a#&Z+\xbb-\xe0%\xff\x97<\xaa\xbbL\\\x9c;\x95'
    b'\x1a1Ifl\xbeN\x01\x98\xfb\xa1-N\x9f\xb1q\xb4\x92J\x7f\xf8\xcdf\xf9'
    b'\xeb\xdbM\x89\xd9\xae)\xef\xc7\xbbK\x8c\x1c%\x9e\x90'
    b'\xc1\xd7\xd1\xccM\x9bB\xcf\xa9\nD4>\x0f\x9d\x9fe:\x92\x93'
    b'8\xd7m\xba\xf4&a\x9e\x82D(\x13\xc7\xca\xc4w\xaa\xa0\x17\xf0'
    b'\xc2\x9f\xdb\xd9\xd69*~\xec\xb3\x84\xd3\xc6\x92u\x0c\xf3h\x1b\x9b'
    b'\xab\x9e-\x80]\xbam\xbe\xb0\xddJ\xd6\xda\xc5\x94$\xe88\x00\xec'
    b'i\xa3H\x1a\\\xafvZ}l\x11%\n2\n\xb0\x0b\xf8C\xef\xf1\x06\xdd\xac'
    b'\xf4\xae\xbeh\x96\xea<\x92\xc55\xef\x900\x05\xb3\xf8b\x89\x9bV'
    b'A\xc4\x8c\rZ\x1d\xacB\x16\xf2\xdb\x92\x00\x00\x00\x00i\x99t\xd5'
    b"\xd3\xbb 5\x00\x01\xd9\x04\xd5\x08\x00\x00\xe9'}\x1c\xb1\xc4g\xfb"
    b'\x02\x00\x00\x00\x00\x04YZ'
).decode()


def serve(data_dir=None, port=8080):
    """Starts the web server.

    Parameters
    ----------
    data_dir: str
        The path to the data directory. If not set, will try to find inside
        the default temporary file.

    port: int
        Defines the network port which the web server will start listening.
    """
    if not data_dir:
        data_dir = FileIO.pupyl_temp_data_dir()

    pupyl_image_search = PupylImageSearch(data_dir)

    class RequestHandler(SimpleHTTPRequestHandler):
        """A web request handler."""

        _data_dir = data_dir

        def __init__(self, request, client_address, server):
            SimpleHTTPRequestHandler.__init__(
                self, request, client_address, server
            )

        def do_GET(self):
            """Handler for GET request methods."""

            query_image = None

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            query_string = parse_qs(urlparse(self.path).query)

            query_list = query_string.get('uri', None)

            image_tags = self.images(query_list)

            if query_list:
                query_image = '<img class="img-thumbnail" ' + \
                    f'src="{query_list[0]}">' + \
                    '<figcaption class="figure-caption">' + \
                    'Query image used in the search.</figcaption>'

            self.wfile.write(
                bytes(
                    TEMPLATE.format(
                        images=image_tags,
                        query=query_image if query_image else ''),
                    'utf-8'
                )
            )

        @staticmethod
        def filter_metadata(index):
            """Returns a filtered metadata information.

            Parameters
            ----------
            index: int
                Index number of image

            Returns
            -------
            dict:
                With a pre-filtered metadata.
            """
            metadata = pupyl_image_search.image_database.\
                load_image_metadata(
                    index, filtered=(
                        'original_file_name',
                        'original_file_size'
                    )
                )

            return ', '.join(map(str, metadata.values()))

        def images(self, query_uri=None, top=None):
            """Returns image tags from database.

            Parameters
            ----------
            query_uri: str
                Location where the query image is stored.

            top: int
                How many results should be returned from some search request.

            Returns
            -------
            str:
                With base64 strings related to images inside database.

            Raises
            ------
            OSError:
                If some problem happened when starting the server.
            KeyboardInterrupt:
                If a command to stop the server is issued (like CTRL+c).
            """

            image_tags = ''
            img_src = '<figure class="figure">' + \
                '<img class="img-fluid border"' + \
                'src="data:image/jpg;base64, {image_b64}" ' + \
                'alt="&#129535; Pupyl"><figcaption class="figure-caption">' + \
                '{figure_caption}</figcaption></figure>'

            top = top if top else 24

            if query_uri:
                query_uri = query_uri[0]

                for result in pupyl_image_search.search(query_uri, top=top):
                    result = int(result)

                    image = pupyl_image_search.image_database.\
                        get_image_bytes_to_base64(
                            pupyl_image_search.image_database.
                            load_image(result)
                        ).decode('utf-8')

                    filtered_metadata = self.filter_metadata(result)

                    image_tags += img_src.format(
                        image_b64=image,
                        figure_caption=filtered_metadata
                    )

                return image_tags

            for index, image in pupyl_image_search.image_database.list_images(
                    return_index=True,
                    top=9
            ):
                image_base64 = pupyl_image_search.image_database.\
                    get_image_base64(
                        image
                    ).decode('utf-8')

                filtered_metadata = self.filter_metadata(index)

                image_tags += img_src.format(
                    image_b64=image_base64,
                    figure_caption=filtered_metadata
                )

            return image_tags

    if not port:
        port = 8080

    try:
        with socketserver.TCPServer(('', port), RequestHandler) as httpd:
            print(
                termcolor.colored(
                    f'Server listening on port {port}.',
                    color='green',
                    attrs=['bold']
                )
            )

            webbrowser.open_new_tab(f'http://localhost:{port}')
            httpd.serve_forever()

    except OSError:
        print(
            termcolor.colored(
                f'Port {port} already in use. Trying {port + 1}...',
                color='red',
                attrs=['bold']
            )
        )

        serve(data_dir=data_dir, port=port + 1)
    except KeyboardInterrupt:
        print('🧿 Pupyl says bye.')
