#!/bin/bash

# Entrée : chemin vers l'image à traiter
INPUT_PATH="$1"
SLICER_PATH="/home/nicolas.tempier/Slicer-5.6.2-linux-amd64/Slicer"

# Vérification de l'entrée
if [ ! -f "$INPUT_PATH" ]; then
  echo "Fichier introuvable : $INPUT_PATH"
  exit 1
fi

# Script Python à exécuter dans Slicer
PYTHON_SCRIPT=$(cat <<EOF
import os
inputPath = "$INPUT_PATH"

[success, inputVolume] = slicer.util.loadVolume(inputPath, returnNode=True)
if not success:
    raise RuntimeError(f"Échec du chargement : {inputPath}")

hdBetLogic = slicer.modules.hdbrainextractiontool.widgetRepresentation().self().logic

baseName = os.path.splitext(os.path.basename(inputPath))[0]
outputName = f"{baseName}_brain"

outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", outputName)
outputSegmentation = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", f"{outputName}_segmentation")

print(f"Traitement de : {baseName}")
hdBetLogic.process(inputVolume, outputVolume, outputSegmentation)

outputPath = os.path.join(os.path.dirname(inputPath), f"{outputName}.nii")
slicer.util.saveNode(outputVolume, outputPath)
print(f"Extraction terminée, sauvegardée ici : {outputPath}")
EOF
)

# Exécution dans Slicer en mode terminal
"$SLICER_PATH" --no-main-window --python-code "$PYTHON_SCRIPT"
