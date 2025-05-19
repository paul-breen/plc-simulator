# Changelog

## [v0.4.0] - 2025-05-19

### Added

- Add GitHub workflow to build and publish API docs
- Add pdoc as a development dependency

### Changed

- Update the README to reflect the new command line invocation
- Update all the API docs
- Update the build to export the package main functionality as a proper console script
- Update build process to use poetry

## [v0.3.0] - 2019-09-20

### Added

- Add exception code for illegal function in Modbus module
- Add transform simulation
- Add the copy simulation
- Add random number simulations
- Add optional range parameters for certain simulation types
- Add initial simulation functions to IoManager
- Add a new IoManager class to handle simulated IO
- Add project README and LICENSE
- Add functions to service Modbus requests
- Add memory manager class
- Add generic Fieldbus Message class

### Changed

- Complete response for preset multiple registers
- Slice doesn't include its end so end_addr can be length of memspace
- Return Modbus exception to client if request exceeds bounds of memspace
- Raise IndexError if slice exceeds bounds of memspace section
- Update docs and examples to explain how fieldbus objects are mapped by TCP port
- The fieldbus module for incoming connections is chosen by port
- Make a copy of the required fieldbus module to service a client request
- Reorganising files for packaging
- Ensure all simulations have an ID
- Updates to configuration for faster waveforms
- Minor mod. to remove superfluous code
- Develop simple simulation functions for IoManager
- Rename n to nwords in MemoryManager methods
- Rename get_section_size() method to better reflect its purpose
- Implement mutex locking for direct access to memspace
- Ensure the ModbusModule receives the full message length
- Correct typos in the README
- Main application functionality now wrapped up in a class
- Initial commit of the PLC Simulator software
