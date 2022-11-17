#!/bin/bash
commit_message=`cat $1`
echo $commit_message
echo "done"
message_regx="^(feat|fix|docs|style|refactor|perf|test|workflow|ci|build|release)(\(.+\))?: .{1,100}"


if [[ ! $commit_message =~ $message_regx ]]
then
        echo -e "\n不合法的 commit 消息提交格式，请使用正确的格式：\
        \nfeat(service:approval): add comments\
        \nfix(service:monitor): handle events on blur (close #28)\
        # 异常退出
        exit 1
else:
    echo "commit checking passed "
fi
