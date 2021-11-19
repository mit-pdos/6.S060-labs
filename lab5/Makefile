venv:
	python3 -m venv venv
	${SHELL} -c ". venv/bin/activate && pip install -r requirements.txt"

check: venv
	. venv/bin/activate && python3 attacker.py
.PHONY: check

lab5-ag: venv 
	. venv/bin/activate && ag5/ag5.py
.PHONY: lab5-ag

clean:
	-rm -r venv
.PHONY: clean

