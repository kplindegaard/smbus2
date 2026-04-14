# Troubleshooting

Diagnose and fix common runtime errors. Entries are organised by error type.

## `OSError: [Errno 121] Remote I/O error`

**Cause:** The slave device did not acknowledge (ACK) the I2C address or a data byte.
This is almost always caused by:

- Incorrect wiring (SDA/SCL swapped, missing pull-up resistors).
- Wrong I2C device address.
- Wrong command sequence — e.g. sending a register byte to a device that does not
  expect one.
- Device not powered or not yet ready.

**Resolution:**

1. Verify wiring and confirm pull-up resistors are present on SDA and SCL (typically
   4.7 kΩ to 3.3 V or 5 V, depending on the bus voltage).
2. Scan for the device address: `i2cdetect -y 1` (replace `1` with your bus number).
3. Check the kernel log for driver-level messages:

   ```bash
   dmesg | grep -i i2c
   ```

4. If the device has no register-addressing concept, switch from `*_data` functions to
   `i2c_rdwr` — see {ref}`prefer-i2c-rdwr-for-devices-that-do-not-use-the-register-address-protocol`.
5. For devices like the AHT25/DHT20, use a write-then-read pattern
   ([#110](https://github.com/kplindegaard/smbus2/issues/110)):

   ```python
   write = i2c_msg.write(0x38, [0xac, 0x33, 0x00])
   read  = i2c_msg.read(0x38, 6)
   bus.i2c_rdwr(write, read)
   ```

## `OSError: [Errno 5] Input/output error`

**Cause:** A bus-level error — the slave NAK'd a data byte (not just the address),
electrical noise disrupted the transaction, or the master timed out waiting for clock
stretching to complete.

**Resolution:**

- Check pull-up resistor values (too high → marginal signalling).
- Reduce the I2C clock speed via the kernel driver (see
  {ref}`setting-i2c-bus-clock-speed-baud-rate`).
- Add a small delay between operations — see
  {ref}`add-small-delays-between-operations-on-slow-devices`.
- Check `dmesg | grep i2c` for `sendbytes: NAK bailout` messages
  ([#110](https://github.com/kplindegaard/smbus2/issues/110)).

## `ModuleNotFoundError: No module named 'fcntl'`

**Cause:** `fcntl` is a Linux-only standard library module. smbus2 imports it at
startup and will fail with this error on Windows or macOS
([#73](https://github.com/kplindegaard/smbus2/issues/73)).

**Resolution:** smbus2 **only runs on Linux**. There is no supported workaround for
other operating systems. If you need I2C access on macOS or Windows, consider hardware
bridges such as CP2112 or MCP2221 with their respective vendor Python libraries.

## `SystemError: buffer overflow` (Python 3.14+)

**Cause:** On Python 3.14+ running on 64-bit systems, the `I2C_FUNCS` ioctl used
`c_uint32` for the output buffer, which is too small for 64-bit kernels, causing a
buffer overflow
([#124](https://github.com/kplindegaard/smbus2/issues/124)).

**Resolution:** Upgrade smbus2 to **v0.6.0 or later**. The fix changes the internal
`c_uint32` to `c_ulong`, which matches the kernel's expected buffer size.

```bash
pip install --upgrade smbus2
```

## Reads Return Unexpected Values or Incorrect Data

**Possible causes and resolutions:**

- **Wiring** — check connections; poor contact or loose wires cause intermittent errors.
- **Wrong address** — run `i2cdetect -y 1` to confirm the device address.
- **Wrong byte count** — some devices return a length byte as the first byte of a block
  read; the actual data starts at index 1
  ([#68](https://github.com/kplindegaard/smbus2/issues/68)).
- **Register-byte confusion** — if the device does not use register addressing, the
  `*_data` functions send an unwanted write before the read, corrupting device state.
  Use `i2c_rdwr` instead
  ([#115](https://github.com/kplindegaard/smbus2/issues/115),
  [#101](https://github.com/kplindegaard/smbus2/issues/101)).
- **Endianness** — the word may be big-endian; see {ref}`endianness-byte-order-conversion`.
- **Signed vs. unsigned** — all values are returned unsigned; convert with `ctypes` if
  needed; see {ref}`signed-integer-conversion`.

## Very Slow Reads (`read_byte_data`, `read_i2c_block_data`)

**Cause:** smbus2 itself adds negligible overhead. Slowness is almost always caused by:

- The Linux kernel I2C driver (clock speed, scheduling latency).
- Clock stretching by the slave device holding SCL low.
- A driver bound to the device blocking the `ioctl` call
  ([#76](https://github.com/kplindegaard/smbus2/issues/76),
  [#108](https://github.com/kplindegaard/smbus2/issues/108)).

**Resolution:**

- Try `force=True` on the call if a kernel driver is already bound to the device
  address (use with caution — bypasses driver safety).
- Reduce the I2C clock speed so the device has more time per bit.
- For high-throughput scenarios consider batching reads with `i2c_rdwr`.
