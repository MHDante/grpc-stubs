import grpc
from ._metadata import Metadata
from ._typing import DoneCallbackType, EOFType, RequestType, ResponseType
from abc import ABCMeta, abstractmethod
from typing import AsyncIterable, Awaitable, Generic, Optional, Union


class RpcContext(metaclass=ABCMeta):
    @abstractmethod
    def cancelled(self) -> bool: ...

    @abstractmethod
    def done(self) -> bool: ...

    @abstractmethod
    def time_remaining(self) -> Optional[float]: ...

    @abstractmethod
    def cancel(self) -> bool: ...

    @abstractmethod
    def add_done_callback(self, callback: DoneCallbackType) -> None: ...


class Call(RpcContext, metaclass=ABCMeta):

    # TODO(@MHDante): the return type of the next 2 methods is inconsistent with the implementation
    # typing, but is required in order to allow InterceptedCall to return optional Metadata.
    # Upstream changes proposed: https://github.com/grpc/grpc/pull/26499
    @abstractmethod
    async def initial_metadata(self) -> Optional[Metadata]: ...

    @abstractmethod
    async def trailing_metadata(self) -> Optional[Metadata]: ...

    @abstractmethod
    async def code(self) -> grpc.StatusCode: ...

    @abstractmethod
    async def details(self) -> str: ...

    @abstractmethod
    async def wait_for_connection(self) -> None: ...


class UnaryUnaryCall(Generic[RequestType, ResponseType], Call, metaclass=ABCMeta):
    @abstractmethod
    def __await__(self) -> Awaitable[ResponseType]: ...


class UnaryStreamCall(Generic[RequestType, ResponseType], Call, metaclass=ABCMeta):
    @abstractmethod
    def __aiter__(self) -> AsyncIterable[ResponseType]: ...

    @abstractmethod
    async def read(self) -> Union[EOFType, ResponseType]: ...


class StreamUnaryCall(Generic[RequestType, ResponseType], Call, metaclass=ABCMeta):
    @abstractmethod
    async def write(self, request: RequestType) -> None: ...

    @abstractmethod
    async def done_writing(self) -> None: ...

    @abstractmethod
    def __await__(self) -> Awaitable[ResponseType]: ...



class StreamStreamCall(Generic[RequestType, ResponseType], Call, metaclass=ABCMeta):
    @abstractmethod
    def __aiter__(self) -> AsyncIterable[ResponseType]: ...

    @abstractmethod
    async def read(self) -> Union[EOFType, ResponseType]: ...

    @abstractmethod
    async def write(self, request: RequestType) -> None: ...

    @abstractmethod
    async def done_writing(self) -> None: ...
