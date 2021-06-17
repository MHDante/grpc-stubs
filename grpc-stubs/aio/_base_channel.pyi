import abc
import grpc
from . import _base_call
from ._metadata import Metadata as Metadata
from ._typing import (
    DeserializingFunction,
    RequestIterableType,
    SerializingFunction,
    RequestType,
    ResponseType
)
from typing import Any, Generic, Optional


class UnaryUnaryMultiCallable(Generic[RequestType, ResponseType],abc.ABC, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(
        self,
        request: Any,
        *,
        timeout: Optional[float]=...,
        metadata: Optional[Metadata]=...,
        credentials: Optional[grpc.CallCredentials]=...,
        wait_for_ready: Optional[bool]=...,
        compression: Optional[grpc.Compression]=...
    ) -> _base_call.UnaryUnaryCall[RequestType, ResponseType]: ...


class UnaryStreamMultiCallable(Generic[RequestType, ResponseType], abc.ABC, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(
        self, 
        request: Any,
        *,
        timeout: Optional[float]=...,
        metadata: Optional[Metadata]=...,
        credentials: Optional[grpc.CallCredentials]=...,
        wait_for_ready: Optional[bool]=...,
        compression: Optional[grpc.Compression]=...
    ) -> _base_call.UnaryStreamCall[RequestType, ResponseType]: ...


class StreamUnaryMultiCallable(Generic[RequestType, ResponseType], abc.ABC, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(
        self,
        request_iterator: Optional[RequestIterableType]=...,
        timeout: Optional[float]=...,
        metadata: Optional[Metadata]=...,
        credentials: Optional[grpc.CallCredentials]=...,
        wait_for_ready: Optional[bool]=...,
        compression: Optional[grpc.Compression]=...
    ) -> _base_call.StreamUnaryCall[RequestType, ResponseType]: ...


class StreamStreamMultiCallable(Generic[RequestType, ResponseType], abc.ABC, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(
        self,
        request_iterator: Optional[RequestIterableType]=...,
        timeout: Optional[float]=...,
        metadata: Optional[Metadata]=...,
        credentials: Optional[grpc.CallCredentials]=...,
        wait_for_ready: Optional[bool]=...,
        compression: Optional[grpc.Compression]=...
    ) -> _base_call.StreamStreamCall[RequestType, ResponseType]: ...


class Channel(abc.ABC, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def __aenter__(self) -> Any: ...

    @abc.abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any: ...

    @abc.abstractmethod
    async def close(self, grace: Optional[float]=...) -> Any: ...

    @abc.abstractmethod
    def get_state(self, try_to_connect: bool=...) -> grpc.ChannelConnectivity: ...

    @abc.abstractmethod
    async def wait_for_state_change(
        self,
        last_observed_state: grpc.ChannelConnectivity
    ) -> None: ...

    @abc.abstractmethod
    async def channel_ready(self) -> None: ...

    @abc.abstractmethod
    def unary_unary(
        self,
        method: str,
        request_serializer: Optional[SerializingFunction[RequestType]]=...,
        response_deserializer: Optional[DeserializingFunction[ResponseType]]=...
    ) -> UnaryUnaryMultiCallable[RequestType, ResponseType]: ...

    @abc.abstractmethod
    def unary_stream(
        self,
        method: str,
        request_serializer: Optional[SerializingFunction[RequestType]]=...,
        response_deserializer: Optional[DeserializingFunction[ResponseType]]=...
    ) -> UnaryStreamMultiCallable[RequestType, ResponseType]: ...

    @abc.abstractmethod
    def stream_unary(
        self,
        method: str,
        request_serializer: Optional[SerializingFunction[RequestType]]=...,
        response_deserializer: Optional[DeserializingFunction[ResponseType]]=...
    ) -> StreamUnaryMultiCallable[RequestType, ResponseType]: ...

    @abc.abstractmethod
    def stream_stream(
        self,
        method: str,
        request_serializer: Optional[SerializingFunction[RequestType]]=...,
        response_deserializer: Optional[DeserializingFunction[ResponseType]]=...
    ) -> StreamStreamMultiCallable[RequestType, ResponseType]: ...
