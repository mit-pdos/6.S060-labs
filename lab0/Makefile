venv:
	python3 -m venv venv
	${SHELL} -c ". venv/bin/activate && pip install -r requirements.txt"

web: venv
	./web.py
.PHONY: web

test:
	python3 client.py && python3 crypto.py && python3 codec.py
.PHONY: test

clean:
	-rm -r venv
.PHONY: clean

lab0-ag:
	ag0/ag0.py
.PHONY: lab0-ag
