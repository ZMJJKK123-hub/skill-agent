from PIL import Image
import os

# 更详细地分析经验条图片
img = Image.open(r'微信图片_20260804233248_1072_38.png')
w, h = img.size
print(f'经验条图片尺寸: {w}x{h}')

# 逐像素分析颜色分布
pixels = list(img.getdata())
# 统计所有颜色
from collections import Counter
color_counts = Counter(pixels)
for color, count in color_counts.most_common(30):
    hex_c = '#' + ''.join(f'{c:02X}' for c in color)
    pct = round(count / len(pixels) * 100, 2)
    if pct > 0.3:
        print(f'  {hex_c} (R{color[0]} G{color[1]} B{color[2]}) - {pct}%')

# 分析水平方向颜色变化 - 看看经验条的渐变
print('\n水平方向颜色采样（每隔40px）：')
for x in range(0, w, 40):
    col = img.getpixel((min(x, w-1), h//2))
    hex_c = '#' + ''.join(f'{c:02X}' for c in col)
    print(f'  x={x}: {hex_c} R={col[0]} G={col[1]} B={col[2]}')

print('\n垂直方向颜色采样：')
for y in range(0, h, 5):
    col = img.getpixel((w//2, y))
    hex_c = '#' + ''.join(f'{c:02X}' for c in col)
    print(f'  y={y}: {hex_c} R={col[0]} G={col[1]} B={col[2]}')