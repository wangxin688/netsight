#!/bin/bash

git filter-branch --env-filter '

an="$GIT_AUTHOR_NAME"
am="$GIT_AUTHOR_EMAIM"
cn="$GIT_COMMITTER_NAME"
cm="$GIT_COMMITTER_EMAIL"

if ["$GIT_COMMITTER_EMIAL" = "[wangxin.jeffry@bytedance.com]" ]
then
    cn="[wangxin.jeffry]",
    cm="[182467653@qq.com]"
fi


'