# Operations

This page covers the full smbus2 API with code examples, organised by operation type.
All examples assume the following imports unless stated otherwise:

```python
from smbus2 import SMBus, i2c_msg, I2cFunc
```

---

## Opening and Closing the Bus

### By Bus Number

Pass the integer index of the I2C adapter.  `SMBus(1)` opens `/dev/i2c-1`.

```python
bus = SMBus(1)
# ... use bus ...
bus.close()
```

### By File Path

Since v0.3.0 the `bus` argument can also be a full device path
([#17](https://github.com/kplindegaard/smbus2/issues/17)):

```python
bus = SMBus('/dev/i2c-1')
bus.close()
```

### Using the Context Manager (Recommended)

The context manager ensures the bus is **always** closed, even when an exception occurs.
This is the preferred pattern:

```python
with SMBus(1) as bus:
    # bus is open here
    ...
# bus is automatically closed here
```

### Explicit open / close

If you need to open and close the bus multiple times within the same object's lifetime:

```python
bus = SMBus()      # not yet open
bus.open(1)        # open bus 1
# ... use bus ...
bus.close()
bus.open(1)        # re-open
# ...
bus.close()
```

---

## SMBus Read Operations

### `read_byte(addr)` — Read a byte without a register address

Reads a single byte from the device.  No register/offset is written first.

```python
with SMBus(1) as bus:
    value = bus.read_byte(0x50)
    print(value)
```

### `read_byte_data(addr, register)` — Read a byte from a register

Writes `register` to the device, then reads one byte back.

```python
with SMBus(1) as bus:
    value = bus.read_byte_data(0x50, 0x00)
    print(value)
```

### `read_word_data(addr, register)` — Read a 16-bit word from a register

Writes `register`, then reads two bytes.  The value is returned as a Python `int`.

```python
with SMBus(1) as bus:
    word = bus.read_word_data(0x50, 0x00)
    print(hex(word))
```

> **Note on endianness:** The SMBus spec transfers the low byte first (little-endian).
> The Linux kernel assembles the two bytes accordingly, so the returned integer matches
> the device datasheet for most sensors.  If your device uses big-endian word order, swap
> manually — see [[Tips and Tricks#endianness--byte-order-conversion]].

### `read_block_data(addr, register)` — Read an SMBus block

The device sends a length byte followed by up to 32 data bytes.  Returns a list.

```python
with SMBus(1) as bus:
    data = bus.read_block_data(0x50, 0x00)
    print(data)
```

> **Note:** This command is normally not supported by pure I2C devices that lack an
> SMBus-compliant block-read implementation.

### `read_i2c_block_data(addr, register, length)` — Read up to 32 bytes from a register

```python
with SMBus(1) as bus:
    # Read 16 bytes starting from register 0x00
    data = bus.read_i2c_block_data(0x50, 0x00, 16)
    print(data)  # list of 16 integers
```

> Maximum `length` is 32, as imposed by the Linux SMBus implementation.
> For larger transfers use [`i2c_rdwr`](#combined-transactions-with-i2c_rdwr).

---

## SMBus Write Operations

### `write_byte(addr, value)` — Write a byte without a register address

```python
with SMBus(1) as bus:
    bus.write_byte(0x50, 0xFF)
```

### `write_byte_data(addr, register, value)` — Write a byte to a register

```python
with SMBus(1) as bus:
    bus.write_byte_data(0x50, 0x00, 0x42)
```

### `write_word_data(addr, register, value)` — Write a 16-bit word to a register

```python
with SMBus(1) as bus:
    bus.write_word_data(0x50, 0x00, 0x1234)
```

### `write_block_data(addr, register, data)` — Write an SMBus block

```python
with SMBus(1) as bus:
    bus.write_block_data(0x50, 0x00, [1, 2, 3, 4])
```

### `write_i2c_block_data(addr, register, data)` — Write up to 32 bytes to a register

```python
with SMBus(1) as bus:
    data = [0x10, 0x20, 0x30, 0x40]
    bus.write_i2c_block_data(0x50, 0x00, data)
```

> Writing large blocks can be unreliable on some hardware.  If you observe errors, split
> the transfer into smaller chunks and add a short `time.sleep()` between them.

### `write_quick(addr)` — SMBus Quick Command

Sends the device address with the R/W bit only — no data byte.  Used to probe whether a
device is present ([#7](https://github.com/kplindegaard/smbus2/issues/7)).

```python
with SMBus(1) as bus:
    bus.write_quick(0x50)
```

---

## Combined Transactions with `i2c_rdwr`

`i2c_rdwr` performs one or more I2C messages in a **single kernel ioctl call** with
repeated-start semantics between messages (no STOP between them).  This enables two key
scenarios that standard SMBus commands cannot handle:

1. **Transfers larger than 32 bytes** — the SMBus block limit does not apply.
2. **Write-then-read in a single transaction** — the slave address is not released between
   the write phase and the read phase.

Each message is an `i2c_msg` object created with `i2c_msg.write()` or `i2c_msg.read()`.

> **Important:** `i2c_rdwr` has **no return value**.  Read data is stored in the
> `i2c_msg` object itself.  Access it via `list(msg)`, iteration, or `msg.buf`.

### Single write message

```python
with SMBus(1) as bus:
    msg = i2c_msg.write(0x50, [0x00, 0x01, 0x02])
    bus.i2c_rdwr(msg)
```

### Single read message

```python
with SMBus(1) as bus:
    msg = i2c_msg.read(0x50, 64)   # read 64 bytes
    bus.i2c_rdwr(msg)
    data = list(msg)               # convert to a Python list
    print(data)
```

### Dual message — write then read (repeated start)

```python
with SMBus(1) as bus:
    write = i2c_msg.write(0x50, [0x00])   # select register
    read  = i2c_msg.read(0x50, 2)          # read 2 bytes back
    bus.i2c_rdwr(write, read)
    data = list(read)
    print(data)
```

### Accessing `i2c_msg` data

```python
msg = i2c_msg.read(0x50, 4)
bus.i2c_rdwr(msg)

# Option 1: convert to list
data = list(msg)

# Option 2: iterate
for byte_val in msg:
    print(byte_val)

# Option 3: access via buf
for k in range(msg.len):
    print(msg.buf[k])
```

---

## PEC — Packet Error Checking

Enable PEC on the bus object before performing operations:

```python
with SMBus(1) as bus:
    bus.pec = 1                            # enable PEC
    value = bus.read_byte_data(0x50, 0x00)
    print(value)
```

Set `bus.pec = 0` to disable.  Not all I2C adapters and devices support PEC.

---

## Querying Adapter Capabilities

Use `bus.funcs` (an `I2cFunc` IntFlag) to check what the adapter supports:

```python
with SMBus(1) as bus:
    funcs = bus.funcs
    print(funcs)
```

### Notable `I2cFunc` flags

| Flag | Meaning |
|------|---------|
| `I2cFunc.I2C` | Adapter supports raw I2C (`i2c_rdwr`) |
| `I2cFunc.SMBUS_READ_BYTE` | `read_byte` supported |
| `I2cFunc.SMBUS_WRITE_BYTE` | `write_byte` supported |
| `I2cFunc.SMBUS_READ_BYTE_DATA` | `read_byte_data` supported |
| `I2cFunc.SMBUS_WRITE_BYTE_DATA` | `write_byte_data` supported |
| `I2cFunc.SMBUS_READ_WORD_DATA` | `read_word_data` supported |
| `I2cFunc.SMBUS_WRITE_WORD_DATA` | `write_word_data` supported |
| `I2cFunc.SMBUS_READ_BLOCK_DATA` | `read_block_data` supported |
| `I2cFunc.SMBUS_WRITE_BLOCK_DATA` | `write_block_data` supported |
| `I2cFunc.SMBUS_PEC` | PEC supported |
| `I2cFunc.ADDR_10BIT` | 10-bit addressing supported |

Example — check for 10-bit address support
([#64](https://github.com/kplindegaard/smbus2/issues/64)):

```python
with SMBus(1) as bus:
    if bus.funcs & I2cFunc.ADDR_10BIT:
        print("10-bit addressing is supported")
    else:
        print("10-bit addressing is NOT supported")
```

---

## Process Call and Block Process Call

### `process_call(addr, register, value)` — Write word, read word

Writes a 16-bit value to a register and reads a 16-bit result in a single transaction.

```python
with SMBus(1) as bus:
    result = bus.process_call(0x50, 0x01, 0x1234)
    print(hex(result))
```

### `block_process_call(addr, register, data)` — Write block, read block

Sends a block of bytes to a register and receives a block of bytes in return.

```python
with SMBus(1) as bus:
    response = bus.block_process_call(0x50, 0x02, [0xAA, 0xBB])
    print(response)
```

> **Note:** Block process call is normally not supported by pure I2C devices; it requires
> an SMBus-compliant implementation in the slave.
