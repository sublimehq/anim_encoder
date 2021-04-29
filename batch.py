import os
import re

d = os.getcwd()
script_dir = os.path.dirname(os.path.realpath(__file__))

sections = [
    'linux_dark',
    'linux_dark@2x',
    'linux_light',
    'linux_light@2x',
    'osx_dark',
    'osx_dark@2x',
    'osx_light',
    'osx_light@2x',
    'windows_dark',
    'windows_dark@2x',
    'windows_light',
    'windows_light@2x',
]

js_files = {}
png_files = {}

for s in sections:
    js_files[s] = []
    png_files[s] = []


for sd in sorted(list(os.listdir(d))):
    sub_path = os.path.join(d, sd)
    if not os.path.isdir(sub_path):
        continue

    non_png = False
    for f in os.listdir(sub_path):
        if f == '.DS_Store':
            continue
        if not f.endswith('.png'):
            non_png = True
            break

    if non_png:
        print("Skipping folder %s since it contains files other than .png" % sub_path)
        continue

    js_file = os.path.join(d, sd + '_anim.js')
    png_file = os.path.join(d, sd + '_packed.png')

    if os.path.exists(js_file) and os.path.exists(png_file):
        print("Found existing animation for %s" % sub_path)
    else:
        print("Running anim_encoder.py in %s" % sub_path)
        os.system('%s/anim_encoder.py %s' % (script_dir, sd))


    name = sd
    is_2x = name.endswith('@2x')

    if is_2x:
        name = name[:-3]
    is_light = name.endswith('_light')
    is_dark = name.endswith('_dark')

    is_linux = name.startswith('linux_')
    is_mac = name.startswith('osx_') or name.startswith('mac_')
    is_win = name.startswith('windows_')

    group = 'linux'
    if is_win:
        group = 'windows'
    elif is_mac:
        group = 'osx'

    if is_dark:
        group += '_dark'
    else:
        group += '_light'

    if is_2x:
        group += '@2x'

    js_files[group].append(js_file)
    png_files[group].append(png_file)


for s in sections:
    combined_js_file = s + '.js'

    master_js = "animation_urls =\n"
    master_js += "[\n"

    for png_file in png_files[s]:
        png_filename = os.path.basename(png_file)
        master_js += "    \"/screencasts/%s\",\n" % png_filename

    master_js += "];\n"
    master_js += "\n"
    master_js += "animation_timelines =\n"
    master_js += "[\n"

    for js_file in js_files[s]:
        js = ''
        with open(js_file, 'r', encoding='utf-8') as f:
            js = f.read()
        js = re.sub(r'^[^=]+= ', '', js)
        master_js += "    %s,\n" % js

    master_js += "];\n"
    master_js += "\n"
    master_js += "transition()\n"


    with open(os.path.join(d, combined_js_file), 'w', encoding='utf-8') as f:
        f.write(master_js)
