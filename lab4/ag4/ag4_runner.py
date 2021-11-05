#!/usr/bin/env python3

import traceback
import random

import clientdb
import photobox

from typing import Callable, Sequence
from copy import deepcopy

# from util import trace, auto_str

# name -> (fn, pts)
tests = {}

# aliases for documentation
WasmPointer = int
WasmUint32 = int
Uint32 = int

def test_run_program(db: clientdb.Photobase, prog: photobox.PhotoEditingProgram, entry_point_name: str, permissions_tag: str, args: Sequence[WasmUint32]) -> WasmUint32:
    """test_run_program attempts to run the given program under permissions of the given tag,
    returning its result (if any)."""
    sandbox = prog.new_sandboxed_instance(db, permissions_tag)
    return sandbox.execute(entry_point_name, *args)

def test_this(pts: int) -> Callable[[Callable[[], bool]], Callable[[], int]]:
    def wrap(f: Callable[[], bool]) -> Callable[[], int]:
        def wrapper() -> int:
            try:
                if f():
                    return pts
                return 0
            except:
                traceback.print_exc()
                return 0
        tests[f.__name__] = (wrapper, pts)
        return wrapper
    return wrap


class TestingPhotobase:
    def __init__(self, base: clientdb.Photobase = None):
        self.base = base
        self.triggers = {}
        if base is None:
            self.base = clientdb.Photobase()

    def add_photo(self, photo: clientdb.Photo, read_only: bool) -> Uint32:
        if 'add_photo' in self.triggers:
            self.triggers['add_photo']()
        return self.base.add_photo(photo, read_only)

    def add_tag_to_photo(self, photo_id: Uint32, tag: str):
        if 'add_tag_to_photo' in self.triggers:
            self.triggers['add_tag_to_photo']()
        self.base.add_tag_to_photo(photo_id, tag)

    def all_photo_ids(self) -> Sequence[Uint32]:
        if 'all_photo_ids' in self.triggers:
            self.triggers['all_photo_ids']()
        return self.base.all_photo_ids()

    def assign_photo_to_id(self, photo_id: Uint32, photo: clientdb.Photo):
        if 'assign_photo_to_id' in self.triggers:
            self.triggers['assign_photo_to_id']()
        self.base.assign_photo_to_id(photo_id, photo)

    def photo_with_id(self, photo_id: Uint32) -> clientdb.Photo:
        if 'photo_with_id' in self.triggers:
            self.triggers['photo_with_id']()
        return self.base.photo_with_id(photo_id)

    def photo_writable(self, photo_id: Uint32) -> bool:
        if 'photo_writable' in self.triggers:
            self.triggers['photo_writable']()
        return self.base.photo_writable(photo_id)

    def tags_of_photo(self, photo_id: Uint32) -> Sequence[str]:
        if 'tags_of_photo' in self.triggers:
            self.triggers['tags_of_photo']()
        return self.base.tags_of_photo(photo_id)

photos_raw = [
    (1, 3, [2837027, 12281481, 6825119]),
    (2, 4, [15168995, 4193605, 14613417, 16412050, 3423999, 3958321, 9426336, 14680584]),
    (3, 5, [13916378, 11402046, 16156576, 10908361, 15482213, 10358933, 12481992, 8722411, 6822656, 10098045, 15883670, 6844262, 5854612, 3931462, 16431084]),
    (4, 6, [10879384, 8622497, 8312024, 12530869, 15410732, 4076744, 8003494, 4729564, 9464903, 2615761, 11959292, 13045908, 8607779, 11328883, 11165909, 2758743, 3924995, 4686937, 13162221, 14098895, 13619204, 2707271, 13836659, 7197500]),
    (5, 7, [4336299, 14522672, 15425418, 12171100, 2136189, 13904704, 5773946, 15754718, 14877963, 16052670, 3716771, 8776032, 5806410, 2037573, 7824091, 3093203, 14060886, 2953048, 5526464, 477150, 10820217, 2395531, 2299493, 4925309, 4762943, 9512054, 270836, 1954366, 8560286, 8083405, 16533157, 101446, 12713254, 8859105, 8077606])
]

### correctness

@test_this(1)
def test_correctness_dimensions():
    base = TestingPhotobase()
    return check_correctness_dimensions(base)

