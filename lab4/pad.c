#include <stdint.h>
#include <stddef.h>
#include <limits.h>

#include "alloc.h"
#include "host.h"
#include "util.h"

// pad the photo with a border of some color.
//
// photo_id is the ID of the photo to be padded.
// color is the color the border should be.
// left is the side of the photo's left border.
// right is the side of the photo's right border.
// top is the side of the photo's top border.
// bottom is the side of the photo's bottom border.
//
// The return value is 1 if padding succeeded and 0 otherwise.
int pad(const uint32_t photo_id, const uint32_t color,
        const uint32_t left, const uint32_t right,
        const uint32_t top, const uint32_t bottom) {
  uint32_t old_width = photo_width(photo_id);
  uint32_t old_height = photo_height(photo_id);
  uint64_t new_width_unchecked = (((uint64_t) old_width) + left) + right;
  uint64_t new_height_unchecked = (((uint64_t) old_height) + top) + bottom;

  const uint32_t max_dim = -1;
  if (new_width_unchecked > max_dim) {
    return 0;
  }
  if (new_height_unchecked > max_dim) {
    return 0;
  }
  uint32_t new_width = new_width_unchecked;
  uint32_t new_height = new_height_unchecked;

  uint32_t *old_photo_data, *new_photo_data;
  if (alloc_and_read_photo(photo_id, &old_photo_data) != old_width * old_height) {
    return 0;
  }

  if (!alloc_photo_buf(new_width, new_height, &new_photo_data)) {
    return 0;
  }

  for (int i = 0; i < new_height; i++) {
    for (int j = 0; j < new_width; j++) {
      int new_offset = i * new_width + j;
      new_photo_data[new_offset] = color;
    }
  }

  for (int i = 0; i < old_height; i++) {
    int x = top + i;
    for (int j = 0; j < old_width; j++) {
      int y = left + j;

      int old_offset = i * old_width + j;
      int new_offset = x * new_width + y;
      new_photo_data[new_offset] = old_photo_data[old_offset];
    }
  }

  if (!write_photo(photo_id, new_width, new_height, new_photo_data)) {
    return 0;
  }
  return 1;
}
