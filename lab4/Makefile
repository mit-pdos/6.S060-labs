CC = /usr/local/opt/llvm/bin/clang # set this to the one in your installation
CFLAGS = \
--target=wasm32 \
--no-standard-libraries \
-Wl,--export-all \
-Wl,--no-entry \
-Wl,--allow-undefined

OBJS := $(patsubst %.c,%.wasm,$(wildcard *.c))

all: wasm venv

wasm: $(OBJS)

%.wasm: %.c alloc.h host.h util.h
	$(CC) $(CFLAGS) $< -o $@

venv:
	python3 -m venv venv
	${SHELL} -c ". venv/bin/activate && pip install -r requirements.txt"

lab4-ag: all
	. venv/bin/activate && ag4/ag4.py
.PHONY: lab4-ag

clean:
	-rm *.wasm
	-rm venv
.PHONY: clean

