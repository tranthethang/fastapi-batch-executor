.PHONY: format test verify start stop

format:
	@chmod +x bin/format.sh
	@./bin/format.sh

test:
	@chmod +x bin/test.sh
	@./bin/test.sh

verify:
	@chmod +x bin/verify.sh
	@./bin/verify.sh

start:
	@chmod +x bin/start.sh
	@./bin/start.sh

stop:
	@chmod +x bin/stop.sh
	@./bin/stop.sh
