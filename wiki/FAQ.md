# FAQ

Short answers to questions asked frequently in the issue tracker.

### Does smbus2 work on Windows or macOS?

No. smbus2 requires the Linux kernel's I2C character device subsystem (`/dev/i2c-*`)
and imports the Linux-only `fcntl` module.  Neither macOS nor Windows provides these.
See [#73](https://github.com/kplindegaard/smbus2/issues/73) and
[[Introduction#platform-support]].

### Can I read or write more than 32 bytes at once?

Not with the standard SMBus block commands (`read_i2c_block_data`,
`write_i2c_block_data`), which are capped at 32 bytes by the Linux SMBus implementation.
Use `i2c_rdwr` with `i2c_msg` objects for larger transfers — there is no fixed limit at
the smbus2 level for `i2c_rdwr`.
See [#35](https://github.com/kplindegaard/smbus2/issues/35),
[#67](https://github.com/kplindegaard/smbus2/issues/67),
[#99](https://github.com/kplindegaard/smbus2/issues/99), and
[[Operations#combined-transactions-with-i2c_rdwr]].

### How do I perform a repeated start (write then read without STOP)?

Use `bus.i2c_rdwr(write_msg, read_msg)` where both messages are `i2c_msg` objects.
A single `ioctl` call is made; the kernel inserts a repeated-start condition between the
two messages.
See [#25](https://github.com/kplindegaard/smbus2/issues/25) and
[[Tips and Tricks#write-then-read-repeated-start]].

### Can I use 10-bit I2C addresses?

smbus2 does not provide a dedicated 10-bit address API.  You can check whether the
adapter supports 10-bit addressing with `bus.funcs & I2cFunc.ADDR_10BIT`, but there is
no built-in convenience method for opening or sending to 10-bit addresses.
See [#54](https://github.com/kplindegaard/smbus2/issues/54).

### Why does my device not respond when I use `read_byte_data` or `write_byte_data`?

The `*_data` functions always prepend a write of the register/offset byte to every
transaction.  Devices that do not implement the SMBus register-addressing model are
confused by this extra write and may NAK the address or return wrong data.

Use `i2c_rdwr` with bare `i2c_msg` objects for such devices, or `write_byte` /
`read_byte` for single-byte commands.
See [#19](https://github.com/kplindegaard/smbus2/issues/19),
[#84](https://github.com/kplindegaard/smbus2/issues/84),
[#117](https://github.com/kplindegaard/smbus2/issues/117), and
[[Tips and Tricks#reading-devices-that-have-no-register-address]].

### Can I use smbus2 with asyncio?

Not directly — smbus2 is synchronous.  Options:

1. Wrap individual calls with `loop.run_in_executor` (simplest).
2. Use the community library **smbus2_asyncio**:
   <https://github.com/jabdoa2/smbus2_asyncio>.

See [#18](https://github.com/kplindegaard/smbus2/issues/18) and
[[Tips and Tricks#asyncio--async-support]].

### How do I set the I2C clock speed?

smbus2 does not control the clock speed.  Configure it via the Linux kernel — for
example, through a device-tree overlay on Raspberry Pi, or a kernel module parameter.
See [#77](https://github.com/kplindegaard/smbus2/issues/77) and
[[Tips and Tricks#setting-i2c-bus-clock-speed-baud-rate]].

### Can I open multiple `SMBus` instances for the same bus in one process?

It is not recommended.  Multiple open file descriptors on the same `/dev/i2c-N` can
lead to unexpected errors.  Share a single `SMBus` instance across your code; use a
`threading.Lock` if accessed from multiple threads.
See [#75](https://github.com/kplindegaard/smbus2/issues/75) and
[[Best Practices#do-not-create-multiple-smbus-instances-for-the-same-bus]].

### What happened to `SMBusWrapper`?

It was deprecated in v0.3.0 and removed in v0.4.0.  Replace it with `SMBus`, which
supports the same context-manager protocol (`with SMBus(1) as bus:`).
See [#78](https://github.com/kplindegaard/smbus2/issues/78) and
[[Installation#migrating-from-smbuswrapper]].

### How do I convert a raw unsigned value to a signed integer?

Use Python's `ctypes`:

```python
from ctypes import c_int8
signed = c_int8(bus.read_byte_data(addr, reg)).value
```

See [[Tips and Tricks#signed-integer-conversion]] for the full recipe including 16-bit
words.

### Where is the API documentation?

Full API documentation is hosted on Read the Docs:
<https://smbus2.readthedocs.io/en/latest/>
