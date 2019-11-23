# Vim 实用技巧

Tags: `<vim>`

### vim 中搜索选中内容

1. 按下 `v` 进入可视化模式，选中内容
2. 按下 `y` 复制内容到默认寄存器
3. 按下 `/` 或者 `?` 进入搜索模式，再按 `"`+ `<Enter>` 

建议使用键盘映射，在 vimrc 中加入

```vim
vnoremap // y/<c-r>"<cr>
```

### vim 中多行编辑技巧

1. 多行追加，`<Ctr>+v` ->  `<Shift>+I` -> edit -> `double <Esc>`
2. 多行替换，`<Ctr>+v` ->  `c` -> edit -> `double <Esc>`

