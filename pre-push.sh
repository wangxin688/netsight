# echo "export requirements.txt"
# poetry export -o requirements.txt --without-hashes
# poetry export -o requirements-dev.txt --with dev --without-hashes
echo "autoflake"
autoflake --recursive --in-place  \
        --remove-unused-variables \
        --remove-all-unused-imports  \
        --ignore-init-module-imports \
        src
echo "black"
black src
echo "isort"
isort src
echo "flake8"
flake8 src --count --statistics
echo "OK"