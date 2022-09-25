rm -rf dist
poetry build
pip uninstall -y zillionare-ths-boards
pip install "dist/zillionare_ths_boards-`poetry version --short`-py3-none-any.whl"
