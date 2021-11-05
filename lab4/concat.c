#include <stdint.h>
#include <stddef.h>
#include <limits.h>

#include "alloc.h"
#include "host.h"
#include "util.h"

static int concat_vertical(const uint32_t *photo_list, const uint32_t num_photos) {
  uint32_t *height_list;
  if (!alloc_uint32_buf(num_photos, &height_list)) {
    return 0;
  }
  
  uint32_t width = photo_width(photo_list[0]);
  uint32_t height = 0;
  for (int i = 0; i < num_photos; i++) {
    if (photo_width(photo_list[i]) != width) {
      return 0;
    }
    height_list[i] = photo_height(photo_list[i]);
    height += height_list[i];
  }

  uint32_t *new_photo;
  if (!alloc_photo_buf(width, height, &new_photo)) {
    return 0;
  }

  uint32_t *read_ptr = new_photo;
  for (int i = 0; i < num_photos; i++) {
    uint32_t size = width * height_list[i];
    if (read_photo(photo_list[i], size, read_ptr) < size) {
      return 0;
    }
    read_ptr += size;
  }

  return write_photo(0, width, height, new_photo);
}

static int concat_horizontal(const uint32_t *photo_list, const uint32_t num_photos) {
  uint32_t *width_list;
  if (!alloc_uint32_buf(num_photos, &width_list)) {
    return 0;
  }

  void **ptr_list;
  if (!alloc_ptr_buf(num_photos, &ptr_list)) {
    return 0;
  }

  uint32_t height = photo_height(photo_list[0]);
  uint32_t width = 0;
  for (int i = 0; i < num_photos; i++) {
    if (photo_height(photo_list[i]) != height) {
      return 0;
    }
    width_list[i] = photo_width(photo_list[i]);
    width += width_list[i];

    uint32_t *photo_data;
    if (alloc_and_read_photo(photo_list[i], &photo_data) != height * width_list[i]) {
      return 0;
    }
    ptr_list[i] = photo_data;
  }

  uint32_t *new_photo;
  if (!alloc_photo_buf(width, height, &new_photo)) {
    return 0;
  }

  uint32_t *read_ptr = new_photo;
  for (int row = 0; row < height; row++) {
    for (int i = 0; i < num_photos; i++) {
      uint32_t *photo_data = ptr_list[i];
      uint32_t offset = row * width_list[i];
      uint32_t limit = width_list[i];
      for (int k = 0; k < limit; k++) {
        read_ptr[k] = photo_data[offset+k];
      }
      read_ptr += limit;
    }
  }

  return write_photo(0, width, height, new_photo);
}

// concatenate all photos along some axis.
//
// All photos must have matching dimensions according to the provided
// axis.  In particular, for vertical concatenation all photos must
// have the same width; for horizontal concatenation all photos must
// have the same height.
//
// axis is 0 for vertical and 1 for horizontal concatenation.
//
// The return value is the resulting photo ID if concatenation
// succeeded and 0 otherwise.
int concat(const uint32_t axis) {
  uint32_t *photo_list;
  int num_photos = alloc_and_list_photo_ids(&photo_list);
  if (num_photos == 0) {
    return 0;
  }

  if (axis == 0) {
    return concat_vertical(photo_list, num_photos);
  } else if (axis == 1) {
    return concat_horizontal(photo_list, num_photos);
  } else {
    return 0;
  }
}
