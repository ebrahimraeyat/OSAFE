## FreeCAD Civil Engineering Workbench
A collection of civil engineering tools in FreeCAD.

![image](https://user-images.githubusercontent.com/8196112/48443187-3674e880-e788-11e8-9eec-3668095d8f65.png)

![image](https://user-images.githubusercontent.com/8196112/48443621-aa63c080-e789-11e8-9760-f912d981232b.png)

![image](https://user-images.githubusercontent.com/8196112/48443232-53112080-e788-11e8-84e7-1cc939a87d72.png) 

At present this workbench includes two different functionalities:

### Shear Punching
This reads an excel output from CSI Safe software and calculate shear punching ratio. 

### Sections
This converts a combined steel section to one standard section (I shape) to be imported in CSI Etabs for checking classification of compact level of section.

## Installation
### Debian 10 (Buster)

```bash
$ sudo apt install freecad-python3
$ sudo update-alternatives --set freecad /usr/lib/freecad/bin/freecad-python3
$ sudo apt install git python3-pandas
$ mkdir -p $HOME/.FreeCAD/Mod
$ cd $HOME/.FreeCAD/Mod
$ git clone https://github.com/ebrahimraeyat/Civil.git 
```

## Discussion
Forum thread to discuss this workbench can be found in the [FreeCAD Subforums](https://forum.freecadweb.org/viewtopic.php?f=24&t=31813#p264539)

## Contribute
Pull Requests are welcome. Please feel free to discuss them on the forum thread.
