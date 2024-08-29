import argparse
import subprocess
import os

def run_command(command):
    print(f"Running command: {command}")
    subprocess.run(command, shell=True, check=True)

def main():
    parser = argparse.ArgumentParser(description="Run SR_InstantMesh with IPG or DRCT.")
    parser.add_argument('--method', choices=['ipg', 'drct'], required=True, help="Choose between 'ipg' or 'drct' for super resolution.")
    parser.add_argument('--input_image', required=True, help="Path to the input image.")
    parser.add_argument('--output_dir', required=True, help="Path to the output directory for results.")
    parser.add_argument('--ipg_model', type=str, default="IPG_SRx4.pth", help="Path to the IPG pre-trained model.")
    parser.add_argument('--drct_model', required=False, help="Path to the DRCT pre-trained model.")

    args = parser.parse_args()

    # Define the copy directory based on the method
    if args.method == 'ipg':
        copy_dir = os.path.abspath('IPG/imgs')  # Convert to absolute path
    elif args.method == 'drct':
        copy_dir = os.path.abspath('DRCT/datasets')  # Convert to absolute path
    else:
        raise ValueError("Invalid method. Choose between 'ipg' or 'drct'.")

    # Step 1: Run Instant Mesh
    instant_mesh_cmd = (f"python run.py configs/instant-mesh-large.yaml {args.input_image} "
                        f"--copy_dir {copy_dir} --export_texmap")
    run_command(instant_mesh_cmd)

    if args.method == 'ipg':
        if not args.ipg_model:
            raise ValueError("IPG pre-trained model path must be provided when using 'ipg' method.")
        
        # Run IPG Super Resolution
        ipg_dir = "IPG"
        os.chdir(ipg_dir)
        ipg_cmd = (f"python exec.py --eval_folder {args.ipg_model} --eval_opt options/test_mod/test_IPG_SR_x4.yml")

        run_command(ipg_cmd)
        os.chdir("..")  

        # Run InstantMesh with IPG
        sr_run_cmd = (f"python sr_run.py configs/instant-mesh-large.yaml "
                      f"--export_texmap --ipg")
        run_command(sr_run_cmd)

    elif args.method == 'drct':
        if not args.drct_model:
            raise ValueError("DRCT pre-trained model path must be provided when using 'drct' method.")
        
        # Run DRCT Super Resolution
        drct_dir = "DRCT"
        output_dir = os.path.abspath(os.path.join(drct_dir, "results"))  # Convert to absolute path
        #print(f"Output will be saved to: {args.output_dir}")

        os.chdir(drct_dir)
        drct_cmd = (f"python inference.py --input {copy_dir} --output {args.output_dir} --model_path {args.drct_model}")
        run_command(drct_cmd)
        os.chdir("..")  # Go back to the previous directory

        # Run InstantMesh with DRCT
        sr_run_cmd = (f"python sr_run.py configs/instant-mesh-large.yaml "
                      f"--export_texmap --drct")

        run_command(sr_run_cmd)

if __name__ == "__main__":
    main()
