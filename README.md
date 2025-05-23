https://github.com/0nionn58/path-traversal-mini-lab.git

sudo apt update
sudo apt install docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

cd "path-traversal-mini-lab"
docker build -t lab .
docker run --rm --network=host lab
