
# Web app for the enriched conformace checking

The application is a simulator for the process discovery and conformance checking by using the Multi dimension approach (see https://github.com/gemmadifederico/enrichedcc or  https://github.com/gemmadifederico/multidimtool).


## Features

The project is composed by two main elements:
- Logger: runs an interactive floormap that can be used to log the movement of a person inside an environment (see https://github.com/delas/interactive-simulation-floormap),
- Webapp: executes discovery and conformance of the simulated data.
  
## Usage

First run the interactive floormap, and simulate the movements of an agent (the project can be found at https://github.com/delas/interactive-simulation-floormap).
To run the web app execute: 
```python
flask -app app run
```
The interface offers the possibility to run the discovery of the simulated data.

For the conformance, first simulate a new instance of the behavior by using the interactive floormap.
Then, open the conformance checking tab, and visualize the results.
