import re

with open('/Users/karthikeyachalla/ats stock predection/presentation/index.html', 'r') as f:
    content = f.read()

# Fix fragments that hide the whole slide
content = content.replace('class="h-full flex flex-col justify-center fragment fade-up"', 'class="h-full flex flex-col justify-center"')
content = content.replace('class="w-full h-full flex flex-col justify-center fragment fade-up items-center text-center px-20"', 'class="w-full h-full flex flex-col justify-center items-center text-center px-20"')
content = content.replace('class="px-20 py-10 w-full h-full flex flex-col justify-center fragment fade-up"', 'class="px-20 py-10 w-full h-full flex flex-col justify-center"')

# Change Colors to Rolex theme (Black, Dark Green, Gold)
content = content.replace("bg: '#0a0e1a',", "bg: '#000000',")
content = content.replace("surface: '#111827',", "surface: '#0a0f0d',")
content = content.replace("electric: '#00d4ff',", "electric: '#006039',") # Rolex Green
content = content.replace("gold: '#ffd700',", "gold: '#d4af37',") # Rolex Gold

content = content.replace("background-color: #0a0e1a;", "background-color: #000000;")
content = content.replace("radial-gradient(circle at 50% 100%, #111827 0%, #0a0e1a 100%)", "radial-gradient(circle at 50% 100%, #0a0f0d 0%, #000000 100%)")
content = content.replace("rgba(17, 24, 39,", "rgba(10, 15, 13,")

content = content.replace("background: #00d4ff;", "background: #006039;")
content = content.replace("rgba(0, 212, 255,", "rgba(0, 96, 57,")
content = content.replace("color: #00d4ff;", "color: #006039;")
content = content.replace("from-blue-500 to-brand-electric", "from-green-800 to-brand-electric")
content = content.replace("border-l-blue-400", "border-l-green-600")
content = content.replace("text-blue-400", "text-green-600")

with open('/Users/karthikeyachalla/ats stock predection/presentation/index.html', 'w') as f:
    f.write(content)

