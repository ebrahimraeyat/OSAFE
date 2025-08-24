# FreeCAD Civil Foundation Model Workbench
A Workbench in [FreeCAD](https://freecadweb.org) for creating foundation model in [CSI SAFE](https://www.csiamerica.com/products/safe) from [CSI ETABS](https://www.csiamerica.com/products/etabs) Model. It also can Import [CSI SAFE](https://www.csiamerica.com/products/safe) model into FreeCAD and calculate Shear punching of columns according to ACI 318-19.

![3](https://user-images.githubusercontent.com/8196112/155970780-e83b9fe9-5e46-4b75-82b6-860aa44f9ee7.jpg)

## Dependencies
- This Addon/workbench runs on:  
  - [x] Most up to date stable release
  - [x] Most up to date development release
  - [x] Python 3 compatible
  - [x] Qt5 compatible
  - [ ] Qt5 and Qt6 compatible (uses "import PySide" rather than "import PySide")
- [x] Backward compatible with 0.19 version of FC.
- [x] 3rd party dependencies:  
  - [x] numpy
  - [x] scipy
  - [x] pandas
  - [x] git
  - [x] comtypes
  


## Installation

### Addon Manager
1. Start the Addons Manager from menu Tools -> Addons manager
2. Locate and install the OSAFE addon
3. Restart FreeCAD, and switch to the OSAFE workbench

### Manually
#### Windows
You can download FreeCAD from below links and install it in windows. After installation, you must clear Civil folder in FreeCAD installation folder (ec. C:\Program Files\FreeCAD 0.19\Mod\Civil) and then clone this two repositories .

https://github.com/ebrahimraeyat/OSAFE.git  
https://github.com/ebrahimraeyat/etabs_api.git

[link1](https://github.com/ebrahimraeyat/OSAFE/releases/tag/v0.9)  
[link2](https://mega.nz/file/sUlAQaoA#SvTKQu_HswPNQxW9wT8PlCxLGXBZbBH_F-xp6A_bsps)

#### Debian 10 (Buster)

```bash
$ sudo apt install freecad-python3
$ sudo update-alternatives --set freecad /usr/lib/freecad/bin/freecad-python3
$ sudo apt install git python3-pandas
$ mkdir -p $HOME/.FreeCAD/Mod
$ cd $HOME/.FreeCAD/Mod
$ git clone https://github.com/ebrahimraeyat/OSAFE.git 
$ git clone https://github.com/ebrahimraeyat/etabs_api.git 
```

## Discussion
Forum thread to discuss this workbench can be found in the [FreeCAD Subforums](https://forum.freecadweb.org/viewtopic.php?f=24&t=31813#p264539)

## Contribute
Pull Requests are welcome. Please feel free to discuss them on the forum thread.
