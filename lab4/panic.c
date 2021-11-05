#include <stdint.h>
#include <stddef.h>
#include <limits.h>

#include "alloc.h"
#include "host.h"
#include "util.h"

// trap causes a WASM trap.
int trap() {
  uintptr_t minus1 = 0;
  minus1 = minus1 - 1;
  uint32_t *invalid_ptr = (uint32_t *)minus1;
  return *invalid_ptr;
}

// badptr gives the host a bad pointer and asks it to read from it.
int badptr(const uint32_t photo_id) {
  uintptr_t pretty_big_number = 1 << 28;
  uint32_t *invalid_ptr = (uint32_t *)pretty_big_number;
  return write_photo(photo_id, 20, 20, invalid_ptr);
}
