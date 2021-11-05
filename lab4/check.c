#include <stdint.h>
#include <stddef.h>
#include <limits.h>

#include "alloc.h"
#include "host.h"
#include "util.h"

// check_the_sum returns a very simple checksum over the photo data.
//
// If 0 is returned, the program was not able to compute the checksum.
uint32_t check_the_sum(const uint32_t photo_id) {
  uint32_t height = photo_height(photo_id);
  uint32_t width = photo_width(photo_id);
  
  uint32_t *photo_data;
  if (alloc_and_read_photo(photo_id, &photo_data) != height * width) {
    return 0;
  }

  uint32_t accum = 0;
  for (int i = 0; i < height * width; i++) {
    accum += photo_data[i];
  }

  // set last bit to distinguish from 0
  accum = accum | 0x1;
  return accum;
}

// check_ered_pattern writes a simple patterned square of the given size,
// returning 0 on failure and otherwise the value of write_photo.
uint32_t check_ered_pattern(const uint32_t size) {
  const uint32_t black = 0;
  const uint32_t white = -1;

  uint32_t *buf;
  if (!alloc_photo_buf(size, size, &buf)) {
    return 0;
  }

  for (int i = 0; i < size; i++) {
    for (int j = 0; j < size; j++) {
      int offset = (i * size) + j;
      if ((i + j) % 2) {
        buf[offset] = black;
      } else {
        buf[offset] = white;
      }
    }
  }
  return write_photo(0, size, size, buf);
}

// check_width simply asks for the photo's width.
uint32_t check_width(const uint32_t photo_id) {
  return photo_width(photo_id);
}

// check_height simply asks for the photo's height.
uint32_t check_height(const uint32_t photo_id) {
  return photo_height(photo_id);
}