def check_correctness_dimensions(base: TestingPhotobase):
    processing_tag = "check"
    photo_ids = []
    for i, raw in enumerate(photos_raw):
        photo_id = base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)
        base.add_tag_to_photo(photo_id, processing_tag)
        photo_ids.append(photo_id)

    prog = photobox.PhotoEditingProgram("check.wasm")

    for photo_id in photo_ids:
        width = test_run_program(base, prog, "check_width", processing_tag, (photo_id,))
        height = test_run_program(base, prog, "check_height", processing_tag, (photo_id,))
        photo = base.photo_with_id(photo_id)
        if width != photo.width:
            return False
        if height != photo.height:
            return False
    return True

@test_this(1)
def test_correctness_read():
    base = TestingPhotobase()
    return check_correctness_read(base)

def check_correctness_read(base: TestingPhotobase):
    processing_tag = "check"
    photo_ids = []
    for i, raw in enumerate(photos_raw):
        photo_id = base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)
        base.add_tag_to_photo(photo_id, processing_tag)
        photo_ids.append(photo_id)

    prog = photobox.PhotoEditingProgram("check.wasm")

    expected = [21943627, 81877307, 165294701, 216746169, 269096315]
    for i, photo_id in enumerate(photo_ids):
        csum = test_run_program(base, prog, "check_the_sum", processing_tag, (photo_id,))
        if csum != expected[i]:
            return False
    return True

@test_this(1)
def test_correctness_write():
    base = TestingPhotobase()
    return check_correctness_write(base)

def check_correctness_write(base: TestingPhotobase):
    processing_tag = "check"
    prog = photobox.PhotoEditingProgram("check.wasm")
    result = test_run_program(base, prog, "check_ered_pattern", processing_tag, (5,))

    if result == 0:
        return False

    photo = base.photo_with_id(result)
    return photo == clientdb.Photo(5, 5, [4294967295, 0, 4294967295, 0, 4294967295, 0, 4294967295, 0, 4294967295, 0, 4294967295, 0, 4294967295, 0, 4294967295, 0, 4294967295, 0, 4294967295, 0, 4294967295, 0, 4294967295, 0, 4294967295])

@test_this(1)
def test_correctness_list():
    base = TestingPhotobase()
    return check_correctness_list(base)

def check_correctness_list(base: TestingPhotobase):
    processing_tag = "mark"
    prog = photobox.PhotoEditingProgram("inlist.wasm")

    expected = []
    for i, raw in enumerate(photos_raw):
        photo_id = base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)
        if i < len(photos_raw):
            base.add_tag_to_photo(photo_id, processing_tag)
            expected.append(photo_id)

    for photo_id in expected:
        result = test_run_program(base, prog, "find", processing_tag, (photo_id,))
        if result == 0:
            return False
    return True

@test_this(1)
def test_correctness_crop():
    base = TestingPhotobase()
    return check_correctness_crop(base)

def check_correctness_crop(base: TestingPhotobase):
    for i, raw in enumerate(photos_raw):
        base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)

    target_photo_id = 5
    processing_tag = "touchups"
    prog = photobox.PhotoEditingProgram("crop.wasm")

    base.add_tag_to_photo(target_photo_id, processing_tag)
    result = test_run_program(base,
                              prog,
                              "crop",
                              processing_tag,
                              (target_photo_id, 1, 2, 1, 3))

    if result == 0:
        return False

    photo = base.photo_with_id(target_photo_id)
    return photo == clientdb.Photo(2, 3, [5773946, 15754718, 8776032, 5806410, 14060886, 2953048])

@test_this(1)
def test_correctness_pad():
    base = TestingPhotobase()
    return check_correctness_pad(base)

