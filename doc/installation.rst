Installation
============

System Prerequisites
--------------------

smbus2 requires:

- **Linux** — the library uses Linux-specific ``ioctl`` calls and ``/dev/i2c-*`` devices.
- **I2C kernel support** — the ``i2c-dev`` kernel module must be loaded. On most
  distributions this is either built in or can be loaded with:

  .. code-block:: bash

     sudo modprobe i2c-dev

  To load it automatically at boot, add ``i2c-dev`` to ``/etc/modules``.

- **Device permissions** — the user running your Python script must have read/write
  access to ``/dev/i2c-*``. The easiest way is to add the user to the ``i2c`` group:

  .. code-block:: bash

     sudo usermod -aG i2c $USER
     # Log out and back in for the change to take effect

  Alternatively, run with ``sudo`` (not recommended for production).

From PyPI
---------

.. code-block:: bash

   pip install smbus2

Installs the latest stable release. Use a virtual environment to avoid polluting the
system Python environment.

uv users can use ``uv add smbus2`` (uv-managed projects) or
``uv pip install smbus2``.

From conda-forge
----------------

.. code-block:: bash

   conda install -c conda-forge smbus2

From Source
-----------

.. code-block:: bash

   git clone https://github.com/kplindegaard/smbus2.git
   cd smbus2
   python setup.py install

Or, using ``pip`` in editable mode (preferred for development):

.. code-block:: bash

   pip install -e .

Verifying the Installation
--------------------------

.. code-block:: python

   python -c "import smbus2; print(smbus2.__version__)"

You can also verify that your I2C bus is accessible:

.. code-block:: python

   from smbus2 import SMBus

   with SMBus(1) as bus:
       print("Bus opened successfully")


