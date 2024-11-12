import os
import re
import numpy as np

def max_file_index(directory, prefix="step_"):
    # List all files in the directory
    files = os.listdir(directory)
    
    # Extract numbers from filenames that match the pattern
    numbers = []
    for file in files:
        match = re.match(rf"{prefix}(\d+)", file)
        if match:
            numbers.append(int(match.group(1)))
    
    # Find the highest number
    max_index = max(numbers) if numbers else None

    return max_index


def parse_spectral_data(file_path):
    spectral_data = []
    
    with open(file_path, 'r') as file:
        for line in file:
            # Use regex to match lines that contain spectral data (lines starting with a space and contain two comma-separated values)
            match = re.match(r"^\s*(\d+),([\d.eE+-]+)", line)
            if match:
                wavelength = int(match.group(1))
                intensity = float(match.group(2))  # This automatically handles scientific notation
                spectral_data.append((wavelength, intensity))

    spectral_data = np.array(spectral_data)
    return spectral_data

def main():

    directory = os.getcwd() + "\parseData"
    prefix="step_"

    # Find the highest numbered file
    max_index = max_file_index(directory, prefix)
    if max_index is None:
        print("No matching files found.")
        return
    
    # Iterate through the files from 0 to the highest number
    spectral_csv = parse_spectral_data(os.path.join(directory, f"white_ref_0.txt"))

    for i in range(max_index + 1):
        file_path = os.path.join(directory, f"{prefix}{i}.txt")
        if os.path.exists(file_path):
            print(f"Processing {file_path}")

            # Add your file processing logic here
            spectral_data = parse_spectral_data(file_path)
            spectral_csv = np.append(spectral_csv, spectral_data[:, 1].reshape(102, 1), axis=1)

            # spectral_csv = spectral_data[:, 0].reshape(102, 1)
            
        else:
            print(f"File {file_path} does not exist.")
    try:
        np.savetxt(os.path.join(directory, f"transmission.csv"), spectral_csv, delimiter=",", fmt= "%.2e")
        print(os.path.join(directory, f"transmission.csv"))
    except:
        pass
    
if __name__ == "__main__":
    main()



