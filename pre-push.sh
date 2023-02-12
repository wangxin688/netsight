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