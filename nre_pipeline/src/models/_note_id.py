# from typing import Generic, TypeVar

# NoteIdType = TypeVar("NoteIdType", int, str)


# class NoteId(Generic[NoteIdType]):

#     def __init__(self, id: NoteIdType) -> None:
#         super().__init__()
#         self._id: NoteIdType = id

#     def __str__(self) -> str:
#         """Return string representation of the ID."""
#         return str(self._id)

#     def __repr__(self) -> str:
#         """Return detailed string representation."""
#         return f"NoteId({self._id!r})"

#     def __eq__(self, other) -> bool:
#         """Compare with another NoteId or with the underlying type."""
#         if isinstance(other, NoteId):
#             return self._id == other._id
#         return self._id == other

#     def __hash__(self) -> int:
#         """Make NoteId hashable."""
#         return hash(self._id)

#     def __int__(self) -> int:
#         """Convert to int if underlying type supports it."""
#         return int(self._id)

#     def __format__(self, format_spec: str) -> str:
#         """Support format strings."""
#         return format(self._id, format_spec)

#     @property
#     def value(self) -> NoteIdType:
#         """Access the underlying value."""
#         return self._id
