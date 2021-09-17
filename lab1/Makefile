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

lab1-ag: venv
	. venv/bin/activate && ag1/ag1.py
.PHONY: lab1-ag
