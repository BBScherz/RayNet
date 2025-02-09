from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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

class UploadSceneRequest(_message.Message):
    __slots__ = ("scene_data", "filename")
    SCENE_DATA_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    scene_data: bytes
    filename: str
    def __init__(self, scene_data: _Optional[bytes] = ..., filename: _Optional[str] = ...) -> None: ...

class UploadSceneResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class RenderStatsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RenderStatsResponse(_message.Message):
    __slots__ = ("jobs_expected", "jobs_completed", "job_ids_pending", "job_ids_completed")
    JOBS_EXPECTED_FIELD_NUMBER: _ClassVar[int]
    JOBS_COMPLETED_FIELD_NUMBER: _ClassVar[int]
    JOB_IDS_PENDING_FIELD_NUMBER: _ClassVar[int]
    JOB_IDS_COMPLETED_FIELD_NUMBER: _ClassVar[int]
    jobs_expected: int
    jobs_completed: int
    job_ids_pending: _containers.RepeatedScalarFieldContainer[int]
    job_ids_completed: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, jobs_expected: _Optional[int] = ..., jobs_completed: _Optional[int] = ..., job_ids_pending: _Optional[_Iterable[int]] = ..., job_ids_completed: _Optional[_Iterable[int]] = ...) -> None: ...

class DownloadRenderedImageRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DownloadRenderedImageResponse(_message.Message):
    __slots__ = ("image_data", "rendering_complete")
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    RENDERING_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    image_data: bytes
    rendering_complete: bool
    def __init__(self, image_data: _Optional[bytes] = ..., rendering_complete: bool = ...) -> None: ...
