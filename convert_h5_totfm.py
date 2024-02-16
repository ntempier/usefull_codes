import h5py
import numpy as np

def read_itk_h5_transform(h5_file_path):
    with h5py.File(h5_file_path, 'r') as file:
        if 'TransformGroup/0/TransformParameters' in file:
            parameters = file['TransformGroup/0/TransformParameters'][...]
        else:
            raise ValueError("Expected transformation dataset not found in the file.")
        
        if 'TransformGroup/0/FixedParameters' in file:
            fixed_parameters = file['TransformGroup/0/FixedParameters'][...]
        else:
            fixed_parameters = np.array([0, 0, 0])

    # Construct the affine matrix. Assuming parameters has 12 elements for affine transformation.
    if parameters.size == 12:
        # Reshape the first 12 parameters to 3x4 matrix
        affine_matrix = np.reshape(parameters, (3, 4))
        # Append the last row [0, 0, 0, 1] to make it 4x4
        affine_matrix = np.vstack((affine_matrix, [0, 0, 0, 1]))
    else:
        raise ValueError("Unexpected number of parameters in transformation matrix.")

    return affine_matrix, fixed_parameters

def itk_h5_to_tfm(h5_file_path, tfm_file_path):
    matrix, fixed_parameters = read_itk_h5_transform(h5_file_path)
    
    # Prepare the .tfm content
    tfm_content = "#Insight Transform File V1.0\n"
    tfm_content += "Transform: AffineTransform_double_3_3\n"
    tfm_content += "Parameters: "
    tfm_content += " ".join(map(str, matrix[:3, :].flatten())) + "\n"  # Flatten the top 3x4 of the matrix for parameters
    tfm_content += "FixedParameters: " + " ".join(map(str, fixed_parameters)) + "\n"
    
    # Write the content to the .tfm file
    with open(tfm_file_path, 'w') as file:
        file.write(tfm_content)


h5_file_path = '/network/lustre/iss02/lau-karachi/data_raw/Human/Nicolas_Tempier/H3H/NDPI_Loading_For_Trace/PERLS/MAN_322_to_Cryoslice_107.h5'
tfm_file_path = '/network/lustre/iss02/lau-karachi/data_raw/Human/Nicolas_Tempier/H3H/NDPI_Loading_For_Trace/PERLS/MAN_322_to_Cryoslice_107.tfm'
itk_h5_to_tfm(h5_file_path, tfm_file_path)
