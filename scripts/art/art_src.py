# ruff: noqa: E501  (SVG path data reads best on one line)
"""Pakkam illustration source. One SVG per drawing, styled with classes so the site can theme
and animate them; build.py turns these into web/js/art.js (site) and colour-resolved copies
for the Figma file. Style: 2px rounded lines, flat fills, simple faceless figures."""

# shared bits
def head(cx, cy, r, hair='dark'):
    hair_path = (f'<path class="hair-{hair}" d="M{cx - r} {cy - 1} Q{cx} {cy - r * 2.1} {cx + r} {cy - 1} Q{cx} {cy - r * 0.55} {cx - r} {cy - 1}Z"/>')
    return f'<circle class="skin" cx="{cx}" cy="{cy}" r="{r}"/>{hair_path}'

CATEGORY = {
    'women': '''<svg viewBox="0 0 96 72">
  <path class="ground" d="M10 66h76"/>
  <g class="figure">
    <path class="saree" d="M26 66C28 46 32 32 40 30C48 32 52 46 54 66Z"/>
    <path class="saree-border" d="M27 60h26"/>
    <path class="line" d="M36 31L52 47"/>
    <path class="line" d="M46 40Q56 44 63 42"/>
    <circle class="skin" cx="65" cy="42" r="3"/>
    ''' + head(40, 20, 7) + '''
    <circle class="hair-dark" cx="33" cy="17" r="3.5"/>
  </g>
  <g class="coin anim-drop"><circle class="gold" cx="66" cy="20" r="6"/><path class="line-thin" d="M63.5 20h5M66 17.5v5"/></g>
</svg>''',
    'farmers': '''<svg viewBox="0 0 96 72">
  <path class="ground" d="M8 66h80"/>
  <g class="figure">
    <path class="shirt" d="M22 66C23 46 27 34 34 32C41 34 45 46 46 66Z"/>
    <path class="line" d="M28 50h12"/>
    ''' + head(34, 21, 7) + '''
    <path class="turban" d="M26 17Q34 9 42 17Q34 14 26 17Z"/>
  </g>
  <g class="crop anim-sway">
    <path class="stem" d="M70 66V28"/>
    <path class="leaf" d="M70 52Q60 47 58 38Q68 40 70 52Z"/>
    <path class="leaf" d="M70 44Q80 39 82 30Q72 32 70 44Z"/>
    <ellipse class="grain" cx="70" cy="24" rx="3.5" ry="6"/>
  </g>
</svg>''',
    'pension': '''<svg viewBox="0 0 96 72">
  <path class="ground" d="M8 66h80"/>
  <g class="figure">
    <path class="shirt" d="M24 66C25 46 29 34 36 32C43 34 47 46 48 66Z"/>
    <path class="towel" d="M30 34L44 58"/>
    ''' + head(36, 21, 7, 'white') + '''
    <path class="line" d="M48 42L54 66"/>
  </g>
  <g class="calendar"><rect class="paper" x="60" y="16" width="26" height="24" rx="4"/><path class="accent-fill" d="M60 20a4 4 0 0 1 4-4h18a4 4 0 0 1 4 4v3H60Z"/><path class="line-thin" d="M65 29h4M71 29h4M77 29h4M65 34h4M71 34h4"/></g>
  <g class="coin anim-drop"><circle class="gold" cx="73" cy="52" r="6"/><path class="line-thin" d="M70.5 52h5M73 49.5v5"/></g>
</svg>''',
    'gas': '''<svg viewBox="0 0 96 72">
  <path class="ground" d="M8 66h80"/>
  <rect class="cylinder" x="16" y="24" width="26" height="42" rx="10"/>
  <rect class="cylinder" x="24" y="16" width="10" height="9" rx="2"/>
  <path class="line-thin" d="M18 38h22"/>
  <rect class="paper" x="50" y="52" width="36" height="9" rx="3"/>
  <path class="line" d="M58 52v-3h20v3"/>
  <g class="flame anim-flicker"><path class="fire" d="M68 48C61 41 64 33 68 26C72 33 75 41 68 48Z"/><path class="fire-in" d="M68 47C65 44 66 40 68 36C70 40 71 44 68 47Z"/></g>
</svg>''',
    'children': '''<svg viewBox="0 0 96 72">
  <path class="ground" d="M8 66h80"/>
  <g class="figure">
    <path class="kid-shirt" d="M20 66C21 52 24 44 30 42C36 44 39 52 40 66Z"/>
    ''' + head(30, 33, 6) + '''
  </g>
  <path class="paper" d="M50 50h34a17 12 0 0 1-34 0Z"/>
  <path class="line" d="M46 50h42"/>
  <g class="steam anim-steam"><path class="line-soft" d="M60 42q-3-5 0-10"/><path class="line-soft" d="M67 42q-3-5 0-10"/><path class="line-soft" d="M74 42q-3-5 0-10"/></g>
</svg>''',
    'health': '''<svg viewBox="0 0 96 72">
  <path class="tint line" d="M48 58C30 46 24 38 24 29C24 22 29 17 35 17C41 17 45 21 48 26C51 21 55 17 61 17C67 17 72 22 72 29C72 38 66 46 48 58Z"/>
  <path class="cross" d="M48 27v14M41 34h14"/>
  <path class="pulse anim-pulse" d="M6 64h22l5-8l6 14l5-10h46"/>
</svg>''',
    'education': '''<svg viewBox="0 0 96 72">
  <path class="paper" d="M48 62C38 56 24 56 14 58V30C24 28 38 28 48 34C58 28 72 28 82 30V58C72 56 58 56 48 62Z"/>
  <path class="line" d="M48 34V62"/>
  <path class="line-soft" d="M22 40h16M22 46h16M58 40h16M58 46h16"/>
  <path class="accent-fill" d="M48 6L76 16L48 26L20 16Z"/>
  <path class="line" d="M30 20v7c5 4 31 4 36 0v-7"/>
  <g class="tassel anim-swing"><path class="line" d="M74 17v10"/><circle class="gold" cx="74" cy="29" r="2.5"/></g>
</svg>''',
    'welfare': '''<svg viewBox="0 0 96 72">
  <path class="paper" d="M30 44L48 30L66 44V58H30Z"/>
  <rect class="tint line" x="43" y="46" width="10" height="12" rx="2"/>
  <path class="skin-line" d="M10 60Q28 70 48 64"/>
  <path class="skin-line" d="M86 60Q68 70 48 64"/>
  <path class="heart anim-float" d="M48 22C42 18 40 15 40 12C40 9.5 42 8 44 8C46 8 47 9 48 11C49 9 50 8 52 8C54 8 56 9.5 56 12C56 15 54 18 48 22Z"/>
</svg>''',
}