def check_correctness_pad(base: TestingPhotobase):
    for i, raw in enumerate(photos_raw):
        base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)

    target_photo_id = 1
    processing_tag = "touchups"
    prog = photobox.PhotoEditingProgram("pad.wasm")

    base.add_tag_to_photo(target_photo_id, processing_tag)
    result = test_run_program(base,
                              prog,
                              "pad",
                              processing_tag,
                              (target_photo_id, 0, 1, 2, 1, 3))

    if result == 0:
        return False

    photo = base.photo_with_id(target_photo_id)
    return photo == clientdb.Photo(4, 7, [0, 0, 0, 0, 0, 2837027, 0, 0, 0, 12281481, 0, 0, 0, 6825119, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

@test_this(1)
def test_correctness_pad_then_crop():
    base = TestingPhotobase()

    for i, raw in enumerate(photos_raw):
        base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)

    target_photo_id = 3
    processing_tag = "touchups"
    prog1 = photobox.PhotoEditingProgram("pad.wasm")
    prog2 = photobox.PhotoEditingProgram("crop.wasm")

    base.add_tag_to_photo(target_photo_id, processing_tag)
    result = test_run_program(base, prog1, "pad", processing_tag,
                              (target_photo_id, 0, 1, 2, 1, 3))
    result = test_run_program(base, prog2, "crop", processing_tag,
                              (target_photo_id, 1, 2, 1, 3))

    if result == 0:
        return False

    photo = base.photo_with_id(target_photo_id)

    return photo == clientdb.Photo(2, 3, [13916378, 11402046, 10908361, 15482213, 12481992, 8722411])

@test_this(1)
def test_correctness_pad_then_crop_tags():
    base = TestingPhotobase()

    for i, raw in enumerate(photos_raw):
        base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)

    target_photo_id = 3
    processing_tag1 = "pad"
    processing_tag2 = "crop"
    prog1 = photobox.PhotoEditingProgram("pad.wasm")
    prog2 = photobox.PhotoEditingProgram("crop.wasm")

    base.add_tag_to_photo(target_photo_id, processing_tag1)
    base.add_tag_to_photo(target_photo_id, processing_tag2)
    result = test_run_program(base, prog1, "pad", processing_tag1,
                              (target_photo_id, 0, 1, 2, 1, 3))
    result = test_run_program(base, prog2, "crop", processing_tag2,
                              (target_photo_id, 1, 2, 1, 3))

    if result == 0:
        return False

    photo = base.photo_with_id(target_photo_id)

    return photo == clientdb.Photo(2, 3, [13916378, 11402046, 10908361, 15482213, 12481992, 8722411])

@test_this(2)
def test_correctness_concat():
    base = TestingPhotobase()
    return check_correctness_concat(base)

def check_correctness_concat(base: TestingPhotobase):
    for i, raw in enumerate(photos_raw):
        base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)

    target_photo_id = 3
    copies = 3
    base_photo = base.photo_with_id(target_photo_id)
    tag_ids = []
    for j in range(copies):
        for k in range(len(base_photo.data)):
            base_photo.data[k] += (j+1)
            base_photo.data[k] %= 16581375
        tag_ids.append(base.add_photo(base_photo, True))

    prog = photobox.PhotoEditingProgram("concat.wasm")

    processing_tag = "concath"
    base.add_tag_to_photo(target_photo_id, processing_tag)
    for tag_id in tag_ids:
        base.add_tag_to_photo(tag_id, processing_tag)

    result = test_run_program(base,
                              prog,
                              "concat",
                              processing_tag,
                              (1,))

    if result == 0:
        return False

    photo = base.photo_with_id(result)
    if photo != clientdb.Photo(12, 5, [13916378, 11402046, 16156576, 13916379, 11402047, 16156577, 13916381, 11402049, 16156579, 13916384, 11402052, 16156582, 10908361, 15482213, 10358933, 10908362, 15482214, 10358934, 10908364, 15482216, 10358936, 10908367, 15482219, 10358939, 12481992, 8722411, 6822656, 12481993, 8722412, 6822657, 12481995, 8722414, 6822659, 12481998, 8722417, 6822662, 10098045, 15883670, 6844262, 10098046, 15883671, 6844263, 10098048, 15883673, 6844265, 10098051, 15883676, 6844268, 5854612, 3931462, 16431084, 5854613, 3931463, 16431085, 5854615, 3931465, 16431087, 5854618, 3931468, 16431090]):
        return False

    ###

    processing_tag = "concatv"
    base.add_tag_to_photo(target_photo_id, processing_tag)
    for tag_id in tag_ids:
        base.add_tag_to_photo(tag_id, processing_tag)

    result = test_run_program(base,
                              prog,
                              "concat",
                              processing_tag,
                              (0,))

    if result == 0:
        return False

    photo = base.photo_with_id(result)
    if photo != clientdb.Photo(3, 20, [13916378, 11402046, 16156576, 10908361, 15482213, 10358933, 12481992, 8722411, 6822656, 10098045, 15883670, 6844262, 5854612, 3931462, 16431084, 13916379, 11402047, 16156577, 10908362, 15482214, 10358934, 12481993, 8722412, 6822657, 10098046, 15883671, 6844263, 5854613, 3931463, 16431085, 13916381, 11402049, 16156579, 10908364, 15482216, 10358936, 12481995, 8722414, 6822659, 10098048, 15883673, 6844265, 5854615, 3931465, 16431087, 13916384, 11402052, 16156582, 10908367, 15482219, 10358939, 12481998, 8722417, 6822662, 10098051, 15883676, 6844268, 5854618, 3931468, 16431090]):
        return False

    return True

