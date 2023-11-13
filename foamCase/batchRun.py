import os
import cv2

## This script is used to run through a sweep of snappyHexMesh layer addition settings
## pvpython is used to generate images, and these images are then combined using opencv
## Currently this does not run in parallel, so with a little coding it could be made 
## significantly faster

###############
## Functions ##
###############

def changeSnappySetting(setting, value, dict='./system/snappyHexMeshDict'):
    os.system('foamDictionary -entry ' + setting + ' -set ' + value + ' ' + dict)

def disableMeshQualityChecks():
    # Set all the mesh quality checks to values which will have no effect
    # Generally negative values for settings = disabled
    meshQual = {}
    meshQual['maxNonOrtho']         = '180'
    meshQual['maxBoundarySkewness'] = '-1'
    meshQual['maxInternalSkewness'] = '-1'
    meshQual['maxConcave']          = '180'
    meshQual['minVol']              = '-1e-30'
    meshQual['minTetQuality']       = '-1e+30'
    meshQual['minArea']             = '-1'
    meshQual['minTwist']            = '-2'
    meshQual['minDeterminant']      = '1e-5'
    meshQual['minFaceWeight']       = '1e-5'
    meshQual['minVolRatio']         = '1e-5'
    meshQual['minTriangleTwist']    = '-1'
    meshQual['minEdgeLength']       = '-1'

    for key, value in meshQual.items():
        changeSnappySetting('meshQualityControls.' + key, value)

def displacementSolver(dict='./system/snappyHexMeshDict'):
    # Add the settings required to use the laplacian displacement shrinker
    changeSnappySetting('addLayersControls.meshShrinker', 'displacementMotionSolver', dict=dict)
    changeSnappySetting('addLayersControls.solver', 'displacementLaplacian', dict=dict)
    os.system('foamDictionary -entry addLayersControls.displacementLaplacianCoeffs -add "{diffusivity quadratic inverseDistance 1(wall);}" ' + dict)


def combineImages(testDict, imageDir='../images', combinedDir='../combinedImages'):
    # use opencv to combine images
    for key, value in testDict.items():
        for sliceType in ['slice', 'surface']:
            images = []
            for val in value:
                if not os.path.isfile(f'{imageDir}/{key}_{str(val)}_{sliceType}.png'):
                    print(f'{key}_{str(val)}_{sliceType}.png does not exist, skipping')
                    continue
                images.append(cv2.imread(f'{imageDir}/{key}_{str(val)}_{sliceType}.png'))

            combinedImages = cv2.hconcat(images)

            for idx,val in enumerate(value):
                xcoord = (idx)*1200 + 20
                cv2.putText(
                    img = combinedImages, 
                    text = f'{key} = {val}',
                    org = (xcoord, 100),
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale = 2,
                    color = (0, 0, 0),
                    thickness = 6,
                )
            cv2.imwrite(f'{combinedDir}/{key}_{sliceType}.png', combinedImages)

##################
## Snappy tests ##
##################

layerTests = {}
layerTests['featureAngle']              = [5, 30, 90, 120, 180]
layerTests['nGrow']                     = [0, 1, 2, 3]
layerTests['maxFaceThicknessRatio']     = [0.01, 0.1, 0.5, 1, 2]
layerTests['maxThicknessToMedialRatio'] = [0.01, 0.1, 0.5, 1, 2]
layerTests['minMedialAxisAngle']        = [5, 30, 90, 120, 180]
layerTests['minThickness']              = [0.001, 0.01, 0.1, 0.5]
layerTests['nSmoothNormals']            = [0, 1, 3, 10, 30]
layerTests['nSmoothSurfaceNormals']     = [0, 1, 3, 10, 30]
layerTests['nSmoothThickness']          = [1, 10, 100]

###############
##   main    ##
###############


snappyDict = './system/snappyHexMeshDict'
snappyTemplate = './system/snappy.template'

if os.path.isfile(snappyDict):
    os.system(f'rm {snappyDict}')

## ----- Check Snappy Layer Settings ----- ##
for key, value in layerTests.items():
    for val in value:
        os.system(f'cp {snappyTemplate} {snappyDict}')
        changeSnappySetting('addLayersControls.' + key, str(val))
        name = f'{key}_{str(val)}'
        os.system(f'./mesh {name}')
        os.system(f'rm {snappyDict}')

combineImages(layerTests)

## ----- Check Mesh Quality Settings ----- #
qualityOnOff = {}
qualityOnOff['MeshQualityControls'] = ['True', 'False']

for key, value in qualityOnOff.items():
    for val in value:
        os.system(f'cp {snappyTemplate} {snappyDict}')
        if val == 'False':
            disableMeshQualityChecks()
        name = f'{key}_{str(val)}'
        os.system(f'./mesh {name}')
        os.system(f'rm {snappyDict}')

combineImages(qualityOnOff)

## ----- Best of each setting ----- #
bestOf = {}
bestOf['featureAngle']              = 180
bestOf['nGrow']                     = 0
bestOf['maxFaceThicknessRatio']     = 1
bestOf['maxThicknessToMedialRatio'] = 1
bestOf['minMedialAxisAngle']        = 30
bestOf['minThickness']              = 0.1
bestOf['nSmoothNormals']            = 1
bestOf['nSmoothSurfaceNormals']     = 3
bestOf['nSmoothThickness']          = 0

os.system(f'cp {snappyTemplate} {snappyDict}')

for key, value in bestOf.items():
    changeSnappySetting('addLayersControls.' + key, str(value))

name = f'bestOf'
os.system(f'./mesh {name}')
os.system(f'rm {snappyDict}')

## ----- Test the Laplacian shrinker ----- #
displacement = {}
displacement['shrinker'] = ['default', 'laplacian', 'bestOf+laplacian']

for key, value in displacement.items():
    for val in value:
        os.system(f'cp {snappyTemplate} {snappyDict}')

        if val == 'bestOf+laplacian':
            for k,v in bestOf.items():
                changeSnappySetting('addLayersControls.' + k, str(v))
        if val == 'laplacian':
            displacementSolver()

        name = f'{key}_{str(val)}'
        os.system(f'./mesh {name}')
        os.system(f'rm {snappyDict}')

combineImages(displacement)










