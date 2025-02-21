import subprocess
import csv
import os

def caculate_FAD(path_vggish, path_clap, path_encodec)
    command_1 = ["fadtk", "vggish", baseline_path, evaluation_path, "--indv", path_vggish]
    result_1 = subprocess.run(command_1, capture_output=True, text=True)

    if result_1.returncode == 0:
        print("finish caculate FAD with Vggish embedding")
    else:
        print("Error running command:")
        print(result_1.stderr)

    command_2 = ["fadtk", "clap-laion-music", baseline_path, evaluation_path, "--indv", path_clap]
    result_2 = subprocess.run(command_2, capture_output=True, text=True)

    if result_2.returncode == 0:
        print("finish caculate FAD with CLAP embedding")
    else:
        print("Error running command:")
        print(result_2.stderr)

    command_3 = ["fadtk", "encodec-emb-48k", baseline_path, evaluation_path, "--indv", path_encodec]
    result_3 = subprocess.run(command_3, capture_output=True, text=True)

    if result_3.returncode == 0:
        print("finish caculate FAD with Encodec embedding")
    else:
        print("Error running command:")
        print(result_3.stderr)
        
    print("finish caculate FAD")

def main(base, eval, pr):
    os.makedirs(pr, exist_ok=True)

    vggish_csv_path = os.path.join(process_path, "vggish.csv")
    clap_csv_path = os.path.join(process_path, "clap.csv")
    encodec_csv_path = os.path.join(process_path, "encodec.csv")

    with open(vggish_csv_path, "w", newline="") as file: pass
    with open(clap_csv_path, "w", newline="") as file: pass
    with open(encodec_csv_path, "w", newline="") as file: pass

    caculate_FAD(vggish_csv_path, clap_csv_path, encodec_csv_path)


baseline_path = "/path/to/baseline/audio"
evaluation_path = "/path/to/evaluation/audio"
process_path = "/home/user/process"
main(baseline_path, evaluation_path, process_path)
