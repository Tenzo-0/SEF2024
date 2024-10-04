# SEF projekt
Requirements
```bash
# requirements
# if you use anaconda
conda install "ffmpeg<5" -c conda-forge
# if you use system
sudo apt-get install ffmpeg
# library
cd setup
# audiocraft requirements (for training)
pip install -r musicgen_r.txt
# preprocessing raw data
pip install -r predata_r.txt
```
Setup jupyterlab
```bash
jupyter lab --ip=0.0.0.0 --port=8890
ssh -N -f -L 8890:localhost:8890 user@remote -p PORT