STEPS = {
    'step-pick': '''<svg viewBox="0 0 72 56">
  <rect class="paper" x="6" y="4" width="44" height="46" rx="6"/>
  <rect class="tint" x="10" y="20" width="36" height="9" rx="3"/>
  <path class="line-soft" d="M13 13h28M13 24.5h24M13 37h26"/>
  <path class="tap anim-tap cyan-fill line" d="M50 32l12 6l-5 2l4 7l-3 1.5l-4-7l-4 3Z"/>
</svg>''',
    'step-read': '''<svg viewBox="0 0 72 56">
  <rect class="paper" x="8" y="6" width="48" height="40" rx="6"/>
  <path class="accent-line" d="M14 16h20"/>
  <path class="line-soft" d="M14 25h34M14 32h28"/>
  <circle class="good" cx="54" cy="42" r="9"/>
  <path class="tick" d="M49.5 42l3 3l6-6"/>
</svg>''',
    'step-open': '''<svg viewBox="0 0 72 56">
  <path class="paper" d="M10 4h28l10 10v38H10Z"/>
  <path class="line" d="M38 4v10h10"/>
  <path class="line-soft" d="M16 20h24M16 36h20M16 42h24"/>
  <rect class="mark" x="15" y="25" width="26" height="6" rx="2"/>
  <g class="lens anim-peek"><circle class="cyan-ring" cx="52" cy="34" r="9"/><path class="cyan-line" d="M58.5 40.5l7 7"/></g>
</svg>''',
}

