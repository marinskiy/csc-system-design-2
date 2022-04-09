# Yet Another Roguelike 
This project is done for System Design course of CSC / YSDA, Spring 2022.


# Installation

To run roguelike you will need to install conda.

Then you need to create env and install all needed dependencies. 
To do so execute `make local-env-create`.
This will create conda env from `environment.yml` and install `cli` into this env.


# Running application

After passing installation you may run application using `make launch`.


# Testing & Code-style

The code is covered by several linters, static code checking and tests:
1. pytest - testing the whole system functionality
2. mypy - static type checking
3. flake8 - code style
4. pylint - code style

## Tests

To run tests execute `make test`

## Code style

To run code style checks `make lint`

## Authors
- **Alexander Marinskiy**
- **Daria Turichina**
- **Vladislav Milshin**
- **Yaroslav Starukhin**

## Acknowledgments

  - CSC / YSDA course of System Design, Spring 2022