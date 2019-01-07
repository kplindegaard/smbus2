# Changelog
Notable changes to this project will be recorded here.

## Unreleased

### Changed


## [0.2.2] - 2019-01-03

### Added
- SMBus Quick command [#7](https://github.com/kplindegaard/smbus2/issues/7)

## [0.2.1] - 2018-06-02

### Added
- Ability to force individual r/w operations [PR #20]((https://github.com/kplindegaard/smbus2/pull/27))
- API docs available on readthedocs.io, [PR #16](https://github.com/kplindegaard/smbus2/pull/16)

## [0.2.0] - 2017-08-19

### Added
- I2C: Support for i2c_rdwr transactions [PR #12](https://github.com/kplindegaard/smbus2/pull/12)

## [0.1.5] - 2017-05-17

### Added
- SMBus support for read and write single bytes without offset/register address.

## [0.1.4] - 2016-09-18

### Added
- Force option for SMBusWrapper class

## [0.1.3] - 2016-08-14

### Added
- Flag flag for forcing address use even when a driver is already using it.

### Fixed
- Accept zero (0) as bus ID.
- Save address when setting it.

## [0.1.2] - 2016-04-19
First published version.