VERSION != cat setup.py | grep version= | egrep -o "([0-9]{1,}\.)+[0-9]{1,}"

.PHONY: clean
clean:
	rm -fr build/
	rm -rf	dist/

.PHONY: print-version
print-version:
	echo $(VERSION)

.PHONY: venv/activate
venv/activate:
	./venv/bin/activate

.PHONY: format
format:
	black memory_consumer tests

.PHONY: lint
lint: format
	flake8 memory_consumer tests
	pylint memory_consumer tests

.PHONY: test-coverage
test-coverage:
	pytest -s --cov=memory_consumer tests/test_mem_pattern.py tests/test_mem_consumer_alloc.py tests/test_mem_consumer.py

.PHONY: test
test:
	pytest -s tests/test_mem_pattern.py
	pytest -s tests/test_mem_consumer_alloc.py
	pytest -s tests/test_mem_consumer.py

.PHONY: run-help
run-help:
	python	memory_consumer/start_mem_consumer.py -h

.PHONY: run
run:	# run the application for 1 minute (-d 60)
	python	memory_consumer/start_mem_consumer.py	-f patterns/s/high_low_10s.csv -n 10 -m 2000 -t 3 -s 0.1 -b -d 60

.PHONY: docker-build
docker-build:
	docker build -t memory_consumer:$(VERSION) .
	docker image prune -f

.PHONY: docker-run
docker-run:
	docker run -it --rm memory_consumer:$(VERSION) -f patterns/s/high_low_10s.csv -n 10 -m 2000 -t 3 -s 0.1 -b -d 60
