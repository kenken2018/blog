# Git 彻底删除大文件

Tags: `<git>`

pyecharts 的 git history 中存在着很多以前文档需要的图片，导致 pyecharts 整个 git 仓库体积达到 90M+，现在需要把这些图片彻底从 .git 中删除，整个过程会 overwrite 所有跟图片有关的 commit。

```shell
# 查看 git 文件对象大小
$ git count-objects -v

# 列出体积最大的 topN
$ git verify-pack -v .git/objects/pack/pack-*.idx | sort -k 3 -g | tail -5

# 查看具体文件名称
$ git rev-list --objects --all | grep <commit-id>

# 清除该文件
$ git filter-branch --force --index-filter 'git rm --cached -r --ignore-unmatch file_you_want_to_delete' --prune-empty --tag-name-filter cat -- --all

# 清空 git 历史
$ rm -rf .git/refs/original/
$ git reflog expire --expire=now --all
$ git gc --prune=now
$ git gc --aggressive --prune=now
```

