"""
MLOps Tycoon – Build Your AI Factory
=====================================
Python + Pygame Game  |  Sound Edition 🔊

Install karo:
    pip install pygame requests

Chalao:
    python mlops_tycoon_sound.py

Sound files automatically generate honge 'sounds/' folder mein.
M key se mute/unmute, +/- se volume control.
"""

import pygame
import sys
import math
import random
import time
import threading
import os
import wave
import struct

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ─────────────────────────────────────────
#  🔊 SOUND GENERATION (no external files needed)
# ─────────────────────────────────────────
def _generate_sounds():
    """Programmatically generate all WAV sound files."""
    sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
    os.makedirs(sounds_dir, exist_ok=True)
    SR = 44100

    def write_wav(filename, samples):
        path = os.path.join(sounds_dir, filename)
        if os.path.exists(path):
            return  # already generated
        with wave.open(path, 'w') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
            data = struct.pack(f'<{len(samples)}h',
                               *[max(-32767, min(32767, int(s))) for s in samples])
            f.writeframes(data)

    def sine(freq, dur, amp=0.5):
        return [amp * 32767 * math.sin(2*math.pi*freq*i/SR) for i in range(int(dur*SR))]

    def fade(s, fin=0.01, fout=0.05):
        n = len(s)
        fi = int(fin*SR); fo = int(fout*SR)
        return [s[i] * (i/fi if i < fi else (n-i)/fo if i > n-fo else 1.0) for i in range(n)]

    def mix(*tracks):
        n = max(len(t) for t in tracks)
        return [sum(t[i] if i < len(t) else 0 for t in tracks)/len(tracks) for i in range(n)]

    # correct_drop – pleasant C-E-G chord
    write_wav("correct_drop.wav",
        fade(mix(sine(523.25,0.25,0.4), sine(659.25,0.25,0.3), sine(783.99,0.15,0.2))))

    # wrong_drop – dissonant buzz
    df2 = [int((0.5*math.sin(2*math.pi*180*i/SR)+0.3*math.sin(2*math.pi*270*i/SR*(1+i/SR)))
               * math.exp(-i/SR*8) * 32767) for i in range(int(0.3*SR))]
    write_wav("wrong_drop.wav", df2)

    # level_complete – ascending fanfare
    fc = []
    for freq, dur in [(523.25,0.1),(659.25,0.1),(783.99,0.1),(1046.5,0.35)]:
        fc += fade(sine(freq, dur, 0.5))
    write_wav("level_complete.wav", fc)

    # train_start – sci-fi power-up sweep
    sw = [int(0.4*math.sin(2*math.pi*(200+800*(i/SR/1.2)**2)*i/SR)
              * min(i/SR*4,1.0) * max(0,1-(i/SR-0.9)*5) * 32767)
          for i in range(int(1.2*SR))]
    write_wav("train_start.wav", sw)

    # train_complete – success ding sequence
    tc = []
    for freq, delay in [(880,0),(1100,0.08),(1320,0.16),(1760,0.28)]:
        chunk = [0]*int(delay*SR) + fade(sine(freq,0.18,0.35))
        tc = mix(tc, chunk) if tc else chunk
    write_wav("train_complete.wav", fade(tc, fout=0.1))

    # deploy_success – bright rising chime
    write_wav("deploy_success.wav",
        fade(mix(sine(1046.5,0.4,0.4),sine(1318.5,0.4,0.3),sine(1567.98,0.3,0.2)),fout=0.15))

    # deploy_fail – heavy thud
    df3 = [int((0.6*math.sin(2*math.pi*60*i/SR)+0.3*math.sin(2*math.pi*120*i/SR*(1+i/SR))
               +0.15*(random.random()-0.5)) * math.exp(-i/SR*5) * 32767)
           for i in range(int(0.5*SR))]
    write_wav("deploy_fail.wav", df3)

    # action_click – crisp UI click
    cl = [int((0.6*math.sin(2*math.pi*1200*i/SR)+0.3*math.sin(2*math.pi*2400*i/SR))
              * math.exp(-i/SR*40) * 32767) for i in range(int(0.06*SR))]
    write_wav("action_click.wav", cl)

    # drift_alert – pulsing alarm
    al = [int(0.5*(0.5+0.5*math.sin(2*math.pi*6*i/SR))
              * math.sin(2*math.pi*(440+80*math.sin(2*math.pi*4*i/SR))*i/SR)*32767)
          for i in range(int(1.5*SR))]
    write_wav("drift_alert.wav", fade(al, fin=0.02, fout=0.1))

    # ambient_hum – subtle background
    hm = [int((0.06*math.sin(2*math.pi*60*i/SR)+0.04*math.sin(2*math.pi*90*i/SR)
               +0.03*math.sin(2*math.pi*120*i/SR))*32767) for i in range(int(3.0*SR))]
    write_wav("ambient_hum.wav", hm)

    # xp_gain – quick sparkle
    write_wav("xp_gain.wav", fade(mix(sine(1760,0.08,0.3),sine(2093,0.08,0.2)),fout=0.04))

    # game_complete – victory melody
    vc = []
    for freq, dur in [(523.25,0.12),(523.25,0.12),(523.25,0.12),(415.30,0.09),
                      (466.16,0.09),(523.25,0.25),(466.16,0.12),(523.25,0.5)]:
        vc += fade(mix(sine(freq,dur,0.5), sine(freq*2,dur,0.2)), fin=0.01, fout=0.03)
    write_wav("game_complete.wav", vc)

    # server_crash – heavy distorted boom
    sc = [int((0.7*math.sin(2*math.pi*55*i/SR)+0.4*math.sin(2*math.pi*110*i/SR*(1+i/SR*0.5))
               +0.3*(random.random()-0.5)) * math.exp(-i/SR*3) * 32767)
          for i in range(int(0.8*SR))]
    write_wav("server_crash.wav", sc)

    # data_breach – eerie descending whine
    db2 = [int(0.5*math.sin(2*math.pi*(900-600*(i/SR/0.6))*i/SR)
               * math.exp(-i/SR*1.5) * 32767) for i in range(int(0.6*SR))]
    write_wav("data_breach.wav", db2)

    # competitor – energetic rising stab
    cp = mix(sine(392,0.18,0.5), sine(493.88,0.18,0.3), sine(587.33,0.12,0.2))
    write_wav("competitor.wav", fade(cp, fout=0.08))

    # quiz_correct – bright sparkle + chime
    qc = mix(sine(1046.5,0.12,0.4), sine(1318.5,0.12,0.3), sine(1760,0.08,0.2))
    write_wav("quiz_correct.wav", fade(qc, fout=0.06))

    # quiz_wrong – short buzz
    qw = [int(0.5*math.sin(2*math.pi*220*i/SR)*math.exp(-i/SR*12)*32767)
          for i in range(int(0.2*SR))]
    write_wav("quiz_wrong.wav", qw)

    return sounds_dir

# Generate sounds before pygame mixer starts
_SOUNDS_DIR = _generate_sounds()

# ─────────────────────────────────────────
#  INIT
# ─────────────────────────────────────────
pygame.init()
pygame.font.init()

W, H = 1280, 780
SIDEBAR_W = 290
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("MLOps Tycoon – Build Your AI Factory 🔊")
clock = pygame.time.Clock()

# ─────────────────────────────────────────
#  🔊 SOUND MANAGER
# ─────────────────────────────────────────
class SoundManager:
    """Lightweight sound manager with mute, volume, cooldown support."""

    SOUNDS = {
        "correct_drop":   "correct_drop.wav",
        "wrong_drop":     "wrong_drop.wav",
        "level_complete": "level_complete.wav",
        "train_start":    "train_start.wav",
        "train_complete": "train_complete.wav",
        "deploy_success": "deploy_success.wav",
        "deploy_fail":    "deploy_fail.wav",
        "action_click":   "action_click.wav",
        "drift_alert":    "drift_alert.wav",
        "ambient_hum":    "ambient_hum.wav",
        "xp_gain":        "xp_gain.wav",
        "game_complete":  "game_complete.wav",
        "server_crash":   "server_crash.wav",
        "data_breach":    "data_breach.wav",
        "competitor":     "competitor.wav",
        "quiz_correct":   "quiz_correct.wav",
        "quiz_wrong":     "quiz_wrong.wav",
    }

    def __init__(self, sounds_dir, master_vol=0.7):
        self._dir     = sounds_dir
        self._volume  = master_vol
        self._muted   = False
        self._cache   = {}
        self._cd      = {}   # cooldown: name → last ticks
        self._ok      = False
        self._music   = None

        try:
            pygame.mixer.pre_init(44100, -16, 1, 512)
            pygame.mixer.init()
            self._ok = True
            self._preload()
        except Exception as e:
            print(f"[SFX] mixer init failed: {e}")

    def _preload(self):
        for name, fname in self.SOUNDS.items():
            path = os.path.join(self._dir, fname)
            try:
                snd = pygame.mixer.Sound(path)
                snd.set_volume(self._volume)
                self._cache[name] = snd
            except Exception as e:
                print(f"[SFX] Cannot load {fname}: {e}")

    def play(self, name, cooldown_ms=80):
        if not self._ok or self._muted:
            return
        now = pygame.time.get_ticks()
        if now - self._cd.get(name, 0) < cooldown_ms:
            return
        self._cd[name] = now
        snd = self._cache.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def play_music(self, name, loops=-1):
        if not self._ok:
            return
        if self._music == name and pygame.mixer.music.get_busy():
            return
        path = os.path.join(self._dir, self.SOUNDS.get(name, ""))
        if not os.path.isfile(path):
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.0 if self._muted else self._volume * 0.35)
            pygame.mixer.music.play(loops, fade_ms=1200)
            self._music = name
        except Exception as e:
            print(f"[SFX] music error: {e}")

    def stop_music(self):
        if self._ok:
            try: pygame.mixer.music.fadeout(600)
            except Exception: pass
        self._music = None

    def toggle_mute(self):
        self._muted = not self._muted
        vol = 0.0 if self._muted else self._volume
        for snd in self._cache.values():
            snd.set_volume(vol)
        try:
            pygame.mixer.music.set_volume(0.0 if self._muted else self._volume * 0.35)
        except Exception:
            pass
        return self._muted

    def change_volume(self, delta):
        self._volume = max(0.0, min(1.0, self._volume + delta))
        if not self._muted:
            for snd in self._cache.values():
                snd.set_volume(self._volume)
            try:
                pygame.mixer.music.set_volume(self._volume * 0.35)
            except Exception:
                pass

    @property
    def muted(self): return self._muted
    @property
    def volume(self): return self._volume


sfx = SoundManager(_SOUNDS_DIR)
sfx.play_music("ambient_hum")   # 🔊 start ambient background loop

# ─────────────────────────────────────────
#  COLORS
# ─────────────────────────────────────────
BG        = (5,  10, 20)
PANEL     = (10, 22, 40)
BORDER    = (26, 58, 107)
ACCENT    = (0,  212, 255)
GREEN     = (0,  255, 159)
RED       = (255, 51, 102)
YELLOW    = (255, 204,  0)
PURPLE    = (180,  74, 255)
TEXT      = (200, 222, 255)
DIM       = (74, 106, 154)
WHITE     = (255, 255, 255)
BLACK     = (0,   0,   0)

# ─────────────────────────────────────────
#  FONTS
# ─────────────────────────────────────────
def load_font(size, bold=False):
    preferred = ["Arial", "Verdana", "Trebuchet MS", "Tahoma",
                 "Courier New", "DejaVu Sans", None]
    for name in preferred:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f: return f
        except Exception:
            continue
    return pygame.font.Font(None, size)

F_TINY  = load_font(15, bold=True)
F_SMALL = load_font(18, bold=True)
F_MED   = load_font(22, bold=True)
F_LARGE = load_font(30, bold=True)
F_TITLE = load_font(46, bold=True)
F_HUGE  = load_font(64, bold=True)

# ─────────────────────────────────────────
#  HOLOGRAM BACKGROUND
# ─────────────────────────────────────────
_COLS       = 52
_col_w      = 1280 // _COLS
_rain_y     = [random.randint(0, 780) for _ in range(_COLS)]
_rain_speed = [random.uniform(60, 160) for _ in range(_COLS)]
_rain_chars = list("01アイウエオカキクケコMLOPS01アイウ10データ訓練展開監視")

_orbs = [{
    "x": random.uniform(0, 1280), "y": random.uniform(0, 780),
    "vx": random.uniform(-18, 18), "vy": random.uniform(-18, 18),
    "r": random.randint(2, 5), "phase": random.uniform(0, math.pi*2),
    "color": random.choice([(0,212,255),(0,255,159),(180,74,255),(255,204,0)]),
} for _ in range(80)]

random.seed(42)
_circuits = []
for _ in range(18):
    sx2 = random.randint(0, 1280); sy2 = random.randint(100, 780)
    segs = []; cx2, cy2 = sx2, sy2
    for _ in range(random.randint(3, 6)):
        d = random.choice(["h","v"]); ln = random.randint(40,160)
        nx = cx2+random.choice([-1,1])*ln if d=="h" else cx2
        ny = cy2 if d=="h" else cy2+random.choice([-1,1])*ln
        segs.append(((cx2,cy2),(nx,ny))); cx2,cy2=nx,ny
    _circuits.append(segs)
random.seed()

_rings = [{"r": i*180, "speed": 40+i*15} for i in range(5)]

_static_bg = pygame.Surface((1280, 780))
for row in range(780):
    frac = row/780
    pygame.draw.rect(_static_bg, (int(3+frac*8),int(6+frac*12),int(15+frac*30)), (0,row,1280,1))

_F_MATRIX = pygame.font.Font(None, 14)

