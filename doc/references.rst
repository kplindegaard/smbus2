References
==========

This page collects the authoritative technical documents, Linux kernel sources, and
related tools that underpin smbus2. They are useful background reading when you need
to understand what happens at the protocol or kernel level.

SMBus Protocol Specification
-----------------------------

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Document
     - Description
   * - `System Management Bus (SMBus) Specification, Version 3.2 (2021) <https://smbus.org/specs/SMBus_3_2_20220112.pdf>`_
     - The primary SMBus protocol specification published by the SBS Implementers Forum.
       Defines the electrical characteristics, command set (Quick Command, Send/Receive Byte,
       Read/Write Byte Data, Word Data, Block Data, Process Call, Block Process Call, Host Notify),
       Packet Error Checking (PEC), and Address Resolution Protocol (ARP).
   * - `SMBus specification archive at smbus.org <https://smbus.org/specs/>`_
     - Index of all published SMBus specification revisions (1.0 through 3.2) for historical reference.

I²C Specification
-----------------

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Document
     - Description
   * - `UM10204 — I²C-bus specification and user manual, Rev. 7.0 (2021) <https://www.nxp.com/docs/en/user-guide/UM10204.pdf>`_
     - The authoritative NXP/Philips I²C specification. Defines the physical layer, START/STOP
       conditions, repeated-start, clock stretching, 7-bit and 10-bit addressing, and multi-master
       arbitration.

Linux Kernel I2C / SMBus Documentation
---------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Document
     - Description
   * - `Linux I2C subsystem documentation <https://www.kernel.org/doc/html/latest/i2c/index.html>`_
     - Top-level index for the Linux kernel's ``Documentation/i2c/`` tree, covering the I2C
       subsystem from both a device-driver and user-space perspective.
   * - `Implementing I2C device drivers in user-space <https://www.kernel.org/doc/html/latest/i2c/dev-interface.html>`_
     - Describes ``/dev/i2c-N``, the ``ioctl`` interface (``I2C_RDWR``, ``I2C_SMBUS``,
       ``I2C_FUNCS``, ``I2C_SLAVE``, ``I2C_SLAVE_FORCE``, ``I2C_PEC``, ``I2C_TENBIT``),
       and how user-space programs should use them — this is the exact interface smbus2 wraps.
   * - `SMBus protocol summary in the kernel docs <https://www.kernel.org/doc/html/latest/i2c/smbus-protocol.html>`_
     - Kernel-side summary of every SMBus transaction type and the corresponding ``ioctl``
       arguments used by the in-kernel SMBus layer.
   * - `Fault codes returned by the I2C/SMBus layer <https://www.kernel.org/doc/html/latest/i2c/fault-codes.html>`_
     - Documents the ``errno`` values that the kernel I2C subsystem can return — helpful when
       interpreting ``OSError`` exceptions raised by smbus2.
   * - `I2C / SMBus Functionality Flags <https://www.kernel.org/doc/html/latest/i2c/functionality.html>`_
     - Explains the ``I2C_FUNCS`` flags (read via ``bus.funcs`` / ``I2cFunc`` in smbus2) and
       which flags correspond to which operations.
   * - `10-bit I2C addressing <https://www.kernel.org/doc/html/latest/i2c/ten-bit-addresses.html>`_
     - Background on 10-bit address support in the Linux I2C subsystem (``I2C_FUNC_10BIT_ADDR``).
   * - `Instantiating I2C devices <https://www.kernel.org/doc/html/latest/i2c/instantiating-devices.html>`_
     - How the kernel binds drivers to I2C devices — relevant when a device is already claimed
       by a kernel driver and you receive ``EBUSY``.

Linux Kernel Header Files
--------------------------

