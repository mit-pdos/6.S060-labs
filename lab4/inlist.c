#include <stdint.h>
#include <stddef.h>
#include <limits.h>

#include "alloc.h"
#include "host.h"
#include "util.h"

// find a photo ID within the list of photo IDs
int find(const uint32_t photo_id) {
  uint32_t *photo_list;
  int num_photos = alloc_and_list_photo_ids(&photo_list);
  if (num_photos == 0) {
    return 0;
  }

  for (int i = 0; i < num_photos; i++) {
    if (photo_list[i] == photo_id) {
      return 1;
    }
  }
  return 0;
}
