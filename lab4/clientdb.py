#!/usr/bin/env python3

from typing import Sequence
from copy import deepcopy

# aliases for documentation
Uint32 = int

class Photo:
    def __init__(self, width: Uint32, height: Uint32, data: Sequence[Uint32]):
        self.width = width
        self.height = height
        self.data = data
    def __str__(self) -> str:
        return "Photo({}, {}, {})".format(self.width, self.height, self.data)
    def __eq__(self, other) -> bool:
        if self.width != other.width:
            return False
        if self.height != other.height:
            return False
        return self.data == other.data

class Photobase:
    def __init__(self):
        self._next_photo_id = 1

        # photo_id -> Photo
        self._photos = {}
        # photo_id -> bool
        self._read_only = {}
        # photo_id -> [tag]
        self._tags = {}

    def _allocate_photo_id(self) -> Uint32:
        """_allocate_photo_id generates the next sequential photo ID."""
        assigned = self._next_photo_id
        self._next_photo_id += 1
        return assigned

    def add_photo(self, photo: Photo, read_only: bool) -> Uint32:
        """add_photo adds the given photo to the database and returns the assigned photo ID."""
        next_id = self._allocate_photo_id()

        self._photos[next_id] = deepcopy(photo)
        self._read_only[next_id] = read_only
        self._tags[next_id] = []

        return next_id

    def all_photo_ids(self) -> Sequence[Uint32]:
        """all_photo_ids returns a list of all photo IDs."""
        return self._photos.keys()

    def photo_with_id(self, photo_id: Uint32) -> Photo:
        """photo_with_id gets the photo associated with the given ID."""
        return deepcopy(self._photos[photo_id])

    def assign_photo_to_id(self, photo_id: Uint32, photo: Photo):
        """assign_photo_to_id sets the contents of the database under photo_id to be photo"""
        self._photos[photo_id] = photo

    def photo_writable(self, photo_id: Uint32) -> bool:
        """photo_writable returns a bit indicating whether a photo can be modified."""
        return not self._read_only[photo_id]

    def add_tag_to_photo(self, photo_id: Uint32, tag: str):
        """add_tag_to_photo associates a photo with a given tag."""
        self._tags[photo_id].append(tag)

    def tags_of_photo(self, photo_id: Uint32) -> Sequence[str]:
        """tags_of_photo gets the tags associated with a given photo."""
        return deepcopy(self._tags[photo_id])
