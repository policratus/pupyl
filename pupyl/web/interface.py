"""
interface Module.

Create a web interface to query images and see results
based on indexed images on database.
"""
import webbrowser
from http.server import SimpleHTTPRequestHandler
import socketserver
from urllib.parse import urlparse, parse_qs

import termcolor

from pupyl.duplex.file_io import FileIO
from pupyl.search import PupylImageSearch


TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<link rel="stylesheet"
href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"
integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk"
crossorigin="anonymous">
<meta charset="UTF-8">
<title>
&#129535; Pupyl is a really fast image search library which you can index your
own (thousands of) images and find similar images in milliseconds.
</title>
</head>
<body>
<div class="jumbotron text-center">
<h1>&#129535; Pupyl Image Search</h1>
<p class="lead">Pupyl is a really fast image search library which you can index
your own (thousands of) images and find similar images in milliseconds.</p>
<form>
<div class="form-group">
<label for="uri">Choose an image url as query.</label>
<input type="url" class="form-control" id="uri" name="uri"
placeholder="Place an image url here for search." aria-describedby="url_help">
<small id="url_help" class="form-text text-muted">
Image's URL to use as query.</small>
</div>
<button type="submit" class="btn btn-primary">Submit</button>
</form>
<br>
<div class="text-center">
<figure class="figure">
{query}
</figure>
</div>
</div>
<div class="text-center">
{images}
</div>
</body>
</html>
"""


def serve(data_dir=None, port=8080):
    """
    Start the web server.

    Parameters
    ----------
    port (optional)(default: 8080): int
        Defines the network port which the web server
        will start listening.
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
            """
            Return a filtered metadata information.

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
            """
            Return image tags from database.

            Parameters
            ----------
            query_uri (optional): str
                Location where the query image is stored.

            top (optional)(default: 24): int
                How many results should be returned from some search request.
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
