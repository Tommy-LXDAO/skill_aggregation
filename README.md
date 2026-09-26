# Skill 聚合平台

把好用的 AI Agent Skills 放在一起：**生图、股票与投资研究、论文写作、网页演示文稿**，一个入口发现，一句话安装。

本仓库采用「**本地 Skill + 外部仓库引用**」的聚合方式：自带 `generate-relay-image` 生图 Skill，其他项目直接引用原作者仓库，不重复搬运代码；安装时从各自来源获取。

## Skills 导航

| 分类 | Skill / 项目 | 能做什么 | 来源 |
| --- | --- | --- | --- |
| 🎨 生图 | **Generate Relay Image** | 读取当前 Codex 的模型服务配置和认证信息，通过配置的服务调用 `gpt-image-2`，将图片保存到本地 | [本仓库](./generate-relay-image/SKILL.md) |
| 📊 个股分析 | **UZI-Skill（游资 Skills）** | 汇集多种投资流派视角，进行个股深度分析、龙虎榜分析、估值与风险排查 | [wbh604/UZI-Skill](https://github.com/wbh604/UZI-Skill) |
| 🏛️ 价值投资 | **AI Berkshire** | 将巴菲特、芒格、段永平、李录的方法论组织为投资研究 Skill 合集，覆盖公司、财报、行业和持仓研究 | [xbtlin/ai-berkshire](https://github.com/xbtlin/ai-berkshire/blob/main/README.md) |
| 🔮 宏观研究 | **Digital Oracle 📈** | 从金融市场数据中提取信号，分析宏观事件趋势，形成概率估计与推理链 | [komako-workshop/digital-oracle](https://github.com/komako-workshop/digital-oracle) |
| 📝 论文写作 | **Research Writing Skill** | 支持选题与头脑风暴、文献综述、章节写作、图表、LaTeX 输出和投稿前自审 | [norman-bury/research-writing-skill](https://github.com/norman-bury/research-writing-skill) |
| 🎞️ 网页演示 | **Frontend Slides** | 创建带动画的 HTML 演示文稿，预览并选择视觉风格，也可将 PowerPoint 转成网页幻灯片 | [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) |

> 这里收录的是 **6 个项目来源**，不是只有 6 个独立 Skill：投资研究和论文写作仓库内还包含多个子 Skill。

## 一句话安装全部 Skills

### 方式一：直接对 AI 说（推荐）

把下面这句话复制给具备联网、终端和文件写入能力的 Codex 或其他 AI 编程助手：

```text
请读取 https://github.com/Tommy-LXDAO/skill_aggregation 的 README，按其中的 Skills 导航及各项目官方安装说明，为我当前使用的 AI Agent 安装全部六个项目的 Skills：本仓库的 generate-relay-image、wbh604/UZI-Skill、xbtlin/ai-berkshire、komako-workshop/digital-oracle、norman-bury/research-writing-skill、zarazhangrui/frontend-slides；包含合集中的子 Skill，保留必要的脚本和资源，遇到已有同名 Skill 先询问再覆盖，缺少依赖或密钥时提示我，最后列出安装成功、失败和待配置项，不要自动执行生图、投资分析或论文写作任务。
```

不同 Agent 的技能目录和插件机制不同，请让助手选择对应平台的安装方式，不要把 Claude Code 的插件命令直接当成 Codex 命令执行。

### 方式二：一条终端命令（Codex）

前置条件：安装 **Node.js / npm（提供 `npx`）和 Git**，能够访问 npm 与 GitHub。以下使用 [Vercel Skills CLI](https://github.com/vercel-labs/skills)，适用于 macOS / Linux 的 Bash、Zsh，以及 Windows 的 WSL / Git Bash，**不是 PowerShell 命令**。

```bash
(for source in Tommy-LXDAO/skill_aggregation wbh604/UZI-Skill https://github.com/xbtlin/ai-berkshire/tree/main/codex-skills komako-workshop/digital-oracle norman-bury/research-writing-skill zarazhangrui/frontend-slides; do npx --yes skills add "$source" --skill '*' --full-depth --agent codex --global --yes || exit $?; done)
```

这条命令会依次安装全部六个来源，任一来源失败即停止，不会把后续成功误当成全部成功。

- `--skill '*'`：选择发现的全部 Skills，而不是只选择一个。
- `--full-depth`：继续发现嵌套的子 Skill，避免在找到根目录的 `SKILL.md` 后提前停止。
- AI Berkshire 使用上游的 `codex-skills` 目录，安装可被 Skills CLI 识别的 `SKILL.md` 版本。
- `--agent codex --global`：为 Codex 安装到用户级技能位置，可跨项目使用；安装位置以 CLI 输出为准。
- `--yes`：跳过交互确认；**已有同名 Skill 可能被覆盖，请先备份自定义内容**。需要逐项确认时，去掉末尾的 `--yes`（前面的 `npx --yes` 只用于确认下载 CLI）。
- 这是 Skills 文件安装命令，**不会替你完成所有 Python 依赖、模型服务、数据源或 API 密钥配置**，也不等于上游的完整插件安装。
- AI Berkshire 的部分工作流还会引用仓库根目录的 `tools/`、`skills/` 和 `AGENTS.md`；仅安装 `codex-skills` 不包含这些共享资源。需要完整研究环境时，请采用上面的 AI 安装方式，按上游说明保留完整仓库并配置工具，不要将技能发现成功当作完整功能已就绪。

> 本仓库的生图目录需要先提交并推送到 GitHub，远程安装才能发现它。如果你正在尚未推送的本地仓库根目录验证，把命令中的第一个来源 `Tommy-LXDAO/skill_aggregation` 换成 `.` 即可。外部仓库仍从各自上游获取。

安装后可查看 Codex 的全局 Skills 清单：

```bash
npx skills list --global --agent codex
```

如果当前会话没有发现新技能，请重新打开会话，必要时重启对应客户端。**清单中出现 Skill 仅表示文件已安装，不表示其外部服务和运行依赖已验证。**

## 收录项目介绍

### 🎨 Generate Relay Image · 生图

本仓库自带的图片生成 Skill，读取 `~/.codex/config.toml` 中当前启用的 provider 与 Base URL，并按配置从环境变量或 `~/.codex/auth.json` 获取认证信息，调用该服务的图片生成接口。

- 固定使用 `gpt-image-2`，支持提示词、尺寸、质量、生成数量和输出格式等参数。
- 图片保存为本地文件，便于继续编辑、用于论文插图或演示文稿。
- 需要配置的服务实际支持该模型和图片生成接口；**安装 Skill 不包含 API 额度**。
- 不要将 API Key 写入本仓库或提交到 Git。

示例：`帮我生成一张未来城市主题的海报，保存到本地。`

→ [查看 Skill 与使用说明](./generate-relay-image/SKILL.md)

### 📊 UZI-Skill · 多流派个股分析

> *“66 个投资大佬帮你看盘，巴菲特、赵老哥和股海贼王终于坐在了同一张桌子上。”*

围绕 A 股、港股、美股的个股研究，结合投资评审团、游资与龙虎榜、估值和风险排查等工作流，从多个视角审视同一家公司。

示例：`用 UZI-Skill 分析贵州茅台，分别列出价值投资和游资视角的判断、依据与风险。`

→ [项目主页](https://github.com/wbh604/UZI-Skill) · [Codex 安装说明](https://github.com/wbh604/UZI-Skill/blob/main/.codex/INSTALL.md)

### 🏛️ AI Berkshire · AI 时代的价值投资研究框架

以巴菲特、芒格、段永平、李录的投资方法论为基础，组织公司研究、财报精读、行业筛选、管理层分析、投资检查清单、组合复盘等 Skills，适合系统性、证据驱动的长期投资研究。

示例：`用 AI Berkshire 研究这家公司，重点分析商业模式、护城河、现金流和估值假设。`

→ [项目介绍与完整 Skill 列表](https://github.com/xbtlin/ai-berkshire/blob/main/README.md) · [Codex Skills](https://github.com/xbtlin/ai-berkshire/tree/main/codex-skills)

### 🔮 Digital Oracle 📈 · 金融数据驱动的宏观研究

让 AI Agent 从金融市场数据中挖掘宏观事件的发展趋势，结合预测市场、利率、持仓、衍生品等信号，给出概率估计、场景分析和可追溯的推理过程。

示例：`用 Digital Oracle 分析黄金走势的关键市场信号，区分已知数据、推断和不确定性。`

→ [项目主页与安装说明](https://github.com/komako-workshop/digital-oracle)

### 📝 Research Writing Skill · 科研与论文写作

从研究目标和论文结构开始，逐步完成文献整理、章节写作、实验与图表规划、LaTeX 输出和自审。包含多个写作子 Skill，默认产物以 Markdown、纯文本、LaTeX 和图表脚本等项目文件为主，**不是直接交付排版完成的 Word 论文**。

示例：`用 Research Writing Skill 帮我规划毕业论文，先确认研究问题、现有数据和章节结构。`

→ [项目主页](https://github.com/norman-bury/research-writing-skill) · [Codex 安装说明](https://github.com/norman-bury/research-writing-skill/blob/main/.codex/INSTALL.md)

### 🎞️ Frontend Slides · HTML 演示文稿

面向网页演示文稿的制作与转换：可以从主题、提纲或现有 PPT 出发，先预览视觉风格，再生成带动画的 HTML 幻灯片。适合项目介绍、研究汇报和论文答辩展示。

示例：`用 Frontend Slides 把这份研究报告做成 10 页 HTML 演示文稿，先给我几个风格预览。`

→ [项目主页与安装说明](https://github.com/zarazhangrui/frontend-slides)

## 安装后的配置与边界

| 项目 | 使用前需要确认 |
| --- | --- |
| Generate Relay Image | 本机 Python 环境、Codex provider / Base URL / 认证配置，以及服务端是否支持对应图片接口；调用可能产生费用 |
| UZI-Skill | 按上游要求准备 Python 环境与 `requirements.txt` 依赖，确认所用金融数据源可访问 |
| AI Berkshire | 保留完整上游仓库及其共享 `tools/`、`skills/`、`AGENTS.md`；确认联网检索、数据获取和多 Agent 协作能力 |
| Digital Oracle | 上游要求的 `uv` / Python 环境；期权链功能还需要 `yfinance` 等对应依赖 |
| Research Writing Skill | 按任务准备文献、真实数据和模板；绘图、格式转换或本地 LaTeX 编译的依赖按需配置 |
| Frontend Slides | 浏览器预览能力；PPT 提取、PDF 导出等附加流程按上游说明准备依赖 |

- **第三方来源**：外部项目由各自作者维护，功能、目录结构、依赖与许可证以上游为准；本仓库的许可证不会替代外部项目的许可证。
- **安装安全**：安装前应审阅 Skill 指令与脚本；不要上传密钥、账户信息或其他敏感数据。
- **投资研究**：这些工具辅助整理信息和研究，不保证数据实时、分析正确或投资收益，不构成投资建议。
- **学术使用**：遵守所在机构的 AI 使用与学术诚信要求，人工核对引用、数据、实验和结论，不编造文献或结果。

## 仓库结构

```text
skill_aggregation/
├── README.md                 # 聚合导航与统一安装入口
├── LICENSE                   # 本仓库许可证
└── generate-relay-image/      # 本仓库自带的生图 Skill
    ├── SKILL.md
    ├── agents/
    └── scripts/
```

外部 Skills 通过上文链接和安装入口获取，不需要复制进本仓库。