EMPTY = '''<svg viewBox="0 0 120 90">
  <path class="ground" d="M14 84h92"/>
  <path class="paper" d="M30 10h44l14 14v58H30Z"/>
  <path class="line" d="M74 10v14h14"/>
  <path class="line-soft" d="M38 34h34M38 44h26M38 54h30"/>
  <g class="lens anim-search"><circle class="cyan-ring tint-cyan" cx="72" cy="56" r="14"/><path class="cyan-line wide" d="M82 66l12 12"/></g>
</svg>'''

def person_seated(cx, base, hair='white', shirt='shirt', veshti=True, scale=1.0):
    s = scale
    top = base - 72 * s
    body = (f'<path class="{shirt}" d="M{cx - 20 * s} {base - 30 * s}C{cx - 18 * s} {top + 26 * s} {cx - 12 * s} {top + 16 * s} {cx} {top + 14 * s}'
            f'C{cx + 12 * s} {top + 16 * s} {cx + 18 * s} {top + 26 * s} {cx + 20 * s} {base - 30 * s}Z"/>')
    legs = (f'<path class="{"veshti" if veshti else "kid-pants"}" d="M{cx - 20 * s} {base - 30 * s}h{40 * s}v{28 * s}h-{40 * s}Z"/>'
            + (f'<path class="saree-border" d="M{cx - 20 * s} {base - 7 * s}h{40 * s}"/>' if veshti else ''))
    return legs + body + head(cx, top, 13 * s, hair)