def check_correctness():
    base = TestingPhotobase()
    def runtest(f):
        # shared base
        if f(base) == 0:
            raise Exception("{} correctness test failed".format(f.__name__))
    runtest(check_correctness_dimensions)
    runtest(check_correctness_read)
    runtest(check_correctness_write)
    runtest(check_correctness_list)
    runtest(check_correctness_crop)
    runtest(check_correctness_pad)
    runtest(check_correctness_concat)

@test_this(2)
def test_correctness_several():
    check_correctness()
    return True

### security: host vs sandbox

@test_this(2)
def test_security_readonly():
    check_correctness()

    base = TestingPhotobase()

    raw = photos_raw[0]
    original_photo = clientdb.Photo(raw[0], raw[1], raw[2])
    photo_id = base.add_photo(original_photo, True)

    processing_tag = "readonly"
    prog = photobox.PhotoEditingProgram("crop.wasm")

    base.add_tag_to_photo(photo_id, processing_tag)
    result = test_run_program(base,
                              prog,
                              "crop",
                              processing_tag,
                              (photo_id, 0, 0, 1, 1))

    new_photo = base.photo_with_id(photo_id)
    return new_photo == original_photo

@test_this(2)
def test_security_read_bad_tag():
    check_correctness()

    base = TestingPhotobase()

    raw = photos_raw[0]
    original_photo = clientdb.Photo(raw[0], raw[1], raw[2])
    photo_id = base.add_photo(original_photo, False)

    processing_tag = "badtag"
    prog = photobox.PhotoEditingProgram("check.wasm")
    base.add_tag_to_photo(photo_id, processing_tag + "000")

    width = test_run_program(base, prog, "check_width", processing_tag, (photo_id,))
    height = test_run_program(base, prog, "check_height", processing_tag, (photo_id,))
    csum = test_run_program(base, prog, "check_the_sum", processing_tag, (photo_id,))
    return (csum == 1) and (width == 0) and (height == 0)

@test_this(2)
def test_security_write_bad_tag():
    check_correctness()

    base = TestingPhotobase()

    raw = photos_raw[0]
    original_photo = clientdb.Photo(raw[0], raw[1], raw[2])
    photo_id = base.add_photo(original_photo, False)

    processing_tag = "badtag"
    prog = photobox.PhotoEditingProgram("crop.wasm")
    base.add_tag_to_photo(photo_id, processing_tag + "000")

    result = test_run_program(base, prog, "crop", processing_tag,
                              (photo_id, 0, 0, 1, 1))

    new_photo = base.photo_with_id(photo_id)
    return new_photo == original_photo

@test_this(2)
def test_security_write_bad_tag_readonly():
    check_correctness()

    base = TestingPhotobase()

    raw = photos_raw[0]
    original_photo = clientdb.Photo(raw[0], raw[1], raw[2])
    photo_id = base.add_photo(original_photo, True)

    processing_tag = "badtag"
    prog = photobox.PhotoEditingProgram("crop.wasm")
    base.add_tag_to_photo(photo_id, processing_tag + "000")

    result = test_run_program(base, prog, "crop", processing_tag,
                              (photo_id, 0, 0, 1, 1))

    new_photo = base.photo_with_id(photo_id)
    return new_photo == original_photo

