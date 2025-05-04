# Orchard Worker Simulation

A multiprocess fruit-picking and crate-loading simulation with both console and graphical (Pygame) user interfaces.

## 📝 Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)

  * [Console Simulation](#console-simulation)
  * [Graphical UI Simulation](#graphical-ui-simulation)
  * [Automated Test Cases](#automated-test-cases)
* [Project Structure](#project-structure)
* [Contributing](#contributing)
* [License](#license)

---

## Overview

This project simulates an orchard workflow where multiple picker processes harvest fruits from a tree and place them into a crate, while a loader process packages full crates for delivery. The simulation can be run as a textual console application or with an interactive graphical interface using Pygame.

## Features

* **Multiprocessing Core**: Utilizes Python's `multiprocessing` module for realistic concurrency and synchronization.
* **Console Output**: Color-coded state transitions in the terminal via `colorama`.
* **Graphical UI**: Real-time visualization of pickers, loader, tree, crate, and event log using Pygame.
* **Centralized Configuration**: Leverages `config.py` for UI constants, layout settings, and speed controls.
* **Event Processor**: Uses `eventprocessor.py` to run the console simulation as a subprocess, parse its output, and synchronize the graphical state.
* **Configurable Parameters**: Number of fruits, pickers, and crate capacity via command-line arguments.
* **Automated Test Cases**: Quick validation of simulation logic against multiple scenarios.
* **Screenshot Support**: Automatically saves final UI frames for analysis.

## Prerequisites

* Python 10
* [Pygame](https://www.pygame.org/)
* [Colorama](https://pypi.org/project/colorama/)

Install dependencies with:

```bash
pip install pygame colorama
```

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/FatimaMansoor-dev/Spring-Pickers-A-Synchronization-Problem

   ```

2. **Install dependencies**:
     ```bash
 
   pip install -r requirements.txt
   ```

 
## Configuration

Adjust simulation parameters in `config.py`:

* `FPS` – frames per second for UI rendering.
* `SPEED_LEVELS` – array of delays for event pacing.
* `SCREEN_WIDTH`, `SCREEN_HEIGHT` – dimensions of the Pygame window.
* Asset paths and UI constants (colors, positions, sizes).

## Usage

### Console Simulation

Run the core simulation in the terminal:

```bash
python main.py --fruits 20 --pickers 4 --capacity 10
```

* `-f`, `--fruits`: Number of fruits to pick (default: 26)
* `-p`, `--pickers`: Number of picker processes (default: 3)
* `-c`, `--capacity`: Crate capacity (default: 12)

### Graphical UI Simulation

Launch the Pygame interface:

```bash
python ui.py -f 15 -p 3 -c 12
```

* Also supports: `--run-all-tests` to sequentially run test scenarios defined in `test_case.py`.

Use **Up** / **Down** arrow keys to control simulation speed. Press any key after completion to exit.

Screenshots of completed runs are saved under the `screenshots/` directory.

### Automated Test Cases

Run predefined scenarios with varying fruit counts:

```bash
python test_case.py
```

This executes simulations for fruit counts defined in `TEST_FRUITS` array.

## Project Structure

```
├── README.md            # Project overview and instructions
├── main.py              # Entry point for console simulation
├── util.py              # Shared resources, Picker and Loader implementations
├── ui.py                # Entry point for graphical UI using Pygame
├── ui_components.py     # Rendering logic for Pygame interface
├── simulationstate.py   # State management and positioning calculations
├── event_processor.py   # Event-driven simulation step logic (UI)
├── config.py            # UI and simulation constants
├── test_case.py         # Automated test runner
├── screenshots/         # Directory for storing UI screenshots
└── assets/              # Images used by the UI (tree, truck, loader, etc.)
```

## Contributing

Contributions, issues, and feature requests are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/YourFeature`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/YourFeature`.
5. Open a pull request.


