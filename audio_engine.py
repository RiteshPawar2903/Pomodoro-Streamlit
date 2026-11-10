"""
Audio Engine module delivering browser-based synthesized sound and ambient soundscapes
using HTML5 Web Audio API synthesizers.
Built according to IEEE Std 730/1016 standards.
"""

from __future__ import annotations

import streamlit.components.v1 as components
from models import AmbientSound, ChimeSound


def play_sound_script(sound_type: ChimeSound, volume: float = 0.6) -> str:
    """Return an HTML snippet running client-side Web Audio synthesis for bell/chime."""
    stype = sound_type.value if hasattr(sound_type, "value") else str(sound_type)
    return f"""
    <div style="display:none;" id="zen-audio-trigger">
    <script>
    (function() {{
        try {{
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (!AudioCtx) return;
            const ctx = new AudioCtx();
            const chime = "{stype}";
            const vol = {volume};

            if (chime !== 'none' && vol > 0) {{
                const now = ctx.currentTime;
                if (chime === 'singing-bowl' || chime === 'zen-gong') {{
                    const baseFreq = chime === 'zen-gong' ? 130.81 : 261.63;
                    const freqs = [baseFreq, baseFreq * 2, baseFreq * 3.01];
                    freqs.forEach((f, idx) => {{
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(f, now);
                        gain.gain.setValueAtTime(0, now);
                        gain.gain.linearRampToValueAtTime((vol * 0.45) / (idx + 1), now + 0.08);
                        gain.gain.exponentialRampToValueAtTime(0.0001, now + (chime === 'zen-gong' ? 4.0 : 3.5));
                        osc.connect(gain);
                        gain.connect(ctx.destination);
                        osc.start(now);
                        osc.stop(now + 4.0);
                    }});
                }} else if (chime === 'soft-bell' || chime === 'crystal-chime') {{
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = chime === 'crystal-chime' ? 'sine' : 'triangle';
                    osc.frequency.setValueAtTime(chime === 'crystal-chime' ? 1760 : 880, now);
                    osc.frequency.exponentialRampToValueAtTime(chime === 'crystal-chime' ? 880 : 440, now + 1.2);
                    gain.gain.setValueAtTime(vol * 0.5, now);
                    gain.gain.exponentialRampToValueAtTime(0.001, now + 1.8);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(now);
                    osc.stop(now + 1.8);
                }} else if (chime === 'wooden-clack') {{
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'square';
                    osc.frequency.setValueAtTime(320, now);
                    gain.gain.setValueAtTime(vol * 0.6, now);
                    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.12);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(now);
                    osc.stop(now + 0.15);
                }} else if (chime === 'gentle-marimba') {{
                    [523.25, 659.25, 783.99].forEach((f, i) => {{
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(f, now + (i * 0.1));
                        gain.gain.setValueAtTime(0, now + (i * 0.1));
                        gain.gain.linearRampToValueAtTime(vol * 0.45, now + (i * 0.1) + 0.02);
                        gain.gain.exponentialRampToValueAtTime(0.001, now + (i * 0.1) + 0.9);
                        osc.connect(gain);
                        gain.connect(ctx.destination);
                        osc.start(now + (i * 0.1));
                        osc.stop(now + (i * 0.1) + 0.95);
                    }});
                }}
            }}
        }} catch(e) {{
            console.warn("Audio trigger note:", e);
        }}
    }})();
    </script>
    </div>
    """


def render_ambient_player(ambient_sound: AmbientSound, volume: float, is_running: bool) -> None:
    """Render browser ambient sound generator via Web Audio API."""
    if ambient_sound == AmbientSound.NONE or not is_running:
        return

    sound_mode = ambient_sound.value if hasattr(ambient_sound, "value") else ambient_sound
    js_code = f"""
    <div style="padding: 6px 14px; border-radius: 12px; background: rgba(0,0,0,0.04); font-size: 12px; display: inline-flex; align-items: center; gap: 8px;">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10b981; animation: pulse 2s infinite;"></span>
        <span>Soundscape: <b>{sound_mode.replace('-', ' ').title()}</b></span>
        <script>
        (function() {{
            try {{
                const AudioCtx = window.AudioContext || window.webkitAudioContext;
                if (!AudioCtx) return;
                window.zenAmbientCtx = window.zenAmbientCtx || new AudioCtx();
                const ctx = window.zenAmbientCtx;
                if (ctx.state === 'suspended') ctx.resume();

                if (window.zenAmbientNode) {{
                    window.zenAmbientNode.disconnect();
                }}

                const bufferSize = ctx.sampleRate * 2;
                const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
                const data = buffer.getChannelData(0);
                let lastOut = 0.0;

                for (let i = 0; i < bufferSize; i++) {{
                    const white = Math.random() * 2 - 1;
                    if ('{sound_mode}' === 'brown-noise') {{
                        lastOut = (lastOut + (0.02 * white)) / 1.02;
                        data[i] = lastOut * 3.5;
                    }} else if ('{sound_mode}' === 'gentle-rain') {{
                        lastOut = (lastOut + (0.08 * white)) / 1.08;
                        const drop = Math.random() < 0.001 ? (Math.random() * 1.5) : 0;
                        data[i] = (lastOut * 2.2) + drop;
                    }} else if ('{sound_mode}' === 'crackling-fireplace') {{
                        lastOut = (lastOut + (0.015 * white)) / 1.015;
                        const pop = Math.random() < 0.003 ? (Math.random() * 2.5 - 1.25) : 0;
                        data[i] = (lastOut * 3.0) + pop;
                    }} else {{
                        lastOut = (lastOut + (0.03 * white)) / 1.03;
                        data[i] = lastOut * 2.8;
                    }}
                }}

                const noise = ctx.createBufferSource();
                noise.buffer = buffer;
                noise.loop = true;

                const filter = ctx.createBiquadFilter();
                filter.type = 'lowpass';
                filter.frequency.value = '{sound_mode}' === 'brown-noise' ? 380 : 700;

                const gain = ctx.createGain();
                gain.gain.setValueAtTime({volume} * 0.16, ctx.currentTime);

                noise.connect(filter);
                filter.connect(gain);
                gain.connect(ctx.destination);
                noise.start();
                window.zenAmbientNode = noise;
            }} catch(e) {{
                console.warn("Ambient generator note:", e);
            }}
        }})();
        </script>
    </div>
    """
    components.html(js_code, height=45)
