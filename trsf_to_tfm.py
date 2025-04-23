import SimpleITK as sitk
import numpy as np

def trsfToTfm(trsfPath, referencePath, outputTfmPath):
    """
    Convertit un fichier .trsf (champ de vecteurs) en .tfm (DisplacementFieldTransform ITK).
    """
    HEADER_SIZE = 256

    def getDataStreamFromVectorField(vectorfieldPath):
        with open(vectorfieldPath, mode='rb') as f:
            f.seek(HEADER_SIZE)  # on saute l'en-tête .trsf
            raw_data = f.read()
        # np.frombuffer → Float32, on copie pour autoriser les modifications
        return np.frombuffer(raw_data, dtype=np.float32).copy()

    # 1) Lecture du .trsf en tableau 1D
    stream = getDataStreamFromVectorField(trsfPath)
    print("Taille du tableau 1D (stream):", stream.shape)

    # 2) Lecture de l'image de référence
    referenceImage = sitk.ReadImage(referencePath)
    size_ref = list(referenceImage.GetSize())  # ex: (dimX, dimY, dimZ)
    print("Taille referenceImage (dimX, dimY, dimZ):", referenceImage.GetSize())
    
    size_ref.reverse()                        # (dimZ, dimY, dimX)
    print("Taille referenceImage inversée (dimZ, dimY, dimX):", size_ref)
    
    componentsPerVector = 3
    size_ref.append(componentsPerVector)      # => (dimZ, dimY, dimX, 3)
    print("Shape complet incluant la composante (3):", size_ref)

    # 3) Reshape en volume 4D (Z, Y, X, 3)
    reshaped = stream.reshape(size_ref)
    print("reshaped.shape:", reshaped.shape, "dtype:", reshaped.dtype)

    # 4) Conversion RAS -> LPS : on inverse la composante X et Y
    reshaped[..., :2] *= -1

    # 5) Construction du champ de déplacements en SimpleITK
    #    "isVector=True" => on indique à SITK que la dernière dimension est un vecteur
    displacementImage = sitk.GetImageFromArray(reshaped, isVector=True)

    # Affectation du header de l'image de référence
    displacementImage.SetOrigin(referenceImage.GetOrigin())
    displacementImage.SetDirection(referenceImage.GetDirection())
    displacementImage.SetSpacing(referenceImage.GetSpacing())

    print("displacementImage PixelIDValue:", displacementImage.GetPixelIDValue())  
    # Par défaut, ce sera du Float32 Vector. On veut du Float64 Vector.

    # 6) Conversion explicite en Float64 (Vector)
    displacementImage = sitk.Cast(displacementImage, sitk.sitkVectorFloat64)
    print("displacementImage PixelIDValue apres Cast:", displacementImage.GetPixelIDValue())

    # 7) Création de la transformation DisplacementFieldTransform
    displacementTransform = sitk.DisplacementFieldTransform(displacementImage)

    # 8) Sauvegarde au format ITK .tfm
    sitk.WriteTransform(displacementTransform, outputTfmPath)
    print("Transformation .tfm écrite vers:", outputTfmPath)


# Exemple d'utilisation :
# trsfToTfm("/network/iss/lau-karachi/data_raw/Human/Nicolas_Tempier/GPe_STN_3T/rawdatas/sujet_2/put_yeb_in_dti/put_t1_in_dti/bm_res_dir/t1_in_dti_result_transformation_vectorfield3D.trsf", "/network/iss/lau-karachi/data_raw/Human/Nicolas_Tempier/GPe_STN_3T/rawdatas/sujet_2/traitement_mrtrix/1_5mm/dti/fa.nii", "/network/iss/lau-karachi/data_raw/Human/Nicolas_Tempier/GPe_STN_3T/rawdatas/sujet_2/put_yeb_in_dti/put_t1_in_dti/bm_res_dir/t1_in_dti_result_transformation_vectorfield3D.tfm")
trsf="/network/iss/lau-karachi/data_raw/Human/Nicolas_Tempier/GPe_STN_3T/rawdatas/sujet_6/traitement_mrtrix/ROIs/bm_res_yeb_2_sujet_6/Yeb_in_sujet_6_result_transformation_vectorfield3D.trsf"
ref_im="/network/iss/lau-karachi/data_raw/Human/Nicolas_Tempier/GPe_STN_3T/rawdatas/sujet_6/traitement_mrtrix/ROIs/sujet_6_FLAIR_brain.nii"

trsfToTfm(trsf,ref_im,trsf.replace(".trsf",".tfm"))


#loop in different trsf and corrsponding ref_im
# trsf_list=["/network/iss/lau-karachi/data_raw/Human/Zohra/T1_inFA_all/yeb_trsfs_and_tfm_in_pat_fa_bm_res/DV/DV_transformation_vectorfield3D.trsf","/network/iss/lau-karachi/data_raw/Human/Zohra/T1_inFA_all/yeb_trsfs_and_tfm_in_pat_fa_bm_res/HT/HT_transformation_vectorfield3D.trsf","/network/iss/lau-karachi/data_raw/Human/Zohra/T1_inFA_all/yeb_trsfs_and_tfm_in_pat_fa_bm_res/MA/MA_transformation_vectorfield3D.trsf","/network/iss/lau-karachi/data_raw/Human/Zohra/T1_inFA_all/yeb_trsfs_and_tfm_in_pat_fa_bm_res/PN/PN_transformation_vectorfield3D.trsf","/network/iss/lau-karachi/data_raw/Human/Zohra/T1_inFA_all/yeb_trsfs_and_tfm_in_pat_fa_bm_res/SC/SC_transformation_vectorfield3D.trsf","/network/iss/lau-karachi/data_raw/Human/Zohra/T1_inFA_all/yeb_trsfs_and_tfm_in_pat_fa_bm_res/VJ/VJ_transformation_vectorfield3D.trsf"]
# ref_im_list=["/network/iss/lau-karachi/data_raw/Human/Zohra/T1_inFA_all/DV_T1_inDTIviaFA_bm.nii","/network/iss/lau-karachi/data_raw/Human/Zohra/T1_inFA_all/HT_T1_inDTIviaFA_bm.nii","/network/iss/lau-karachi/data_raw/Human/Zohra/T1_inFA_all/MA_T1_inDTIviaFA_bm.nii","/network/iss/lau-karachi/data_raw/Human/Zohra/T1_inFA_all/PN_T1_inDTIviaFA_bm.nii","/network/iss/lau-karachi/data_raw/Human/Zohra/T1_inFA_all/SC_T1_inDTIviaFA_bm.nii","/network/iss/lau-karachi/data_raw/Human/Zohra/T1_inFA_all/VJ_T1_inDTIviaFA_bm.nii"]
# i=0
# for trsf in trsf_list:
#     ref_im=ref_im_list[i]
#     trsfToTfm(trsf,ref_im,trsf.replace(".trsf",".tfm"))
#     i+=1