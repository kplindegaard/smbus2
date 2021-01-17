# Changelog
Notable changes to the smbus2 project are recorded here.

## [Unreleased]
No unreleased updates.

## [0.4.1] - 2021-01-17
### General
- SonarCloud quality checks.
- Tests added to the dist package.

## [0.4.0] - 2020-12-05
### Added
- Support for SMBus PEC (Packet Error Checking).
- Support for Python 3 type hinting and mypy static type analysis. Type stubs added to the project.

### Removed
As of this version the `SMBusWrapper` class is removed and must be replaced with `SMBus`:

```python
# No longer valid!
with SMBusWrapper(1) as bus:
    ...

# Replace with
with SMBus(1) as bus:
    ...
```

### General
- Added Python 3.8 and 3.9 to Travis-CI build config.
- Cleaner docs:
   - Removed redundant `README.rst`.
   - `README.md`, `CHANGELOG.md` and `LICENSE` added to dist package.

## [0.3.0] - 2019-09-07
### Added
- Missing SMBus commands added: `process_call`, `write_block_data`, `read_block_data`, `block_process_call`.
  Note that the latter two are normally not supported by pure i2c-devices.
- SMBus.__init__(), SMBus.open(): `bus` can be a file path as well (issue #17).
- Added enter/exit handler to `SMBus` class.
- Expose enumeration of i2c funcs. Previously, smbus.funcs was defined, but its flags were not exported. All flags moved into the `I2cFunc` class and exported that.
- Added convenience features making the `i2c_msg` class easier to work with.

### Deprecation warning
- The `SMBusWrapper` class is now considered deprecated. Please replace with `SMBus`.

### Changed
- Removed `__slots__` from `i2c_msg` class.
- Whole `i2c_msg_iter` class replaced by a simple generator function with same functionality


## [0.2.3] - 2019-01-10
### Fixed
- Incorrect `i2c_msg` created in Python 3.x if str input contains ascii chars >= 128. 

## [0.2.2] - 2019-01-03
### Added
- SMBus `write_quick` command.

## [0.2.1] - 2018-06-02
### Added
- Ability to force individual r/w operations.
- API docs available on readthedocs.org.

## [0.2.0] - 2017-08-19
### Added
- I2C: Support for i2c_rdwr transactions.

## [0.1.5] - 2017-05-17
### Added
- SMBus support for read and write single bytes without offset/register address.

## [0.1.4] - 2016-09-18
### Added
- Force option for SMBusWrapper class.

## [0.1.3] - 2016-08-14
### Added
- Flag flag for forcing address use even when a driver is already using it.
### Fixed bugs
- Accept zero (0) as bus ID.
- Save address when setting it.

## 0.1.2 - 2016-04-19
First published version.


[Unreleased]: https://github.com/kplindegaard/smbus2/compare/0.4.1...HEAD
[0.4.1]: https://github.com/kplindegaard/smbus2/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/kplindegaard/smbus2/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/kplindegaard/smbus2/compare/0.2.3...0.3.0
[0.2.3]: https://github.com/kplindegaard/smbus2/compare/0.2.2...0.2.3
[0.2.2]: https://github.com/kplindegaard/smbus2/compare/0.2.1...0.2.2
[0.2.1]: https://github.com/kplindegaard/smbus2/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/kplindegaard/smbus2/compare/0.1.5...0.2.0
[0.1.5]: https://github.com/kplindegaard/smbus2/compare/0.1.4...0.1.5
[0.1.4]: https://github.com/kplindegaard/smbus2/compare/0.1.3...0.1.4
[0.1.3]: https://github.com/kplindegaard/smbus2/compare/0.1.2...0.1.3
