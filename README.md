![demo](demo.jpg)


# Introduction
A simple **image viewer** _soft-ware_ that focuses on cumulative browsing.
Images are queried from a *search bar* and loaded onto an infinite *board*, it can accomodates and infinite amount of images at different scales without compromises on quality.


## Installation
1. Download a *Python 3.14.5 (or higher)* installer from [here](https://www.python.org/downloads/), unless the former isn't already installed on your machine

### Linux
2. Execute the installer with privilege `python -BO install.py`
3. Uninstall the program with privilege `python -BO install.py uninstall`

### Windows
2. Open `Command Prompt` with elevated privilege (right click on application and left click *run as administrator*)
3. Move to the directory with `cd %USERPROFILE%\Desktop\gatti-main`
4. Run the installer with `python -BO install.py`

## Usage
1. Run the program with `gatti [SAVE].gatti` (replace `[SAVE]` with a name of your choice)
2. Press `s` on your keyboard to open the *search bar*
3. Write a path to a valid image file and press `RETURN` on the keyboard to load it onto the *board*
4. Left click an image and drag the mouse, the image will drag as well
5. Left click an image and scroll the mouse wheel, the image will rescale
6. Right click and drag the mouse, the entire canvas will drag as well
7. Scroll the mouse wheel, the canvas will rescale
8. Left click the mouse cursor onto an image and press `x` on the keyboard to delete it


## Troubleshooting
* If *PyGame Community Edition* doesn't install regularly from pip, try following the specifications from [here](https://pypi.org/project/pygame-ce/)


## Trivia
1. This program originated from an idea of mine at the end of July of 2026, I had many exams to take but the excuse to spend time making this was that it was *essential* for organizing my notes.
2. The name *tom* came to mind while thinking of the song title "tower of memories" by ivri.
3. The name *gatti* means *cats* in italian, its an acronym for **g**allery **a**rranger **t**hat **t**akes **i**mages or maybe **g**allery **a**rranger **t**ooled **t**owards **i**mages. This will also make more sense later...


# Development
The execution starts from `main.py` that applies `gatti_serialization.py` to calculate the initial state of `gatti_program.py`, a state machine that handles transitions between an *image board* implemented in `gatti_board.py` and a *search query* implemented in `gatti_search.py`.


## Upcoming features
* Image comments
* Physical panning and zooming (momentum, viscousity and elasticity)
* Local and global rotation
* Image cropping
* Image preview while searching

## Issues
* The gaussian blur implementation is approximated with three passes of `pg.transform.box_blur`, its better than `pg.transform.gaussian_blur` but it could be made better.


## Methods

### Levenshtein distance
A method used to compare the similarity between two strings. This is used in the search algorithm to show the best hints possible.