These C headers define the data structures and constants that smbus2 mirrors via
``ctypes``. They ship with the Linux kernel source tree and are also available in most
distributions' ``linux-headers-*`` or ``kernel-headers`` packages.

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Header
     - Relevance
   * - `include/uapi/linux/i2c.h <https://github.com/torvalds/linux/blob/master/include/uapi/linux/i2c.h>`_
     - Defines ``struct i2c_msg``, ``I2C_M_*`` message flags, and ``struct i2c_rdwr_ioctl_data``
       — the data structure passed to ``I2C_RDWR``.
   * - `include/uapi/linux/i2c-dev.h <https://github.com/torvalds/linux/blob/master/include/uapi/linux/i2c-dev.h>`_
     - Defines all ``ioctl`` request codes for ``/dev/i2c-N``: ``I2C_SLAVE``,
       ``I2C_SLAVE_FORCE``, ``I2C_TENBIT``, ``I2C_FUNCS``, ``I2C_RDWR``, ``I2C_PEC``,
       ``I2C_SMBUS``; also defines ``struct i2c_smbus_ioctl_data`` and ``union i2c_smbus_data``.
   * - `include/uapi/linux/i2c-smbus.h <https://github.com/torvalds/linux/blob/master/include/uapi/linux/i2c-smbus.h>`_
     - Defines ``I2C_SMBUS_*`` transaction-type constants (``I2C_SMBUS_BYTE``,
       ``I2C_SMBUS_BYTE_DATA``, ``I2C_SMBUS_WORD_DATA``, ``I2C_SMBUS_BLOCK_DATA``,
       ``I2C_SMBUS_I2C_BLOCK_DATA``, ``I2C_SMBUS_PROC_CALL``, etc.) that correspond to each
       smbus2 method.

i2c-tools User-Space Utilities
-------------------------------

The ``i2c-tools`` package provides the command-line utilities commonly used alongside
smbus2 for bus discovery and manual device interrogation.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Tool / Resource
     - Description
   * - `i2c-tools project page (kernel.org) <https://i2c.wiki.kernel.org/index.php/I2C_Tools>`_
     - Home page for the ``i2c-tools`` package.
   * - `i2c-tools source repository <https://git.kernel.org/pub/scm/utils/i2c-tools/i2c-tools.git/>`_
     - Source for ``i2cdetect``, ``i2cdump``, ``i2cget``, ``i2cset``, and ``i2ctransfer``.
   * - ``i2cdetect -y 1``
     - Scan bus 1 for responding device addresses — the first diagnostic step when a device
       is not found.
   * - ``i2cdump -y 1 0x50``
     - Dump all registers of the device at address ``0x50`` on bus 1.
   * - ``i2ctransfer -y 1 w1@0x50 0x00 r2@0x50``
     - Perform a write-then-read transaction (equivalent to smbus2's ``i2c_rdwr`` with two
       messages).

Python ``ctypes`` and ``struct`` References
-------------------------------------------

smbus2 uses ``ctypes`` internally to construct kernel data structures. The tips in the
documentation (e.g. signed-integer conversion, endianness swap) also use standard-library
modules.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Reference
     - Description
   * - `Python ctypes documentation <https://docs.python.org/3/library/ctypes.html>`_
     - Python's foreign-function and C-compatible type library — used by smbus2 for
       ``ioctl`` buffer layout and by users for signed-integer conversion.
   * - `Python struct documentation <https://docs.python.org/3/library/struct.html>`_
     - Pack/unpack bytes with format strings — useful for byte-order conversion of
       multi-byte sensor values.
   * - `Python fcntl documentation <https://docs.python.org/3/library/fcntl.html>`_
     - The Linux-only standard-library module that smbus2 uses to issue ``ioctl`` system
       calls.

smbus2 Project Resources
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Resource
     - URL
   * - GitHub repository
     - https://github.com/kplindegaard/smbus2
   * - PyPI package
     - https://pypi.org/project/smbus2/
   * - Read the Docs (API docs)
     - https://smbus2.readthedocs.io/en/latest/
   * - Changelog
     - `CHANGELOG.md <https://github.com/kplindegaard/smbus2/blob/master/CHANGELOG.md>`_
   * - Issue tracker
     - https://github.com/kplindegaard/smbus2/issues
