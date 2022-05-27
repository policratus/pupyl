UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S), Linux)
    OPEN_EXECUTABLE ?= xdg-open
endif
ifeq ($(UNAME_S), Darwin)
    OPEN_EXECUTABLE ?= open
endif
OPEN_EXECUTABLE ?= :

clean:
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@find . -name "dist" -type d | xargs rm -rf
	@find . -name "htmlcov" | xargs rm -rf
	@find . -name ".coverage" | xargs rm -rf
	@find . -name ".cache" | xargs rm -rf
	@find . -name "*.log" | xargs rm -rf
	@find . -name "*.egg-info" | xargs rm -rf
	@find . -name "*build" | xargs rm -rf
	@find . -name ".mypy_cache" | xargs rm -rf
	@-pkill -i 8888 || true

flake8: clean
	@flake8 --show-source --ignore=E402 .

static-check: clean
	@mypy pupyl/

test_http_server:
	@python -c "import http.server;import socketserver;import os;os.chdir(os.path.join('tests', 'tar_files'));httpd = socketserver.TCPServer(('', 8888), http.server.SimpleHTTPRequestHandler);httpd.serve_forever()" &

test: clean test_http_server
	py.test -vv -rxs

coverage:
	py.test --cov-report=xml --cov=.

linter:
	pylint -j0 --rcfile=$(GITHUB_WORKSPACE)/.pylintrc pupyl

coverage-html: clean test_http_server
	py.test -vv -rxs --cov-report=html --cov=.
	$(OPEN_EXECUTABLE) htmlcov/index.html

docs: clean
	@pyreverse --ignore=exceptions.py -o png -p pupyl -d docs/source/_static/ pupyl