@test_this(2)
def test_security_write_then_bad_tag():
    check_correctness()

    base = TestingPhotobase()

    original_photo = clientdb.Photo(photos_raw[0][0], photos_raw[0][1], photos_raw[0][2])
    next1_photo = clientdb.Photo(photos_raw[0][0], photos_raw[0][1], photos_raw[0][2])
    next2_photo = clientdb.Photo(photos_raw[0][0], photos_raw[0][1], photos_raw[0][2])

    original_id = base.add_photo(original_photo, False)
    next1_id = base.add_photo(next1_photo, False)
    next2_id = base.add_photo(next2_photo, False)

    processing_tag = "badtag"

    base.add_tag_to_photo(original_id, processing_tag + "000")

    base.add_tag_to_photo(next1_id, processing_tag)
    base.add_tag_to_photo(next2_id, processing_tag)

    prog = photobox.PhotoEditingProgram("concat.wasm")

    result = test_run_program(base,
                              prog,
                              "concat",
                              processing_tag,
                              (1,))

    prog = photobox.PhotoEditingProgram("crop.wasm")

    result = test_run_program(base,
                              prog,
                              "crop",
                              processing_tag,
                              (original_id, 0, 0, 1, 1))

    if result != 0:
        return False

    new_photo = base.photo_with_id(original_id)
    return new_photo == original_photo

@test_this(1)
def test_security_list():
    check_correctness()

    base = TestingPhotobase()
    processing_tag = "mark"
    prog = photobox.PhotoEditingProgram("inlist.wasm")

    expected = []
    for i, raw in enumerate(photos_raw):
        photo_id = base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)
        if i < len(photos_raw):
            base.add_tag_to_photo(photo_id, processing_tag)
        else:
            expected.append(photo_id)

    for photo_id in expected:
        result = test_run_program(base, prog, "find", processing_tag, (photo_id,))
        if result == 1:
            return False
    return True

@test_this(2)
def test_security_crash():
    check_correctness()

    base = TestingPhotobase()

    raw = photos_raw[0]
    processing_tag = "crash"
    prog = photobox.PhotoEditingProgram("panic.wasm")
    test_run_program(base, prog, "trap", processing_tag, ())
    return True

@test_this(2)
def test_security_bad_host_write():
    check_correctness()

    base = TestingPhotobase()

    raw = photos_raw[0]
    original_photo = clientdb.Photo(raw[0], raw[1], raw[2])
    photo_id = base.add_photo(original_photo, False)

    processing_tag = "badptr"
    prog = photobox.PhotoEditingProgram("panic.wasm")

    base.add_tag_to_photo(photo_id, processing_tag)
    test_run_program(base, prog, "badptr", processing_tag, (photo_id,))
    return True

@test_this(2)
def test_security_reentrant():
    check_correctness()

    base = TestingPhotobase()

    for i, raw in enumerate(photos_raw):
        base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)

    target_photo_id = 5
    processing_tag = "tag1"
    prog = photobox.PhotoEditingProgram("crop.wasm")

    base.add_tag_to_photo(target_photo_id, processing_tag)

    def interrupt():
        del base.triggers['assign_photo_to_id']
        test_run_program(base, prog, "crop", processing_tag,
                         (target_photo_id, 1, 2, 1, 3))

    base.triggers['assign_photo_to_id'] = interrupt

    result = test_run_program(base, prog, "crop", processing_tag,
                              (target_photo_id, 0, 1, 0, 1))

    ## not required by spec
    # if result == 0:
    #     return False

    # photo = base.photo_with_id(target_photo_id)
    # return photo == clientdb.Photo(1, 1, [5773946])

    return True

### security: sandbox vs sandbox