CHAPTERS = {
    'ch1': '''<svg viewBox="0 0 320 200">
  <path class="ground" d="M20 186h280"/>
  <rect class="bench" x="58" y="152" width="200" height="9" rx="3"/>
  <path class="line" d="M74 161v24M242 161v24"/>
  <g class="figure grandpa">''' + person_seated(118, 152) + '''
    <path class="towel" d="M106 90L126 122"/>
    <path class="line" d="M130 112Q140 114 146 108"/>
    <g class="phone anim-shake"><rect class="device" x="142" y="92" width="18" height="30" rx="3"/><path class="tangle" d="M146 100l10 4l-9 4l9 4l-8 4"/></g>
  </g>
  <g class="figure child">''' + person_seated(206, 152, hair='dark', shirt='kid-shirt', veshti=False, scale=0.78) + '''
    <path class="line" d="M192 120Q182 116 170 116"/>
  </g>
  <g class="bubble b1"><rect class="paper" x="34" y="22" width="64" height="30" rx="14"/><path class="paper" d="M78 50l10 12l-2-12Z"/><circle class="dot" cx="54" cy="37" r="3"/><circle class="dot" cx="66" cy="37" r="3"/><circle class="dot" cx="78" cy="37" r="3"/></g>
  <g class="bubble b2"><rect class="paper" x="222" y="40" width="58" height="30" rx="14"/><path class="paper" d="M230 68l-6 12l14-12Z"/><path class="accent-line" d="M245 49a6 6 0 1 1 7 6c-1.5.6-1.5 2-1.5 3.5M250.5 63v.5"/></g>
</svg>''',
    'ch2': '''<svg viewBox="0 0 320 200">
  <defs><radialGradient id="ART_ORB" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="var(--accent-cyan)"/><stop offset="0.6" stop-color="var(--accent-2)"/><stop offset="1" stop-color="var(--accent-2)" stop-opacity="0.25"/></radialGradient></defs>
  <path class="ground" d="M20 186h280"/>
  <g class="figure elder">
    <path class="shirt" d="M56 186C58 140 64 116 80 112C96 116 102 140 104 186Z"/>
    <path class="towel" d="M68 116L92 150"/>
    ''' + head(80, 94, 13, 'white') + '''
    <path class="line" d="M96 132Q108 124 112 112"/>
    <rect class="device" x="108" y="94" width="16" height="26" rx="3"/>
  </g>
  <g class="waves">
    <path class="cyan-line w1" d="M134 100a14 14 0 0 1 0 20"/>
    <path class="cyan-line w2" d="M146 92a26 26 0 0 1 0 36"/>
    <path class="cyan-line w3" d="M158 84a38 38 0 0 1 0 52"/>
    <text class="tamil-letter l1" x="168" y="96">அ</text>
    <text class="tamil-letter l2" x="186" y="128">இ</text>
    <text class="tamil-letter l3" x="178" y="150">உ</text>
  </g>
  <g class="orb-wrap"><circle class="halo" cx="246" cy="96" r="44"/><circle class="orb" cx="246" cy="96" r="30" fill="url(#ART_ORB)"/></g>
  <g class="answer-page"><path class="paper" d="M226 140h32l8 8v30h-40Z"/><path class="line-soft" d="M232 154h24M232 168h18"/><rect class="mark" x="231" y="158" width="28" height="5" rx="2"/></g>
</svg>''',
    'ch3': '''<svg viewBox="0 0 320 200">
  <defs><radialGradient id="ART_ORB3" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="var(--accent-cyan)"/><stop offset="0.6" stop-color="var(--accent-2)"/><stop offset="1" stop-color="var(--accent-2)" stop-opacity="0.25"/></radialGradient></defs>
  <g class="doc d1"><path class="paper" d="M24 40h30l8 8v42H24Z"/><path class="line-soft" d="M30 56h24M30 64h20M30 72h24"/></g>
  <g class="doc d2"><path class="paper" d="M34 84h30l8 8v42H34Z"/><circle class="accent-ring" cx="53" cy="96" r="5"/><path class="line-soft" d="M40 110h24M40 118h18"/></g>
  <g class="doc d3"><path class="paper" d="M20 128h30l8 8v42H20Z"/><rect class="tint" x="26" y="142" width="24" height="7" rx="2"/><path class="line-soft" d="M26 156h24M26 164h16"/></g>
  <path class="cyan-line dash flow" d="M78 100H122"/>
  <g class="orb-wrap"><circle class="halo" cx="156" cy="100" r="40"/><circle class="orb" cx="156" cy="100" r="28" fill="url(#ART_ORB3)"/></g>
  <path class="cyan-line dash flow" d="M190 100H208"/>
  <g class="card">
    <rect class="paper2" x="212" y="62" width="94" height="76" rx="12"/>
    <path class="accent-line" d="M224 78h36"/>
    <path class="line-soft" d="M224 92h68M224 118h56"/>
    <rect class="mark" x="223" y="101" width="70" height="8" rx="3"/>
    <circle class="good" cx="300" cy="134" r="11"/>
    <path class="tick" d="M294.5 134l3.5 3.5l7-7"/>
  </g>
</svg>''',
    'ch4': '''<svg viewBox="0 0 320 200">
  <path class="ground" d="M40 186h240"/>
  <path class="paper" d="M160 62Q118 48 64 56V170Q118 162 160 176Z"/>
  <path class="paper" d="M160 62Q202 48 256 56V170Q202 162 160 176Z"/>
  <path class="line-soft" d="M80 80h60M80 94h54M80 108h60M80 122h46M80 136h56"/>
  <text class="tamil-word" x="208" y="122" text-anchor="middle">பக்கம்</text>
  <path class="accent-line" d="M184 136h48"/>
  <g class="turn"><path class="paper turning" d="M160 62Q118 48 64 56V170Q118 162 160 176Z"/><path class="line-soft" d="M80 88h56M80 104h50M80 120h56"/></g>
  <path class="line" d="M160 62V176"/>
</svg>''',
    'ch5': '''<svg viewBox="0 0 320 200">
  <path class="ground" d="M14 186h292"/>
  <g class="building">
    <path class="accent-fill-soft line" d="M24 76L74 50L124 76Z"/>
    <rect class="paper" x="30" y="76" width="88" height="8" rx="2"/>
    <path class="pillar" d="M40 88v58M58 88v58M76 88v58M94 88v58M110 88v58"/>
    <rect class="paper" x="26" y="146" width="96" height="10" rx="2"/>
    <rect class="paper" x="20" y="156" width="108" height="10" rx="2"/>
  </g>
  <path class="road" d="M128 168C170 194 200 132 236 160"/>
  <g class="home">
    <path class="paper" d="M232 120L264 94L296 120V170H232Z"/>
    <rect class="tint line" x="256" y="140" width="16" height="30" rx="2"/>
    <rect class="cyan-ring" x="240" y="128" width="12" height="12" rx="2"/>
  </g>
  <g class="walker">''' + head(150, 130, 8, 'dark') + '''<path class="kid-shirt" d="M140 168C141 152 145 142 150 140C155 142 159 152 160 168Z"/></g>
  <path class="heart float" d="M264 82C258 78 256 75 256 72C256 69.5 258 68 260 68C262 68 263 69 264 71C265 69 266 68 268 68C270 68 272 69.5 272 72C272 75 270 78 264 82Z"/>
</svg>''',
}

