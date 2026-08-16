import re

with open('presentation/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Increase Base Typography sizes
html = html.replace('text-[3.5rem]', 'text-[4.5rem]')
html = html.replace('text-[2.2rem]', 'text-[3rem]')
html = html.replace('text-2xl', 'text-3xl')
html = html.replace('text-xl', 'text-2xl')
html = html.replace('text-lg', 'text-xl')
html = html.replace('text-sm', 'text-lg')
html = html.replace('h-full flex flex-col justify-center', 'h-full flex flex-col justify-center fragment fade-up')

# Ensure slides have transitions
html = html.replace('<section data-transition="slide"', '<section data-transition="zoom" data-transition-speed="slow"')

# Inject fragments for lists to trigger in-slide animations
html = html.replace('<li class="flex">', '<li class="flex fragment fade-left">')
html = html.replace('<li class="flex items-start">', '<li class="flex items-start fragment fade-left">')
html = html.replace('<div class="fade-in-up glass-panel', '<div class="fade-in-up glass-panel fragment zoom-in"')

# 9th Slide
thank_you_slide = """
            <!-- SLIDE 9: THANK YOU -->
            <section data-transition="zoom" class="h-full flex flex-col justify-center">
                <div class="px-20 py-10 w-full h-full flex flex-col justify-center items-center text-center">
                    <div class="w-32 h-32 mx-auto bg-brand-gold/20 border border-brand-gold/50 rounded-full flex items-center justify-center mb-10 fragment zoom-in">
                        <i class="fas fa-chart-line text-6xl text-brand-gold"></i>
                    </div>
                    <h1 class="text-[5rem] font-bold text-white mb-6 fragment fade-up">Thank You</h1>
                    <p class="text-3xl text-gray-400 max-w-4xl mx-auto fragment fade-up">
                        We are open to questions regarding the Hybrid EGARCH-LSTM pipeline, quantitative mapping, or architecture setup.
                    </p>
                </div>
            </section>
"""

# Insert Slide 9 right before </div></div> <!-- Initialization Scripts -->
html = html.replace('        </div>\n    </div>\n\n    <!-- Initialization Scripts -->', thank_you_slide + '\n        </div>\n    </div>\n\n    <!-- Initialization Scripts -->')

# Save
with open('presentation/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Patched presentation/index.html successfully")
