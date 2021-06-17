import asyncio
import grpc
from . import _base_call
from ._call import (
    AioRpcError as AioRpcError,
    StreamStreamCall as StreamStreamCall,
    StreamUnaryCall as StreamUnaryCall,
    UnaryStreamCall as UnaryStreamCall,
    UnaryUnaryCall as UnaryUnaryCall
)
from ._metadata import Metadata as Metadata
from ._typing import (
    DeserializingFunction as DeserializingFunction,
    DoneCallbackType as DoneCallbackType,
    RequestIterableType as RequestIterableType,
    RequestType as RequestType,
    ResponseIterableType as ResponseIterableType,
    ResponseType as ResponseType,
    SerializingFunction as SerializingFunction
)
from abc import ABCMeta, abstractmethod
import grpc._cython.cygrpc as cygrpc
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Generic,
    Optional,
    Sequence,
    Union
)


class ServerInterceptor(metaclass=ABCMeta):
    @abstractmethod
    async def intercept_service(
        self,
        continuation: Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler[RequestType, ResponseType]]],
        handler_call_details: grpc.HandlerCallDetails
    ) -> grpc.RpcMethodHandler[RequestType, ResponseType]: ...


class ClientCallDetails(grpc.ClientCallDetails):
    method: str
    timeout: Optional[float]
    metadata: Optional[Metadata]
    credentials: Optional[grpc.CallCredentials]
    wait_for_ready: Optional[bool]


class ClientInterceptor(metaclass=ABCMeta): ...


class UnaryUnaryClientInterceptor(ClientInterceptor, metaclass=ABCMeta):
    @abstractmethod
    async def intercept_unary_unary(
        self,
        continuation: Callable[[ClientCallDetails, RequestType], UnaryUnaryCall[RequestType, ResponseType]],
        client_call_details: ClientCallDetails,
        request: RequestType
    ) -> Union[UnaryUnaryCall[RequestType, ResponseType], ResponseType]: ...


class UnaryStreamClientInterceptor(ClientInterceptor, metaclass=ABCMeta):
    @abstractmethod
    async def intercept_unary_stream(
        self,
        continuation: Callable[[ClientCallDetails, RequestType], UnaryStreamCall[RequestType, ResponseType]],
        client_call_details: ClientCallDetails,
        request: RequestType
    ) -> Union[ResponseIterableType, UnaryStreamCall[RequestType, ResponseType]]: ...


class StreamUnaryClientInterceptor(ClientInterceptor, metaclass=ABCMeta):
    @abstractmethod
    async def intercept_stream_unary(
        self,
        #BUG(@MHDANTE): The continuation of a stream-unary call should be Stream-Unary. This contracdicts the 
        # typing upstream in grpc/grpc, but I think that's a bug due to copy-pasting.
        continuation: Callable[[ClientCallDetails, RequestType], StreamUnaryCall[RequestType, ResponseType]], 
        client_call_details: ClientCallDetails,
        request_iterator: RequestIterableType
    ) -> StreamUnaryCall[RequestType, ResponseType]: ...


class StreamStreamClientInterceptor(ClientInterceptor, metaclass=ABCMeta):
    @abstractmethod
    async def intercept_stream_stream(
        self,
        #BUG(@MHDANTE): The continuation of a stream-unary call should be Stream-Unary. This contracdicts the 
        # typing upstream in grpc/grpc, but I think that's a bug due to copy-pasting.
        # Pending upstream here: https://github.com/grpc/grpc/pull/26500
        continuation: Callable[[ClientCallDetails, RequestType], StreamStreamCall[RequestType, ResponseType]],
        client_call_details: ClientCallDetails,
        request_iterator: RequestIterableType
    ) -> Union[ResponseIterableType, StreamStreamCall[RequestType, ResponseType]]: ...


class InterceptedCall:
    def __init__(self, interceptors_task: asyncio.Task[_base_call.Call]) -> None: ...

    def __del__(self) -> None: ...

    def cancel(self) -> bool: ...

    def cancelled(self) -> bool: ...

    def done(self) -> bool: ...

    def add_done_callback(self, callback: DoneCallbackType) -> None: ...

    def time_remaining(self) -> Optional[float]: ...

    async def initial_metadata(self) -> Optional[Metadata]: ...

    async def trailing_metadata(self) -> Optional[Metadata]: ...

    async def code(self) -> grpc.StatusCode: ...

    async def details(self) -> str: ...

    async def debug_error_string(self) -> Optional[str]: ...

    async def wait_for_connection(self) -> None: ...


class _InterceptedUnaryResponseMixin(Generic[ResponseType]):
    def __await__(self)-> Awaitable[ResponseType]: ...


class _InterceptedStreamResponseMixin(Generic[ResponseType]):
    def __aiter__(self) -> AsyncIterable[ResponseType]: ...

    async def read(self) -> ResponseType: ...


class _InterceptedStreamRequestMixin(Generic[RequestType]):
    async def write(self, request: RequestType) -> None: ...

    async def done_writing(self) -> None: ...


