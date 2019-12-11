from enum import IntFlag
from typing import Any, Optional, Sequence, List, Type
from typing import Union as _UnionT
from types import TracebackType
from ctypes import c_uint32, c_uint8, c_uint16, pointer, Structure, Array, Union

I2C_SLAVE: int
I2C_SLAVE_FORCE: int
I2C_FUNCS: int
I2C_RDWR: int
I2C_SMBUS: int
I2C_SMBUS_WRITE: int
I2C_SMBUS_READ: int
I2C_SMBUS_QUICK: int
I2C_SMBUS_BYTE: int
I2C_SMBUS_BYTE_DATA: int
I2C_SMBUS_WORD_DATA: int
I2C_SMBUS_PROC_CALL: int
I2C_SMBUS_BLOCK_DATA: int
I2C_SMBUS_BLOCK_PROC_CALL: int
I2C_SMBUS_I2C_BLOCK_DATA: int
I2C_SMBUS_BLOCK_MAX: int

class I2cFunc(IntFlag):
    I2C = ...
    ADDR_10BIT = ...
    PROTOCOL_MANGLING = ...
    SMBUS_PEC = ...
    NOSTART = ...
    SLAVE = ...
    SMBUS_BLOCK_PROC_CALL = ...
    SMBUS_QUICK = ...
    SMBUS_READ_BYTE = ...
    SMBUS_WRITE_BYTE = ...
    SMBUS_READ_BYTE_DATA = ...
    SMBUS_WRITE_BYTE_DATA = ...
    SMBUS_READ_WORD_DATA = ...
    SMBUS_WRITE_WORD_DATA = ...
    SMBUS_PROC_CALL = ...
    SMBUS_READ_BLOCK_DATA = ...
    SMBUS_WRITE_BLOCK_DATA = ...
    SMBUS_READ_I2C_BLOCK = ...
    SMBUS_WRITE_I2C_BLOCK = ...
    SMBUS_HOST_NOTIFY = ...
    SMBUS_BYTE = ...
    SMBUS_BYTE_DATA = ...
    SMBUS_WORD_DATA = ...
    SMBUS_BLOCK_DATA = ...
    SMBUS_I2C_BLOCK = ...
    SMBUS_EMUL = ...

I2C_M_RD: int
LP_c_uint8: Type[pointer[c_uint8]]
LP_c_uint16: Type[pointer[c_uint16]]
LP_c_uint32: Type[pointer[c_uint32]]

class i2c_smbus_data(Array): ...
class union_i2c_smbus_data(Union): ...

union_pointer_type: pointer[union_i2c_smbus_data]

class i2c_smbus_ioctl_data(Structure):
    @staticmethod
    def create(
        read_write: int = ..., command: int = ..., size: int = ...
    ) -> "i2c_smbus_ioctl_data": ...

class i2c_msg(Structure):
    def __iter__(self) -> int: ...
    def __len__(self) -> int: ...
    def __bytes__(self) -> str: ...
    @staticmethod
    def read(address: int, length: int) -> "i2c_msg": ...
    @staticmethod
    def write(address: int, buf: list) -> "i2c_msg": ...

class i2c_rdwr_ioctl_data(Structure):
    @staticmethod
    def create(*i2c_msg_instances: Sequence[i2c_msg]) -> "i2c_rdwr_ioctl_data": ...

class SMBus:
    fd: int = ...
    funcs: I2cFunc = ...
    address: Optional[int] = ...
    force: Optional[bool] = ...
    def __init__(
        self, bus: _UnionT[None, int, str] = ..., force: bool = ...
    ) -> None: ...
    def __enter__(self) -> "SMBus": ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None: ...
    def open(self, bus: _UnionT[int, str]) -> None: ...
    def close(self) -> None: ...
    def write_quick(self, i2c_addr: int, force: Optional[bool] = ...) -> None: ...
    def read_byte(self, i2c_addr: int, force: Optional[bool] = ...) -> int: ...
    def write_byte(
        self, i2c_addr: int, value: int, force: Optional[bool] = ...
    ) -> None: ...
    def read_byte_data(
        self, i2c_addr: int, register: int, force: Optional[bool] = ...
    ) -> int: ...
    def write_byte_data(
        self, i2c_addr: int, register: int, value: int, force: Optional[bool] = ...
    ) -> None: ...
    def read_word_data(
        self, i2c_addr: int, register: int, force: Optional[bool] = ...
    ) -> int: ...
    def write_word_data(
        self, i2c_addr: int, register: int, value: int, force: Optional[bool] = ...
    ) -> None: ...
    def process_call(
        self, i2c_addr: int, register: int, value: int, force: Optional[bool] = ...
    ): ...
    def read_block_data(
        self, i2c_addr: int, register: int, force: Optional[bool] = ...
    ) -> List[int]: ...
    def write_block_data(
        self,
        i2c_addr: int,
        register: int,
        data: Sequence[int],
        force: Optional[bool] = ...,
    ) -> None: ...
    def block_process_call(
        self,
        i2c_addr: int,
        register: int,
        data: Sequence[int],
        force: Optional[bool] = ...,
    ) -> List[int]: ...
    def read_i2c_block_data(
        self, i2c_addr: int, register: int, length: int, force: Optional[bool] = ...
    ) -> List[int]: ...
    def write_i2c_block_data(
        self,
        i2c_addr: int,
        register: int,
        data: Sequence[int],
        force: Optional[bool] = ...,
    ) -> None: ...
    def i2c_rdwr(self, *i2c_msgs: i2c_msg) -> None: ...

class SMBusWrapper:
    bus_number: int = ...
    auto_cleanup: bool = ...
    force: bool = ...
    bus: SMBus = ...
    def __init__(
        self, bus_number: int = ..., auto_cleanup: bool = ..., force: bool = ...
    ) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None: ...
