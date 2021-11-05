#include <stdint.h>
#include <stddef.h>
#include <limits.h>

#ifndef HOST_H_INCLUDED
#define HOST_H_INCLUDED

/* functions exported by the Python host */

// list_photo_ids asks the host for all the photo IDs it has access
// to.
//
// limit is the maximum number of photo IDs to return.
// photo_ids marks the start of the array containing the photo IDs.
// The returned value is the total number of accessible photo IDs.
extern uint32_t list_photo_ids(const uint32_t limit, uint32_t *photo_ids);

// photo_width asks the host for the width of a photo with the given ID.
//
// photo_id is the ID of the requested photo.
// The returned value is the photo's width.  If no such photo exists,
// 0 is returned.
extern uint32_t photo_width(const uint32_t photo_id);

// photo_height asks the host for the height of a photo with the given
// ID.
//
// photo_id is the ID of the requested photo.
// The returned value is the photo's height.  If no such photo exists,
// 0 is returned.
extern uint32_t photo_height(const uint32_t photo_id);

// read_photo asks the host to fill a pixel array with photo data.
//
// photo_id is the ID of the requested photo.
// limit is the maximum number of pixels to write.
// photo_data marks the start of the array containing the photo data.
// The returned value is the number of pixels written.  If no such photo
// exists, 0 is returned.
extern uint32_t read_photo(const uint32_t photo_id,
                           const uint32_t limit,
                           uint32_t *photo_data);

// write_photo asks the host to save a photo with some ID.
//
// photo_id is the ID of the target photo.  If 0 is given, a new photo
// is instead created.
// width is the photo's width.
// height is the photo's height.
// The returned value is the ID of the written photo.  If the write
// failed, 0 is returned.
extern uint32_t write_photo(const uint32_t photo_id,
                            const uint32_t width, const uint32_t height,
                            const uint32_t *photo_data);

#endif
