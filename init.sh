#!/bin/bash
echo "install python package"
poetry install
echo "set git hooks"
cp commit-msg.sh .git/hooks/commit-msg
cp pre-push.sh .git/hooks/pre-commit
echo "set git hooks done"
echo "create log directory"
mkdir log