class InterceptedUnaryUnaryCall(_InterceptedUnaryResponseMixin[ResponseType],
                                InterceptedCall,
                                _base_call.UnaryUnaryCall[RequestType, ResponseType]):
    def __init__(
        self,
        interceptors: Sequence[UnaryUnaryClientInterceptor],
        request: RequestType,
        timeout: Optional[float],
        metadata: Metadata,
        credentials: Optional[grpc.CallCredentials],
        wait_for_ready: Optional[bool],
        channel: cygrpc.AioChannel,
        method: bytes,
        request_serializer: SerializingFunction[RequestType],
        response_deserializer: DeserializingFunction[ResponseType],
        loop: asyncio.AbstractEventLoop
    ) -> None: ...

    def time_remaining(self) -> Optional[float]: ...


class InterceptedUnaryStreamCall(_InterceptedStreamResponseMixin[ResponseType],
                                 InterceptedCall,
                                 _base_call.UnaryStreamCall[RequestType, ResponseType]):
    def __init__(
        self,
        interceptors: Sequence[UnaryStreamClientInterceptor],
        request: RequestType,
        timeout: Optional[float],
        metadata: Metadata,
        credentials: Optional[grpc.CallCredentials],
        wait_for_ready: Optional[bool],
        channel: cygrpc.AioChannel,
        method: bytes,
        request_serializer: SerializingFunction[RequestType],
        response_deserializer: DeserializingFunction[ResponseType],
        loop: asyncio.AbstractEventLoop
    ) -> None: ...

    def time_remaining(self) -> Optional[float]: ...


class InterceptedStreamUnaryCall(_InterceptedUnaryResponseMixin[ResponseType],
                                 _InterceptedStreamRequestMixin[RequestType],
                                 InterceptedCall,
                                 _base_call.StreamUnaryCall[RequestType, ResponseType]):
    def __init__(
        self,
        interceptors: Sequence[StreamUnaryClientInterceptor],
        request_iterator: Optional[RequestIterableType],
        timeout: Optional[float],
        metadata: Metadata,
        credentials: Optional[grpc.CallCredentials],
        wait_for_ready: Optional[bool],
        channel: cygrpc.AioChannel,
        method: bytes,
        request_serializer: SerializingFunction[RequestType],
        response_deserializer: DeserializingFunction[ResponseType],
        loop: asyncio.AbstractEventLoop
    ) -> None: ...

    def time_remaining(self) -> Optional[float]: ...


class InterceptedStreamStreamCall(_InterceptedStreamResponseMixin[ResponseType],
                                  _InterceptedStreamRequestMixin[RequestType],
                                  InterceptedCall,
                                  _base_call.StreamStreamCall[RequestType, ResponseType]):
    def __init__(
        self,
        interceptors: Sequence[StreamStreamClientInterceptor],
        request_iterator: Optional[RequestIterableType],
        timeout: Optional[float],
        metadata: Metadata,
        credentials: Optional[grpc.CallCredentials],
        wait_for_ready: Optional[bool],
        channel: cygrpc.AioChannel,
        method: bytes,
        request_serializer: SerializingFunction[RequestType],
        response_deserializer: DeserializingFunction[ResponseType], 
        loop: asyncio.AbstractEventLoop
    ) -> None: ...

    def time_remaining(self) -> Optional[float]: ...


class UnaryUnaryCallResponse(_base_call.UnaryUnaryCall[RequestType, ResponseType]):
    def __init__(self, response: ResponseType) -> None: ...

    def cancel(self) -> bool: ...

    def cancelled(self) -> bool: ...

    def done(self) -> bool: ...

    def add_done_callback(self, unused_callback: Any) -> None: ...

    def time_remaining(self) -> Optional[float]: ...

    async def initial_metadata(self) -> Optional[Metadata]: ...

    async def trailing_metadata(self) -> Optional[Metadata]: ...

    async def code(self) -> grpc.StatusCode: ...

    async def details(self) -> str: ...

    async def debug_error_string(self) -> Optional[str]: ...

    def __await__(self)-> Awaitable[ResponseType]: ...

    async def wait_for_connection(self) -> None: ...


class _StreamCallResponseIterator(Generic[ResponseType]):
    def __init__(
        self,
        call: Union[_base_call.UnaryStreamCall[Any, ResponseType], _base_call.StreamStreamCall[Any, ResponseType]],
        response_iterator: AsyncIterable[ResponseType]
    ) -> None: ...

    def cancel(self) -> bool: ...

    def cancelled(self) -> bool: ...

    def done(self) -> bool: ...

    def add_done_callback(self, callback: Any) -> None: ...

    def time_remaining(self) -> Optional[float]: ...

    async def initial_metadata(self) -> Optional[Metadata]: ...

    async def trailing_metadata(self) -> Optional[Metadata]: ...

    async def code(self) -> grpc.StatusCode: ...

    async def details(self) -> str: ...

    async def debug_error_string(self) -> Optional[str]: ...

    def __aiter__(self)->AsyncIterator[ResponseType]: ...

    async def wait_for_connection(self) -> None: ...


class UnaryStreamCallResponseIterator(_StreamCallResponseIterator[ResponseType],
                                      _base_call.UnaryStreamCall[RequestType, ResponseType]):
    async def read(self) -> ResponseType: ...


class StreamStreamCallResponseIterator(_StreamCallResponseIterator[ResponseType],
                                       _base_call.StreamStreamCall[RequestType, ResponseType]):
    async def read(self) -> ResponseType: ...

    async def write(self, request: RequestType) -> None: ...

    async def done_writing(self) -> None: ...
