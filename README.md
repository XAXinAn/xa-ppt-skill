# xa-ppt-skill

xa-ppt-skill 是一个通过自然语言生成图片嵌入式 PPT 的 skill 包。AI 负责理解需求、生成大纲、选择布局、匹配主题和生成页面内容；脚本负责渲染截图、组装 PPTX，并生成运行清单。

## 核心入口

- [skill 说明](./.claude/skills/xa-ppt/skill.md)
- [Codex skill](./.codex/skills/xa-ppt/SKILL.md)
- [设计系统](./design-system/design-system.json)
- [页面级规格](./deck-spec.json)

## 生成流程

```
自然语言 / 参考资料
        ↓
AI 生成 deck-spec.json
        ↓
validate -> review -> generate_html -> render -> build -> manifest
        ↓
输出 HTML / PNG / PPTX / manifest
```

## 一键流水线

```bash
python scripts/run_pipeline.py --allow-warn
```

严格模式：

```bash
python scripts/run_pipeline.py --stop-on-warn
```

## 目录说明

- `.claude/skills/xa-ppt/skill.md`：Claude 侧的完整工作流与生成规则
- `.codex/skills/xa-ppt/SKILL.md`：Codex 侧的入口与最小工作流
- `deck-spec.json`：当前主用的页面级中间规格文件
- `design-system/`：主题、布局与回归约束
- `schemas/`：结构校验 schema
- `scripts/`：校验、review、流水线脚本
- `src/`：HTML 生成、渲染和 PPTX 组装
- `output/`：生成物目录，默认不纳入版本管理

## 命名约定

- 当前主文件名是 `deck-spec.json`
- `presentation-content.json` 仅作为兼容别名保留给脚本回退
- 最终交付不应包含 `output/`、`__pycache__/`、`*.pyc` 这类临时文件

## 适用方式

这个仓库更适合作为“可执行 skill 包”来维护：

1. 先由 AI 读 `skill.md`
2. 再根据 `deck-spec.json` 和设计系统生成页面
3. 最后通过流水线输出可审阅的 PPTX

如果要修改视觉规则，优先改设计系统和布局约束；如果要修改生成习惯，优先改 `skill.md`。
