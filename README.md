# 奈绪 · Codex Desktop Pet

一个适用于 Codex 桌面端的 v2 动画桌宠。角色采用银白色低双马尾、宝石蓝眼睛和红色学院风水手服设计，包含 9 类标准动画以及 16 个顺时针注视方向。

![动作总览](previews/contact-sheet.png)

## 动画

- 待机、左右移动、招手和蹦跳
- 失败/委屈、等待/撒娇、工作中、检查结果
- 16 个鼠标注视方向
- 8×11 图集，单元格 192×208，`spriteVersionNumber: 2`

## 安装

在 PowerShell 中运行：

```powershell
.\install.ps1
```

脚本会把 `pet` 目录复制到 `$CODEX_HOME/pets/nao`。未设置 `CODEX_HOME` 时，使用 `$HOME/.codex/pets/nao`。安装后重新启动 Codex，再从桌宠选择器中选择“奈绪”。

也可以手动复制：

```text
pet/pet.json          -> ~/.codex/pets/nao/pet.json
pet/spritesheet.webp  -> ~/.codex/pets/nao/spritesheet.webp
```

## 动画触发

| 状态 | 触发场景 |
| --- | --- |
| idle | 空闲待机 |
| running-right / running-left | 左右拖动 |
| waving | 问候或提醒 |
| jumping | 活跃或庆祝事件 |
| failed | 任务失败、取消或阻塞 |
| waiting | 等待输入、确认或授权 |
| running | Codex 正在处理任务 |
| review | 任务完成并等待查看 |
| look directions | 鼠标在桌宠周围移动 |

## 文件

- `pet/`：可直接安装的桌宠包
- `previews/`：动作总览和动画示例
- `install.ps1`：Windows 安装脚本

## 许可与声明

安装脚本、配置和仓库文档采用 [MIT License](LICENSE)。角色图像属于非商业同人衍生创作；相关原作角色、名称及设定权利归各自权利人所有。详见 [NOTICE.md](NOTICE.md)。

