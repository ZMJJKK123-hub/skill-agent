from PIL import Image
import os

images = [
    r'微信图片_20260804233248_1072_38.png',
    r'af4ed4ae08a1dce35113914e08d98843.jpg',
    r'OIP-C.webp'
]

for img_path in images:
    if os.path.exists(img_path):
        img = Image.open(img_path)
        w, h = img.size
        mode = img.mode
        print(f'=== {img_path} ===')
        print(f'Size: {w}x{h}, Mode: {mode}')
        
        # Dominant colors
        img_small = img.resize((100, int(100*h/w))) if w > 100 else img
        colors = img_small.getcolors(maxcolors=10000)
        if colors:
            colors.sort(reverse=True, key=lambda x: x[0])
            print('Dominant colors:')
            for count, color in colors[:20]:
                if count > 10:
                    hex_c = '#' + ''.join(f'{c:02X}' for c in color[:3])
                    pct = round(count / (img_small.width * img_small.height) * 100, 1)
                    print(f'  {hex_c} - {pct}% ({count}px)')
        
        # Analyze sections (top, middle, bottom) 
        h3 = h // 3
        for idx, (y1, y2, name) in enumerate([
            (0, h3, 'top'),
            (h3, h3*2, 'middle'),
            (h3*2, h, 'bottom')
        ]):
            crop = img.crop((0, y1, w, y2))
            cs = crop.resize((50, 50)).getcolors(maxcolors=10000)
            if cs:
                cs.sort(reverse=True, key=lambda x: x[0])
                top_colors = [f'#{c[0]:02X}{c[1]:02X}{c[2]:02X}' for _, c in cs[:5] if _ > 5]
                print(f'  {name}: {top_colors[:3]}')
        
        print()
    else:
        print(f'NOT FOUND: {img_path}')
        print()