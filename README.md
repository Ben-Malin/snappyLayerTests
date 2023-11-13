# SnappyLayerTests

Refer to blog post [here](https://ben-malin.github.io/2023/11/06/snappyLayers.html)

Just a simple set of scripts to iterate through snappyHexMesh layer settings  
Just clone the repo and run the python batch script:  

```bash
git clone https://github.com/Ben-Malin/snappyLayerTests.git
cd snappyLayerTests/foamCase
python batchRun.py
```
At the moment it runs completely in serial. It would be ideal to parallelise it to run multiple cases at once, but in serial it doesn't take that long anyway  

When a case completes, a pvpython script is used to output images of the mesh, and the case is then deleted to save space  
