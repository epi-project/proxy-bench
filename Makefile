all: setup run

build: build-nginx

build-nginx:
	docker build -t proxy_bench/nginx ./images/nginx

pull:
	docker pull nginx:1.19
	docker pull onnovalkering/socksx-httping
	docker pull onnovalkering/socksx-proxy

setup: build pull
	mkdir /tmp/docker-tc
	pipenv install

run:
	pipenv run python -m proxy_bench

ping:
	docker network create ping --subnet 172.23.0.0/24 --gateway 172.23.0.1
	docker run --rm -dt --name nginx --net ping nginx:1.19	
	docker run --rm -t --net ping busybox ping -c 60 172.23.0.2
	docker kill nginx
	docker network remove ping

ping-delayed:
	docker network create ping --subnet 172.23.0.0/24 --gateway 172.23.0.1
	
	docker run --rm -dt --name ping-tc \
		--network host \
		--cap-add NET_ADMIN	\
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v /tmp/docker-tc:/var/docker-tc \
		lukaszlach/docker-tc
	
	docker run --rm -dt --name nginx \
		--net ping \
		--label "com.docker-tc.enabled=1" \
		--label "com.docker-tc.delay=0.4ms" \
		nginx:1.19	
	
	docker run --rm -it --name ping \
		--net ping \
		--label "com.docker-tc.enabled=1" \
		--label "com.docker-tc.delay=0.4ms" \
		busybox \
		ping -c 60 172.23.0.2
	
	docker kill nginx
	docker kill ping-tc

	docker network remove ping
