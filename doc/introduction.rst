Introduction
============

What is smbus2?
---------------

smbus2 is a pure-Python library that provides access to Linux I2C and SMBus peripherals.
It wraps the Linux kernel's I2C character device interface (``/dev/i2c-*``) through ``ioctl``
system calls, using Python's ``ctypes`` to map directly onto the kernel's SMBus and I2C data
structures. No compiled C extension is required — the package is 100% Python.

smbus2 was designed as a familiar drop-in replacement for the ``python-smbus`` /
``python3-smbus`` bindings that ship with many Linux distributions. The same method names
are preserved so that existing code can be migrated by changing a single import line:

.. code-block:: python

   # Before
   import smbus
   bus = smbus.SMBus(1)

   # After
   import smbus2
   bus = smbus2.SMBus(1)

Goals
-----

1. **Familiar API** — provide the same interface as the original ``smbus`` Python package so
   that the migration cost for existing users is minimal.
2. **Complete Linux I2C/SMBus functionality** — expose features that the original bindings
   lack, including combined read/write transactions (``i2c_rdwr``), Packet Error Checking
   (PEC), and all standard SMBus commands.

.. _platform-support:

Platform Support
----------------

smbus2 is a **Linux-only** library. It relies on the Linux kernel's I2C subsystem and the
``/dev/i2c-N`` character devices that it exposes. The underlying ``ioctl`` calls and data
structures (``i2c_smbus_ioctl_data``, ``i2c_rdwr_ioctl_data``, etc.) are Linux-specific.

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Platform
     - Supported
     - Notes
   * - Linux
     - ✅ Yes
     - Primary target; all features available
   * - macOS
     - ❌ No
     - Lacks the Linux I2C character device subsystem
   * - Windows
     - ❌ No
     - No ``fcntl`` module; no ``/dev/i2c-*`` devices (`#73 <https://github.com/kplindegaard/smbus2/issues/73>`_)

Tested Python Versions
-----------------------

smbus2 currently targets **Python 3.7 and later**. Python 2.7 and 3.6 are no longer
actively tested in CI (`#128 <https://github.com/kplindegaard/smbus2/issues/128>`_).
The test matrix explicitly covers Python 3.7 through 3.14.

Supported Hardware
------------------

Any Linux board or system that exposes an I2C adapter via ``/dev/i2c-N`` is supported.
Common examples include:

- Raspberry Pi (all models)
- NVIDIA Jetson Nano / Xavier
- BeagleBone Black / Green
- Orange Pi, Rock Pi, and other Allwinner / Rockchip SBCs
- Desktop / server systems with SMBus-capable chipsets
- Any embedded Linux board with ``CONFIG_I2C_CHARDEV`` enabled in the kernel

Supported SMBus / I2C Operations
---------------------------------

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Operation
     - Method
   * - Read byte (no register)
     - ``read_byte``
   * - Write byte (no register)
     - ``write_byte``
   * - Read byte from register
     - ``read_byte_data``
   * - Write byte to register
     - ``write_byte_data``
   * - Read word from register
     - ``read_word_data``
   * - Write word to register
     - ``write_word_data``
   * - Read I2C block
     - ``read_i2c_block_data``
   * - Write I2C block
     - ``write_i2c_block_data``
   * - Read SMBus block
     - ``read_block_data``
   * - Write SMBus block
     - ``write_block_data``
   * - Quick command
     - ``write_quick``
   * - Process call
     - ``process_call``
   * - Block process call
     - ``block_process_call``
   * - Combined write/read (repeated start)
     - ``i2c_rdwr``
   * - Packet Error Checking
     - ``bus.pec``
   * - Query adapter capabilities
     - ``bus.funcs`` / ``I2cFunc``

Relationship to ``python-smbus``
---------------------------------

smbus2 is intended to be a drop-in replacement for ``python-smbus``. All standard SMBus
method names are identical. The only required change in existing code is the import
statement (see example above). smbus2 additionally exposes ``i2c_rdwr``, PEC support,
``I2cFunc`` capability flags, and named-bus support — features that are absent from
``python-smbus``.

Further Reading
---------------

For the authoritative SMBus and I2C specifications, Linux kernel header definitions, and
related user-space tools, see :doc:`references`.