# Colours for the Figma copies (light theme), matching the site's tokens.
FIGMA_COLORS = {
    'line': ('none', '#52617A'), 'line-thin': ('none', '#52617A'), 'line-soft': ('none', '#8A97AE'),
    'ground': ('none', '#C9CFDD'), 'paper': ('#FFFFFF', '#52617A'), 'paper2': ('#FAF8FF', '#6D28D9'),
    'skin': ('#C98B5E', 'none'), 'hair-dark': ('#3B2F4A', 'none'), 'hair-white': ('#E8E6EF', 'none'),
    'saree': ('#8B5CF6', 'none'), 'saree-border': ('none', '#E0A526'), 'shirt': ('#F7F4EC', '#52617A'),
    'veshti': ('#F7F4EC', '#52617A'), 'kid-shirt': ('#079EAC', 'none'), 'kid-pants': ('#3B4A6B', 'none'),
    'towel': ('none', '#6D28D9'), 'turban': ('#E0A526', 'none'), 'gold': ('#E0A526', '#B7791F'),
    'stem': ('none', '#15803D'), 'leaf': ('#22C55E', 'none'), 'grain': ('#E0A526', 'none'),
    'accent-fill': ('#6D28D9', 'none'), 'accent-fill-soft': ('#EDE6FB', 'none'), 'accent-line': ('none', '#6D28D9'), 'accent-ring': ('none', '#6D28D9'),
    'cylinder': ('#EF4444', '#B91C1C'), 'fire': ('#F97316', 'none'), 'fire-in': ('#FDE68A', 'none'),
    'tint': ('#EDE6FB', 'none'), 'tint-cyan': ('#E0F6F8', 'none'), 'cross': ('none', '#FFFFFF'), 'pulse': ('none', '#079EAC'),
    'skin-line': ('none', '#C98B5E'), 'heart': ('#EC4899', 'none'), 'good': ('#16A34A', 'none'), 'tick': ('none', '#FFFFFF'),
    'mark': ('#BFEFF3', 'none'), 'cyan-fill': ('#079EAC', 'none'), 'cyan-line': ('none', '#079EAC'), 'cyan-ring': ('none', '#079EAC'),
    'device': ('#1F2937', 'none'), 'tangle': ('none', '#42DDEB'), 'bench': ('#D9B98C', '#8B6B3E'), 'dot': ('#8A97AE', 'none'),
    'tamil-letter': ('#079EAC', 'none'), 'tamil-word': ('#172440', 'none'), 'halo': ('#EDE6FB', 'none'),
    'pillar': ('none', '#52617A'), 'road': ('none', '#079EAC'), 'orb': ('#8B5CF6', 'none'),
}
