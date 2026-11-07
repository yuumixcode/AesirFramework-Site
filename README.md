# AesirFramework-Site

**AesirFramework 的产品综合站点** —— 产品介绍、上手路径、使用文档与 Scripting API 参考。

- 线上地址:https://yuumixcode.github.io/AesirFramework-Site/
- 框架源码:https://github.com/yuumixcode/AesirFramework
- 开发者内部笔记:`Aesir-Notebook`(私有,不对外)

## 站点定位

这个仓库早期只是"文档站",现在承担的是**产品门面 + 文档中心**两层职责:

| 分区 | 面向 | 内容 |
| --- | --- | --- |
| 首页 | 第一次来的人 | 产品定位、入口分流、快速安装、价值主张 |
| **开始** | 准备上手的人 | 安装与升级、两包快速开始、兼容性、FAQ |
| **产品** | 评估选型的人 | 特性总览、示例总览、版本与下载、路线图、工具链与生态 |
| **文档** | 已经上手的人 | Aesir Architecture / Aesir Modules 的专题文档 |
| **Scripting API** | 查类型与成员的人 | 284 个类型的自动生成参考页 |

## 技术栈

- [Zensical](https://zensical.org/)(Rust 静态站生成器,Material for MkDocs 继任者),当前锁定 `0.0.65`
- 内容:Markdown(`docs/`),配置:`zensical.toml`
- 部署:GitHub Pages(GitHub Actions,见 `.github/workflows/deploy.yml`)

## 本地开发

```bash
pip install "zensical==0.0.65"   # 或 pipx install zensical
zensical serve                   # 本地预览,默认 http://localhost:8000
zensical build                   # 构建到 site/
zensical build --strict          # 严格模式(CI 用,警告即失败)
```

## 目录结构

```
docs/
├── index.md                 # 产品落地页
├── start/                   # 开始:安装、兼容性
├── product/                 # 产品:特性、示例、版本、路线图、生态
├── architecture/            # Aesir Architecture 文档(+ scripting-api/)
├── modules/                 # Aesir Modules 文档(+ scripting-api/)
├── changelog.md / faq.md / support.md
├── assets/                  # logo、favicon
└── stylesheets/             # extra.css(产品页样式)、api.css(API 页样式)
```

`architecture/` 与 `modules/` 的**物理路径不要改** —— Scripting API 的生成与导航重建脚本(`docs-site-rebuild-api-nav.py`)按这些路径读写,`package.json` 的 `documentationUrl` / `changelogUrl` 也指向它们。

## 内容维护约定

- **正文使用半角标点**(`,` `:` `;` `(` `)`),与主仓 README 的全角风格不同;从 README 拷贝内容时需要转换
- **中文标题必须带显式英文锚点** `## 标题 {#anchor}` —— slugify 会丢弃中文字符,含中文锚点的页内链接会构建失败
- 表格加 class 必须用 `<div class="x" markdown="1">` 包裹(`{: .cls }` 对表格无效)
- **版本落点标注**("`<版本>` 起 / 已于 `<版本>`")随发版替换为当前版本;`changelog.md` 的历史段永不改写
- 提交信息:`docs: 中文单行主题`;提交身份用 `zeriying@gmail.com`

## Scripting API 页的更新流程

API 页由包内 Script Doc Generator 反射生成,不手写:

1. 清空本地 `ScriptDocGenerator/Runestone`
2. 用编辑器脚本调用 `ScriptDocGeneratorUtility.AnalyzeMultipleAssemblies(...)` + `GenerateMultipleTypeDocs(...)`
3. `rsync -a --delete` 到 `docs/architecture/scripting-api/` 与 `docs/modules/scripting-api/`
4. 重跑索引 / 导航重建脚本(生成 `index.md` 与 `zensical.toml` 的 Scripting API 导航块)
5. `zensical build --strict` 验证

MIT License © 2026 Runestone Yuumix
