"""
[变更日志]
修改时间：2026-09-17
AI模型：GLM (CodeBuddy)
修改内容：[初版：项目地图三层自检——清单存在性 / agent.md 引用存在性 / 活跃区反向扫描，另加 150 行体积预算断言；纯标准库零依赖]
用法:
  python scripts/test_project_map.py     # 独立运行（红灯退出码 1）
  pytest scripts/test_project_map.py     # 并入 pytest 流程自动收编
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "project-map.md"

# 忽略表（反向扫描）：构建产物/缓存/资源目录，与地图清单块内 "# 产物区/资源区" 标注共用定义
IGNORE = {"node_modules", "__pycache__", "dist", "build", "uploads", "data",
          "venv", "assets", "static", "images"}
# 结构活跃区：这些层级的子目录必须已在清单登记（再深层不反扫，由断言一管存在性）
ACTIVE_PARENTS = ["", "backend", "tob", "toc-new", "scripts", "docs", "history"]
# agent.md 启动协议引用的活跃文档白名单（协议加新引用时同步此处）
AGENT_REFERENCES = ["agent.md", "progress.md", "tech-spec.md",
                    "api-contract.md", "product.md", "project-map.md",
                    "scripts/test_project_map.py"]


def load_manifest():
    """唯一解析面：project-map.md 内的 ```map-paths 围栏块"""
    text = MAP.read_text(encoding="utf-8")
    m = re.search(r"```map-paths\s*\n(.*?)```", text, re.S)
    if not m:
        raise AssertionError("project-map.md 中未找到 ```map-paths 清单块")
    paths = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # 支持 "路径 # 行内注释" 格式，只取首段为路径
        paths.append(line.split("#")[0].strip().rstrip("/"))
    return paths


def test_project_map():
    errors = []
    manifest = load_manifest()

    # 断言一：清单声明路径全部存在（防"声明失效"）
    for p in manifest:
        if not (ROOT / p).exists():
            errors.append(f"[声明失效] 清单声明但不存在: {p}")

    # 断言二：agent.md 引用的核心文档存在（防"引用静默失效"）
    for p in AGENT_REFERENCES:
        if not (ROOT / p).exists():
            errors.append(f"[引用失效] agent.md 引用但缺失: {p}")

    # 断言三：反向扫描活跃区——未登记的新目录必须暴露（防"新增未登记"）
    declared = set(manifest)
    for parent in ACTIVE_PARENTS:
        base = ROOT if parent == "" else ROOT / parent
        if not base.is_dir():
            continue
        for child in base.iterdir():
            if not child.is_dir() or child.name.startswith(".") or child.name in IGNORE:
                continue
            rel = f"{parent}/{child.name}" if parent else child.name
            if rel not in declared:
                errors.append(f"[未登记] 活跃区新目录未在地图清单声明: {rel}/")

    # 断言四：体积预算红线（设计契约 ④）
    line_count = len(MAP.read_text(encoding="utf-8").splitlines())
    if line_count > 150:
        errors.append(f"[预算超限] project-map.md 共 {line_count} 行，超出 150 行红线，必须精简")

    if errors:
        raise AssertionError("\n".join(errors))
    print(f"OK: 地图四层断言全部通过（清单声明 {len(declared)} 项，共 {line_count} 行）")


if __name__ == "__main__":
    try:
        test_project_map()
    except AssertionError as e:
        print(str(e))
        sys.exit(1)
