# chenjiandongx's blog

> 在尝试了多种博客工具之后，我觉得还是要回归本真。博客应该要随心随性，易于编写和维护，所以决定使用比较有趣的方式来实现。

工具栈是 grep+vim+fpp ，在每篇博客标题下为该文章打 Tags，便于搜索。

日常工作流

1. vim 编辑文档，markdown 文档可以使用 [grip](https://github.com/joeyespo/grip) 工具预览
2. grep 搜索文档，`grep -i <pattern> | fpp`
3. [fpp](https://github.com/facebook/PathPicker) 支持将 grep 搜索到后的结果输入到管道里面，可以从搜索结果中直接打开文件。

