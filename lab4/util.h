#include <stdint.h>
#include <stddef.h>
#include <limits.h>

#ifndef UTIL_H_INCLUDED
#define UTIL_H_INCLUDED

// alloc_ptr_buf allocates a (void *) array of the given size.
//
// 1 is returned on success; otherwise, 0 is returned.
static int alloc_ptr_buf(const uint32_t size, void ***buf) {
  void *data_alloc;
  size_t data_size = sizeof(void *) * size;
  if (heapalloc(data_size, &data_alloc) < data_size) {
    return 0;
  }
  
  void **data_ptr = data_alloc;
  *buf = data_ptr;
  return 1;  
}

// alloc_uint32_buf allocates a uint32_t array of the given size.
//
// 1 is returned on success; otherwise, 0 is returned.
static int alloc_uint32_buf(const uint32_t size, uint32_t **buf) {
  void *data_alloc;
  size_t data_size = sizeof(uint32_t) * size;
  if (heapalloc(data_size, &data_alloc) < data_size) {
    return 0;
  }
  
  uint32_t *data_ptr = data_alloc;
  *buf = data_ptr;
  return 1;  
}

// alloc_and_list_photo_ids allocates and returns the list of photo IDs.
//
// The list size is returned on success; otherwise 0 is returned.
static int alloc_and_list_photo_ids(uint32_t **buf) {
  uint32_t num_photos = list_photo_ids(0, &num_photos); // no write to num_photos
  if (num_photos == 0) {
      return 1;
  }
  
  uint32_t *photo_list;
  if (!alloc_uint32_buf(num_photos, &photo_list)) {
    return 0;
  }
  
  int num_photos_written = list_photo_ids(num_photos, photo_list);
  if (num_photos_written != num_photos) {
    // concurrently-changed list; caller must retry
    return 0;
  }

  *buf = photo_list;
  return num_photos;
}

// alloc_photo_buf allocates a buffer to hold a photo of size width*height.
//
// 1 is returned on success; otherwise, 0 is returned.
static int alloc_photo_buf(const uint32_t width, const uint32_t height,
                           uint32_t **buf) {
  void *photo_alloc;
  size_t photo_size = sizeof(uint32_t) * width * height;
  if (heapalloc(photo_size, &photo_alloc) < photo_size) {
    return 0;
  }
  
  uint32_t *photo_data = photo_alloc;
  *buf = photo_data;
  return 1;
}

// alloc_and_read_photo allocates a buffer and reads a photo into it.
//
// The photo size in pixels is returned on success; otherwise, 0 is returned.
static int alloc_and_read_photo(const uint32_t photo_id,
                                uint32_t **buf) {
  uint32_t width = photo_width(photo_id);
  uint32_t height = photo_height(photo_id);

  uint32_t *photo_data;
  if (!alloc_photo_buf(width, height, &photo_data)) {
    return 0;
  }
  uint32_t area = width * height;
  if (read_photo(photo_id, area, photo_data) < area) {
    return 0;
  }
  *buf = photo_data;
  return area;
}

#endif