def draw_hologram_bg(surf, t):
    dt = 1/60
    surf.blit(pygame.transform.scale(_static_bg,(W,H)),(0,0))

    circ_surf = pygame.Surface((W,H),pygame.SRCALPHA)
    for segs in _circuits:
        pulse_pos = (t*0.4)%1.0
        for (x1,y1),(x2,y2) in segs:
            sx1=int(x1*W/1280);sy1=int(y1*H/780);sx2=int(x2*W/1280);sy2=int(y2*H/780)
            pygame.draw.line(circ_surf,(0,180,255,22),(sx1,sy1),(sx2,sy2),1)
            pygame.draw.circle(circ_surf,(0,220,255,40),(sx1,sy1),3)
        if segs:
            (x1,y1),(x2,y2)=segs[int(pulse_pos*len(segs))%len(segs)]
            px=int(x1*W/1280+(x2-x1)*W/1280*(pulse_pos*len(segs)%1))
            py=int(y1*H/780+(y2-y1)*H/780*(pulse_pos*len(segs)%1))
            pygame.draw.circle(circ_surf,(0,255,200,200),(px,py),4)
            pygame.draw.circle(circ_surf,(0,255,200,60),(px,py),8)
    surf.blit(circ_surf,(0,0))

    rain_surf = pygame.Surface((W,H),pygame.SRCALPHA)
    for i in range(_COLS):
        _rain_y[i] += _rain_speed[i]*dt
        if _rain_y[i]>H+40: _rain_y[i]=random.randint(-80,0); _rain_speed[i]=random.uniform(60,160)
        col_x=int(i*W/_COLS)
        for j in range(12):
            cy_r=int(_rain_y[i])-j*14
            if cy_r<0 or cy_r>H: continue
            alpha=max(0,200-j*18)
            char_col=(180,255,255,alpha) if j==0 else (0,max(0,140-j*10)+80,max(0,140-j*10)+120,alpha//2)
            ch=random.choice(_rain_chars)
            rendered=_F_MATRIX.render(ch,True,char_col[:3]); rendered.set_alpha(char_col[3])
            rain_surf.blit(rendered,(col_x,cy_r))
    surf.blit(rain_surf,(0,0))

    ring_surf=pygame.Surface((W,H),pygame.SRCALPHA)
    cx_r,cy_r2=W//2,H//2
    for ring in _rings:
        ring["r"]+=ring["speed"]*dt
        max_r=math.sqrt(W**2+H**2)/2
        if ring["r"]>max_r: ring["r"]=0
        frac=ring["r"]/max_r; alpha=int(max(0,60*(1-frac)))
        col_ring=(int(frac*80),int(180-frac*80),255,alpha)
        r_int=int(ring["r"])
        if r_int>0: pygame.draw.circle(ring_surf,col_ring,(cx_r,cy_r2),r_int,1)
    surf.blit(ring_surf,(0,0))

    orb_surf=pygame.Surface((W,H),pygame.SRCALPHA)
    for orb in _orbs:
        orb["x"]+=orb["vx"]*dt; orb["y"]+=orb["vy"]*dt
        if orb["x"]<0 or orb["x"]>W: orb["vx"]*=-1
        if orb["y"]<0 or orb["y"]>H: orb["vy"]*=-1
        orb["phase"]+=dt*1.5; flicker=0.5+0.5*math.sin(orb["phase"])
        base_alpha=int(50+flicker*100); oc=orb["color"]
        ox,oy=int(orb["x"]),int(orb["y"])
        for gr in range(orb["r"]+6,orb["r"],-2):
            pygame.draw.circle(orb_surf,(*oc,max(0,base_alpha-(gr-orb["r"])*18)),(ox,oy),gr)
        pygame.draw.circle(orb_surf,(*oc,base_alpha),(ox,oy),orb["r"])
    surf.blit(orb_surf,(0,0))

    scan_surf=pygame.Surface((W,H),pygame.SRCALPHA)
    for sy3 in range(int(t*30)%4,H,4):
        pygame.draw.line(scan_surf,(0,200,255,6),(0,sy3),(W,sy3),1)
    surf.blit(scan_surf,(0,0))

    vig_surf=pygame.Surface((W,H),pygame.SRCALPHA)
    vp=0.7+0.3*math.sin(t*1.2)
    for i in range(40):
        a=int((1-i/40)*35*vp)
        pygame.draw.line(vig_surf,(0,200,255,a),(0,110+i),(W,110+i),1)
        pygame.draw.line(vig_surf,(0,200,255,a),(0,H-i-1),(W,H-i-1),1)
    for i in range(30):
        a=int((1-i/30)*25*vp)
        pygame.draw.line(vig_surf,(0,160,255,a),(i,110),(i,H),1)
        pygame.draw.line(vig_surf,(0,160,255,a),(W-SIDEBAR_W-i,110),(W-SIDEBAR_W-i,H),1)
    surf.blit(vig_surf,(0,0))

    br_surf=pygame.Surface((W,H),pygame.SRCALPHA)
    br_alpha=int(120+60*math.sin(t*2)); bc=(0,220,255,br_alpha); blen=30
    for (bx,by,xd,yd) in [(10,110,1,1),(W-SIDEBAR_W-10,110,-1,1),(10,H-10,1,-1),(W-SIDEBAR_W-10,H-10,-1,-1)]:
        pygame.draw.line(br_surf,bc,(bx,by),(bx+xd*blen,by),2)
        pygame.draw.line(br_surf,bc,(bx,by),(bx,by+yd*blen),2)
    surf.blit(br_surf,(0,0))

# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────
def draw_rect(surf, color, rect, radius=6, alpha=255):
    s=pygame.Surface((rect[2],rect[3]),pygame.SRCALPHA)
    pygame.draw.rect(s,(*color,alpha),(0,0,rect[2],rect[3]),border_radius=radius)
    surf.blit(s,(rect[0],rect[1]))

def draw_border_rect(surf, color, rect, width=1, radius=6):
    pygame.draw.rect(surf,color,rect,width,border_radius=radius)

def draw_text(surf, text, font, color, x, y, center=False, right=False):
    rendered=font.render(str(text),True,color)
    rx=x-rendered.get_width()//2 if center else (x-rendered.get_width() if right else x)
    shadow=font.render(str(text),True,(0,0,0))
    surf.blit(shadow,(rx+2,y+2)); surf.blit(rendered,(rx,y))
    return rendered.get_width()

def draw_text_wrap(surf, text, font, color, x, y, max_width, line_height=26):
    words=text.split(); lines=[]; current=""
    for w in words:
        test=current+(" " if current else "")+w
        if font.size(test)[0]<=max_width: current=test
        else:
            if current: lines.append(current)
            current=w
    if current: lines.append(current)
    for i,line in enumerate(lines):
        draw_text(surf,line,font,color,x,y+i*line_height)
    return len(lines)*line_height

def lerp_color(c1, c2, t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

def draw_glow_rect(surf, color, rect, radius=6):
    for i in range(4,0,-1):
        expanded=(rect[0]-i,rect[1]-i,rect[2]+i*2,rect[3]+i*2)
        draw_rect(surf,color,expanded,radius+i,30-i*6)
    draw_rect(surf,color,rect,radius,40)
    draw_border_rect(surf,color,rect,1,radius)

# ─────────────────────────────────────────
#  🔊 SOUND HUD (mute button + volume bar)
# ─────────────────────────────────────────
def draw_sound_hud(surf):
    """Draw mute toggle + volume indicator in top-right of game area."""
    hud_x = W - SIDEBAR_W - 180
    hud_y = 12
    # Volume bar background
    bar_w = 80; bar_h = 10
    bx = hud_x + 28; by = hud_y + 14
    draw_rect(surf, BORDER, (bx, by, bar_w, bar_h), 3)
    if not sfx.muted:
        fill = int(bar_w * sfx.volume)
        col = lerp_color(DIM, ACCENT, sfx.volume)
        draw_rect(surf, col, (bx, by, fill, bar_h), 3)
    # Mute icon button
    mute_rect = pygame.Rect(hud_x, hud_y+6, 22, 22)
    icon = "🔇" if sfx.muted else "🔊"
    draw_text(surf, icon, F_SMALL, DIM if sfx.muted else ACCENT, hud_x, hud_y+6)
    # +/- labels hint
    draw_text(surf, "+/-  vol  M mute", F_TINY, DIM, bx, by+14)
    return mute_rect

# ─────────────────────────────────────────
#  NOTIFICATION
# ─────────────────────────────────────────
class Notification:
    def __init__(self):
        self.msg=""; self.color=ACCENT; self.timer=0; self.alpha=0

    def show(self, msg, color=ACCENT, duration=2.5):
        self.msg=msg; self.color=color; self.timer=duration; self.alpha=255

    def update(self, dt):
        if self.timer>0:
            self.timer-=dt
            self.alpha=int(255*(self.timer/0.5)) if self.timer<0.5 else 255

    def draw(self, surf):
        if self.timer<=0 or not self.msg: return
        rendered=F_MED.render(self.msg,True,self.color)
        rw=rendered.get_width()+40; rh=44
        rx=(W-rw)//2; ry=75
        s=pygame.Surface((rw,rh),pygame.SRCALPHA)
        pygame.draw.rect(s,(*PANEL,self.alpha),(0,0,rw,rh),border_radius=8)
        pygame.draw.rect(s,(*self.color,self.alpha),(0,0,rw,rh),2,border_radius=8)
        s.blit(rendered,(20,(rh-rendered.get_height())//2))
        surf.blit(s,(rx,ry))

notif = Notification()

# ─────────────────────────────────────────
#  SCORE EFFECTS
# ─────────────────────────────────────────
score_effects = []

def add_score_effect(x, y, text, color=GREEN):
    score_effects.append({"x":x,"y":y,"text":text,"color":color,"life":1.0,"vy":-60})

def update_score_effects(dt):
    for e in score_effects[:]:
        e["life"]-=dt; e["y"]+=e["vy"]*dt
        if e["life"]<=0: score_effects.remove(e)

def draw_score_effects(surf):
    for e in score_effects:
        rendered=F_MED.render(e["text"],True,e["color"])
        s=pygame.Surface(rendered.get_size(),pygame.SRCALPHA)
        s.fill((0,0,0,0)); s.blit(rendered,(0,0)); s.set_alpha(int(255*e["life"]))
        surf.blit(s,(int(e["x"]),int(e["y"])))

# ─────────────────────────────────────────
#  GAME STATE
# ─────────────────────────────────────────
state = {
    "score":0,"xp":0,"screen":"welcome",
    "unlocked":{1:True,2:False,3:False,4:False},
    "model_acc":0.0,
    "l1":{"clean":0,"corrupt":0,"biased":0,"errors":0,"goal":{"clean":8,"corrupt":5,"biased":5},"done":False},
    "l2":{"epochs":50,"lr_raw":10,"acc":0.0,"trained":False,"done":False,"graph_pts":[],"training":False,"train_timer":0,"train_total":0},
    "l3":{"choice":None,"done":False,"result":None},
    "l4":{"drift_acc":75.0,"actions":{"collect":False,"retrain":False,"rollback":False},"done":False,"pts":[],"complaint_timer":0},
    "mistakes":[],"deploy_attempts":0,"train_attempts":0,
    "_drift_alerted": False,   # 🔊 track if drift_alert was played
}

def add_score(pts):
    state["score"]+=pts; state["xp"]=min(state["xp"]+pts,1000)
    sfx.play("xp_gain", cooldown_ms=300)   # 🔊

# ═════════════════════════════════════════
#  🎲 RANDOM EVENTS SYSTEM
# ═════════════════════════════════════════
RANDOM_EVENTS = [
    {
        "id": "server_crash",
        "title": "💥 SERVER CRASH!",
        "desc": "Production server down ho gaya! Emergency maintenance mode.",
        "detail": "Tumhara deployed model temporarily offline hai. Quick response zaroori hai!",
        "color_key": "RED",
        "penalty": -100,
        "choice_a": "Emergency Restart Karo (+50 pts, 8 sec wait)",
        "choice_b": "Rollback to Backup (+20 pts, instant)",
        "result_a": ("Server restart successful! Model wapas online hai.", 50, "server_crash"),
        "result_b": ("Backup version restore hua. Stable but older model.", 20, "server_crash"),
        "levels": [3, 4],
        "sound": "server_crash",
    },
    {
        "id": "data_breach",
        "title": "🔓 DATA BREACH ALERT!",
        "desc": "Training data mein unauthorized access detect hua!",
        "detail": "Sensitive user data potentially exposed. GDPR compliance at risk!",
        "color_key": "RED",
        "penalty": -150,
        "choice_a": "Isolate & Patch System (+80 pts)",
        "choice_b": "Audit & Notify Users (+60 pts, good PR)",
        "result_a": ("System patched! Security restored. Data safe hai.", 80, "action_click"),
        "result_b": ("Transparent response! Users trust badhaa. +60 pts.", 60, "action_click"),
        "levels": [2, 3, 4],
        "sound": "data_breach",
    },
    {
        "id": "competitor",
        "title": "🏆 COMPETITOR LAUNCHED!",
        "desc": "Rival company ne tumse better model launch kar diya!",
        "detail": "Users switch kar rahe hain. Tumhe apna model improve karna hoga!",
        "color_key": "YELLOW",
        "penalty": -80,
        "choice_a": "Fast Retrain with New Data (+100 pts)",
        "choice_b": "Add Unique Features (+70 pts)",
        "result_a": ("Retrained model ne competitor ko beat kar diya! 🚀", 100, "competitor"),
        "result_b": ("Unique features add hue! Users wapas aaye. 💡", 70, "competitor"),
        "levels": [3, 4],
        "sound": "competitor",
    },
    {
        "id": "gpu_shortage",
        "title": "⚡ GPU SHORTAGE!",
        "desc": "Cloud GPU prices 3x ho gayi! Training budget crisis.",
        "detail": "Training cost budget se bahar ja raha hai. Smart choices karo!",
        "color_key": "YELLOW",
        "penalty": -60,
        "choice_a": "Smaller Model Train Karo (+50 pts, faster)",
        "choice_b": "Spot Instances Use Karo (+40 pts, cheaper)",
        "result_a": ("Efficient model ready! Kam resources mein zyada performance.", 50, "action_click"),
        "result_b": ("Spot instances se 70% cost save hua! Smart move.", 40, "action_click"),
        "levels": [2, 3],
        "sound": "wrong_drop",
    },
]

random_event_state = {
    "active": False,
    "event": None,
    "timer": 0,
    "cooldown": 0,       # seconds before next event can fire
    "choice_made": None,
    "result_msg": "",
    "result_pts": 0,
    "result_timer": 0,
    "waiting_a": False,
    "wait_timer": 0,
    "dismissed": False,
}

def maybe_fire_event(screen_name, dt):
    re = random_event_state
    if re["active"] or re["dismissed"]: return
    re["cooldown"] = max(0, re["cooldown"] - dt)
    if re["cooldown"] > 0: return
    # Fire with ~1.2% chance per second (avg every ~83s, on eligible levels)
    lvl_num = int(screen_name[-1]) if screen_name.startswith("level") else 0
    eligible = [e for e in RANDOM_EVENTS if lvl_num in e["levels"]]
    if not eligible: return
    if random.random() < 0.012 * dt * 60:
        ev = random.choice(eligible)
        re["active"] = True
        re["event"] = ev
        re["timer"] = 0
        re["choice_made"] = None
        re["result_msg"] = ""
        re["waiting_a"] = False
        re["wait_timer"] = 0
        re["dismissed"] = False
        state["score"] = max(0, state["score"] + ev["penalty"])
        sfx.play(ev["sound"], cooldown_ms=0)
        aira_speak(f"⚠️ Random Event! {ev['title']} — {ev['desc']}")

def update_event(dt):
    re = random_event_state
    if not re["active"]: return
    re["timer"] += dt
    if re["waiting_a"]:
        re["wait_timer"] -= dt
        if re["wait_timer"] <= 0:
            re["waiting_a"] = False
            _finish_event_choice_a()
    if re["result_timer"] > 0:
        re["result_timer"] -= dt
        if re["result_timer"] <= 0:
            re["active"] = False
            re["cooldown"] = random.uniform(60, 120)

def _finish_event_choice_a():
    re = random_event_state; ev = re["event"]
    msg, pts, snd = ev["result_a"]
    add_score(pts); re["result_msg"] = msg; re["result_pts"] = pts
    re["result_timer"] = 3.0; sfx.play(snd, cooldown_ms=0)

def handle_event_choice(choice):
    re = random_event_state; ev = re["event"]
    if re["choice_made"]: return
    re["choice_made"] = choice
    sfx.play("action_click")
    if choice == "a":
        if "8 sec" in ev["choice_a"]:
            re["waiting_a"] = True; re["wait_timer"] = 2.0
            re["result_msg"] = "⏳ Restarting... please wait"
        else:
            _finish_event_choice_a()
    else:
        msg, pts, snd = ev["result_b"]
        add_score(pts); re["result_msg"] = msg; re["result_pts"] = pts
        re["result_timer"] = 3.0; sfx.play(snd, cooldown_ms=0)

_event_btn_a = None
_event_btn_b = None

def draw_random_event(surf):
    global _event_btn_a, _event_btn_b
    re = random_event_state
    if not re["active"]: return
    ev = re["event"]
    colors = {"RED": RED, "YELLOW": YELLOW, "GREEN": GREEN}
    col = colors.get(ev["color_key"], RED)

    # Full overlay
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160)); surf.blit(ov, (0, 0))

    mw, mh = 640, 340; mx2 = (W - mw)//2; my2 = (H - mh)//2

    # Pulsing border
    pulse = 0.6 + 0.4*math.sin(time.time()*4)
    pcol = lerp_color(col, WHITE, pulse*0.3)

    draw_rect(surf, PANEL, (mx2,my2,mw,mh), 12)
    draw_border_rect(surf, pcol, (mx2,my2,mw,mh), 3, 12)

    # Title
    draw_text(surf, ev["title"], F_LARGE, col, mx2+mw//2, my2+16, center=True)
    # Warning bar
    draw_rect(surf, col, (mx2+20, my2+56, mw-40, 4), 2, 80)

    draw_text_wrap(surf, ev["desc"],   F_MED,   TEXT, mx2+24, my2+68,  mw-48, 28)
    draw_text_wrap(surf, ev["detail"], F_SMALL, DIM,  mx2+24, my2+102, mw-48, 22)
    draw_text(surf, f"Penalty: {ev['penalty']} pts already applied", F_TINY, col, mx2+mw//2, my2+140, center=True)

    if re["result_msg"]:
        rcol = GREEN if re["result_pts"]>0 else RED
        draw_rect(surf, rcol, (mx2+20, my2+160, mw-40, 80), 8, 30)
        draw_border_rect(surf, rcol, (mx2+20, my2+160, mw-40, 80), 2, 8)
        draw_text(surf, re["result_msg"], F_SMALL, rcol, mx2+mw//2, my2+178, center=True)
        draw_text(surf, f"+{re['result_pts']} pts recovered!", F_MED, rcol, mx2+mw//2, my2+210, center=True)
        return

    if re["waiting_a"]:
        draw_rect(surf, YELLOW, (mx2+20, my2+160, mw-40, 60), 8, 30)
        prog = 1.0 - re["wait_timer"]/2.0
        draw_rect(surf, YELLOW, (mx2+20, my2+210, int((mw-40)*prog), 8), 4)
        draw_text(surf, "⏳ " + re["result_msg"], F_SMALL, YELLOW, mx2+mw//2, my2+175, center=True)
        return

    if not re["choice_made"]:
        bw2 = (mw-60)//2
        _event_btn_a = pygame.Rect(mx2+20,       my2+mh-90, bw2, 70)
        _event_btn_b = pygame.Rect(mx2+40+bw2,   my2+mh-90, bw2, 70)
        draw_glow_rect(surf, GREEN,  (_event_btn_a.x, _event_btn_a.y, bw2, 70), 8)
        draw_glow_rect(surf, ACCENT, (_event_btn_b.x, _event_btn_b.y, bw2, 70), 8)
        draw_text_wrap(surf, ev["choice_a"], F_TINY, BLACK, _event_btn_a.x+8, _event_btn_a.y+10, bw2-16, 18)
        draw_text_wrap(surf, ev["choice_b"], F_TINY, BLACK, _event_btn_b.x+8, _event_btn_b.y+10, bw2-16, 18)


# ═════════════════════════════════════════
#  📚 TUTORIAL OVERLAY SYSTEM
# ═════════════════════════════════════════
TUTORIALS = {
    "level1": [
        {"arrow_to": (400, 300), "dir": "down",
         "text": "Data items yahaan stream hote hain!\nInhein drag karo sahi bucket mein."},
        {"arrow_to": (120, 650), "dir": "up",
         "text": "Clean Data Bucket:\nAccurate, complete, unbiased data."},
        {"arrow_to": (340, 650), "dir": "up",
         "text": "Corrupt Bucket:\nNull values, malformed data, errors."},
        {"arrow_to": (560, 650), "dir": "up",
         "text": "Biased Bucket:\nLimited diversity, one-sided data."},
    ],
    "level2": [
        {"arrow_to": (200, 300), "dir": "right",
         "text": "Epochs Slider:\nZyada = zyada learning\n(but overfitting risk!)"},
        {"arrow_to": (200, 400), "dir": "right",
         "text": "Learning Rate:\nBahut bada = unstable\nBahut chota = very slow"},
        {"arrow_to": (700, 220), "dir": "left",
         "text": "Accuracy Meter:\n65-85% = Sweet Spot!\nIs zone mein laao."},
        {"arrow_to": (200, 600), "dir": "up",
         "text": "TRAIN button:\nSirf tab dabao jab\naccuracy 65-85% mein ho!"},
    ],
    "level3": [
        {"arrow_to": (180, 300), "dir": "down",
         "text": "Local Machine:\nSafe testing environment.\nKoi risk nahi!"},
        {"arrow_to": (480, 300), "dir": "down",
         "text": "Cloud Server:\n70%+ accuracy chahiye.\n10,000+ users!"},
        {"arrow_to": (780, 300), "dir": "down",
         "text": "Mobile App:\n80%+ accuracy chahiye.\nEdge deployment!"},
    ],
    "level4": [
        {"arrow_to": (220, 350), "dir": "right",
         "text": "Performance Graph:\nAccuracy girna = Data Drift!\nReal-time monitor karo."},
        {"arrow_to": (700, 450), "dir": "left",
         "text": "Teeno Actions karo:\nCollect → Retrain → Rollback\nSab zaroori hain!"},
    ],
}

tutorial_state = {
    "shown": set(),          # levels jahan tutorial already show hua
    "active": False,
    "level": None,
    "step": 0,
    "alpha": 0,              # fade-in
    "btn_rect": None,
}

def maybe_start_tutorial(level_key):
    ts = tutorial_state
    if level_key not in TUTORIALS: return
    if level_key in ts["shown"]: return
    ts["shown"].add(level_key)
    ts["active"] = True
    ts["level"]  = level_key
    ts["step"]   = 0
    ts["alpha"]  = 0

def advance_tutorial():
    ts = tutorial_state
    steps = TUTORIALS.get(ts["level"], [])
    ts["step"] += 1
    if ts["step"] >= len(steps):
        ts["active"] = False
        ts["level"]  = None
    sfx.play("action_click")

def draw_tutorial(surf):
    ts = tutorial_state
    if not ts["active"]: return None
    steps = TUTORIALS.get(ts["level"], [])
    if ts["step"] >= len(steps): ts["active"]=False; return None

    # Fade in
    ts["alpha"] = min(255, ts["alpha"] + 12)
    step = steps[ts["step"]]
    ax, ay = step["arrow_to"]
    direction = step["dir"]
    text_lines = step["text"].split("\n")

    # Tooltip box size
    tw = 240; line_h = 22
    th = len(text_lines) * line_h + 44

    # Position tooltip away from arrow target
    offset = 28
    if direction == "down":
        tx, ty = ax - tw//2, ay + offset
    elif direction == "up":
        tx, ty = ax - tw//2, ay - th - offset
    elif direction == "right":
        tx, ty = ax + offset, ay - th//2
    else:  # left
        tx, ty = ax - tw - offset, ay - th//2

    tx = max(10, min(tx, W - SIDEBAR_W - tw - 10))
    ty = max(120, min(ty, H - th - 10))

    # Animated pulse on arrow target
    pulse = 0.5 + 0.5 * math.sin(time.time() * 4)
    ring_r = int(20 + pulse * 10)
    ring_alpha = int(180 * (1 - pulse * 0.4))

    ring_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.circle(ring_surf, (0, 255, 200, ring_alpha), (ax, ay), ring_r, 3)
    pygame.draw.circle(ring_surf, (0, 255, 200, 220), (ax, ay), 7)
    pygame.draw.circle(ring_surf, WHITE, (ax, ay), 4)
    ring_surf.set_alpha(ts["alpha"])
    surf.blit(ring_surf, (0, 0))

    # Arrow line from tooltip to target
    tooltip_cx = tx + tw//2
    tooltip_cy = ty if direction in ["down","right","left"] else ty+th
    arrow_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    arrow_surf.set_alpha(ts["alpha"])
    col_arrow = (0, 255, 200, 180)
    # Draw dashed line
    dx, dy = ax - tooltip_cx, ay - tooltip_cy
    dist = max(1, math.sqrt(dx*dx + dy*dy))
    steps_n = int(dist / 8)
    for si in range(0, steps_n, 2):
        fx = tooltip_cx + dx*(si/steps_n); fy = tooltip_cy + dy*(si/steps_n)
        ex = tooltip_cx + dx*min(1,(si+1)/steps_n); ey = tooltip_cy + dy*min(1,(si+1)/steps_n)
        pygame.draw.line(arrow_surf, col_arrow, (int(fx),int(fy)), (int(ex),int(ey)), 2)
    surf.blit(arrow_surf, (0, 0))

    # Tooltip box
    box_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
    pygame.draw.rect(box_surf, (*PANEL, min(ts["alpha"], 220)), (0,0,tw,th), border_radius=10)
    pygame.draw.rect(box_surf, (*ACCENT, min(ts["alpha"], 255)), (0,0,tw,th), 2, border_radius=10)
    for i, line in enumerate(text_lines):
        rendered = F_SMALL.render(line, True, TEXT)
        box_surf.blit(rendered, (10, 8 + i * line_h))
    # Step indicator dots
    total_steps = len(steps)
    dot_y = th - 22; dot_spacing = 14
    dot_start = tw//2 - (total_steps-1)*dot_spacing//2
    for di in range(total_steps):
        dc = ACCENT if di == ts["step"] else DIM
        pygame.draw.circle(box_surf, (*dc, 200), (dot_start + di*dot_spacing, dot_y), 4 if di==ts["step"] else 3)
    surf.blit(box_surf, (tx, ty))

    # NEXT button
    btn = pygame.Rect(tx + tw//2 - 48, ty + th - 20, 96, 26)
    draw_glow_rect(surf, ACCENT, (btn.x, btn.y, btn.w, btn.h), 4)
    lbl = "SAMAJH GAYA! ✓" if ts["step"] == len(steps)-1 else f"NEXT ({ts['step']+1}/{len(steps)})"
    draw_text(surf, lbl, F_TINY, BLACK, btn.centerx, btn.y+6, center=True)
    ts["btn_rect"] = btn
    return btn


# ═════════════════════════════════════════
#  🧠 QUIZ MODE SYSTEM
# ═════════════════════════════════════════
QUIZZES = {
    2: [  # After Level 2
        {
            "q": "Overfitting tab hota hai jab...",
            "opts": ["Model training data pe bahut achha karta hai", "Model kuch nahi seekhta",
                     "Learning rate bahut kam hoti hai", "Epochs bahut kam hote hain"],
            "ans": 0, "explain": "Sahi! Overfitting = model training data 'ratta' maar leta hai. Naye data pe fail hota hai."
        },
        {
            "q": "Ideal Accuracy range konsi hai training ke baad?",
            "opts": ["0–40%", "40–65%", "65–85%", "90–100%"],
            "ans": 2, "explain": "65–85% sweet spot hai! Usse kam = underfitting, zyada = overfitting risk."
        },
        {
            "q": "Learning Rate ka kya role hai?",
            "opts": ["Data clean karta hai", "Model ki seekhne ki speed control karta hai",
                     "Deployment decide karta hai", "Accuracy directly fix karta hai"],
            "ans": 1, "explain": "Learning Rate controls karta hai ki model kitni tezi se weights update kare."
        },
    ],
    3: [  # After Level 3
        {
            "q": "Mobile deployment ke liye minimum accuracy chahiye?",
            "opts": ["50%", "60%", "70%", "80%"],
            "ans": 3, "explain": "Mobile pe 80%+ chahiye kyunki edge devices pe limited resources hote hain!"
        },
        {
            "q": "Production environment kya hota hai?",
            "opts": ["Testing server", "Developer laptop", "Real users ke liye live system", "Training machine"],
            "ans": 2, "explain": "Production = real users ke liye live deployed system. Development se alag hota hai!"
        },
        {
            "q": "CI/CD ka full form kya hai?",
            "opts": ["Code Integration / Code Deployment", "Continuous Integration / Continuous Deployment",
                     "Computer Intelligence / Computer Design", "Cloud Infrastructure / Cloud Data"],
            "ans": 1, "explain": "CI/CD = Continuous Integration / Continuous Deployment — automatic build, test, deploy pipeline!"
        },
    ],
    4: [  # After Level 4
        {
            "q": "Data Drift kya hoti hai?",
            "opts": ["Training data corrupt ho jaati hai", "Real-world data ka pattern change ho jaata hai",
                     "Model weights delete ho jaate hain", "Server crash ho jaata hai"],
            "ans": 1, "explain": "Data Drift = real world mein user behavior ya data patterns badal jaate hain, model outdated ho jaata hai!"
        },
        {
            "q": "Model monitoring ka kya fayda hai?",
            "opts": ["Training fast hoti hai", "Data clean hota hai",
                     "Deployed model ki accuracy real-time track hoti hai", "Deployment cheaper hoti hai"],
            "ans": 2, "explain": "Monitoring se pata chalta hai kab model ka performance girne laga — alert trigger hota hai!"
        },
        {
            "q": "MLOps loop ka sahi order kya hai?",
            "opts": ["Train → Data → Deploy → Monitor", "Data → Train → Deploy → Monitor → Retrain",
                     "Deploy → Train → Monitor → Data", "Monitor → Deploy → Train → Data"],
            "ans": 1, "explain": "Data → Train → Deploy → Monitor → Retrain — yahi hai MLOps ka poora lifecycle! 🔄"
        },
    ],
}

quiz_state = {
    "active": False,
    "level": None,
    "questions": [],
    "current": 0,
    "selected": None,
    "answered": False,
    "score": 0,
    "results": [],          # list of True/False per question
    "done": False,
    "btn_rects": [],
    "next_btn": None,
    "xp_earned": 0,
    "showed_for": set(),    # which levels quiz already showed
}

def start_quiz(level):
    qs = quiz_state
    if level not in QUIZZES: return
    if level in qs["showed_for"]: return
    qs["showed_for"].add(level)
    qs["active"]   = True
    qs["level"]    = level
    qs["questions"]= QUIZZES[level]
    qs["current"]  = 0
    qs["selected"] = None
    qs["answered"] = False
    qs["score"]    = 0
    qs["results"]  = []
    qs["done"]     = False
    qs["xp_earned"]= 0

def quiz_select(idx):
    qs = quiz_state
    if qs["answered"]: return
    qs["selected"] = idx
    q = qs["questions"][qs["current"]]
    correct = (idx == q["ans"])
    qs["answered"] = True
    qs["results"].append(correct)
    if correct:
        qs["score"] += 1
        pts = 75
        add_score(pts); qs["xp_earned"] += pts
        sfx.play("quiz_correct", cooldown_ms=0)
        aira_speak(q["explain"])
    else:
        sfx.play("quiz_wrong", cooldown_ms=0)
        aira_speak(f"❌ Galat! Sahi jawab: '{q['opts'][q['ans']]}'. {q['explain']}")

def quiz_next():
    qs = quiz_state
    qs["current"] += 1
    qs["selected"] = None
    qs["answered"] = False
    sfx.play("action_click")
    if qs["current"] >= len(qs["questions"]):
        qs["done"] = True
        bonus = qs["score"] * 25
        add_score(bonus); qs["xp_earned"] += bonus

def draw_quiz(surf):
    qs = quiz_state
    if not qs["active"]: return None

    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 190)); surf.blit(ov, (0, 0))

    mw, mh = 680, 480; mx2 = (W-mw)//2; my2 = (H-mh)//2
    draw_rect(surf, PANEL, (mx2,my2,mw,mh), 12)
    draw_border_rect(surf, PURPLE, (mx2,my2,mw,mh), 3, 12)

    if qs["done"]:
        # Results screen
        draw_text(surf, "🧠 QUIZ COMPLETE!", F_LARGE, PURPLE, mx2+mw//2, my2+24, center=True)
        sc = qs["score"]; total = len(qs["questions"])
        pct = sc/total
        msg = "Perfect! 🌟 MLOps Master!" if pct==1 else ("Bahut achha! 👏" if pct>=0.67 else "Practice karo! 💪")
        draw_text(surf, f"{sc}/{total} sahi jawab — {msg}", F_MED, GREEN if pct>=0.67 else YELLOW, mx2+mw//2, my2+72, center=True)

        # Result dots
        dot_y = my2+120
        for i, correct in enumerate(qs["results"]):
            col = GREEN if correct else RED
            bx = mx2 + 100 + i*180
            draw_rect(surf, col, (bx, dot_y, 140, 50), 8, 40)
            draw_border_rect(surf, col, (bx, dot_y, 140, 50), 2, 8)
            draw_text(surf, "✓ Sahi" if correct else "✗ Galat", F_MED, col, bx+70, dot_y+15, center=True)

        # XP earned
        draw_rect(surf, PURPLE, (mx2+40, my2+190, mw-80, 60), 8, 30)
        draw_border_rect(surf, PURPLE, (mx2+40, my2+190, mw-80, 60), 2, 8)
        draw_text(surf, f"XP Earned: +{qs['xp_earned']} pts", F_LARGE, PURPLE, mx2+mw//2, my2+210, center=True)

        # Explanation strip
        draw_text(surf, "AIRA ne explanations di hain → sidebar mein dekho!", F_SMALL, DIM, mx2+mw//2, my2+275, center=True)

        close_btn = pygame.Rect(mx2+mw//2-100, my2+mh-60, 200, 44)
        draw_glow_rect(surf, GREEN, (close_btn.x, close_btn.y, close_btn.w, close_btn.h))
        draw_text(surf, "CONTINUE ▶", F_MED, BLACK, close_btn.centerx, close_btn.y+12, center=True)
        qs["next_btn"] = close_btn
        return close_btn

    # Active question
    q = qs["questions"][qs["current"]]
    # Header
    draw_text(surf, f"🧠 AIRA QUIZ — Level {qs['level']}", F_MED, PURPLE, mx2+mw//2, my2+16, center=True)
    draw_text(surf, f"Question {qs['current']+1} of {len(qs['questions'])}", F_TINY, DIM, mx2+mw//2, my2+46, center=True)
    # Progress bar
    prog_w = int((mw-80) * (qs["current"]/len(qs["questions"])))
    draw_rect(surf, BORDER, (mx2+40, my2+62, mw-80, 6), 3)
    if prog_w>0: draw_rect(surf, PURPLE, (mx2+40, my2+62, prog_w, 6), 3)

    # Question box
    draw_rect(surf, (20,10,40), (mx2+30, my2+78, mw-60, 68), 8)
    draw_border_rect(surf, PURPLE, (mx2+30, my2+78, mw-60, 68), 1, 8)
    draw_text_wrap(surf, q["q"], F_MED, TEXT, mx2+44, my2+88, mw-88, 26)

    # Options
    qs["btn_rects"] = []
    for i, opt in enumerate(q["opts"]):
        by = my2 + 162 + i * 62
        bx = mx2 + 30; bw2 = mw - 60; bh2 = 52
        answered = qs["answered"]; sel = qs["selected"]; correct_idx = q["ans"]
        if answered:
            if i == correct_idx: col = GREEN
            elif i == sel:       col = RED
            else:                col = DIM
        elif sel == i:           col = ACCENT
        else:                    col = BORDER
        draw_rect(surf, col, (bx,by,bw2,bh2), 8, 40 if i==sel else 20)
        draw_border_rect(surf, col, (bx,by,bw2,bh2), 2, 8)
        label = ["A","B","C","D"][i]
        draw_text(surf, f"{label}.", F_MED, col, bx+14, by+14)
        draw_text_wrap(surf, opt, F_SMALL, WHITE if i==sel else TEXT, bx+40, by+14, bw2-54, 22)
        qs["btn_rects"].append(pygame.Rect(bx,by,bw2,bh2))

    # Next / Submit button
    if qs["answered"]:
        lbl = "AGLI QUESTION ▶" if qs["current"] < len(qs["questions"])-1 else "RESULTS DEKHO ▶"
        nb = pygame.Rect(mx2+mw//2-110, my2+mh-54, 220, 40)
        draw_glow_rect(surf, GREEN, (nb.x,nb.y,nb.w,nb.h))
        draw_text(surf, lbl, F_MED, BLACK, nb.centerx, nb.y+10, center=True)
        qs["next_btn"] = nb
        return nb
    qs["next_btn"] = None
    return None


# ═════════════════════════════════════════
#  📊 CONFUSION MATRIX VISUALIZATION
# ═════════════════════════════════════════
conf_matrix_state = {
    "active": False,
    "data": None,
    "close_btn": None,
    "anim_timer": 0,
}

def build_confusion_matrix():
    """Build confusion matrix from level 1 drop data."""
    l1 = state["l1"]
    # Simulate realistic matrix from what player collected
    clean_c  = l1.get("clean", 8)
    corrupt_c= l1.get("corrupt", 5)
    biased_c = l1.get("biased", 5)
    errors   = l1.get("errors", 0)
    total    = clean_c + corrupt_c + biased_c

    # Simulate TP/FP/FN for a 3-class matrix
    # Perfect would be diagonal, errors create off-diagonal entries
    noise = max(0, errors)
    matrix = {
        # predicted → actual
        ("clean","clean"):   clean_c,
        ("clean","corrupt"): max(0, noise//3),
        ("clean","biased"):  max(0, noise//4),
        ("corrupt","clean"): max(0, noise//4),
        ("corrupt","corrupt"):corrupt_c,
        ("corrupt","biased"): max(0, noise//3),
        ("biased","clean"):  max(0, noise//4),
        ("biased","corrupt"): max(0, noise//4),
        ("biased","biased"): biased_c,
    }
    precision = {}; recall = {}
    for cls in ["clean","corrupt","biased"]:
        tp = matrix[(cls,cls)]
        fp = sum(matrix[(cls,o)] for o in ["clean","corrupt","biased"] if o!=cls)
        fn = sum(matrix[(o,cls)] for o in ["clean","corrupt","biased"] if o!=cls)
        precision[cls] = round(tp/max(1,tp+fp)*100)
        recall[cls]    = round(tp/max(1,tp+fn)*100)
    overall = round(sum(matrix[(c,c)] for c in ["clean","corrupt","biased"]) / max(1,total) * 100)
    return {"matrix": matrix, "precision": precision, "recall": recall,
            "overall": overall, "total": total,
            "clean":clean_c, "corrupt":corrupt_c, "biased":biased_c, "errors":errors}

def show_confusion_matrix():
    conf_matrix_state["active"] = True
    conf_matrix_state["data"]   = build_confusion_matrix()
    conf_matrix_state["anim_timer"] = 0

def draw_confusion_matrix(surf):
    cms = conf_matrix_state
    if not cms["active"]: return None
    cms["anim_timer"] += 1/60
    anim = min(1.0, cms["anim_timer"] / 0.8)  # 0.8s fill animation

    ov = pygame.Surface((W,H), pygame.SRCALPHA)
    ov.fill((0,0,0,180)); surf.blit(ov,(0,0))

    mw, mh = 700, 520; mx2=(W-mw)//2; my2=(H-mh)//2
    draw_rect(surf, PANEL, (mx2,my2,mw,mh), 12)
    draw_border_rect(surf, GREEN, (mx2,my2,mw,mh), 2, 12)

    draw_text(surf, "📊 CONFUSION MATRIX – Data Distribution", F_MED, GREEN, mx2+mw//2, my2+14, center=True)
    draw_text(surf, "Tumne Level 1 mein kaise data classify kiya – yeh raha breakdown!", F_SMALL, DIM, mx2+mw//2, my2+44, center=True)

    d = cms["data"]
    classes = ["clean","corrupt","biased"]
    class_colors = {"clean":GREEN,"corrupt":RED,"biased":YELLOW}
    class_icons  = {"clean":"[C]","corrupt":"[X]","biased":"[!]"}

    # Grid
    cell_size = 90; grid_x = mx2+160; grid_y = my2+80

    # Column headers (Predicted)
    draw_text(surf, "← PREDICTED →", F_TINY, DIM, grid_x+cell_size+80, my2+68, center=True)
    for j,cls in enumerate(classes):
        cx2 = grid_x + (j+1)*cell_size + cell_size//2
        col = class_colors[cls]
        draw_rect(surf, col, (grid_x+(j+1)*cell_size, grid_y, cell_size, 30), 4, 30)
        draw_text(surf, class_icons[cls]+" "+cls[:5], F_TINY, col, cx2, grid_y+8, center=True)

    # Row headers (Actual) + cells
    for i,actual in enumerate(classes):
        ry = grid_y + 30 + i*cell_size
        col_a = class_colors[actual]
        draw_rect(surf, col_a, (grid_x, ry, cell_size, cell_size), 4, 30)
        draw_text(surf, class_icons[actual], F_MED, col_a, grid_x+cell_size//2, ry+14, center=True)
        draw_text(surf, actual[:6], F_TINY, col_a, grid_x+cell_size//2, ry+36, center=True)

        for j,predicted in enumerate(classes):
            val = d["matrix"][(predicted, actual)]
            cx2 = grid_x + (j+1)*cell_size; cy2 = ry
            is_diag = (i==j)
            base_col = class_colors[actual] if is_diag else RED
            max_val = max(1, max(d["clean"], d["corrupt"], d["biased"]))
            fill_frac = min(1.0, (val/max_val) * anim)
            # Cell bg
            draw_rect(surf, (5,12,25), (cx2+2,cy2+2,cell_size-4,cell_size-4), 4)
            # Fill
            fill_h = int((cell_size-8)*fill_frac)
            if fill_h > 0 and val > 0:
                fill_alpha = 180 if is_diag else 100
                draw_rect(surf, base_col, (cx2+4,cy2+cell_size-4-fill_h,cell_size-8,fill_h), 4, fill_alpha)
            draw_border_rect(surf, base_col if is_diag else (40,60,90), (cx2+2,cy2+2,cell_size-4,cell_size-4), 2 if is_diag else 1, 4)
            # Value
            val_col = WHITE if is_diag else (150,80,80)
            draw_text(surf, str(val), F_LARGE, val_col, cx2+cell_size//2, cy2+cell_size//2-16, center=True)
            if is_diag: draw_text(surf, "✓TP", F_TINY, base_col, cx2+cell_size//2, cy2+cell_size//2+10, center=True)
            elif val>0: draw_text(surf, "✗FP", F_TINY, (180,60,60), cx2+cell_size//2, cy2+cell_size//2+10, center=True)

    # Axis labels
    lbl_x = grid_x - 10; lbl_y = grid_y+30+cell_size+cell_size//2
    draw_text(surf, "ACTUAL ↕", F_TINY, DIM, lbl_x, my2+180)

    # Metrics panel
    metrics_x = grid_x + 4*cell_size + 20
    metrics_w = mx2+mw - metrics_x - 20
    if metrics_w > 80:
        draw_rect(surf, (8,18,36), (metrics_x, grid_y, metrics_w, 3*cell_size+30), 8)
        draw_border_rect(surf, ACCENT, (metrics_x, grid_y, metrics_w, 3*cell_size+30), 1, 8)
        draw_text(surf, "METRICS", F_TINY, ACCENT, metrics_x+metrics_w//2, grid_y+8, center=True)
        draw_text(surf, f"Overall: {d['overall']}%", F_MED, GREEN if d['overall']>=70 else YELLOW,
                  metrics_x+10, grid_y+36)
        draw_text(surf, f"Errors: {d['errors']}", F_SMALL, RED if d['errors']>2 else DIM,
                  metrics_x+10, grid_y+62)
        my3 = grid_y+90
        for cls in classes:
            col = class_colors[cls]
            draw_text(surf, f"{class_icons[cls]}", F_MED, col, metrics_x+10, my3)
            draw_text(surf, f"P:{d['precision'][cls]}%", F_TINY, col, metrics_x+10, my3+24)
            draw_text(surf, f"R:{d['recall'][cls]}%",    F_TINY, col, metrics_x+10, my3+42)
            my3 += 72

    # Legend
    leg_y = my2+mh-90
    draw_rect(surf, (8,18,36), (mx2+20, leg_y, mw-40, 56), 6)
    draw_border_rect(surf, BORDER, (mx2+20, leg_y, mw-40, 56), 1, 6)
    draw_text(surf, "Diagonal (TP) = Sahi classify kiya  |  Off-diagonal = Galti  |  P=Precision  R=Recall", F_TINY, DIM, mx2+mw//2, leg_y+10, center=True)
    draw_text(surf, f"Total items: {d['total']}  |  Clean: {d['clean']}  Corrupt: {d['corrupt']}  Biased: {d['biased']}", F_TINY, TEXT, mx2+mw//2, leg_y+32, center=True)

    close_btn = pygame.Rect(mx2+mw//2-110, my2+mh-26, 220, 34)
    draw_glow_rect(surf, GREEN, (close_btn.x, close_btn.y, close_btn.w, close_btn.h))
    draw_text(surf, "SAMAJH GAYA – CLOSE ✓", F_SMALL, BLACK, close_btn.centerx, close_btn.y+8, center=True)
    cms["close_btn"] = close_btn
    return close_btn

# ─────────────────────────────────────────
#  AIRA MENTOR
# ─────────────────────────────────────────
mentor_messages=[]; mentor_input_text=""; mentor_focused=False; mentor_typing=False

MENTOR_KNOWLEDGE = {
    "overfitting":"Overfitting tab hota hai jab model training data ko 'ratta' maar leta hai. Naye data pe fail ho jaata hai. Solution: Fewer epochs, regularization!",
    "underfitting":"Underfitting tab hota hai jab model ne enough nahi seekha. Accuracy bahut low hoti hai. Solution: Zyada epochs, better features!",
    "bias":"Data Bias matlab training data mein ek taraf jhukao. Jaise sirf ek gender ke examples. Isse model unfair predictions deta hai!",
    "deploy":"Deployment matlab trained model ko real users ke liye available karna. Production alag hoti hai Development se. CI/CD pipeline automatic deploy karta hai!",
    "monitor":"Monitoring matlab deployed model ki real-time accuracy track karna. Accuracy gire toh alert trigger hota hai – Data Drift ki wajah se!",
    "drift":"Data Drift tab hota hai jab real-world data ka pattern change ho jaata hai lekin model purana hi rehta hai. Retrain karna padta hai!",
    "mlops":"MLOps = ML + DevOps! Models ko reliably deploy, monitor, aur retrain karne ka system. Includes: Version control, CI/CD, monitoring, automated retraining.",
    "accuracy":"Model Accuracy = (Sahi Predictions / Total) x 100%. High accuracy good hai, but precision aur recall bhi dekho!",
    "training":"Training matlab algorithm ko data se patterns seekhna. Neural network weights adjust hote hain har epoch mein – loss minimize karne ke liye!",
    "dataset":"Dataset ek collection hai examples ka. Good dataset: Balanced, diverse, clean, aur labelled. 70% train, 15% val, 15% test!",
    "epoch":"Ek Epoch matlab poora training dataset ek baar model se guzarna. Zyada epochs = zyada learning, but overfitting ka risk!",
    "learning rate":"Learning Rate control karta hai ki model kitni tezi se seekhta hai. Bahut bada = unstable. Bahut chota = bahut slow training!",
    "sound":"M key se mute/unmute karo. + aur - keys se volume badhao/ghataao! 🔊",
}

def aira_speak(msg):
    mentor_messages.append({"role":"aira","text":msg,"alpha":0})

def call_claude_api(question):
    global mentor_typing
    if not REQUESTS_AVAILABLE:
        aira_speak("requests library nahi hai! Main local knowledge se bata sakti hoon.")
        mentor_typing=False; return
    lq=question.lower()
    for key,ans in MENTOR_KNOWLEDGE.items():
        if key in lq:
            aira_speak(ans); mentor_typing=False; return
    try:
        resp=requests.post("https://api.anthropic.com/v1/messages",
            headers={"Content-Type":"application/json"},
            json={"model":"claude-sonnet-4-20250514","max_tokens":200,
                  "system":"You are AIRA, a friendly AI mentor for the MLOps Tycoon game. Teach ML/MLOps in simple Hinglish (Hindi+English mix). Keep responses to 2-3 sentences max. Use emojis.",
                  "messages":[{"role":"user","content":f"Score:{state['score']} Accuracy:{round(state['model_acc'])}%\nQuestion: {question}"}]},
            timeout=10)
        data=resp.json()
        text="".join(c.get("text","") for c in data.get("content",[]))
        aira_speak(text[:300] if text else "Kuch issue aa gaya!")
    except Exception:
        aira_speak("API unavailable! Tip: Data Drift tab hota hai jab real world data change ho jaaye lekin model purana rahe.")
    mentor_typing=False

def send_mentor_question(q):
    global mentor_typing
    if not q.strip(): return
    mentor_messages.append({"role":"user","text":q,"alpha":0})
    mentor_typing=True
    mentor_messages.append({"role":"aira","text":"Soch rahi hoon...","alpha":0,"loading":True})
    sfx.play("action_click")   # 🔊
    threading.Thread(target=call_claude_api,args=(q,),daemon=True).start()

# ─────────────────────────────────────────
#  LEVEL 1 – DATA COLLECTION
# ─────────────────────────────────────────
DATA_ITEMS = [
    ("Sales CSV","clean"),("10K Images","clean"),("User Reviews","clean"),("Stock Prices","clean"),
    ("Sensor Data","clean"),("Email Corpus","clean"),("Audio Samples","clean"),("GPS Logs","clean"),
    ("Corrupted File","corrupt"),("Malformed JSON","corrupt"),("Null Values","corrupt"),
    ("Shuffled Labels","corrupt"),("Empty Rows","corrupt"),
    ("Male-only Data","biased"),("City-only Data","biased"),("Rich-only Users","biased"),
    ("One Region","biased"),("PhD-only Survey","biased"),
]
TYPE_COLOR={"clean":GREEN,"corrupt":RED,"biased":YELLOW}
TYPE_ICON ={"clean":"[C]","corrupt":"[X]","biased":"[!]"}
TYPE_LABEL={"clean":"Clean Data","corrupt":"Corrupted Data","biased":"Biased Data"}

stream_items=[]; dragging_item=None; drag_offset=(0,0)
l1_spawn_timer=0.0; SPAWN_INTERVAL=2.5

def l1_spawn():
    l=state["l1"]
    pool=[d for d in DATA_ITEMS if not(
        (d[1]=="clean"   and l["clean"]  >=l["goal"]["clean"])  or
        (d[1]=="corrupt" and l["corrupt"]>=l["goal"]["corrupt"]) or
        (d[1]=="biased"  and l["biased"] >=l["goal"]["biased"]))]
    if not pool: return
    label,dtype=random.choice(pool)
    stream_items.append({"label":label,"type":dtype,
        "rect":pygame.Rect(random.randint(50,680),random.randint(200,380),150,36),
        "life":8.0,"born":time.time()})

def get_bucket_rects():
    bw,bh=220,110; y=H-160; gap=30
    total=3*bw+2*gap; sx=(W-320-total)//2
    return {"clean":pygame.Rect(sx,y,bw,bh),"corrupt":pygame.Rect(sx+bw+gap,y,bw,bh),
            "biased":pygame.Rect(sx+2*(bw+gap),y,bw,bh)}

# ─────────────────────────────────────────
#  LEVEL 2 – TRAINING
# ─────────────────────────────────────────
def compute_accuracy(epochs, lr_raw):
    if epochs<10: acc=20+epochs*2
    elif epochs>150: acc=90-(epochs-150)*0.3+(5 if lr_raw>50 else 0)
    else: acc=50+epochs*0.3+(50-abs(lr_raw-30))*0.2
    return max(10.0,min(95.0,acc))

def get_training_status(acc):
    if acc<40: return "UNDERFITTING – Zyada train karo!",RED
    elif acc>88: return "OVERFITTING – Kam train karo!",RED
    elif 65<=acc<=85: return "PERFECT ZONE! Train karo!",GREEN
    else: return "Adjust karo...",YELLOW

slider_dragging=None
epoch_slider_rect=None; lr_slider_rect=None; train_btn_rect=None

# ─────────────────────────────────────────
#  LEVEL 3 – DEPLOYMENT
# ─────────────────────────────────────────
DEPLOY_OPTIONS=[
    {"key":"local", "icon":"[PC]",  "name":"Local Machine","desc":"Test environment. Safe for dev. Limited users.","risk":"Risk: LOW  | Users: 1","risk_color":GREEN, "min_acc":0},
    {"key":"cloud", "icon":"[CLD]", "name":"Cloud Server", "desc":"Production env. Scalable. Stable model needed.","risk":"Risk: MED  | Users: 10K+","risk_color":YELLOW,"min_acc":70},
    {"key":"mobile","icon":"[MOB]", "name":"Mobile App",   "desc":"Edge deploy. Very optimized model needed.",     "risk":"Risk: HIGH | Users: 1M+","risk_color":RED,   "min_acc":80},
]

# ─────────────────────────────────────────
#  LEVEL 4 – MONITORING
# ─────────────────────────────────────────
COMPLAINTS=["User: 'Wrong prediction mili!'","User: 'App kaam nahi kar raha!'",
    "User: 'Accuracy bahut kharab hai!'","User: 'Refund chahiye!'",
    "User: 'Model outdated lag raha hai!'","API Error: Timeout 504","Alert: Confidence score < 0.4"]
complaints_log=[]

# ─────────────────────────────────────────
#  MODAL
# ─────────────────────────────────────────
modal={"active":False,"title":"","body":[],"concepts":[],"next_level":0}

def show_modal(title, body, concepts, next_level):
    modal.update({"active":True,"title":title,"body":body,"concepts":concepts,"next_level":next_level})

def draw_modal(surf):
    if not modal["active"]: return False
    ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((0,0,0,180)); surf.blit(ov,(0,0))
    mw,mh=600,440; mx=(W-mw)//2; my=(H-mh)//2
    draw_rect(surf,PANEL,(mx,my,mw,mh),12)
    draw_border_rect(surf,ACCENT,(mx,my,mw,mh),2,12)
    draw_text(surf,modal["title"],F_LARGE,ACCENT,mx+mw//2,my+24,center=True)
    y=my+70
    for line in modal["body"]:
        draw_text_wrap(surf,line,F_SMALL,TEXT,mx+30,y,mw-60); y+=30
    y+=10
    for c in modal["concepts"]:
        draw_rect(surf,GREEN,(mx+30,y,mw-60,32),6,25)
        draw_border_rect(surf,GREEN,(mx+30,y,mw-60,32),1,6)
        draw_text(surf,"✓ "+c,F_SMALL,GREEN,mx+46,y+8); y+=42
    btn=pygame.Rect(mx+mw//2-100,my+mh-60,200,40)
    draw_glow_rect(surf,GREEN,(btn.x,btn.y,btn.w,btn.h))
    draw_text(surf,"NEXT LEVEL →",F_MED,BLACK,btn.centerx,btn.centery-9,center=True)
    return btn

# ─────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────
def draw_header(surf):
    draw_rect(surf,PANEL,(0,0,W,70))
    pygame.draw.line(surf,BORDER,(0,70),(W,70),2)
    draw_text(surf,"MLOps Tycoon",F_LARGE,ACCENT,20,8)
    draw_text(surf,"BUILD YOUR AI FACTORY",F_TINY,DIM,22,42)
    stats=[("SCORE",str(state["score"])),
           ("LEVEL",state["screen"].upper().replace("LEVEL","LVL ")),
           ("ACCURACY",f"{round(state['model_acc'])}%" if state['model_acc'] else "--")]
    stat_start=W-SIDEBAR_W-420
    for i,(label,val) in enumerate(stats):
        x=stat_start+i*120
        draw_text(surf,label,F_TINY,DIM,x,10)
        draw_text(surf,val,F_MED,ACCENT,x,34)
    xp_x=W-SIDEBAR_W-15; xp_pct=state["xp"]/1000
    draw_text(surf,"XP",F_TINY,DIM,xp_x-115,10)
    draw_rect(surf,BORDER,(xp_x-112,34,108,10),4)
    if xp_pct>0: draw_rect(surf,PURPLE,(xp_x-112,34,int(108*xp_pct),10),4)
    ex_x=W-SIDEBAR_W-82
    ex_rect=pygame.Rect(ex_x,14,72,38)
    draw_glow_rect(surf,RED,(ex_rect.x,ex_rect.y,ex_rect.w,ex_rect.h))
    draw_text(surf,"✕ EXIT",F_SMALL,WHITE,ex_rect.centerx,ex_rect.y+10,center=True)
    return ex_rect

# ─────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────
TABS=[("HOME","welcome"),("L1:DATA","level1"),("L2:TRAIN","level2"),
      ("L3:DEPLOY","level3"),("L4:MONITOR","level4"),("🎓ACADEMY","academy")]

def get_tab_rects():
    rects=[]; x=0
    for label,key in TABS:
        tw=F_SMALL.size(label)[0]+40
        rects.append((pygame.Rect(x,70,tw,40),label,key)); x+=tw
    return rects

def draw_tabs(surf):
    draw_rect(surf,PANEL,(0,70,W,40))
    pygame.draw.line(surf,BORDER,(0,110),(W,110),2)
    for rect,label,key in get_tab_rects():
        is_level=key.startswith("level"); lvl_num=int(key[-1]) if is_level else 0
        locked=is_level and not state["unlocked"].get(lvl_num,False)
        active=state["screen"]==key
        if active:
            draw_rect(surf,ACCENT,(rect.x,rect.y,rect.w,rect.h),0,30)
            pygame.draw.rect(surf,ACCENT,(rect.x,rect.y+rect.h-2,rect.w,2))
            color=BLACK
        elif locked: color=(40,60,90)
        else: color=DIM
        draw_text(surf,("🔒 " if locked else "")+label,F_SMALL,color,rect.centerx,rect.y+11,center=True)

# ─────────────────────────────────────────
#  MENTOR SIDEBAR
# ─────────────────────────────────────────
mentor_scroll=0

def draw_mentor(surf):
    sx=W-SIDEBAR_W
    draw_rect(surf,PANEL,(sx,110,SIDEBAR_W,H-110))
    pygame.draw.line(surf,BORDER,(sx,110),(sx,H),2)
    draw_rect(surf,(8,18,36),(sx,110,SIDEBAR_W,54))
    pygame.draw.line(surf,BORDER,(sx,164),(W,164),1)
    cx2,cy2=sx+32,125; t=time.time()
    pygame.draw.circle(surf,PURPLE,(cx2,cy2),20)
    draw_text(surf,"AI",F_SMALL,WHITE,cx2,cy2-9,center=True)
    angle=t*45
    for i in range(0,270,30):
        a=math.radians(angle+i)
        pygame.draw.circle(surf,ACCENT,(int(cx2+23*math.cos(a)),int(cy2+23*math.sin(a))),2)
    draw_text(surf,"AIRA",F_MED,ACCENT,sx+60,110)
    draw_text(surf,"AI Mentor Bot",F_TINY,DIM,sx+60,132)
    chat_y=172; chat_h=H-216
    chat_rect=pygame.Rect(sx+4,chat_y,SIDEBAR_W-8,chat_h)
    old_clip=surf.get_clip(); surf.set_clip(chat_rect)
    y=chat_y+8-mentor_scroll
    for msg in mentor_messages[-20:]:
        is_aira=msg["role"]=="aira"; bc=ACCENT if is_aira else PURPLE
        prefix="AIRA: " if is_aira else "You: "; full_text=prefix+msg["text"]
        wrapped=[]; words=full_text.split(); line=""
        for w in words:
            test=line+(" " if line else "")+w
            if F_TINY.size(test)[0]<=SIDEBAR_W-28: line=test
            else:
                if line: wrapped.append(line)
                line=w
        if line: wrapped.append(line)
        box_h=len(wrapped)*17+14
        draw_rect(surf,bc,(sx+6,y,SIDEBAR_W-12,box_h),6,18)
        draw_border_rect(surf,bc,(sx+6,y,SIDEBAR_W-12,box_h),1,6)
        for j,wline in enumerate(wrapped):
            draw_text(surf,wline,F_TINY,ACCENT if is_aira else (212,180,255),sx+12,y+6+j*17)
        msg["alpha"]=min(255,msg.get("alpha",0)+10); y+=box_h+8
    surf.set_clip(old_clip)
    ib_y=H-50; ibc=ACCENT if mentor_focused else BORDER
    draw_rect(surf,(0,0,0),(sx+4,ib_y,SIDEBAR_W-48,36),4)
    draw_border_rect(surf,ibc,(sx+4,ib_y,SIDEBAR_W-48,36),1,4)
    draw_text(surf,mentor_input_text or "Kuch pucho...",F_TINY,TEXT if mentor_input_text else DIM,sx+10,ib_y+10)
    send_rect=pygame.Rect(W-40,ib_y,36,36)
    draw_glow_rect(surf,ACCENT,(send_rect.x,send_rect.y,36,36),4)
    draw_text(surf,">",F_MED,BLACK,send_rect.centerx,send_rect.y+6,center=True)
    return send_rect

# ─────────────────────────────────────────
#  WELCOME SCREEN
# ─────────────────────────────────────────
def draw_welcome(surf):
    cx=(W-SIDEBAR_W)//2
    draw_text(surf,"MLOps",F_HUGE,ACCENT,cx,130,center=True)
    draw_text(surf,"TYCOON",F_HUGE,PURPLE,cx,188,center=True)
    draw_text(surf,"Build Your AI Factory",F_MED,DIM,cx,250,center=True)
    # 🔊 hint
    draw_text(surf,"🔊 M=Mute  +/-=Volume",F_TINY,DIM,cx,278,center=True)
    cards=[("L1","DATA COLLECTION",GREEN,"Drag clean/biased/corrupt data"),
           ("L2","MODEL TRAINING",ACCENT,"Tune epochs & learning rate"),
           ("L3","DEPLOYMENT",PURPLE,"Choose right deploy environment"),
           ("L4","MONITORING",RED,"Detect drift & retrain model")]
    cw,ch=180,100; gap=20; total=len(cards)*cw+(len(cards)-1)*gap
    sx=cx-total//2; cy_card=300
    for i,(lvl,name,color,desc) in enumerate(cards):
        x=sx+i*(cw+gap)
        draw_rect(surf,PANEL,(x,cy_card,cw,ch),8)
        draw_border_rect(surf,color,(x,cy_card,cw,ch),2,8)
        draw_text(surf,lvl,F_LARGE,color,x+cw//2,cy_card+12,center=True)
        draw_text(surf,name,F_TINY,color,x+cw//2,cy_card+50,center=True)
        draw_text_wrap(surf,desc,F_TINY,DIM,x+10,cy_card+68,cw-20,16)
    btn=pygame.Rect(cx-110,430,220,50)
    draw_glow_rect(surf,GREEN,(btn.x,btn.y,btn.w,btn.h))
    draw_text(surf,"▶  START GAME",F_LARGE,BLACK,btn.centerx,btn.y+12,center=True)
    return btn

# ─────────────────────────────────────────
#  LEVEL 1 DRAW
# ─────────────────────────────────────────
def draw_level1(surf):
    area_w=W-SIDEBAR_W; l1=state["l1"]; CT=118; CB=H-14
    draw_rect(surf,PANEL,(10,CT,area_w-20,68),6)
    draw_border_rect(surf,BORDER,(10,CT,area_w-20,68),1,6)
    draw_text(surf,"LEVEL 1 – DATA COLLECTION",F_MED,GREEN,24,CT+8)
    draw_text(surf,"Data items stream ho rahe hain. Sahi bucket pe drag karo! 5 galat = Fail!",F_SMALL,DIM,24,CT+34)
    g=l1["goal"]; stats_y=CT+72
    draw_text(surf,f"[C] Clean: {l1['clean']}/{g['clean']}",F_SMALL,GREEN,24,stats_y)
    draw_text(surf,f"[X] Corrupt: {l1['corrupt']}/{g['corrupt']}",F_SMALL,RED,240,stats_y)
    draw_text(surf,f"[!] Biased: {l1['biased']}/{g['biased']}",F_SMALL,YELLOW,460,stats_y)
    draw_text(surf,f"Errors: {l1['errors']}/5",F_SMALL,RED if l1["errors"]>=3 else DIM,area_w-140,stats_y)
    stream_top=stats_y+28; stream_h=int((CB-stream_top)*0.48)
    stream_rect=pygame.Rect(10,stream_top,area_w-20,stream_h)
    draw_rect(surf,(0,0,0),(stream_rect.x,stream_rect.y,stream_rect.w,stream_rect.h),6,60)
    draw_border_rect(surf,BORDER,(stream_rect.x,stream_rect.y,stream_rect.w,stream_rect.h),1,6)
    draw_text(surf,"← Data Stream – items yahaan aayenge →",F_TINY,DIM,stream_rect.centerx,stream_rect.centery-8,center=True)
    for item in stream_items:
        col=TYPE_COLOR[item["type"]]; rect=item["rect"]
        draw_rect(surf,col,(rect.x,rect.y,rect.w,rect.h),14,40)
        draw_border_rect(surf,col,(rect.x,rect.y,rect.w,rect.h),1,14)
        draw_text(surf,f"{TYPE_ICON[item['type']]} {item['label']}",F_TINY,col,rect.x+10,rect.y+10)
        pygame.draw.rect(surf,col,(rect.x+2,rect.y+rect.h-4,int((rect.w-4)*item["life"]/8.0),3))
    if dragging_item:
        col=TYPE_COLOR[dragging_item["type"]]; rect=dragging_item["rect"]
        draw_rect(surf,col,(rect.x,rect.y,rect.w,rect.h),14,80)
        draw_border_rect(surf,col,(rect.x,rect.y,rect.w,rect.h),2,14)
        draw_text(surf,f"{TYPE_ICON[dragging_item['type']]} {dragging_item['label']}",F_SMALL,col,rect.x+10,rect.y+8)
    bucket_top=stream_top+stream_h+14; bucket_h=CB-bucket_top
    bw=(area_w-50)//3
    buckets={"clean":pygame.Rect(10,bucket_top,bw,bucket_h),
             "corrupt":pygame.Rect(10+bw+15,bucket_top,bw,bucket_h),
             "biased":pygame.Rect(10+2*(bw+15),bucket_top,bw,bucket_h)}
    for btype,brect in buckets.items():
        col=TYPE_COLOR[btype]
        draw_rect(surf,PANEL,(brect.x,brect.y,brect.w,brect.h),8)
        if dragging_item and dragging_item["rect"].colliderect(brect):
            draw_glow_rect(surf,col,(brect.x,brect.y,brect.w,brect.h))
        else:
            draw_border_rect(surf,col,(brect.x,brect.y,brect.w,brect.h),2,8)
        cy_b=brect.y+brect.h//2
        draw_text(surf,TYPE_ICON[btype],F_HUGE,col,brect.centerx,cy_b-48,center=True)
        draw_text(surf,TYPE_LABEL[btype],F_SMALL,col,brect.centerx,cy_b+4,center=True)
        draw_text(surf,str(l1[btype]),F_LARGE,WHITE,brect.centerx,cy_b+28,center=True)

# ─────────────────────────────────────────
#  LEVEL 2 DRAW
# ─────────────────────────────────────────
deploy_btn_rects={}; continue_btn_rect=None

def draw_level2(surf):
    global epoch_slider_rect,lr_slider_rect,train_btn_rect
    area_w=W-SIDEBAR_W; l2=state["l2"]; CT=118; CB=H-14
    draw_rect(surf,PANEL,(10,CT,area_w-20,62),6)
    draw_border_rect(surf,BORDER,(10,CT,area_w-20,62),1,6)
    draw_text(surf,"LEVEL 2 – MODEL TRAINING",F_MED,ACCENT,24,CT+8)
    draw_text(surf,"Epochs & Learning Rate adjust karo. Goldilocks Zone (65-85%) mein laao, phir Train!",F_SMALL,DIM,24,CT+36)
    panels_top=CT+74; panel_h=CB-panels_top; half_w=(area_w-30)//2
    lp=pygame.Rect(10,panels_top,half_w,panel_h)
    draw_rect(surf,PANEL,(lp.x,lp.y,lp.w,lp.h),8)
    draw_border_rect(surf,BORDER,(lp.x,lp.y,lp.w,lp.h),1,8)
    draw_text(surf,"TRAINING CONTROLS",F_TINY,ACCENT,lp.x+16,lp.y+14)
    epochs=l2["epochs"]; ey=lp.y+52
    draw_text(surf,f"Epochs: {epochs}",F_SMALL,TEXT,lp.x+16,ey)
    sr_x,sr_y,sr_w=lp.x+16,ey+30,lp.w-32; epoch_slider_rect=pygame.Rect(sr_x,sr_y,sr_w,20)
    draw_rect(surf,BORDER,(sr_x,sr_y+6,sr_w,8),4)
    ep_pct=(epochs-1)/199; draw_rect(surf,ACCENT,(sr_x,sr_y+6,int(sr_w*ep_pct),8),4)
    tx=sr_x+int(sr_w*ep_pct)
    pygame.draw.circle(surf,ACCENT,(tx,sr_y+10),11); pygame.draw.circle(surf,WHITE,(tx,sr_y+10),5)
    lr_raw=l2["lr_raw"]; ly2=ey+96
    draw_text(surf,f"Learning Rate: {lr_raw/1000:.4f}",F_SMALL,TEXT,lp.x+16,ly2)
    lr_x,lr_y2=lp.x+16,ly2+30; lr_slider_rect=pygame.Rect(lr_x,lr_y2,lp.w-32,20)
    draw_rect(surf,BORDER,(lr_x,lr_y2+6,lp.w-32,8),4)
    lr_pct=(lr_raw-1)/99; draw_rect(surf,ACCENT,(lr_x,lr_y2+6,int((lp.w-32)*lr_pct),8),4)
    tx2=lr_x+int((lp.w-32)*lr_pct)
    pygame.draw.circle(surf,ACCENT,(tx2,lr_y2+10),11); pygame.draw.circle(surf,WHITE,(tx2,lr_y2+10),5)
    acc=l2["acc"] if l2["acc"]>0 else compute_accuracy(epochs,lr_raw)
    status_text,status_color=get_training_status(acc); badge_y=ly2+76
    draw_rect(surf,status_color,(lp.x+16,badge_y,lp.w-32,44),6,35)
    draw_border_rect(surf,status_color,(lp.x+16,badge_y,lp.w-32,44),2,6)
    draw_text(surf,status_text,F_MED,status_color,lp.x+lp.w//2,badge_y+12,center=True)
    gy=badge_y+66
    draw_text(surf,"Epochs < 10   →  Underfitting",F_SMALL,RED,lp.x+16,gy)
    draw_text(surf,"Epochs > 150  →  Overfitting",F_SMALL,RED,lp.x+16,gy+28)
    draw_text(surf,"65%  –  85%   →  Sweet Spot!",F_SMALL,GREEN,lp.x+16,gy+56)
    train_btn_rect=pygame.Rect(lp.x+16,lp.y+lp.h-62,lp.w-32,50)
    trained=l2.get("trained",False) or l2.get("training",False)
    btn_color=DIM if trained else GREEN
    draw_glow_rect(surf,btn_color,(train_btn_rect.x,train_btn_rect.y,train_btn_rect.w,train_btn_rect.h))
    btn_label="TRAINING..." if l2.get("training") else ("TRAINED ✓" if trained else "TRAIN MODEL")
    draw_text(surf,btn_label,F_LARGE,BLACK if not trained else WHITE,train_btn_rect.centerx,train_btn_rect.y+13,center=True)
    rp=pygame.Rect(lp.x+lp.w+10,panels_top,area_w-lp.w-30,panel_h)
    draw_rect(surf,PANEL,(rp.x,rp.y,rp.w,rp.h),8)
    draw_border_rect(surf,BORDER,(rp.x,rp.y,rp.w,rp.h),1,8)
    draw_text(surf,"ACCURACY METER",F_TINY,ACCENT,rp.x+16,rp.y+14)
    real_acc=compute_accuracy(epochs,lr_raw)
    bar_x,bar_y,bar_w,bar_h=rp.x+16,rp.y+42,rp.w-32,38
    draw_rect(surf,(0,0,0),(bar_x,bar_y,bar_w,bar_h),4)
    fill_w=int(bar_w*real_acc/100)
    for i in range(fill_w):
        t2=i/max(fill_w,1); col=lerp_color(RED,lerp_color(YELLOW,GREEN,t2),t2)
        pygame.draw.line(surf,col,(bar_x+i,bar_y+2),(bar_x+i,bar_y+bar_h-2))
    draw_border_rect(surf,BORDER,(bar_x,bar_y,bar_w,bar_h),1,4)
    draw_text(surf,f"{round(real_acc)}%",F_LARGE,WHITE,bar_x+bar_w-70,bar_y+8)
    graph_label_y=rp.y+100; graph_top=graph_label_y+22
    graph_h=rp.y+rp.h-graph_top-36
    draw_text(surf,"TRAINING LOSS GRAPH",F_TINY,ACCENT,rp.x+16,graph_label_y)
    gx,gy2,gw,gh=rp.x+16,graph_top,rp.w-32,graph_h
    draw_rect(surf,(0,0,0),(gx,gy2,gw,gh),4,80)
    draw_border_rect(surf,BORDER,(gx,gy2,gw,gh),1,4)
    for pct in [25,50,75,100]:
        ly_g=gy2+gh-int(pct/100*gh)
        pygame.draw.line(surf,BORDER,(gx,ly_g),(gx+gw,ly_g),1)
        draw_text(surf,f"{pct}%",F_TINY,DIM,gx+4,ly_g-16)
    pts=l2.get("graph_pts",[])
    if len(pts)>=2:
        scaled=[(gx+int(i/(len(pts)-1)*gw),gy2+gh-int(p*gh)-4) for i,p in enumerate(pts)]
        pygame.draw.lines(surf,ACCENT,False,scaled,2)
        val_pts=[]
        for i,p in enumerate(pts):
            extra=max(0,(i/len(pts)-0.7))*0.3 if len(pts)>1 else 0
            vp=max(0.05,p-0.05+extra)
            val_pts.append((gx+int(i/(len(pts)-1)*gw),gy2+gh-int(min(vp,0.98)*gh)-4))
        pygame.draw.lines(surf,(255,100,0),False,val_pts,2)
    legend_y=gy2+gh+8
    pygame.draw.line(surf,ACCENT,(gx,legend_y+9),(gx+28,legend_y+9),2)
    draw_text(surf,"Train Loss",F_TINY,ACCENT,gx+34,legend_y)
    pygame.draw.line(surf,(255,100,0),(gx+128,legend_y+9),(gx+156,legend_y+9),2)
    draw_text(surf,"Val Loss",F_TINY,(255,100,0),gx+162,legend_y)

# ─────────────────────────────────────────
#  LEVEL 3 DRAW
# ─────────────────────────────────────────
def draw_level3(surf):
    global deploy_btn_rects,continue_btn_rect
    area_w=W-SIDEBAR_W; CT=118; CB=H-14
    draw_rect(surf,PANEL,(10,CT,area_w-20,62),6)
    draw_border_rect(surf,BORDER,(10,CT,area_w-20,62),1,6)
    draw_text(surf,"LEVEL 3 – DEPLOYMENT",F_MED,PURPLE,24,CT+8)
    draw_text(surf,f"Model Accuracy: {round(state['model_acc'])}%   |   Minimum required: 60%",F_SMALL,DIM,24,CT+36)
    cw=(area_w-60)//3; ch=190; cy=CT+74; deploy_btn_rects={}
    for i,opt in enumerate(DEPLOY_OPTIONS):
        x=10+i*(cw+15); col=opt["risk_color"]; rect=pygame.Rect(x,cy,cw,ch)
        draw_rect(surf,PANEL,(x,cy,cw,ch),8)
        draw_border_rect(surf,col,(x,cy,cw,ch),2,8)
        draw_text(surf,opt["icon"],F_LARGE,col,x+cw//2,cy+14,center=True)
        draw_text(surf,opt["name"],F_MED,col,x+cw//2,cy+58,center=True)
        draw_text_wrap(surf,opt["desc"],F_TINY,DIM,x+12,cy+86,cw-24,18)
        draw_text(surf,opt["risk"],F_TINY,col,x+cw//2,cy+148,center=True)
        btn=pygame.Rect(x+20,cy+ch+10,cw-40,38)
        done=state["l3"]["choice"]==opt["key"]
        bc=GREEN if done else col
        draw_glow_rect(surf,bc,(btn.x,btn.y,btn.w,btn.h))
        draw_text(surf,"DEPLOYED ✓" if done else "DEPLOY HERE",F_SMALL,BLACK,btn.centerx,btn.y+10,center=True)
        deploy_btn_rects[opt["key"]]=btn
    result=state["l3"].get("result")
    if result:
        ry=cy+ch+62; col=GREEN if result["success"] else RED
        draw_rect(surf,col,(10,ry,area_w-20,80),8,25)
        draw_border_rect(surf,col,(10,ry,area_w-20,80),2,8)
        draw_text(surf,result["icon"]+"  "+result["title"],F_MED,col,area_w//2,ry+12,center=True)
        draw_text(surf,result["detail"],F_SMALL,TEXT,area_w//2,ry+44,center=True)
        if result["success"] and not state["l3"]["done"]:
            continue_btn_rect=pygame.Rect(area_w//2-100,ry+92,200,40)
            draw_glow_rect(surf,GREEN,(continue_btn_rect.x,continue_btn_rect.y,200,40))
            draw_text(surf,"CONTINUE →",F_MED,BLACK,continue_btn_rect.centerx,continue_btn_rect.y+9,center=True)

# ─────────────────────────────────────────
#  LEVEL 4 DRAW
# ─────────────────────────────────────────
action_btn_rects={}

def draw_level4(surf):
    global action_btn_rects
    area_w=W-SIDEBAR_W; l4=state["l4"]; CT=118; CB=H-14
    draw_rect(surf,PANEL,(10,CT,area_w-20,62),6)
    draw_border_rect(surf,BORDER,(10,CT,area_w-20,62),1,6)
    draw_text(surf,"LEVEL 4 – MONITORING & RETRAINING",F_MED,RED,24,CT+8)
    draw_text(surf,"Model ki accuracy drift ho rahi hai! Teeno actions karo level complete karne ke liye.",F_SMALL,DIM,24,CT+36)
    half=(area_w-30)//2; panels_top=CT+74
    graph_panel_h=int((CB-panels_top)*0.52); alert_y_off=panels_top+graph_panel_h+10
    draw_rect(surf,PANEL,(10,panels_top,half,graph_panel_h),8)
    draw_border_rect(surf,BORDER,(10,panels_top,half,graph_panel_h),1,8)
    draw_text(surf,"MODEL PERFORMANCE",F_TINY,ACCENT,26,panels_top+12)
    pts=l4["pts"]; gx,gy,gw,gh=20,panels_top+32,half-20,graph_panel_h-44
    draw_rect(surf,(0,0,0),(gx,gy,gw,gh),4,80)
    draw_border_rect(surf,BORDER,(gx,gy,gw,gh),1,4)
    for v in [25,50,75,100]:
        ly=gy+gh-int(v/100*gh)
        pygame.draw.line(surf,BORDER,(gx,ly),(gx+gw,ly),1)
        draw_text(surf,f"{v}%",F_TINY,DIM,gx+2,ly-14)
    if len(pts)>=2:
        drawn=pts[-60:]
        coords=[(gx+int(i/(len(drawn)-1)*gw),gy+gh-int(p/100*gh)) for i,p in enumerate(drawn)]
        for i in range(len(coords)-1):
            t=drawn[i]/100; col=lerp_color(RED,lerp_color(YELLOW,GREEN,t),t)
            pygame.draw.line(surf,col,coords[i],coords[i+1],2)
        pygame.draw.circle(surf,RED,coords[-1],5)
    done_count_exp=sum(1 for v in l4["actions"].values() if v)
    exp_graph_y=gy+gh+8; exp_graph_h=panels_top+graph_panel_h-exp_graph_y-4
    if exp_graph_h>30:
        if done_count_exp>=3: exp_col2,exp_msg=GREEN,"✓ Recovery! Retraining ke baad accuracy wapas aayi."
        elif done_count_exp>0: exp_col2,exp_msg=YELLOW,f"Partially recovered. {done_count_exp}/3 actions done."
        else: exp_col2,exp_msg=RED,"Data Drift: Real world data badal gaya. Actions karo!"
        draw_rect(surf,exp_col2,(gx,exp_graph_y,gw,exp_graph_h),4,30)
        draw_border_rect(surf,exp_col2,(gx,exp_graph_y,gw,exp_graph_h),1,4)
        draw_text_wrap(surf,exp_msg,F_TINY,exp_col2,gx+8,exp_graph_y+6,gw-16,18)
    alert_y=alert_y_off
    draw_rect(surf,RED,(10,alert_y,half,46),6,30)
    draw_border_rect(surf,RED,(10,alert_y,half,46),1,6)
    pulse=abs(math.sin(time.time()*2)); col=lerp_color((200,0,50),(255,51,102),pulse)
    draw_text(surf,"  DATA DRIFT DETECTED!",F_MED,col,26,alert_y+6)
    draw_text(surf,f"  Model accuracy: {round(l4['drift_acc'])}% – gir rahi hai!",F_TINY,RED,26,alert_y+28)
    draw_rect(surf,PANEL,(half+20,panels_top,half,graph_panel_h),8)
    draw_border_rect(surf,BORDER,(half+20,panels_top,half,graph_panel_h),1,8)
    draw_text(surf,"USER COMPLAINTS",F_TINY,RED,half+36,panels_top+12)
    clip_rect=pygame.Rect(half+20,panels_top+30,half,graph_panel_h-40)
    old_clip=surf.get_clip(); surf.set_clip(clip_rect)
    for i,c in enumerate(complaints_log[-7:]):
        draw_text(surf,c,F_TINY,(255,80,100),half+28,panels_top+34+i*24)
    surf.set_clip(old_clip)
    actions_y=alert_y_off+56; actions_h=CB-actions_y
    draw_rect(surf,PANEL,(half+20,actions_y,half,actions_h),8)
    draw_border_rect(surf,BORDER,(half+20,actions_y,half,actions_h),1,8)
    draw_text(surf,"ACTIONS",F_TINY,ACCENT,half+36,actions_y+12)
    actions=l4["actions"]
    action_defs=[("collect","New Data Collect Karo",ACCENT),("retrain","Model Retrain Karo",GREEN),("rollback","Rollback to v1.0",YELLOW)]
    action_btn_rects={}
    for i,(key,label,col) in enumerate(action_defs):
        done=actions[key]; by=actions_y+46+i*56; bw,bh=half-40,42; bx=half+30
        if done:
            draw_rect(surf,DIM,(bx,by,bw,bh),6,60); draw_border_rect(surf,DIM,(bx,by,bw,bh),1,6)
            draw_text(surf,f"✓ {label} (Done)",F_SMALL,DIM,bx+bw//2,by+12,center=True)
        else:
            draw_glow_rect(surf,col,(bx,by,bw,bh))
            draw_text(surf,label,F_MED,BLACK,bx+bw//2,by+10,center=True)
        action_btn_rects[key]=pygame.Rect(bx,by,bw,bh)
    done_count=sum(1 for v in actions.values() if v)
    draw_text(surf,f"Actions done: {done_count}/3",F_SMALL,ACCENT,half+36,actions_y+actions_h-44)
    pbar_x,pbar_y,pbar_w,pbar_h=half+30,actions_y+actions_h-20,half-40,8
    draw_rect(surf,BORDER,(pbar_x,pbar_y,pbar_w,pbar_h),4)
    if done_count>0: draw_rect(surf,GREEN,(pbar_x,pbar_y,int(pbar_w*done_count/3),pbar_h),4)

# ─────────────────────────────────────────
#  COMPLETE SCREEN
# ─────────────────────────────────────────
def draw_complete_screen(surf):
    area_w=W-SIDEBAR_W; cx=area_w//2; t_now=time.time()
    pulse=0.6+0.4*math.sin(t_now*2)
    title_y=118
    draw_text(surf,"🏆  GAME COMPLETE!",F_HUGE,GREEN,cx,title_y,center=True)
    draw_text(surf,"Tum ek certified MLOps Engineer ban gaye!",F_MED,ACCENT,cx,title_y+68,center=True)
    banner_y=title_y+104
    draw_rect(surf,PANEL,(10,banner_y,area_w-20,54),8)
    draw_border_rect(surf,YELLOW,(10,banner_y,area_w-20,54),2,8)
    draw_text(surf,f"FINAL SCORE:  {state['score']}  pts",F_LARGE,YELLOW,cx,banner_y+12,center=True)
    col_top=banner_y+68; col_h=H-col_top-70
    col1_x=10; col1_w=(area_w-30)//2; col2_x=col1_x+col1_w+10; col2_w=area_w-col1_w-30
    draw_rect(surf,PANEL,(col1_x,col_top,col1_w,col_h),8)
    draw_border_rect(surf,ACCENT,(col1_x,col_top,col1_w,col_h),2,8)
    draw_text(surf,"📊 GRAPH EXPLANATIONS",F_MED,ACCENT,col1_x+16,col_top+12)
    explanations=[
        (ACCENT,"Level 2 – Training Loss Graph",
         ["Blue line (Train Loss): Har epoch ke baad model","ka error kitna tha. Neeche aana = model seekh raha hai.",
          "Orange line (Val Loss): Validation pe error. Agar","orange upar jaaye aur blue neeche – OVERFITTING hai!",
          f"Tumhara final accuracy: {round(state['model_acc'])}%"]),
        (RED,"Level 4 – Performance Drift Graph",
         ["Ye graph deployed model ki accuracy ko real-time","track karta hai. Accuracy girti hai – yahi DATA DRIFT hai.",
          "Retraining ke baad recovery hoti hai.",f"Final drift recovery: {round(state['l4']['drift_acc'])}%"]),
    ]
    ey=col_top+48
    for color,title,lines in explanations:
        draw_rect(surf,color,(col1_x+12,ey,col1_w-24,14),2,20)
        draw_text(surf,title,F_SMALL,color,col1_x+16,ey+18); ey+=38
        for line in lines:
            draw_text(surf,line,F_TINY,TEXT,col1_x+20,ey); ey+=20
        ey+=12
    draw_rect(surf,PANEL,(col2_x,col_top,col2_w,col_h),8)
    draw_border_rect(surf,RED,(col2_x,col_top,col2_w,col_h),2,8)
    draw_text(surf,"❌ GALTIYON KI SUMMARY",F_MED,RED,col2_x+16,col_top+12)
    mistakes=state.get("mistakes",[]); my2=col_top+48
    if not mistakes:
        draw_rect(surf,GREEN,(col2_x+12,my2,col2_w-24,44),6,30)
        draw_border_rect(surf,GREEN,(col2_x+12,my2,col2_w-24,44),1,6)
        draw_text(surf,"🎉 Koi galti nahi! Perfect game!",F_MED,GREEN,col2_x+col2_w//2,my2+13,center=True)
        my2+=54
    else:
        by_level={}
        for m in mistakes: by_level.setdefault(m["level"],[]).append(m)
        level_colors={1:GREEN,2:ACCENT,3:PURPLE,4:RED}
        level_names={1:"L1: Data",2:"L2: Training",3:"L3: Deploy",4:"L4: Monitor"}
        for lv in sorted(by_level.keys()):
            col3=level_colors.get(lv,DIM)
            draw_text(surf,f"▸ {level_names[lv]}  ({len(by_level[lv])} galtiyan)",F_SMALL,col3,col2_x+16,my2); my2+=24
            for m in by_level[lv][:4]:
                detail=m["detail"][:44]+"…" if len(m["detail"])>44 else m["detail"]
                draw_text(surf,f"  • {detail}",F_TINY,DIM,col2_x+20,my2); my2+=19
            if len(by_level[lv])>4:
                draw_text(surf,f"  …aur {len(by_level[lv])-4} aur",F_TINY,DIM,col2_x+20,my2); my2+=19
            my2+=6
    if my2<col_top+col_h-80:
        my2=max(my2,col_top+col_h-110)
        draw_rect(surf,PANEL,(col2_x+12,my2,col2_w-24,100),6)
        draw_border_rect(surf,BORDER,(col2_x+12,my2,col2_w-24,100),1,6)
        draw_text(surf,"GAME STATS",F_TINY,ACCENT,col2_x+24,my2+8)
        stats_data=[(f"Train attempts: {state.get('train_attempts',0)+1}",DIM),
                    (f"Deploy attempts: {state.get('deploy_attempts',0)}",DIM),
                    (f"L1 wrong drops: {state['l1']['errors']}",RED if state['l1']['errors']>0 else GREEN),
                    (f"Final model acc: {round(state['model_acc'])}%",GREEN),
                    (f"Total mistakes: {len(mistakes)}",RED if mistakes else GREEN)]
        for i,(txt,col3) in enumerate(stats_data):
            draw_text(surf,txt,F_TINY,col3,col2_x+24,my2+28+i*16)
    # ── Bottom buttons ──
    btn_y = H - 60
    acad_btn = pygame.Rect(cx - 260, btn_y, 240, 44)
    draw_glow_rect(surf, PURPLE, (acad_btn.x, acad_btn.y, acad_btn.w, acad_btn.h))
    draw_text(surf, "🎓 ADVANCED ACADEMY", F_MED, WHITE, acad_btn.centerx, acad_btn.y+10, center=True)
    exit_col = lerp_color(RED,(255,100,100),pulse)
    exit_btn = pygame.Rect(cx + 20, btn_y, 240, 44)
    draw_glow_rect(surf, exit_col, (exit_btn.x, exit_btn.y, exit_btn.w, exit_btn.h))
    draw_text(surf, "✕  EXIT GAME", F_LARGE, WHITE, exit_btn.centerx, exit_btn.y+9, center=True)
    draw_text(surf,"Data → Train → Deploy → Monitor → Retrain  =  MLOps Loop! 🔄",
              F_TINY,DIM,cx,btn_y-20,center=True)
    return {"exit": exit_btn, "academy": acad_btn}

# ═════════════════════════════════════════
#  🎓 ADVANCED MLOPS ACADEMY
# ═════════════════════════════════════════

ACADEMY_TOPICS = [
    # ── CONTAINERIZATION ──────────────────────────────────────────────────────
    {
        "id": "docker",
        "category": "Containerization",
        "cat_color": (0, 180, 255),
        "icon": "🐳",
        "title": "Docker",
        "tagline": "Apna model ek portable box mein band karo!",
        "difficulty": 2,
        "real_world": "Netflix, Uber, Airbnb har ML model Docker mein serve karte hain.",
        "sections": [
            {
                "heading": "Docker kya hai?",
                "body": (
                    "Docker ek container technology hai jo tumhara ML model, "
                    "uske saare dependencies (Python version, libraries, configs) "
                    "ek single portable 'image' mein pack kar deta hai. "
                    "Ab 'mere machine pe toh chalata tha!' wali problem khatam!"
                ),
            },
            {
                "heading": "Dockerfile — Tumhara model ka recipe",
                "body": "",
                "code": """\
FROM python:3.11-slim          # Base OS + Python

WORKDIR /app                   # Working directory

COPY requirements.txt .        # Dependencies list copy karo
RUN pip install -r requirements.txt   # Install karo

COPY model/ ./model/           # Trained model files
COPY serve.py .                # FastAPI/Flask server

EXPOSE 8080                    # Port open karo
CMD ["python", "serve.py"]    # Server start karo""",
            },
            {
                "heading": "Key Commands",
                "body": "",
                "code": """\
# Image build karo
docker build -t my-ml-model:v1 .

# Container run karo (port 8080 expose)
docker run -p 8080:8080 my-ml-model:v1

# Running containers dekho
docker ps

# Image registry pe push karo
docker push myregistry/my-ml-model:v1""",
            },
            {
                "heading": "MLOps mein Docker kyun?",
                "body": (
                    "Training environment aur Production environment hamesha same rehta hai. "
                    "CI/CD pipeline automatically naya Docker image build karti hai "
                    "har baar code push hota hai. Multiple models alag-alag containers "
                    "mein independently run kar sakte hain bina conflict ke."
                ),
            },
        ],
        "quiz": {
            "q": "Docker container kya pack karta hai?",
            "opts": ["Sirf Python code", "Model + dependencies + configs sab kuch",
                     "Sirf trained weights", "Sirf OS"],
            "ans": 1,
        },
        "resources": ["docs.docker.com", "play-with-docker.com (free playground)"],
    },

    # ── ORCHESTRATION ─────────────────────────────────────────────────────────
    {
        "id": "kubernetes",
        "category": "Orchestration",
        "cat_color": (74, 144, 226),
        "icon": "☸️",
        "title": "Kubernetes (K8s)",
        "tagline": "Hazaron Docker containers ko ek saath manage karo!",
        "difficulty": 4,
        "real_world": "Google, Meta, LinkedIn — sab K8s use karte hain production ML ke liye.",
        "sections": [
            {
                "heading": "Kubernetes kya problem solve karta hai?",
                "body": (
                    "Ek Docker container chalana easy hai. Lekin agar tumhara model "
                    "10,000 requests/second handle kare, toh? Kubernetes (K8s) "
                    "automatically containers ko scale karta hai, crash hone pe "
                    "restart karta hai, aur load distribute karta hai."
                ),
            },
            {
                "heading": "Core Concepts",
                "body": (
                    "POD: Ek ya zyada containers ka group — deployment ka basic unit.\n"
                    "DEPLOYMENT: Pods ka blueprint — kitne replicas chahiye, kaunsa image.\n"
                    "SERVICE: Network endpoint jo traffic route karta hai pods tak.\n"
                    "INGRESS: External traffic ko sahi service pe forward karta hai.\n"
                    "HPA: Horizontal Pod Autoscaler — load ke hisaab se pods badhata/ghataata hai."
                ),
            },
            {
                "heading": "ML Model Deploy karna K8s pe",
                "body": "",
                "code": """\
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-v2
spec:
  replicas: 3          # 3 copies parallel mein
  selector:
    matchLabels:
      app: ml-model
  template:
    spec:
      containers:
      - name: model
        image: myregistry/ml-model:v2
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
# Auto-scale 2 se 20 pods tak (CPU > 70%)
kubectl autoscale deployment ml-model-v2 \\
  --min=2 --max=20 --cpu-percent=70""",
            },
            {
                "heading": "MLOps workflow with K8s",
                "body": (
                    "1. Code push → GitHub Actions Docker image build kare.\n"
                    "2. Image registry (ECR/GCR) pe push ho.\n"
                    "3. K8s rolling update shuru ho — zero downtime!\n"
                    "4. Canary deployment: pehle 10% traffic naye model ko,\n"
                    "   phir 100% — agar metrics theek hain toh.\n"
                    "5. Kuch gadbad? Ek command se rollback."
                ),
            },
        ],
        "quiz": {
            "q": "Kubernetes ka HPA (Horizontal Pod Autoscaler) kya karta hai?",
            "opts": ["Model retrain karta hai", "Load ke hisaab se containers badhata/ghataata hai",
                     "Docker images build karta hai", "Database backup leta hai"],
            "ans": 1,
        },
        "resources": ["kubernetes.io/docs", "k3s.io (lightweight K8s for learning)"],
    },

    # ── CI/CD ─────────────────────────────────────────────────────────────────
    {
        "id": "cicd",
        "category": "Automation",
        "cat_color": (255, 140, 0),
        "icon": "⚙️",
        "title": "CI/CD for ML",
        "tagline": "Model deployment ko fully automatic karo!",
        "difficulty": 3,
        "real_world": "Spotify, DoorDash — har ML update automatically test aur deploy hoti hai.",
        "sections": [
            {
                "heading": "CI/CD kya hota hai?",
                "body": (
                    "CI = Continuous Integration: Har code push pe automatically "
                    "tests run karo — code sahi hai ya nahi.\n"
                    "CD = Continuous Deployment: Tests pass hone ke baad "
                    "automatically model production mein deploy ho jaaye.\n"
                    "ML ke liye extra steps hain: data validation, model evaluation, "
                    "bias checks — sab automated!"
                ),
            },
            {
                "heading": "GitHub Actions — ML Pipeline Example",
                "body": "",
                "code": """\
# .github/workflows/ml-pipeline.yml
name: ML Model CI/CD

on:
  push:
    branches: [main]

jobs:
  train-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Data Validation
        run: python scripts/validate_data.py
        # Data corrupt/missing hai toh fail!

      - name: Train Model
        run: python train.py --epochs 100

      - name: Evaluate Model
        run: |
          python evaluate.py
          # Accuracy < 70%? Pipeline fail!

      - name: Bias Check
        run: python check_fairness.py

      - name: Build Docker Image
        run: docker build -t model:${{ github.sha }} .

      - name: Deploy to K8s
        run: kubectl set image deployment/ml-app \\
               model=myregistry/model:${{ github.sha }}""",
            },
            {
                "heading": "ML-specific CI/CD checks",
                "body": (
                    "DATA DRIFT CHECK: Naya training data purane se kitna alag hai?\n"
                    "MODEL REGRESSION: Naya model purane se behtar hai?\n"
                    "LATENCY TEST: Inference time acceptable hai? (< 100ms?)\n"
                    "MEMORY PROFILING: Model RAM limit ke andar hai?\n"
                    "SHADOW MODE: Naya model real traffic pe test karo silently."
                ),
            },
        ],
        "quiz": {
            "q": "ML CI/CD mein 'Model Regression Check' kya verify karta hai?",
            "opts": ["Data ki quality", "Naya model purane se behtar performance deta hai",
                     "Docker image size", "Server uptime"],
            "ans": 1,
        },
        "resources": ["github.com/features/actions", "mlflow.org", "dvc.org"],
    },

    # ── EXPERIMENT TRACKING ───────────────────────────────────────────────────
    {
        "id": "mlflow",
        "category": "Experiment Tracking",
        "cat_color": (0, 200, 120),
        "icon": "📊",
        "title": "MLflow & Experiment Tracking",
        "tagline": "Hazaron training runs mein se best model dhundo!",
        "difficulty": 2,
        "real_world": "Microsoft, Booking.com — har ML experiment automatically tracked hoti hai.",
        "sections": [
            {
                "heading": "Problem: Experiment Chaos",
                "body": (
                    "Tumne 50 experiments chalaaye — alag-alag epochs, learning rates, "
                    "architectures. Ab kaunsa best tha? Notes mein likhna? "
                    "Excel spreadsheet? MLflow is sab ko automatically track karta hai "
                    "— metrics, parameters, artifacts, model versions."
                ),
            },
            {
                "heading": "MLflow Integration — 5 lines mein!",
                "body": "",
                "code": """\
import mlflow
import mlflow.sklearn

# Experiment shuru karo
mlflow.set_experiment("fraud-detection-v2")

with mlflow.start_run(run_name="random-forest-100"):
    # Parameters log karo
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    mlflow.log_param("learning_rate", 0.001)

    # Model train karo
    model = train_model(X_train, y_train)

    # Metrics log karo
    mlflow.log_metric("accuracy", 0.94)
    mlflow.log_metric("f1_score", 0.91)
    mlflow.log_metric("inference_ms", 12.3)

    # Model save karo
    mlflow.sklearn.log_model(model, "model")
    # Ab UI mein compare kar sako sab runs!""",
            },
            {
                "heading": "Model Registry",
                "body": (
                    "STAGING: Model test environment mein — QA team check kare.\n"
                    "PRODUCTION: Live users ke liye approved model.\n"
                    "ARCHIVED: Purane versions — rollback ke liye ready.\n\n"
                    "Alternatives: Weights & Biases (W&B), Neptune.ai, Comet ML — "
                    "sab similar concept, different features."
                ),
            },
        ],
        "quiz": {
            "q": "MLflow Model Registry mein 'Staging' stage ka kya matlab hai?",
            "opts": ["Model delete ho gaya", "Test environment mein approve hone ka wait kar raha hai",
                     "Production mein live hai", "Training chal rahi hai"],
            "ans": 1,
        },
        "resources": ["mlflow.org", "wandb.ai (Weights & Biases)"],
    },

    # ── FEATURE STORE ─────────────────────────────────────────────────────────
    {
        "id": "feature_store",
        "category": "Data Engineering",
        "cat_color": (180, 74, 255),
        "icon": "🏪",
        "title": "Feature Store",
        "tagline": "ML features ek jagah manage karo — sab teams ke liye!",
        "difficulty": 3,
        "real_world": "Uber (Michelangelo), Twitter, Shopify — feature stores pe billions of predictions daily.",
        "sections": [
            {
                "heading": "Feature Store kya problem solve karta hai?",
                "body": (
                    "Team A ne 'user_avg_spend_7d' feature banaya. Team B ne bhi same "
                    "feature alag method se banaya — inconsistency! Feature Store ek "
                    "centralized repository hai jahan sab ML features defined, "
                    "versioned, aur shared hote hain."
                ),
            },
            {
                "heading": "Online vs Offline Store",
                "body": (
                    "OFFLINE STORE (Batch): Historical data — training ke liye.\n"
                    "  → Data warehouse: BigQuery, Snowflake, S3\n"
                    "  → Slow access ok hai (hours)\n\n"
                    "ONLINE STORE (Real-time): Live predictions ke liye.\n"
                    "  → Redis, DynamoDB, Cassandra\n"
                    "  → Ultra-fast: < 10ms latency zaroori\n\n"
                    "FEAST (open source) dono ko ek saath handle karta hai!"
                ),
            },
            {
                "heading": "Feast — Feature Store Example",
                "body": "",
                "code": """\
from feast import Entity, Feature, FeatureView, FileSource
from feast.types import Float32, Int64

# Entity define karo
user = Entity(name="user_id", join_keys=["user_id"])

# Feature View — kahan se aata hai data
user_stats_fv = FeatureView(
    name="user_stats",
    entities=[user],
    ttl=timedelta(days=1),
    schema=[
        Feature(name="avg_spend_7d", dtype=Float32),
        Feature(name="login_count_30d", dtype=Int64),
        Feature(name="churn_risk_score", dtype=Float32),
    ],
    source=FileSource(path="data/user_stats.parquet"),
)

# Training data fetch karo
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=["user_stats:avg_spend_7d",
              "user_stats:churn_risk_score"]
).to_df()""",
            },
        ],
        "quiz": {
            "q": "Feature Store ka 'Online Store' kyun use hota hai?",
            "opts": ["Training data store karne ke liye", "Real-time predictions ke liye fast feature retrieval",
                     "Model versioning ke liye", "CI/CD pipeline ke liye"],
            "ans": 1,
        },
        "resources": ["feast.dev", "tecton.ai", "hopsworks.ai"],
    },

    # ── MODEL SERVING ─────────────────────────────────────────────────────────
    {
        "id": "serving",
        "category": "Model Serving",
        "cat_color": (255, 200, 0),
        "icon": "🚀",
        "title": "Model Serving: REST, gRPC & Streaming",
        "tagline": "Trained model ko live API mein badhlo!",
        "difficulty": 2,
        "real_world": "TensorFlow Serving, TorchServe, Triton — industry standard serving frameworks.",
        "sections": [
            {
                "heading": "Serving Patterns",
                "body": (
                    "REST API (FastAPI/Flask): Simple, web-friendly. JSON input/output.\n"
                    "  Best for: Low-medium throughput, general use.\n\n"
                    "gRPC: Binary protocol, 5–10x faster than REST.\n"
                    "  Best for: Inter-service communication, mobile.\n\n"
                    "BATCH INFERENCE: Offline, bulk predictions.\n"
                    "  Best for: Reports, nightly jobs, email campaigns.\n\n"
                    "STREAMING (Kafka): Real-time event-driven predictions.\n"
                    "  Best for: Fraud detection, recommendations feed."
                ),
            },
            {
                "heading": "FastAPI Model Server — Production Ready",
                "body": "",
                "code": """\
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.pyfunc
import time

app = FastAPI(title="ML Model API v2")

# Startup pe model load karo (ek baar)
model = mlflow.pyfunc.load_model("models:/fraud-detector/Production")

class PredictRequest(BaseModel):
    user_id: str
    amount: float
    merchant_category: str
    hour_of_day: int

class PredictResponse(BaseModel):
    prediction: str
    confidence: float
    inference_ms: float

@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    start = time.time()
    try:
        features = extract_features(req)
        prob = model.predict(features)[0]
        return PredictResponse(
            prediction="FRAUD" if prob > 0.8 else "LEGIT",
            confidence=float(prob),
            inference_ms=(time.time()-start)*1000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health(): return {"status": "ok", "model": "fraud-v2"}""",
            },
            {
                "heading": "Triton Inference Server",
                "body": (
                    "NVIDIA Triton: Enterprise-grade serving.\n"
                    "→ Multiple models ek saath serve karo.\n"
                    "→ Dynamic batching: requests ko group karo GPU efficiency ke liye.\n"
                    "→ Model Ensemble: multiple models chain karo.\n"
                    "→ TensorRT optimization: 3–8x faster GPU inference.\n"
                    "→ Supports: PyTorch, TensorFlow, ONNX, XGBoost."
                ),
            },
        ],
        "quiz": {
            "q": "gRPC, REST se better kyun hai high-throughput ML serving mein?",
            "opts": ["Zyada secure hai", "Binary protocol — 5-10x faster, kam bandwidth",
                     "Python mein likhna aasaan hai", "Docker ke saath better kaam karta hai"],
            "ans": 1,
        },
        "resources": ["fastapi.tiangolo.com", "developer.nvidia.com/triton-inference-server"],
    },

    # ── DATA VERSIONING ───────────────────────────────────────────────────────
    {
        "id": "dvc",
        "category": "Data Versioning",
        "cat_color": (0, 210, 180),
        "icon": "📦",
        "title": "DVC — Data Version Control",
        "tagline": "Data aur models ka Git banao!",
        "difficulty": 2,
        "real_world": "Git sirf code track karta hai — 50GB dataset? DVC ke bina impossible.",
        "sections": [
            {
                "heading": "Problem: Data Git mein nahi jaata",
                "body": (
                    "Git large files (GB/TB) handle nahi kar sakta. "
                    "DVC (Data Version Control) Git ke saath kaam karta hai — "
                    "actual data S3/GCS/Azure mein store hota hai, "
                    "sirf ek small .dvc pointer file Git mein jaati hai."
                ),
            },
            {
                "heading": "DVC Basic Workflow",
                "body": "",
                "code": """\
# DVC initialize karo
dvc init
git commit -m "Initialize DVC"

# Data file track karo
dvc add data/training_data.csv
# → data/training_data.csv.dvc create hoga (small pointer)
git add data/training_data.csv.dvc .gitignore
git commit -m "Add training data v1 (10GB)"

# Remote storage configure karo
dvc remote add -d myremote s3://my-ml-bucket/data
dvc push    # Data S3 pe upload

# Naya version — data update hua
dvc add data/training_data.csv   # v2
git commit -m "Training data v2 — added new users"
dvc push

# Purani version pe wapas jao!
git checkout v1-tag
dvc pull    # Automatically correct data pull karo""",
            },
            {
                "heading": "DVC Pipelines — Reproducible ML",
                "body": "",
                "code": """\
# dvc.yaml — poora pipeline define karo
stages:
  preprocess:
    cmd: python preprocess.py
    deps: [data/raw.csv, preprocess.py]
    outs: [data/processed.csv]

  train:
    cmd: python train.py --epochs 100
    deps: [data/processed.csv, train.py]
    outs: [models/model.pkl]
    metrics: [metrics.json]

  evaluate:
    cmd: python evaluate.py
    deps: [models/model.pkl, data/test.csv]
    metrics: [evaluation.json]

# Sab run karo:
dvc repro    # Sirf changed steps re-run honge!""",
            },
        ],
        "quiz": {
            "q": "DVC Git ke saath kaise kaam karta hai?",
            "opts": ["Data directly Git mein push karta hai",
                     "Small pointer file Git mein, actual data remote storage mein",
                     "Git replace karta hai ML ke liye",
                     "Sirf model weights track karta hai"],
            "ans": 1,
        },
        "resources": ["dvc.org", "dvc.org/doc/start (5 min tutorial)"],
    },

    # ── MONITORING ────────────────────────────────────────────────────────────
    {
        "id": "monitoring_adv",
        "category": "Advanced Monitoring",
        "cat_color": (255, 80, 80),
        "icon": "📡",
        "title": "Advanced Monitoring: Evidently & Prometheus",
        "tagline": "Model health 24/7 track karo — automatic alerts!",
        "difficulty": 3,
        "real_world": "Gojek, Tokopedia — production models har minute monitor hote hain.",
        "sections": [
            {
                "heading": "Kya monitor karna chahiye?",
                "body": (
                    "DATA DRIFT: Input features ka distribution badal gaya?\n"
                    "CONCEPT DRIFT: Input-output relationship badal gaya?\n"
                    "PREDICTION DRIFT: Model outputs ka distribution shift?\n"
                    "DATA QUALITY: Null values, outliers, schema changes?\n"
                    "INFRASTRUCTURE: Latency, throughput, error rate, CPU/RAM?"
                ),
            },
            {
                "heading": "Evidently AI — Drift Detection",
                "body": "",
                "code": """\
from evidently.report import Report
from evidently.metric_preset import (
    DataDriftPreset, DataQualityPreset,
    TargetDriftPreset
)

# Reference data (training time)
reference_data = pd.read_parquet("train_data.parquet")
# Current data (production mein aaya)
current_data   = pd.read_parquet("prod_data_today.parquet")

# Report banao
report = Report(metrics=[
    DataDriftPreset(),        # Feature drift
    DataQualityPreset(),      # Quality issues
    TargetDriftPreset(),      # Prediction drift
])

report.run(
    reference_data=reference_data,
    current_data=current_data,
)

report.save_html("drift_report.html")
# Beautiful interactive HTML report!

# Programmatic alert
drift_result = report.as_dict()
if drift_result["metrics"][0]["result"]["dataset_drift"]:
    trigger_retraining_pipeline()  # Auto retrain!""",
            },
            {
                "heading": "Prometheus + Grafana Stack",
                "body": (
                    "PROMETHEUS: Metrics collect karo har 15 seconds.\n"
                    "  → Model inference latency (p50, p95, p99)\n"
                    "  → Prediction distribution per class\n"
                    "  → Error rates, throughput, queue depth\n\n"
                    "GRAFANA: Beautiful dashboards banao.\n"
                    "  → Real-time graphs, heatmaps, alerts\n"
                    "  → PagerDuty/Slack se integrate karo\n"
                    "  → SLA breach? Automatic on-call alert!"
                ),
            },
        ],
        "quiz": {
            "q": "'Concept Drift' kya hoti hai?",
            "opts": ["Server crash ho gaya", "Input-output relationship real world mein badal gayi",
                     "Training data corrupt ho gaya", "Model weights delete ho gaye"],
            "ans": 1,
        },
        "resources": ["evidentlyai.com", "prometheus.io", "grafana.com"],
    },

    # ── LLMOps ───────────────────────────────────────────────────────────────
    {
        "id": "llmops",
        "category": "LLMOps",
        "cat_color": (255, 150, 50),
        "icon": "🤖",
        "title": "LLMOps — Operating Large Language Models",
        "tagline": "GPT/Claude jaisi models ko production mein chalao!",
        "difficulty": 4,
        "real_world": "OpenAI, Anthropic, Google — LLMOps traditional MLOps se alag hai.",
        "sections": [
            {
                "heading": "LLMOps vs Traditional MLOps",
                "body": (
                    "Traditional ML: Custom model train karo from scratch.\n"
                    "LLMOps: Pre-trained foundation model (GPT-4, Llama, Claude) "
                    "ko apne use-case ke liye adapt karo.\n\n"
                    "Key differences:\n"
                    "→ Fine-tuning vs Full training (100x cheaper)\n"
                    "→ Prompt Engineering bhi deployment hai!\n"
                    "→ Evaluation subjective hai — human feedback zaroori\n"
                    "→ Hallucination monitoring — model galat info na de\n"
                    "→ Token cost tracking — API bills control karo"
                ),
            },
            {
                "heading": "RAG — Retrieval Augmented Generation",
                "body": "",
                "code": """\
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# Step 1: Knowledge base embed karo
embeddings = OpenAIEmbeddings()
vectorstore = Pinecone.from_documents(
    documents=your_company_docs,
    embedding=embeddings,
    index_name="company-kb"
)

# Step 2: RAG chain banao
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(model="gpt-4"),
    retriever=vectorstore.as_retriever(
        search_kwargs={"k": 5}  # Top 5 relevant docs
    ),
    return_source_documents=True
)

# Step 3: Query karo
result = qa_chain("Hamari refund policy kya hai?")
# Model sirf tumhare docs se answer dega!
# Hallucination drastically kam!""",
            },
            {
                "heading": "LLMOps Monitoring",
                "body": (
                    "PROMPT VERSIONING: Har prompt ka version track karo.\n"
                    "HALLUCINATION DETECTION: Facts verify karo automatically.\n"
                    "LATENCY: LLM calls slow hain — cache karo common queries.\n"
                    "COST TRACKING: GPT-4 = $0.03/1K tokens — monitor karo!\n"
                    "GUARDRAILS: Harmful content filter karo (Nvidia NeMo).\n"
                    "A/B TESTING: GPT-4 vs Llama3 — kaunsa better hai tumhare use-case mein?\n"
                    "Tools: LangSmith, Helicone, Phoenix (Arize), Langfuse."
                ),
            },
        ],
        "quiz": {
            "q": "RAG (Retrieval Augmented Generation) kya solve karta hai?",
            "opts": ["Model ko faster banata hai", "LLM ko tumhare specific docs se accurate answers dene mein help karta hai",
                     "Training cost kam karta hai", "Docker containers manage karta hai"],
            "ans": 1,
        },
        "resources": ["langchain.com", "llamaindex.ai", "langfuse.com"],
    },

    # ── MLOPS ROADMAP ─────────────────────────────────────────────────────────
    {
        "id": "roadmap",
        "category": "Career Path",
        "cat_color": (255, 215, 0),
        "icon": "🗺️",
        "title": "MLOps Engineer — Complete Roadmap",
        "tagline": "0 se MLOps Engineer — step by step plan!",
        "difficulty": 1,
        "real_world": "MLOps Engineer salary: ₹15L–₹60L India, $120K–$200K USA (2024).",
        "sections": [
            {
                "heading": "Phase 1: Foundations (Month 1-3)",
                "body": (
                    "✅ Python (NumPy, Pandas, Scikit-learn) — already jaante ho!\n"
                    "✅ ML Basics (training, evaluation) — game mein seekha!\n"
                    "→ Linux command line basics\n"
                    "→ Git & GitHub — code versioning\n"
                    "→ SQL — data querying\n"
                    "→ REST APIs — Flask ya FastAPI\n"
                    "→ Cloud basics: AWS/GCP/Azure (free tier se start karo)"
                ),
            },
            {
                "heading": "Phase 2: Core MLOps Tools (Month 4-6)",
                "body": (
                    "→ Docker — containers (is game mein padhha!)\n"
                    "→ Kubernetes basics — K8s (padhha!)\n"
                    "→ MLflow ya W&B — experiment tracking\n"
                    "→ DVC — data versioning\n"
                    "→ GitHub Actions ya GitLab CI — CI/CD\n"
                    "→ Prometheus + Grafana — monitoring"
                ),
            },
            {
                "heading": "Phase 3: Advanced (Month 7-12)",
                "body": (
                    "→ Kubeflow ya MLflow on K8s — full platform\n"
                    "→ Apache Kafka — streaming data\n"
                    "→ Apache Airflow — workflow orchestration\n"
                    "→ Terraform — infrastructure as code\n"
                    "→ Feature Store (Feast/Tecton)\n"
                    "→ Model optimization: ONNX, TensorRT, quantization\n"
                    "→ LLMOps — RAG, fine-tuning, guardrails"
                ),
            },
            {
                "heading": "Projects jo Portfolio mein daalo",
                "body": (
                    "1. End-to-end ML pipeline: Data → Train → Deploy → Monitor\n"
                    "   (GitHub pe README ke saath)\n"
                    "2. Real-time fraud detection system with Kafka\n"
                    "3. LLM chatbot with RAG on custom documents\n"
                    "4. Automated retraining pipeline with drift detection\n\n"
                    "Certifications worth getting:\n"
                    "→ AWS ML Specialty / GCP Professional ML Engineer\n"
                    "→ CKA (Certified Kubernetes Administrator)\n"
                    "→ Databricks Certified ML Professional"
                ),
            },
        ],
        "quiz": {
            "q": "MLOps Career ke liye sabse pehle kya seekhna chahiye?",
            "opts": ["Kubernetes", "Python + ML Basics + Git", "LLMOps", "Terraform"],
            "ans": 1,
        },
        "resources": ["roadmap.sh/mlops", "fullstackdeeplearning.com", "madewithml.com"],
    },
]

# ── Academy State ──────────────────────────────────────────────────────────────
academy_state = {
    "active": False,
    "selected_topic": None,   # topic id currently open
    "scroll": 0,              # card list scroll
    "detail_scroll": 0,       # detail view scroll
    "quiz_selected": None,
    "quiz_answered": False,
    "completed": set(),       # topic ids read
    "cat_filter": None,       # category filter
}
_acad_back_btn   = None
_acad_quiz_btns  = []
_acad_card_rects = {}

def draw_academy(surf):
    global _acad_back_btn, _acad_quiz_btns, _acad_card_rects

    ac = academy_state
    area_w = W - SIDEBAR_W
    t_now  = time.time()

    if ac["selected_topic"]:
        _draw_academy_detail(surf, area_w, t_now)
    else:
        _draw_academy_list(surf, area_w, t_now)

def _draw_academy_list(surf, area_w, t_now):
    global _acad_card_rects
    ac = academy_state

    # Header
    draw_rect(surf, PANEL, (0, 110, area_w, 68), 0)
    pygame.draw.line(surf, BORDER, (0,178),(area_w,178), 1)
    draw_text(surf, "🎓 ADVANCED MLOps ACADEMY", F_LARGE, PURPLE, area_w//2, 118, center=True)
    draw_text(surf, "Game complete! Ab real-world MLOps tools seekho — click any topic", F_SMALL, DIM, area_w//2, 150, center=True)

    # Category pills
    cats = list(dict.fromkeys(t["category"] for t in ACADEMY_TOPICS))
    pill_x = 14; pill_y = 186; pill_h = 28
    cat_pill_rects = {}
    for cat in ["All"] + cats:
        pw = F_TINY.size(cat)[0] + 22
        active = (ac["cat_filter"] == cat) or (cat == "All" and ac["cat_filter"] is None)
        col = PURPLE if active else BORDER
        draw_rect(surf, col, (pill_x, pill_y, pw, pill_h), 14, 80 if active else 30)
        draw_border_rect(surf, col, (pill_x, pill_y, pw, pill_h), 1, 14)
        draw_text(surf, cat, F_TINY, WHITE if active else DIM, pill_x+11, pill_y+7)
        cat_pill_rects[cat] = pygame.Rect(pill_x, pill_y, pw, pill_h)
        pill_x += pw + 8
        if pill_x > area_w - 120:
            pill_x = 14; pill_y += pill_h + 6

    content_top = pill_y + pill_h + 12
    # Progress bar
    total_t = len(ACADEMY_TOPICS); done_t = len(ac["completed"])
    draw_text(surf, f"Progress: {done_t}/{total_t} topics", F_TINY, DIM, 14, content_top)
    pb_x, pb_y, pb_w = 14, content_top+20, area_w-28
    draw_rect(surf, BORDER, (pb_x, pb_y, pb_w, 8), 4)
    if done_t: draw_rect(surf, PURPLE, (pb_x, pb_y, int(pb_w*done_t/total_t), 8), 4)
    content_top += 36

    # Topic cards — 2 column grid
    col_w  = (area_w - 28) // 2
    card_h = 140
    gap    = 10
    _acad_card_rects = {}

    filtered = [t for t in ACADEMY_TOPICS
                if ac["cat_filter"] is None or t["category"] == ac["cat_filter"]]

    for idx, topic in enumerate(filtered):
        col_idx = idx % 2; row_idx = idx // 2
        cx2 = 14 + col_idx*(col_w + gap)
        cy2 = content_top + row_idx*(card_h + gap) - ac["scroll"]
        if cy2 > H or cy2 < content_top - card_h: continue

        done = topic["id"] in ac["completed"]
        cat_col = topic["cat_color"]

        # Card bg + border
        draw_rect(surf, PANEL, (cx2, cy2, col_w, card_h), 10)
        draw_border_rect(surf, cat_col if not done else GREEN,
                         (cx2, cy2, col_w, card_h), 2, 10)
        if done:
            draw_rect(surf, GREEN, (cx2+col_w-36, cy2+6, 30, 20), 10, 50)
            draw_text(surf, "✓", F_SMALL, GREEN, cx2+col_w-24, cy2+7)

        # Left accent strip
        draw_rect(surf, cat_col, (cx2, cy2, 6, card_h), 10, 180)

        # Category chip
        chip_w = F_TINY.size(topic["category"])[0] + 16
        draw_rect(surf, cat_col, (cx2+14, cy2+10, chip_w, 20), 10, 40)
        draw_text(surf, topic["category"], F_TINY, cat_col, cx2+22, cy2+13)

        # Icon + title
        draw_text(surf, topic["icon"], F_LARGE, cat_col, cx2+14, cy2+36)
        draw_text(surf, topic["title"], F_MED, WHITE, cx2+52, cy2+38)

        # Tagline
        draw_text_wrap(surf, topic["tagline"], F_TINY, DIM, cx2+14, cy2+72, col_w-28, 18)

        # Difficulty stars
        stars = "★"*topic["difficulty"] + "☆"*(5-topic["difficulty"])
        draw_text(surf, stars, F_TINY, YELLOW, cx2+14, cy2+card_h-24)

        # Real world teaser
        rw_short = topic["real_world"][:55]+"…" if len(topic["real_world"])>55 else topic["real_world"]
        draw_text(surf, rw_short, F_TINY, DIM, cx2+14, cy2+card_h-42)

        _acad_card_rects[topic["id"]] = pygame.Rect(cx2, cy2, col_w, card_h)

    # Store cat pill rects for click handling
    academy_state["_cat_pill_rects"] = cat_pill_rects

    # Back button
    global _acad_back_btn
    _acad_back_btn = pygame.Rect(area_w//2-90, H-52, 180, 38)
    draw_glow_rect(surf, RED, (_acad_back_btn.x, _acad_back_btn.y, _acad_back_btn.w, _acad_back_btn.h))
    draw_text(surf, "← GAME SUMMARY", F_MED, WHITE, _acad_back_btn.centerx, _acad_back_btn.y+9, center=True)

def _draw_academy_detail(surf, area_w, t_now):
    global _acad_back_btn, _acad_quiz_btns
    ac = academy_state
    topic = next((t for t in ACADEMY_TOPICS if t["id"] == ac["selected_topic"]), None)
    if not topic: return

    cat_col = topic["cat_color"]

    # Fixed header
    draw_rect(surf, PANEL, (0, 110, area_w, 72), 0)
    pygame.draw.line(surf, BORDER, (0, 182),(area_w, 182), 1)
    draw_text(surf, topic["icon"]+"  "+topic["title"], F_LARGE, cat_col, area_w//2, 116, center=True)
    draw_text(surf, topic["tagline"], F_SMALL, DIM, area_w//2, 150, center=True)

    # Real-world banner
    banner_y = 190
    draw_rect(surf, cat_col, (10, banner_y, area_w-20, 32), 6, 30)
    draw_border_rect(surf, cat_col, (10, banner_y, area_w-20, 32), 1, 6)
    draw_text(surf, "🌍 "+topic["real_world"], F_TINY, WHITE, area_w//2, banner_y+9, center=True)

    # Scrollable content area
    content_top = 232
    clip_rect = pygame.Rect(0, content_top, area_w, H - content_top - 110)
    old_clip = surf.get_clip()
    surf.set_clip(clip_rect)

    y = content_top + 8 - ac["detail_scroll"]

    for sec in topic["sections"]:
        # Section heading
        draw_rect(surf, cat_col, (10, y, area_w-20, 30), 6, 40)
        draw_border_rect(surf, cat_col, (10, y, area_w-20, 30), 1, 6)
        draw_text(surf, "▸  "+sec["heading"], F_SMALL, cat_col, 20, y+7)
        y += 38

        if sec.get("body"):
            for line in sec["body"].split("\n"):
                # Highlight special lines
                col = ACCENT if line.startswith("→") else (YELLOW if line.startswith("✅") else TEXT)
                if line.strip():
                    draw_text(surf, line, F_TINY, col, 18, y)
                    y += 19
                else:
                    y += 8

        if sec.get("code"):
            code_lines = sec["code"].split("\n")
            code_h = len(code_lines)*17 + 16
            draw_rect(surf, (4, 10, 18), (10, y, area_w-20, code_h), 6)
            draw_border_rect(surf, (40, 80, 120), (10, y, area_w-20, code_h), 1, 6)
            # Code tag
            draw_rect(surf, cat_col, (10, y, 70, 16), 4, 60)
            draw_text(surf, "CODE", F_TINY, cat_col, 16, y+2)
            y += 20
            for ci, cline in enumerate(code_lines):
                # Syntax colour hints
                if cline.strip().startswith("#"):
                    ccol = (100, 180, 100)    # comments green
                elif any(kw in cline for kw in ["def ","class ","import ","from ","return ","async "]):
                    ccol = (130, 180, 255)    # keywords blue
                elif cline.strip().startswith(("kubectl","docker","dvc","git")):
                    ccol = YELLOW             # CLI commands
                else:
                    ccol = (220, 220, 220)
                draw_text(surf, cline, F_TINY, ccol, 20, y)
                y += 17
            y += 8

        y += 12  # section gap

    # Quiz section
    draw_rect(surf, PURPLE, (10, y, area_w-20, 30), 6, 50)
    draw_border_rect(surf, PURPLE, (10, y, area_w-20, 30), 1, 6)
    draw_text(surf, "🧠 Quick Quiz", F_MED, PURPLE, area_w//2, y+6, center=True)
    y += 38
    q = topic["quiz"]
    draw_text_wrap(surf, q["q"], F_SMALL, TEXT, 16, y, area_w-32, 22)
    y += 36

    _acad_quiz_btns = []
    for qi, opt in enumerate(q["opts"]):
        bh2 = 36; bw2 = area_w - 32
        answered = ac["quiz_answered"]; sel = ac["quiz_selected"]
        if answered:
            if qi == q["ans"]:   bc = GREEN
            elif qi == sel:      bc = RED
            else:                bc = BORDER
        elif sel == qi:          bc = PURPLE
        else:                    bc = BORDER

        draw_rect(surf, bc, (16, y, bw2, bh2), 6, 35)
        draw_border_rect(surf, bc, (16, y, bw2, bh2), 2, 6)
        draw_text(surf, ["A","B","C","D"][qi]+". "+opt, F_SMALL,
                  WHITE if sel==qi or (answered and qi==q["ans"]) else TEXT, 28, y+9)
        _acad_quiz_btns.append(pygame.Rect(16, y, bw2, bh2))
        y += 44

    if ac["quiz_answered"]:
        r_col = GREEN if ac["quiz_selected"] == q["ans"] else RED
        r_msg = "🎉 Sahi!" if ac["quiz_selected"] == q["ans"] else f"❌ Galat! Sahi: {q['opts'][q['ans']]}"
        draw_rect(surf, r_col, (16, y, area_w-32, 36), 6, 35)
        draw_text(surf, r_msg, F_SMALL, r_col, area_w//2, y+9, center=True)
        y += 46

    # Resources
    y += 8
    draw_text(surf, "📚 Resources:", F_SMALL, ACCENT, 16, y); y += 24
    for res in topic.get("resources", []):
        draw_text(surf, "  → "+res, F_TINY, DIM, 16, y); y += 18

    y += 20
    surf.set_clip(old_clip)

    # Scroll indicator
    total_content = y + ac["detail_scroll"] - content_top + 20
    vis_h = clip_rect.height
    if total_content > vis_h:
        sb_h = max(30, int(vis_h * vis_h / total_content))
        sb_y = content_top + int(ac["detail_scroll"] / (total_content - vis_h) * (vis_h - sb_h))
        draw_rect(surf, PURPLE, (area_w-8, sb_y, 6, sb_h), 3, 120)

    # Fixed bottom bar
    bar_y = H - 100
    pygame.draw.line(surf, BORDER, (0, bar_y),(area_w, bar_y), 1)

    # Mark as read button
    done_already = topic["id"] in ac["completed"]
    mark_btn = pygame.Rect(14, bar_y+10, 220, 38)
    bc2 = DIM if done_already else GREEN
    draw_glow_rect(surf, bc2, (mark_btn.x, mark_btn.y, mark_btn.w, mark_btn.h))
    draw_text(surf, "✓ Already Read" if done_already else "✅ Mark as Read",
              F_MED, WHITE, mark_btn.centerx, mark_btn.y+9, center=True)

    _acad_back_btn = pygame.Rect(area_w-200, bar_y+10, 186, 38)
    draw_glow_rect(surf, ACCENT, (_acad_back_btn.x, _acad_back_btn.y, _acad_back_btn.w, _acad_back_btn.h))
    draw_text(surf, "← TOPIC LIST", F_MED, BLACK, _acad_back_btn.centerx, _acad_back_btn.y+9, center=True)

    academy_state["_mark_btn"] = mark_btn

def handle_academy_click(mx, my, button=1):
    ac = academy_state

    if ac["selected_topic"]:
        # Detail view clicks
        topic = next((t for t in ACADEMY_TOPICS if t["id"] == ac["selected_topic"]), None)

        # Scroll (mouse wheel)
        if button == 4:
            ac["detail_scroll"] = max(0, ac["detail_scroll"] - 40)
        elif button == 5:
            ac["detail_scroll"] += 40

        if button != 1: return

        # Quiz options
        if not ac["quiz_answered"]:
            for qi, br in enumerate(_acad_quiz_btns):
                if br.collidepoint(mx, my):
                    ac["quiz_selected"]  = qi
                    ac["quiz_answered"]  = True
                    if qi == topic["quiz"]["ans"]:
                        sfx.play("quiz_correct", cooldown_ms=0)
                        add_score(100)
                        aira_speak(f"Sahi! 🎉 {topic['title']} concept pakad liya! +100 pts")
                    else:
                        sfx.play("quiz_wrong", cooldown_ms=0)
                        aira_speak(f"Galat, lekin seekhne ka moka! Sahi: '{topic['quiz']['opts'][topic['quiz']['ans']]}'")
                    return

        # Mark as read
        mark_btn = ac.get("_mark_btn")
        if mark_btn and mark_btn.collidepoint(mx, my):
            ac["completed"].add(ac["selected_topic"])
            sfx.play("correct_drop")

        # Back button
        if _acad_back_btn and _acad_back_btn.collidepoint(mx, my):
            sfx.play("action_click")
            ac["selected_topic"]  = None
            ac["detail_scroll"]   = 0
            ac["quiz_selected"]   = None
            ac["quiz_answered"]   = False
    else:
        # List view clicks
        if button == 4:
            ac["scroll"] = max(0, ac["scroll"] - 40)
        elif button == 5:
            ac["scroll"] += 40

        if button != 1: return

        # Category filter pills
        for cat, rect in ac.get("_cat_pill_rects", {}).items():
            if rect.collidepoint(mx, my):
                sfx.play("action_click")
                ac["cat_filter"] = None if cat == "All" else cat
                ac["scroll"] = 0
                return

        # Topic cards
        for tid, rect in _acad_card_rects.items():
            if rect.collidepoint(mx, my):
                sfx.play("action_click")
                prev = ac["selected_topic"]
                ac["selected_topic"]  = tid
                ac["detail_scroll"]   = 0
                ac["quiz_selected"]   = None
                ac["quiz_answered"]   = False
                if prev != tid:   # only speak when switching to a NEW topic
                    title = next(t["title"] for t in ACADEMY_TOPICS if t["id"]==tid)
                    aira_speak(f"'{title}' topic khola! Scroll karo, pura padho, phir quiz do! 🎓")
                return

        # Back button (list view → game summary or welcome)
        if _acad_back_btn and _acad_back_btn.collidepoint(mx, my):
            sfx.play("action_click")
            ac["active"] = False
            state["screen"] = "complete" if state["l4"].get("done") else "welcome"


# ─────────────────────────────────────────
#  LEVEL HANDLERS
# ─────────────────────────────────────────
def init_level1():
    stream_items.clear()
    state["l1"]={"clean":0,"corrupt":0,"biased":0,"errors":0,"goal":{"clean":8,"corrupt":5,"biased":5},"done":False}
    global l1_spawn_timer; l1_spawn_timer=0

def init_level2():
    state["l2"].update({"epochs":50,"lr_raw":10,"acc":0.0,"trained":False,"done":False,
                        "graph_pts":[],"training":False,"train_timer":0,"train_total":0})

def init_level4():
    state["l4"]["drift_acc"]=state["model_acc"] or 75.0
    state["l4"]["pts"]=[state["l4"]["drift_acc"]]
    state["l4"]["actions"]={"collect":False,"retrain":False,"rollback":False}
    state["l4"]["done"]=False; state["l4"]["complaint_timer"]=0
    state["_drift_alerted"]=False
    complaints_log.clear()
    aira_speak("Level 4 shuru! Model ki accuracy gir rahi hai – Data Drift! Teeno actions karo.")
    sfx.play("drift_alert", cooldown_ms=0)   # 🔊

def handle_l1_drop(item_type, bucket_type, mx, my):
    l1=state["l1"]; correct=item_type==bucket_type
    if correct:
        if item_type=="clean":    l1["clean"]+=1
        elif item_type=="corrupt": l1["corrupt"]+=1
        elif item_type=="biased":  l1["biased"]+=1
        add_score(50); add_score_effect(mx,my,"+50",GREEN)
        notif.show("Correct! +50 pts",GREEN)
        sfx.play("correct_drop")   # 🔊
    else:
        l1["errors"]+=1
        notif.show(f"Wrong! {l1['errors']}/5 errors",RED)
        add_score_effect(mx,my,"WRONG!",RED)
        sfx.play("wrong_drop")    # 🔊
        state["mistakes"].append({"level":1,"type":"wrong_bucket","detail":f"Data type '{item_type}' ko '{bucket_type}' bucket mein daala"})
        if l1["errors"]>=5:
            notif.show("Too many errors! Retry karo.",RED)
            state["mistakes"].append({"level":1,"type":"level_reset","detail":"5 se zyada galat drops – level restart hua"})
            aira_speak("Bahut galat drops hue. Yaad raho: Clean=accurate, Corrupted=errors/nulls, Biased=limited diversity!")
            init_level1(); return
    g=l1["goal"]
    if l1["clean"]>=g["clean"] and l1["corrupt"]>=g["corrupt"] and l1["biased"]>=g["biased"]:
        l1["done"]=True; state["model_acc"]=50.0; add_score(500)
        sfx.play("level_complete", cooldown_ms=0)   # 🔊
        show_confusion_matrix()          # 📊 Show confusion matrix first
        aira_speak("Zabardast! Dataset ready hai. Confusion matrix dekho – diagonal cells sahi classify hain! Green = TP (True Positive).")
        show_modal("L1 COMPLETE – DATA COLLECTED!",
            [f"Tumne {l1['clean']+l1['corrupt']+l1['biased']} data items classify kiye!","Strong dataset ready hai."],
            ["Data Cleaning kya hota hai","Data Bias kya hota hai","Garbage In = Garbage Out"],2)

def handle_train_click():
    l2=state["l2"]
    if l2.get("trained") or l2.get("training"): return
    acc=compute_accuracy(l2["epochs"],l2["lr_raw"])
    if acc<65 or acc>85:
        notif.show("Accuracy sahi zone mein nahi! Adjust karo.",YELLOW)
        state["train_attempts"]+=1
        sfx.play("wrong_drop")   # 🔊
        if acc<65:
            state["mistakes"].append({"level":2,"type":"underfitting","detail":f"Epochs={l2['epochs']} – model underfit tha (acc={round(acc)}%)"})
            aira_speak("Model underfit ho raha hai! Epochs badhao ya learning rate adjust karo.")
        else:
            state["mistakes"].append({"level":2,"type":"overfitting","detail":f"Epochs={l2['epochs']} – model overfit tha (acc={round(acc)}%)"})
            aira_speak("Overfitting! Epochs kam karo!")
        return
    l2["training"]=True; l2["train_timer"]=0; l2["train_total"]=3.0; l2["graph_pts"]=[]
    notif.show("Training shuru! Ruko...",ACCENT)
    sfx.play("train_start", cooldown_ms=0)   # 🔊
    aira_speak("Training shuru! Loss graph dekho – train loss gir rahi hai. Val loss agar upar jaaye toh overfitting!")

def handle_deploy(key):
    if state["l3"].get("done"): return
    acc=state["model_acc"]
    opt=next(o for o in DEPLOY_OPTIONS if o["key"]==key)
    state["l3"]["choice"]=key; state["deploy_attempts"]+=1
    if acc<60:
        result={"success":False,"icon":"💥","title":"CRASH! Model too weak!","detail":f"Accuracy {round(acc)}% bahut low hai. Pehle better model train karo!"}
        state["mistakes"].append({"level":3,"type":"weak_model_deploy","detail":f"Accuracy {round(acc)}% ke saath deploy try kiya!"})
        sfx.play("deploy_fail", cooldown_ms=0)   # 🔊
        aira_speak("Deployment fail! Model accuracy bahut low hai.")
    elif key=="local":
        result={"success":True,"icon":"✅","title":"Local Deployment Success!","detail":"Local machine pe deploy hua! +100 pts"}
        add_score(100); sfx.play("deploy_success", cooldown_ms=0)   # 🔊
        aira_speak("Local deployment success! Ye Development environment hai.")
    elif key=="cloud":
        if acc>=70:
            result={"success":True,"icon":"☁️","title":"Cloud Deployment Success!","detail":f"10K+ users serve ho rahe hain! +300 pts"}
            add_score(300); sfx.play("deploy_success", cooldown_ms=0)   # 🔊
            aira_speak("Cloud deployment success! Auto-scaling, load balancing – sab automatically handle hota hai!")
        else:
            result={"success":False,"icon":"💥","title":"Cloud Crash!","detail":f"Accuracy {round(acc)}% cloud ke liye kam hai. Min 70% chahiye!"}
            state["mistakes"].append({"level":3,"type":"cloud_crash","detail":f"Cloud deploy fail – acc {round(acc)}%"})
            sfx.play("deploy_fail", cooldown_ms=0)   # 🔊
            aira_speak("Cloud crash! Production mein 70%+ accuracy chahiye.")
    else:
        if acc>=80:
            result={"success":True,"icon":"📱","title":"Mobile App Live!","detail":f"1M+ users pe deploy! +500 pts"}
            add_score(500); sfx.play("deploy_success", cooldown_ms=0)   # 🔊
            aira_speak("Mobile deployment! Edge computing mein model optimize karna padta hai!")
        else:
            result={"success":False,"icon":"💥","title":"App Store Rejected!","detail":f"Mobile ke liye 80%+ accuracy chahiye. Current: {round(acc)}%"}
            state["mistakes"].append({"level":3,"type":"mobile_reject","detail":f"Mobile deploy fail – acc {round(acc)}%"})
            sfx.play("deploy_fail", cooldown_ms=0)   # 🔊
            aira_speak("Mobile reject! Edge deployment mein bahut high accuracy chahiye.")
    state["l3"]["result"]=result
    notif.show(result["title"],GREEN if result["success"] else RED)

def complete_deploy():
    state["l3"]["done"]=True; add_score(500)
    sfx.play("level_complete", cooldown_ms=0)   # 🔊
    start_quiz(3)    # 🧠 Quiz after L3
    show_modal("L3 COMPLETE – DEPLOYED!",
        ["Tumne apna AI model production mein deploy kar diya!","Real users ab model use kar rahe hain."],
        ["Production vs Development","Cloud Deployment kya hota hai","CI/CD basics"],4)

def handle_l4_action(key):
    l4=state["l4"]
    if l4["actions"][key]:
        notif.show("Ye action already ho chuka hai!",YELLOW); return
    l4["actions"][key]=True
    sfx.play("action_click")   # 🔊
    if key=="collect":
        l4["drift_acc"]=min(l4["drift_acc"]+10,95); add_score(100)
        add_score_effect(W//2,400,"+100",GREEN)
        notif.show("New data collected! +100 pts",GREEN)
        aira_speak("Naya data collect karna bahut zaroori hai! Is process ko Continuous Training kehte hain!")
    elif key=="retrain":
        l4["drift_acc"]=min(l4["drift_acc"]+20,95); add_score(150)
        add_score_effect(W//2,400,"+150",GREEN)
        notif.show("Model retrained! +150 pts",ACCENT)
        aira_speak("Retraining success! Deploy → Monitor → Detect Drift → Retrain → Re-deploy = MLOps Loop!")
    elif key=="rollback":
        l4["drift_acc"]=min(l4["drift_acc"]+5,95); add_score(50)
        add_score_effect(W//2,400,"+50",YELLOW)
        notif.show("Rollback done! +50 pts",YELLOW)
        aira_speak("Rollback smart move hai! Isi liye model versioning hamesha karo!")
    done_count=sum(1 for v in l4["actions"].values() if v)
    if done_count>=3 and not l4["done"]:
        l4["done"]=True; add_score(500)
        sfx.play("game_complete", cooldown_ms=0)   # 🔊
        start_quiz(4)    # 🧠 Quiz after L4
        aira_speak("CONGRATULATIONS! Tum ek real MLOps Engineer ban gaye! Quiz bhi do – bonus XP milega!")
        show_modal("L4 COMPLETE – MLOps MASTER!",
            ["Tumne poora MLOps lifecycle complete kar liya!","Data → Train → Deploy → Monitor → Retrain"],
            ["Data Drift kya hota hai","Monitoring Systems","Continuous Training / MLOps Loop"],5)

# ─────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────
def main():
    global dragging_item,drag_offset,l1_spawn_timer
    global slider_dragging,mentor_input_text,mentor_focused,mentor_scroll

    aira_speak("Namaste! Main hoon AIRA – tumhari AI Mentor. 🔊 M=Mute, +/-=Volume. Koi bhi sawaal pucho!")

    running=True
    while running:
        dt=clock.tick(60)/1000.0
        mx,my=pygame.mouse.get_pos()
        screen_name=state["screen"]

        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.VIDEORESIZE:
                global W,H; W,H=event.w,event.h

            elif event.type==pygame.KEYDOWN:
                # 🔊 Global sound controls
                if event.key==pygame.K_m:
                    muted=sfx.toggle_mute()
                    notif.show("🔇 Muted" if muted else "🔊 Unmuted", DIM if muted else ACCENT)
                elif event.key==pygame.K_EQUALS or event.key==pygame.K_PLUS:
                    sfx.change_volume(0.1)
                    notif.show(f"🔊 Volume: {int(sfx.volume*100)}%", ACCENT)
                elif event.key==pygame.K_MINUS:
                    sfx.change_volume(-0.1)
                    notif.show(f"🔊 Volume: {int(sfx.volume*100)}%", DIM)
                # Mentor input
                elif mentor_focused:
                    if event.key==pygame.K_RETURN:
                        send_mentor_question(mentor_input_text); mentor_input_text=""
                    elif event.key==pygame.K_BACKSPACE: mentor_input_text=mentor_input_text[:-1]
                    elif event.key==pygame.K_ESCAPE: mentor_focused=False
                    else:
                        if len(mentor_input_text)<80: mentor_input_text+=event.unicode

            elif event.type==pygame.MOUSEBUTTONDOWN:
                btn=event.button
                # Academy: only handle scroll wheel here; clicks go to MOUSEBUTTONUP
                if screen_name=="academy":
                    if btn in (4, 5):
                        handle_academy_click(mx, my, btn)
                    continue
                ib_y=H-50
                if (W-SIDEBAR_W+4<=mx<=W-48) and (ib_y<=my<=ib_y+36): mentor_focused=True
                elif mx>W-SIDEBAR_W: mentor_focused=True
                else: mentor_focused=False

                if modal["active"]:
                    result=draw_modal(screen)
                    if isinstance(result,pygame.Rect) and result.collidepoint(mx,my):
                        sfx.play("action_click")   # 🔊
                        modal["active"]=False; nl=modal["next_level"]
                        if nl<=4: state["unlocked"][nl]=True
                        if nl==5: state["screen"]="complete"; sfx.play("game_complete",cooldown_ms=0)
                        else:
                            state["screen"]=f"level{nl}"
                            if nl==2: init_level2()
                            if nl==4: init_level4()
                    continue

                for rect,label,key in get_tab_rects():
                    if rect.collidepoint(mx,my):
                        if key=="welcome": state["screen"]="welcome"
                        elif key=="academy":
                            sfx.play("action_click")
                            if state["l4"].get("done") or academy_state.get("active"):
                                academy_state["active"]=True
                                state["screen"]="academy"
                                # Pre-draw once so card rects are populated before first click
                                draw_hologram_bg(screen, time.time())
                                draw_header(screen); draw_tabs(screen)
                                draw_academy(screen)
                                pygame.display.flip()
                            else: notif.show("Pehle game complete karo! 🎓",PURPLE)
                        elif key.startswith("level"):
                            lvl=int(key[-1])
                            if state["unlocked"].get(lvl):
                                sfx.play("action_click")   # 🔊
                                state["screen"]=key
                                if lvl==2: init_level2()
                                if lvl==4: init_level4()
                                maybe_start_tutorial(key)   # 📚
                            else: notif.show("Pehle previous level complete karo!",RED)

                if screen_name=="level1":
                    for item in stream_items:
                        if item["rect"].collidepoint(mx,my):
                            dragging_item=item; stream_items.remove(item)
                            drag_offset=(mx-item["rect"].x,my-item["rect"].y); break
                elif screen_name=="level2":
                    if epoch_slider_rect and epoch_slider_rect.collidepoint(mx,my): slider_dragging="epochs"
                    elif lr_slider_rect and lr_slider_rect.collidepoint(mx,my): slider_dragging="lr"
                    elif train_btn_rect and train_btn_rect.collidepoint(mx,my): handle_train_click()
                elif screen_name=="level3":
                    for key,rect in deploy_btn_rects.items():
                        if rect.collidepoint(mx,my): handle_deploy(key)
                    if continue_btn_rect and continue_btn_rect.collidepoint(mx,my):
                        if state["l3"]["result"] and state["l3"]["result"]["success"]: complete_deploy()
                elif screen_name=="level4":
                    for key,rect in action_btn_rects.items():
                        if rect.collidepoint(mx,my): handle_l4_action(key)

                send_x=W-40; send_y=H-50
                if send_x<=mx<=W-4 and send_y<=my<=send_y+36:
                    send_mentor_question(mentor_input_text); mentor_input_text=""
                if mx>W-SIDEBAR_W:
                    if btn==4: mentor_scroll=max(0,mentor_scroll-30)
                    if btn==5: mentor_scroll+=30

            elif event.type==pygame.MOUSEBUTTONUP:
                slider_dragging=None
                if screen_name=="academy" and event.button==1:
                    handle_academy_click(mx, my, 1)
                    continue

                # Confusion matrix close
                if conf_matrix_state["active"] and conf_matrix_state.get("close_btn"):
                    if conf_matrix_state["close_btn"].collidepoint(mx,my):
                        conf_matrix_state["active"]=False; sfx.play("action_click")

                # Quiz clicks
                if quiz_state["active"]:
                    if quiz_state["done"] and quiz_state.get("next_btn") and quiz_state["next_btn"].collidepoint(mx,my):
                        quiz_state["active"]=False; sfx.play("action_click")
                    elif not quiz_state["done"]:
                        if quiz_state.get("next_btn") and quiz_state["next_btn"].collidepoint(mx,my):
                            quiz_next()
                        else:
                            for i,br in enumerate(quiz_state.get("btn_rects",[])):
                                if br.collidepoint(mx,my): quiz_select(i); break

                # Tutorial next
                if tutorial_state["active"] and tutorial_state.get("btn_rect"):
                    if tutorial_state["btn_rect"].collidepoint(mx,my): advance_tutorial()

                # Random event choices
                if random_event_state["active"] and not random_event_state["choice_made"]:
                    if _event_btn_a and _event_btn_a.collidepoint(mx,my): handle_event_choice("a")
                    elif _event_btn_b and _event_btn_b.collidepoint(mx,my): handle_event_choice("b")

                hdr_exit=state.get("_hdr_exit")
                if hdr_exit and hdr_exit.collidepoint(mx,my):
                    sfx.stop_all(); pygame.quit(); sys.exit()
                if screen_name=="complete":
                    eb=state.get("_exit_btn")
                    ab=state.get("_acad_btn")
                    if eb and eb.collidepoint(mx,my):
                        sfx.stop_all(); pygame.quit(); sys.exit()
                    if ab and ab.collidepoint(mx,my):
                        sfx.play("action_click")
                        academy_state["active"]=True
                        state["screen"]="academy"
                        draw_hologram_bg(screen, time.time())
                        draw_header(screen); draw_tabs(screen)
                        draw_academy(screen); pygame.display.flip()
                        aira_speak("Welcome to Advanced MLOps Academy! 9 topics hain — Docker se LLMOps tak. Kisi bhi card pe click karo!")
                if screen_name=="welcome" and not modal["active"]:
                    cx=(W-SIDEBAR_W)//2
                    if pygame.Rect(cx-110,430,220,50).collidepoint(mx,my):
                        sfx.play("action_click")   # 🔊
                        state["screen"]="level1"; state["unlocked"][1]=True; init_level1()
                        maybe_start_tutorial("level1")   # 📚
                        aira_speak("Level 1 shuru! Data items aa rahe hain. Sahi bucket mein drag karo!")
                if dragging_item and screen_name=="level1":
                    buckets=get_bucket_rects(); dropped=False
                    for btype,brect in buckets.items():
                        if dragging_item["rect"].colliderect(brect):
                            handle_l1_drop(dragging_item["type"],btype,mx,my); dropped=True; break
                    if not dropped: stream_items.append(dragging_item)
                    dragging_item=None

            elif event.type==pygame.MOUSEMOTION:
                if dragging_item:
                    dragging_item["rect"].x=mx-drag_offset[0]; dragging_item["rect"].y=my-drag_offset[1]
                if slider_dragging=="epochs" and epoch_slider_rect:
                    pct=max(0,min(1,(mx-epoch_slider_rect.x)/epoch_slider_rect.width))
                    state["l2"]["epochs"]=max(1,int(1+pct*199))
                elif slider_dragging=="lr" and lr_slider_rect:
                    pct=max(0,min(1,(mx-lr_slider_rect.x)/lr_slider_rect.width))
                    state["l2"]["lr_raw"]=max(1,int(1+pct*99))

        # ── UPDATE ──
        notif.update(dt); update_score_effects(dt)
        update_event(dt)    # 🎲 Random events
        if mentor_typing is False:
            for msg in mentor_messages:
                if msg.get("loading"): msg.pop("loading")

        # Fire random events on active levels
        if screen_name.startswith("level") and not modal["active"] and not quiz_state["active"] and not random_event_state["active"]:
            maybe_fire_event(screen_name, dt)

        if screen_name=="level1" and not state["l1"]["done"]:
            l1_spawn_timer+=dt
            if l1_spawn_timer>=SPAWN_INTERVAL: l1_spawn_timer=0; l1_spawn()
            for item in stream_items[:]:
                item["life"]-=dt
                if item["life"]<=0: stream_items.remove(item)

        if screen_name=="level2" and state["l2"].get("training"):
            state["l2"]["train_timer"]+=dt
            total=state["l2"]["train_total"]; progress=min(1.0,state["l2"]["train_timer"]/total)
            t=progress; loss=0.9*math.exp(-3*t)+0.08
            if state["l2"]["epochs"]>150: loss+=max(0,(t-0.7))*0.4
            state["l2"]["graph_pts"].append(min(0.95,loss))
            if progress>=1.0:
                state["l2"]["training"]=False; state["l2"]["trained"]=True
                acc=compute_accuracy(state["l2"]["epochs"],state["l2"]["lr_raw"])
                state["l2"]["acc"]=acc; state["model_acc"]=acc; add_score(200)
                add_score_effect(W//3,300,"+200 pts",GREEN)
                sfx.play("train_complete", cooldown_ms=0)   # 🔊
                aira_speak(f"Model trained! Accuracy: {round(acc)}%. Ab deployment ke liye ready ho!")
                start_quiz(2)    # 🧠 Quiz after L2
                show_modal("L2 COMPLETE – MODEL TRAINED!",
                    [f"Tumhara model {round(acc)}% accuracy ke saath train hua!","Overfitting aur Underfitting samajh aaya!"],
                    ["Training vs Testing","Overfitting kya hota hai","Learning Rate ka effect"],3)

        if screen_name=="level4" and not state["l4"]["done"]:
            actions_done=sum(1 for v in state["l4"]["actions"].values() if v)
            if actions_done<3: state["l4"]["drift_acc"]=max(30,state["l4"]["drift_acc"]-dt*1.5)
            state["l4"]["pts"].append(state["l4"]["drift_acc"])
            if len(state["l4"]["pts"])>200: state["l4"]["pts"].pop(0)
            state["l4"]["complaint_timer"]+=dt
            if state["l4"]["complaint_timer"]>=3.0 and actions_done<3:
                state["l4"]["complaint_timer"]=0; complaints_log.append(random.choice(COMPLAINTS))
            # 🔊 Play drift alert every 15 seconds when not all actions done
            if not state.get("_drift_alerted") and actions_done<3:
                if len(state["l4"]["pts"])%300==150:
                    sfx.play("drift_alert", cooldown_ms=14000)

        # ── DRAW ──
        t_now=time.time()
        draw_hologram_bg(screen,t_now)
        hdr_exit_rect=draw_header(screen); state["_hdr_exit"]=hdr_exit_rect
        draw_tabs(screen)

        if screen_name=="welcome": draw_welcome(screen)
        elif screen_name=="level1": draw_level1(screen)
        elif screen_name=="level2": draw_level2(screen)
        elif screen_name=="level3": draw_level3(screen)
        elif screen_name=="level4": draw_level4(screen)
        elif screen_name=="academy":
            draw_hologram_bg(screen, t_now)
            draw_header(screen)
            draw_tabs(screen)
            draw_academy(screen)      # ← populates _acad_card_rects, _acad_back_btn etc
            draw_mentor(screen)
            draw_score_effects(screen)
            notif.draw(screen)
            pygame.display.flip()
            continue
        elif screen_name=="complete":
            btns=draw_complete_screen(screen)
            if btns:
                state["_exit_btn"]=btns["exit"]
                state["_acad_btn"]=btns["academy"]

        draw_sound_hud(screen)   # 🔊 volume indicator
        draw_mentor(screen)
        draw_modal(screen)

        # ── NEW OVERLAYS (drawn on top, in priority order) ──
        draw_confusion_matrix(screen)   # 📊 shown right after L1
        draw_quiz(screen)               # 🧠 shown after level complete
        draw_random_event(screen)       # 🎲 random events
        draw_tutorial(screen)           # 📚 tutorial tooltips (topmost)

        notif.draw(screen)
        draw_score_effects(screen)
        pygame.display.flip()

    sfx.stop_all()
    pygame.quit(); sys.exit()

if __name__=="__main__":
    main()