# SEF project

```bash
# requirements
#if you use anaconda
conda install "ffmpeg<5" -c conda-forge
else
sudo apt-get install ffmpeg
#lib
cd setup
#audiocraft requirements (for training)
pip install -r musicgen_r.txt
#preprocessing raw data
pip install -r predata_r.txt
