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
	@find . -name "build" | xargs rm -rf

flake8: clean
	@flake8 . --show-source

test: clean
	PYTHONPATH=$($PYTHONPATH):$(pwd) py.test -vv -rxs

coverage: clean
	PYTHONPATH=$($PYTHONPATH):$(pwd) py.test -vv -rxs --cov-report=term --cov=.

coverage-html: clean
	PYTHONPATH=$($PYTHONPATH):$(pwd) py.test -vv -rxs --cov-report=html --cov=.
	$(OPEN_EXECUTABLE) htmlcov/index.html
