import os

# change "inputFolder"  with your "pathofpatientfolder/mesh/ref_t1mri/yeb_atlas" then copy paste to 3D slicer python console 
# it will create "pathofpatientfolder/mesh/ref_t1mri/yeb_atlas_volumes" with STNs in nifti

inputFolders = [
    r"/network/iss/lau-karachi/data_raw/Human/Nicolas_Tempier/ANR_HIFU/vtk2nii/test_patient/mesh/ref_t1mri/yeb_atlas"
]

# ------------------------------------------------------------------------------

rasProps = {"coordinateSystem": slicer.vtkMRMLStorageNode.CoordinateSystemRAS}
segLogic = slicer.modules.segmentations.logic()

for inputFolder in inputFolders:
    if not os.path.isdir(inputFolder):
        print(f"Skip (not found): {inputFolder}")
        continue

    outputFolder = inputFolder + "_volumes"
    os.makedirs(outputFolder, exist_ok=True)

    for fileName in os.listdir(inputFolder):
        lower_name = fileName.lower()
        if not lower_name.endswith(".vtk") or "stn" not in lower_name:
            continue
        vtkPath = os.path.join(inputFolder, fileName)
        print(f"→ {vtkPath}")

        # Load model as RAS
        modelNode = slicer.util.loadNodeFromFile(vtkPath, "ModelFile", rasProps)
        if modelNode is None:
            print(f"   FAILED load")
            continue

        # Model → Segmentation
        segNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        segLogic.ImportModelToSegmentationNode(modelNode, segNode)
        segNode.CreateBinaryLabelmapRepresentation()

        # Segmentation → LabelMap volume
        labelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        segLogic.ExportAllSegmentsToLabelmapNode(segNode, labelNode)

        # Save NIfTI
        outPath = os.path.join(outputFolder, os.path.splitext(fileName)[0] + ".nii")
        slicer.util.saveNode(labelNode, outPath)

        # Clean scene
        for n in (modelNode, segNode, labelNode):
            slicer.mrmlScene.RemoveNode(n)

print("Done.")

