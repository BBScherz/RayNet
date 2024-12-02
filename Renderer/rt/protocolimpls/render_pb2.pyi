from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetJobRequest(_message.Message):
    __slots__ = ("project_id",)
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: int
    def __init__(self, project_id: _Optional[int] = ...) -> None: ...

class GetCurrentSceneRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCurrentSceneResponse(_message.Message):
    __slots__ = ("scene_data",)
    SCENE_DATA_FIELD_NUMBER: _ClassVar[int]
    scene_data: bytes
    def __init__(self, scene_data: _Optional[bytes] = ...) -> None: ...

class Coordinate(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class Rectangle(_message.Message):
    __slots__ = ("lower_left", "upper_right")
    LOWER_LEFT_FIELD_NUMBER: _ClassVar[int]
    UPPER_RIGHT_FIELD_NUMBER: _ClassVar[int]
    lower_left: Coordinate
    upper_right: Coordinate
    def __init__(self, lower_left: _Optional[_Union[Coordinate, _Mapping]] = ..., upper_right: _Optional[_Union[Coordinate, _Mapping]] = ...) -> None: ...

class GetJobResponse(_message.Message):
    __slots__ = ("image_coordinates_to_render", "job_id")
    IMAGE_COORDINATES_TO_RENDER_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    image_coordinates_to_render: Rectangle
    job_id: int
    def __init__(self, image_coordinates_to_render: _Optional[_Union[Rectangle, _Mapping]] = ..., job_id: _Optional[int] = ...) -> None: ...

class HeartbeatRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HeartbeatResponse(_message.Message):
    __slots__ = ("alive",)
    ALIVE_FIELD_NUMBER: _ClassVar[int]
    alive: bool
    def __init__(self, alive: bool = ...) -> None: ...

class ComputationStatistics(_message.Message):
    __slots__ = ("time_seconds", "pixels_rendered")
    TIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    PIXELS_RENDERED_FIELD_NUMBER: _ClassVar[int]
    time_seconds: float
    pixels_rendered: int
    def __init__(self, time_seconds: _Optional[float] = ..., pixels_rendered: _Optional[int] = ...) -> None: ...

class JobCompleteRequest(_message.Message):
    __slots__ = ("render_chunk", "job_id", "stats")
    RENDER_CHUNK_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    render_chunk: bytes
    job_id: int
    stats: ComputationStatistics
    def __init__(self, render_chunk: _Optional[bytes] = ..., job_id: _Optional[int] = ..., stats: _Optional[_Union[ComputationStatistics, _Mapping]] = ...) -> None: ...

class JobCompleteResponse(_message.Message):
    __slots__ = ("acknowledged",)
    ACKNOWLEDGED_FIELD_NUMBER: _ClassVar[int]
    acknowledged: bool
    def __init__(self, acknowledged: bool = ...) -> None: ...
