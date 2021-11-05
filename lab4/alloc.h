#include <stdint.h>
#include <stddef.h>
#include <limits.h>

#ifndef ALLOC_H_INCLUDED
#define ALLOC_H_INCLUDED

/* a very simple memory allocator */

extern uint8_t __heap_base;

static uint8_t *heap_base = &__heap_base;
static uint8_t *alloc_top = &__heap_base;

#define WASM_PAGE_SIZE 65536

// forward declaration
static int initdone = 0;
static int initok = 0;
static int heapinit();

// heapcap returns the current heap capacity.
static uint32_t heapcap() {
  uintptr_t alloc_top_num = (uintptr_t) alloc_top;
  return (__builtin_wasm_memory_size(0) * WASM_PAGE_SIZE) - alloc_top_num;
}

// heapalloc implements a very simple memory allocator.
//
// size is the minimum number of bytes to allocate.
// handle is set to a pointer to the base of the allocation.
// The returned value is the size of the allocation.
//
// heapalloc works by maintaining a pointer to the top of the
// currently-allocated heap memory.  When a caller wishes to allocate
// more memory, it grows the heap (if necessary) and then bumps the
// pointer up by the size of the allocation.
//
// heapalloc will return an 8-byte aligned allocation.
//
// If there is insufficent space even after attempting to grow the
// heap, heapalloc will return an allocation with zero size.
//
// heapalloc does not support memory reclamation.
static unsigned int heapalloc(const size_t req_size, void **handle) {
  *handle = alloc_top;
  if (!heapinit()) {
    return initok;
  }

  size_t size = ((req_size + 7) / 8) * 8;

  uint32_t cap = heapcap();
  if (cap < size) {
    uint32_t req = size - cap;
    uint32_t pgs = (req + WASM_PAGE_SIZE - 1) / WASM_PAGE_SIZE;
    if (__builtin_wasm_memory_grow(0, pgs) == -1) {
      return 0;
    }
    if (heapcap() < size) {
      return 0;
    }
  }
  alloc_top += size;
  return size;
}

// heapinit initializes the heap.
static int heapinit() {
  if (initdone) {
    return initok;
  }
  initdone = 1;
  initok = 1;

  uintptr_t boundary = ((((uintptr_t) heap_base) + 7) / 8) * 8;
  uintptr_t residue = boundary - (uintptr_t) heap_base;

  if (residue != 0) {
    // drop this memory
    if (__builtin_wasm_memory_grow(0, 1) == -1) {
      initok = 0;
    } else if (heapcap() < residue) {
      initok = 0;
    } else {
      alloc_top += residue;
    }
  }
  return initok;
}

// XXX need wasi-libc to support malloc/free

#endif
