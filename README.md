# Sappho
Sappho is a simple Package Manager, that works on Linux and - might - work on Windows.

I did not compile it, so you might have to do it yourself. Once you do, you can install Programs as easy as this
```
  sappho -S [Package Name]
```
-S is short for "Synchronize". This will automatically download the latest release of a program.
Before you can install Programs though, make sure to run `sappho -y`. This will download all current package Databases. This is done so you can independently install Programs even if the mirrorservers should die.

All mirrors are defined in sappho.yaml. 
