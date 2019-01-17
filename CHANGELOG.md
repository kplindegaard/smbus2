# Changelog
Notable changes to the smbus2 project are recorded here.

## [Unreleased]
### Added
- Missing SMBus commands added: `process_call`, `write_block_data`, `read_block_data`, `write_block_data`.
  Note that the latter two are normally not supported by pure i2c-devices. 
- Added convenience features making the `i2c_msg` class easier to work with.

### Changed
- Removed `__slots__` from `i2c_msg` class.

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


[Unreleased]: https://github.com/kplindegaard/smbus2/compare/0.2.3...HEAD
[0.2.3]: https://github.com/kplindegaard/smbus2/compare/0.2.2...0.2.3
[0.2.2]: https://github.com/kplindegaard/smbus2/compare/0.2.1...0.2.2
[0.2.1]: https://github.com/kplindegaard/smbus2/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/kplindegaard/smbus2/compare/0.1.5...0.2.0
[0.1.5]: https://github.com/kplindegaard/smbus2/compare/0.1.4...0.1.5
[0.1.4]: https://github.com/kplindegaard/smbus2/compare/0.1.3...0.1.4
[0.1.3]: https://github.com/kplindegaard/smbus2/compare/0.1.2...0.1.3
