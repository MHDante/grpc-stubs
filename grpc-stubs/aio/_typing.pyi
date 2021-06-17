from ._metadata import Metadata as Metadata, MetadataKey as MetadataKey, MetadataValue as MetadataValue
from typing import Any, AsyncIterable, Callable, Iterable, Sequence, Tuple, TypeVar, Union

RequestType = TypeVar('RequestType')
ResponseType = TypeVar('ResponseType')
SerializingFunction = Callable[[RequestType], bytes]
DeserializingFunction = Callable[[bytes], ResponseType]
MetadatumType = Tuple[MetadataKey, MetadataValue]
MetadataType = Metadata
ChannelArgumentType = Sequence[Tuple[str, Any]]
EOFType: Any
DoneCallbackType = Callable[[Any], None]
RequestIterableType = Union[Iterable[Any], AsyncIterable[Any]]
ResponseIterableType = AsyncIterable[Any]
