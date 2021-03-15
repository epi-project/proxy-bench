all: setup run

setup: 
	pipenv install

run:
	pipenv run python proxy_bench