@test_this(2)
def test_security_write_append():
    check_correctness()

    base = TestingPhotobase()

    for i, raw in enumerate(photos_raw):
        base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)

    target_photo_id_h = 3
    copies = 3
    base_photo = base.photo_with_id(target_photo_id_h)
    tag_ids = []
    for j in range(copies):
        for k in range(len(base_photo.data)):
            base_photo.data[k] += (j+1)
            base_photo.data[k] %= 16581375
        tag_ids.append(base.add_photo(base_photo, False))

    prog = photobox.PhotoEditingProgram("concat.wasm")

    processing_tag_h = "concath"
    base.add_tag_to_photo(target_photo_id_h, processing_tag_h)
    for tag_id in tag_ids:
        base.add_tag_to_photo(tag_id, processing_tag_h)

    result = test_run_program(base, prog, "concat", processing_tag_h, (0,))
    if result == 0:
        return False
    photo = base.photo_with_id(result)

    prog = photobox.PhotoEditingProgram("crop.wasm")
    processing_tag = "none"
    test_run_program(base, prog, "crop", processing_tag, (result, 1, 2, 1, 3))
    other_photo = base.photo_with_id(result)

    return photo == other_photo

@test_this(2)
def test_security_concurrent_crash():
    check_correctness()

    base = TestingPhotobase()

    for i, raw in enumerate(photos_raw):
        base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)

    target_photo_id = 5
    processing_tag = "tag1"
    prog = photobox.PhotoEditingProgram("crop.wasm")

    base.add_tag_to_photo(target_photo_id, processing_tag)

    def interrupt():
        del base.triggers['assign_photo_to_id']
        prog2 = photobox.PhotoEditingProgram("panic.wasm")
        test_run_program(base, prog2, "trap", processing_tag, ())

    base.triggers['assign_photo_to_id'] = interrupt

    result = test_run_program(base, prog, "crop", processing_tag,
                              (target_photo_id, 0, 1, 0, 1))

    if result == 0:
        return False

    photo = base.photo_with_id(target_photo_id)
    return photo == clientdb.Photo(1, 1, [4336299])

@test_this(2)
def test_security_concurrent_append():
    check_correctness()

    base = TestingPhotobase()

    for i, raw in enumerate(photos_raw):
        base.add_photo(clientdb.Photo(raw[0], raw[1], raw[2]), i%2 == 1)

    target_photo_id_h = 3
    copies = 3
    base_photo = base.photo_with_id(target_photo_id_h)
    tag_ids = []
    for j in range(copies):
        for k in range(len(base_photo.data)):
            base_photo.data[k] += (j+1)
            base_photo.data[k] %= 16581375
        tag_ids.append(base.add_photo(base_photo, False))

    prog = photobox.PhotoEditingProgram("concat.wasm")

    processing_tag_h = "concath"
    base.add_tag_to_photo(target_photo_id_h, processing_tag_h)
    for tag_id in tag_ids:
        base.add_tag_to_photo(tag_id, processing_tag_h)

    target_photo_id_v = 2
    copies = 4
    base_photo = base.photo_with_id(target_photo_id_v)
    tag_ids = []
    for j in range(copies):
        for k in range(len(base_photo.data)):
            base_photo.data[k] += (j+1)
            base_photo.data[k] %= 16581375
        tag_ids.append(base.add_photo(base_photo, False))

    prog = photobox.PhotoEditingProgram("concat.wasm")

    processing_tag_v = "concatv"
    base.add_tag_to_photo(target_photo_id_v, processing_tag_v)
    for tag_id in tag_ids:
        base.add_tag_to_photo(tag_id, processing_tag_v)

    success = True
    photo_id_h = 0
    photo_id_v = 0
    def interrupt():
        nonlocal success, photo_id_h

        del base.triggers['add_photo']
        result = test_run_program(base, prog, "concat", processing_tag_h, (1,))
        if result == 0:
            success = False
        photo_id_h = result

    base.triggers['add_photo'] = interrupt
    result = test_run_program(base, prog, "concat", processing_tag_v, (0,))
    if result == 0:
        success = False
    photo_id_v = result

    if not success:
        return False

    if base.tags_of_photo(photo_id_h) != [processing_tag_h]:
        return False
    if base.tags_of_photo(photo_id_v) != [processing_tag_v]:
        return False

    return success

if __name__ == "__main__":
    total_pts = 0
    max_pts = 0
    for testname in tests:
        (test, full_pts) = tests[testname]
        pts = test()
        print("{}: {} / {} pt(s)".format(testname, pts, full_pts))
        max_pts += full_pts
        total_pts += pts

    print("----------------------------------------------------------------")
    print("total: {} / {} pts".format(total_pts, max_pts))
