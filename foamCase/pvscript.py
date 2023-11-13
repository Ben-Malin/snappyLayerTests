#import paraview
#paraview.compatibility.major 5
#paraview.compatibility.major 9

import os
import sys
from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()

'''
Paraview python script
'''

# First command line argument gives name for file
name = sys.argv[1]

screenshotDir = '../images'
# if the directory doesn't exist, create it
if not os.path.exists(screenshotDir):
    os.makedirs(screenshotDir)

###########################
##      Functions        ##
###########################

# create a new 'OpenFOAMReader'
def loadFoam(dotFoamFile: str, path: str):
    casefoam = OpenFOAMReader(registrationName=dotFoamFile, FileName=path)
    casefoam.SkipZeroTime = 0
    casefoam.CaseType = 'Reconstructed Case'
    casefoam.MeshRegions = ['internalMesh', 'cad']
    casefoam.CellArrays = ['nSurfaceLayers', 'thickness', 'thicknessFraction']
    casefoam.Decomposepolyhedra = 0

    # return the casefoam object
    return casefoam

def displayDefaults(displayObj,variable: str):
    return displayObj

def meshSlice(casefoam):
    # extract just the internalField
    extractBlock1 = ExtractBlock(registrationName='ExtractBlock1', Input=casefoam)
    extractBlock1.BlockIndices = [1]

    # create a new 'Slice'
    slice1 = Slice(registrationName='Slice1', Input=extractBlock1)
    slice1.SliceType = 'Plane'
    slice1.SliceOffsetValues = [0.0]
    slice1.SliceType.Origin = [0.0, 0.0, 0.0867]
    slice1.SliceType.Normal = [0.0, 0.0, 1.0]
    slice1.Triangulatetheslice = 0
    return slice1

def setOverheadCam(camera):
    camera.SetPosition([0.0, 0.0, 0.1])
    camera.SetFocalPoint([0.0, 0.0, 0.0])
    camera.SetViewUp([0.0, 1.0, 0.0])
    camera.SetParallelScale(0.2)
    return camera

def setPerspectiveCam(camera):
    camera.SetPosition([0.301938, 0.366981, 0.56]) #0.588092])
    camera.SetFocalPoint([0.004, -0.01, 0.004])
    camera.SetViewUp([-0.256099,0.862846,-0.435785])
    return camera

def meshSurface(casefoam):
    extractBlock2 = ExtractBlock(registrationName='ExtractBlock2', Input=casefoam)
    extractBlock3 = ExtractBlock(registrationName='ExtractBlock3', Input=casefoam)
    extractBlock2.BlockIndices = [2]
    extractBlock3.BlockIndices = [2]

    extractBlock2Display = Show(extractBlock2, renderView2, 'GeometryRepresentation')
    extractBlock3Display = Show(extractBlock3, renderView2, 'GeometryRepresentation')

    ColorBy(extractBlock2Display, ('CELLS', 'nSurfaceLayers'))
    ColorBy(extractBlock3Display, ('POINTS', 'nSurfaceLayers'))

    extractBlock3Display.SetRepresentationType('Wireframe')

    surfaceLUT = GetColorTransferFunction('nSurfaceLayers')
    surfacePWF = GetOpacityTransferFunction('nSurfaceLayers')

    surfaceLUT.ApplyPreset('Black, Blue and White', True)
    surfacePWF.Points = [0.0, 1.0, 0.5, 0.0, 2.48, 0.994, 0.5, 0.0, 3.0, 0.65, 0.5, 0.0]
    surfaceLUT.EnableOpacityMapping = 1
    surfaceLUT.NumberOfTableValues = 4

    meshLUT = GetColorTransferFunction('nSurfaceLayers',extractBlock3Display,separate=True)
    meshPWF = GetOpacityTransferFunction('nSurfaceLayers',extractBlock3Display,separate=True)
    meshLUT.ApplyPreset('Black, Blue and White', True)
    meshPWF.Points = [0.0, 1.0, 0.5, 0.0, 2.322, 0.1, 0.5, 0.0, 3.0, 0.5, 0.5, 0.0]
    meshLUT.EnableOpacityMapping = 1
    meshLUT.NumberOfTableValues = 256

    extractBlock2Display.RescaleTransferFunctionToDataRange(True, False)
    extractBlock2Display.SetScalarBarVisibility(renderView2, False)
    extractBlock3Display.RescaleTransferFunctionToDataRange(True, False)
    extractBlock3Display.SetScalarBarVisibility(renderView2, False)

    extractBlock3Display.Opacity = 0.5

###########################
## Start the main script ##
###########################

renderView1 = GetActiveViewOrCreate('RenderView')
renderView1.CameraParallelProjection = 1
renderView1.OrientationAxesVisibility = 0
renderView1.Background = [1.0, 1.0, 1.0]

## check if a file exists in the directory called case.foam, if not, create it using touch
if not os.path.exists('./case.foam'):
    os.system('touch ./case.foam')

# create a new 'OpenFOAMReader'
casefoam = loadFoam('case.foam', f'./')

# Create a slice to display the mesh cross section
slice1 = meshSlice(casefoam)
slice1Display = GetDisplayProperties(slice1, view=renderView1)
slice1Display.SetRepresentationType('Surface With Edges')
slice1Display.ScaleFactor = 50

camera = GetActiveCamera()
setOverheadCam(camera)

SaveScreenshot(f'{screenshotDir}/{name}_slice.png',renderView1,ImageResolution=[1200,1200])

## Make a new render view, swap to it and set the camera
SetActiveView(None)
layout2 = CreateLayout(name='Layout #2')
renderView2 = CreateView('RenderView')
renderView2.OrientationAxesVisibility = 0
renderView2.Background = [1.0, 1.0, 1.0]
AssignViewToLayout(view=renderView2, layout=layout2, hint=0)
camera = GetActiveCamera()
setPerspectiveCam(camera)

meshSurface(casefoam)

SaveScreenshot(f'{screenshotDir}/{name}_surface.png',renderView2,ImageResolution=[1200,1200])



