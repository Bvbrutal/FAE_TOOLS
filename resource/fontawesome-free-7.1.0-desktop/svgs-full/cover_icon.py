import os
import cairosvg

# --- 配置 ---
SVG_DIR = "brands/"  # 放 SVG 文件的目录
PNG_DIR = "brands_png/"  # 输出 PNG 的目录
WIDTH = 32  # PNG 宽度
HEIGHT = 32  # PNG 高度
COLOR = None  # 可选：将 SVG 填充色替换为 COLOR，如 "red"，否则保持原色

# 创建输出目录
os.makedirs(PNG_DIR, exist_ok=True)


# 批量转换函数
def convert_svg_to_png(svg_dir, png_dir, width=32, height=32, color=None):
    for file_name in os.listdir(svg_dir):
        if file_name.lower().endswith(".svg"):
            svg_path = os.path.join(svg_dir, file_name)
            png_name = os.path.splitext(file_name)[0] + ".solid_png"
            png_path = os.path.join(png_dir, png_name)

            with open(svg_path, "r", encoding="utf-8") as f:
                svg_content = f.read()

            # 替换颜色（可选）
            if color:
                svg_content = svg_content.replace('fill="currentColor"', f'fill="{color}"')

            # 转 PNG
            cairosvg.svg2png(bytestring=svg_content.encode(), write_to=png_path,
                             output_width=width, output_height=height)
            print(f"✅ 转换完成: {file_name} -> {png_name}")


# 执行批量转换
convert_svg_to_png(SVG_DIR, PNG_DIR, WIDTH, HEIGHT, COLOR)
