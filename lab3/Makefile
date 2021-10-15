venv:
	python3 -m venv venv
	${SHELL} -c ". venv/bin/activate && pip install -r requirements.txt"

web: venv
	./web.py
.PHONY: web

test: venv
	. venv/bin/activate && python3 client.py && python3 crypto.py && python3 codec.py
.PHONY: test

clean:
	-rm -r venv
.PHONY: clean

lab3-ag: venv
	. venv/bin/activate && ag3/ag3.py
.PHONY: lab3-ag
