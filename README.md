# Logic-gate-simulator
# Logic Gate Simulator

A GUI application for simulating basic logic gates using nodes.

## Features
- Intuitive drag-and-drop interface for creating logic circuits
- Support for multiple logic gates (AND, OR, NOT, NAND, NOR, XOR, XNOR)
- Input and output nodes for interaction
- File operations (New, Open, Save)
- Edit operations (Undo, Redo, Cut, Copy, Paste, Delete)
- Theming options

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation
1. Clone this repository:
```
git clone https://github.com/unichronic/Logic-gate-simulator.git
cd LogicGateSimulator
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```
OR
```
conda env create -f environment.yml
conda activate gatesim
```
### Running the Application
Execute the following command from the project root directory:
```
python src/main.py
```

## Usage
1. Drag logic gate nodes from the side panel to the main window
2. Connect nodes by clicking and dragging between connection points
3. Set input values and observe the output
4. Save your circuits for later use
5. Write Output using the write output button. 
