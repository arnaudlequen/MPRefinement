# Summary

A program to detect some unsolvable classical planning instances without search. 
Based on linear- and integer-programming, it makes the most of an incomplete criterion to iteratively refine the STRIPS model, add more information, and remove 
unnecessary elements.

Paper available at : [TBA]

# Installation

Tested with Python 3.10

Create a Python environment, then install the dependencies:
```bash
python3 -m venv env
source ./env/bin/activate
python3 -m pip install -r requirements.txt
```
# Usage

```bash
python3 main.py [-h] [-t TRACE] [-l TESTSLIST] [-s | --nostop | --no-nostop] [-d STRIPSDUMP] domain.pddl instance.pddl
```

## Positional arguments:
- **domain.pddl**: The domain file in PDDL format. Assumed as domain.pddl when not specified
- **instance.pddl**: The file of the problem from which to extract a subproblem, in PDDL format

## options:
-  **-t** *TRACE*, **--trace** *TRACE*: Output a datafile that summarizes the main data points of the execution
-  **-l** *TESTSLIST*, **--testslist** *TESTSLIST*: Input a list of tests to be performed. Choose one from the Data folder
-  **-s**, **--nostop**: If specified, the algorithm will perform all operations before exiting, even if UNSAT is met before
-  **-d** *STRIPSDUMP*, **--stripsdump** *STRIPSDUMP*: Dump the STRIPS model in the specified file
  
# License
  
This software uses the parser of Fast Downward, for which the following license applies:

```
Fast Downward is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

Fast Downward is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
```
