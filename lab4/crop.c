#include <stdint.h>
#include <stddef.h>
#include <limits.h>

#include "alloc.h"
#include "host.h"
#include "util.h"

// crop the photo to the specified dimensions.
//
// photo_id is the ID of the photo to be cropped.
// left is the left side of the photo.
// new_width is the photo's new width.
// left + new_width must be less than the original width.
// top is the top of the photo.
// new_height is the photo's new height.
// top + new_height must be less than the original height.
//
// The return value is 1 if cropping succeeded and 0 otherwise.
int crop(const uint32_t photo_id,
         const uint32_t left, const uint32_t new_width,
         const uint32_t top, const uint32_t new_height) {
  uint32_t old_width = photo_width(photo_id);
  uint32_t old_height = photo_height(photo_id);
  if (left + new_width < new_width) {
    return 0;
  }
  if (top + new_height < new_height) {
    return 0;
  }
  if (left + new_width > old_width) {
    return 0;
  }
  if (top + new_height > old_height) {
    return 0;
  }

  uint32_t *old_photo_data, *new_photo_data;
  if (alloc_and_read_photo(photo_id, &old_photo_data) != old_width * old_height) {
    return 0;
  }

  if (!alloc_photo_buf(new_width, new_height, &new_photo_data)) {
    return 0;
  }

  for (int i = 0; i < new_height; i++) {
    int x = top + i;
    for (int j = 0; j < new_width; j++) {
      int y = left + j;

      int old_offset = x * old_width + y;
      int new_offset = i * new_width + j;
      new_photo_data[new_offset] = old_photo_data[old_offset];
    }
  }

  if (!write_photo(photo_id, new_width, new_height, new_photo_data)) {
    return 0;
  }
  return 1;
}
