all:
	docker build -f Dockerfile.postgis -t registry.jollyturns.com/patroni .
	docker push registry.jollyturns.com/patroni
