# Best Practices

Following these patterns will make your I2C code more reliable, easier to maintain, and
less prone to subtle bugs.

## Always Use the Context Manager

The `with SMBus(...) as bus:` pattern ensures the bus file descriptor is **always**
closed when the block exits, even if an exception is raised.  Unclosed file descriptors
can prevent other processes from accessing the bus.

```python
# Preferred
with SMBus(1) as bus:
    value = bus.read_byte_data(0x50, 0x00)

# Avoid — bus may not be closed if an exception occurs
bus = SMBus(1)
value = bus.read_byte_data(0x50, 0x00)
bus.close()
```

## Do Not Create Multiple `SMBus` Instances for the Same Bus

Linux serialises I2C transactions at the kernel level, but having multiple open file
descriptors for the same `/dev/i2c-N` device can lead to confusing errors and unexpected
interleaving of operations
([#75](https://github.com/kplindegaard/smbus2/issues/75)).

If multiple parts of your application need bus access, share a **single** `SMBus`
instance.  Protect it with a `threading.Lock` if accessed from multiple threads:

```python
import threading
from smbus2 import SMBus

_bus_lock = threading.Lock()
_bus = SMBus(1)

def safe_read(addr, register):
    with _bus_lock:
        return _bus.read_byte_data(addr, register)
```

## Prefer `i2c_rdwr` for Devices That Do Not Use the Register-Address Protocol

Several SMBus `*_data` functions (e.g. `read_byte_data`, `write_byte_data`,
`read_i2c_block_data`) **always send a register/offset byte before the data payload**.
This matches the SMBus specification but is wrong for I2C devices that have no register
concept — the spurious write of the register byte will corrupt the device's state or
trigger an error
([#19](https://github.com/kplindegaard/smbus2/issues/19),
[#110](https://github.com/kplindegaard/smbus2/issues/110)).

For such devices, use `i2c_rdwr` with bare `i2c_msg` objects:

```python
from smbus2 import SMBus, i2c_msg

with SMBus(1) as bus:
    # Read 3 bytes — no register byte is sent
    msg = i2c_msg.read(0x38, 3)
    bus.i2c_rdwr(msg)
    data = list(msg)
```

## Use `i2c_rdwr` to Bypass the 32-Byte SMBus Limit

The Linux SMBus implementation caps block transfers at 32 bytes.  If your device
supports longer I2C transfers, `i2c_rdwr` is the only way to exceed that limit
([#35](https://github.com/kplindegaard/smbus2/issues/35),
[#67](https://github.com/kplindegaard/smbus2/issues/67),
[#99](https://github.com/kplindegaard/smbus2/issues/99)):

```python
with SMBus(1) as bus:
    msg = i2c_msg.read(0x50, 64)   # 64 bytes — impossible with read_i2c_block_data
    bus.i2c_rdwr(msg)
    data = list(msg)
```

## Add Small Delays Between Operations on Slow Devices

Some I2C devices need processing time after receiving a command before they can accept
the next one.  If you observe intermittent `OSError` or incorrect data in a tight loop,
insert a short `time.sleep()` between operations
([#33](https://github.com/kplindegaard/smbus2/issues/33),
[#36](https://github.com/kplindegaard/smbus2/issues/36)):

```python
import time
from smbus2 import SMBus

with SMBus(1) as bus:
    bus.write_byte_data(0x50, 0x00, 0x01)
    time.sleep(0.05)   # give the device 50 ms to process
    result = bus.read_byte_data(0x50, 0x00)
```

The required delay varies by device; consult the datasheet.

## Prefer `write_byte` / `read_byte` for Devices With No Register Concept

For devices that accept a single command byte or return a single byte without any
register addressing, use `write_byte` / `read_byte`.  Unlike the `*_data` variants,
these functions do **not** prepend a register/offset byte to the transaction:

```python
with SMBus(1) as bus:
    bus.write_byte(0x40, 0xAC)        # send command 0xAC
    response = bus.read_byte(0x40)    # read one byte response
```

## Handle `OSError` Gracefully

All smbus2 operations raise `OSError` when the kernel reports an I2C error.  The `errno`
attribute identifies the specific cause:

| `errno` | Meaning |
|---------|---------|
| 5 (`EIO`) | Input/output error — bus-level failure, noise, or NAK |
| 121 (`EREMOTEIO`) | Remote I/O error — slave did not ACK the address or command |
| 16 (`EBUSY`) | Bus busy — another master or driver is using the bus |

```python
import errno
from smbus2 import SMBus

with SMBus(1) as bus:
    try:
        value = bus.read_byte_data(0x50, 0x00)
    except OSError as exc:
        if exc.errno == errno.EREMOTEIO:   # 121
            print("Device not responding — check wiring and address")
        else:
            print(f"I2C error: {exc}")
        raise
```
