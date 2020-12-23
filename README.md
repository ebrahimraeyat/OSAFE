## FreeCAD Shear Punching Engineering Workbench
A Workbench in [FreeCAD](https://freecadweb.org) for calculating shear punching of foundation that have been modeled in [CSI SAFE](https://www.csiamerica.com/products/safe)

![punch](https://user-images.githubusercontent.com/8196112/103041595-11204e80-458c-11eb-9cab-460a1963c802.gif)


### Shear Punching
This reads an excel output from the [CSI SAFE](https://www.csiamerica.com/products/safe) software and calculates shear punching ratio.



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
