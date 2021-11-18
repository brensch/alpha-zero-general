to run in docker:

`docker build -t ml -f snake/dockerfile .`

`docker run --gpus=all -it -v "$(pwd)":/repo ml`
