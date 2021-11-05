#!/usr/bin/env python3

import sys
import traceback
from typing import Callable, Sequence, Any

from wasmer import engine, Store, Module, ImportObject, Function, FunctionType, Type, Instance, Memory, MemoryType, GlobalType
from wasmer_compiler_cranelift import Compiler

import clientdb

def wrap_finally(f):
    def g(*args):
        try:
            return f(*args)
        finally:
            if sys.exc_info() != (None, None, None):
                traceback.print_exc()
    return g

# aliases for documentation
WasmPointer = int
WasmUint32 = int

class ProgramSandbox:
    """A ProgramSandbox encapsulates a guest WebAssembly Instance, giving it access
    to a Photobase according to a given permissions_tag."""
    def __init__(self,
                 store: Store, module: Module,
                 base: clientdb.Photobase, permissions_tag: str):
        imports = ImportObject()
        imports.register("env", {
            "list_photo_ids": Function(store, self.list_photo_ids, _fntype_helper(2)),
            "photo_width": Function(store, self.photo_width, _fntype_helper(1)),
            "photo_height": Function(store, self.photo_height, _fntype_helper(1)),
            "read_photo": Function(store, self.read_photo, _fntype_helper(3)),
            "write_photo": Function(store, self.write_photo, _fntype_helper(4)),
        })
        self.instance = Instance(module, imports)
        self.db = base
        self.tag = permissions_tag

    def execute(self, entry_point_name: str, *args: Sequence) -> Callable:
        """execute launches the Module, given an entry point into the instance
        and a list of arguments."""
        return self.instance.exports.__getattribute__(entry_point_name)(*args)
        try:
            return self.instance.exports.__getattribute__(entry_point_name)(*args)
        except RuntimeError:
            traceback.print_exc()
            return


    @wrap_finally
    def list_photo_ids(self,
                       limit: WasmUint32,
                       photo_ids_ptr: WasmPointer) -> WasmUint32:
        """list_photo_ids lists all the photo IDs the guest has access to
        given its permissions tag.

        limit is the maximum number of photo IDs to return.
        photo_ids_ptr marks the start of the array containing the photo IDs.
        The returned value is the total number of accessible photo IDs.
        """
        return 0


    @wrap_finally
    def photo_width(self, photo_id: WasmUint32) -> WasmUint32:
        """photo_width gives the width of a photo with the given ID.

        photo_id is the ID of the requested photo.
        The returned value is the photo's width.  If no such photo exists,
        0 is returned.
        """
        return 0


    @wrap_finally
    def photo_height(self, photo_id: WasmUint32) -> WasmUint32:
        """photo_height gives the height of a photo with the given ID.

        photo_id is the ID of the requested photo.
        The returned value is the photo's height.  If no such photo exists,
        0 is returned.
        """
        return 0


    @wrap_finally
    def read_photo(self, photo_id: WasmUint32,
                   limit: WasmUint32,
                   photo_data_ptr: WasmPointer) -> WasmUint32:
        """read_photo fills a pixel array with photo data for the guest.

        photo_id is the ID of the requested photo.
        limit is the maximum number of pixels to write.
        photo_data marks the start of the array containing the photo data.
        The returned value is the number of pixels written.  If no such photo
        exists, 0 is returned.
        """
        return 0


    @wrap_finally
    def write_photo(self, photo_id: WasmUint32,
                    width: WasmUint32, height: WasmUint32,
                    photo_data_ptr: WasmPointer) -> WasmUint32:
        """write_photo saves a photo with some ID for the guest.

        photo_id is the ID of the target photo.  If 0 is given, a new photo
        is instead created with the Instance's tag.
        width is the photo's width.
        height is the photo's height.
        The returned value is the ID of the written photo.  If the write
        failed, 0 is returned.
        """
        return 0


def _fntype_helper(n: int) -> FunctionType:
    inputs = [Type.I32] * n
    output = [Type.I32]
    return FunctionType(inputs, output)

class PhotoEditingProgram:
    """A PhotoEditingProgram encapsulates a single WebAssembly Store, loading
    the single Module corresponding to the given binary filename."""
    def __init__(self, wasm_fname: str):
        with open(wasm_fname, "rb") as f:
            self.binary = f.read()
        self.store = Store(engine.JIT(Compiler))
        self.module = Module(self.store, self.binary)

    def new_sandboxed_instance(self, base: clientdb.Photobase, permissions_tag: str) -> ProgramSandbox:
        """new_sandboxed_instance prepares a new sandboxed Instance of the Module."""
        return ProgramSandbox(self.store, self.module, base, permissions_tag)
