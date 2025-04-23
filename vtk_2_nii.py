import os

# Chemin d'entrée (où se trouvent les fichiers .vtk)
inputFolder = r"/network/iss/lau-karachi/data_raw/Human/Nicolas_Tempier/GPe_STN_3T/rawdatas/sujet_6/traitement_mrtrix/ROIs/yeb"

# Chemin de sortie (où vous voulez enregistrer les .nii)
outputFolder = r"/network/iss/lau-karachi/data_raw/Human/Nicolas_Tempier/GPe_STN_3T/rawdatas/sujet_6/traitement_mrtrix/ROIs/yeb_volumes"

# Vérifie que le dossier de sortie existe, sinon le crée
if not os.path.isdir(outputFolder):
    os.makedirs(outputFolder)

# Parcours des fichiers VTK dans le dossier
for fileName in os.listdir(inputFolder):
    if fileName.lower().endswith(".vtk"):
        vtkPath = os.path.join(inputFolder, fileName)
        print(f"Traitement du fichier : {vtkPath}")
        
        # 1) Charger le VTK comme un modèle
        loadedModel = slicer.util.loadModel(vtkPath)
        if not loadedModel:
            print(f"Impossible de charger {fileName} comme modèle.")
            continue
        
        # 2) Créer une segmentation et y importer le modèle
        segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        slicer.modules.segmentations.logic().ImportModelToSegmentationNode(loadedModel, segmentationNode)

        # 3) Créer la représentation labelmap
        segmentationNode.CreateBinaryLabelmapRepresentation()
        
        # 4) Exporter la segmentation en labelmap (volume)
        labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode)
        
        # 5) Sauvegarder le volume en .nii
        outputName = os.path.splitext(fileName)[0] + ".nii"
        outputPath = os.path.join(outputFolder, outputName)
        slicer.util.saveNode(labelmapVolumeNode, outputPath)
        
        # Nettoyage si besoin
        slicer.mrmlScene.RemoveNode(loadedModel)
        slicer.mrmlScene.RemoveNode(segmentationNode)
        slicer.mrmlScene.RemoveNode(labelmapVolumeNode)

print("Conversion terminée.")
