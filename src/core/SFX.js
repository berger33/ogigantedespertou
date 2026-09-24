/**
 * SFX — sons originais via Web Audio (núcleo jogável).
 * Identidade sonora base (spec §120): notificação (clique), carimbo (upgrade),
 * cash (compra), mensagem (Zap), gigante (prestige). Sem assets externos.
 * Na produção Unity, as mesmas "pistas" viram samples originais (não este código).
 */
let ctx = null;
let muted = false;

function ac() {
  if (!ctx) {
    const AC = globalThis.AudioContext || globalThis.webkitAudioContext;
    if (!AC) return null;
    ctx = new AC();
  }
  if (ctx.state === 'suspended') ctx.resume();
  return ctx;
}

/** oscilador + envelope simples */
function tone(freq, { type = 'sine', dur = 0.1, vol = 0.06, slide = 0, delay = 0 } = {}) {
  if (muted) return;
  const c = ac();
  if (!c) return;
  const t0 = c.currentTime + delay;
  const osc = c.createOscillator();
  const gain = c.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, t0);
  if (slide) osc.frequency.exponentialRampToValueAtTime(freq + slide, t0 + dur);
  gain.gain.setValueAtTime(0, t0);
  gain.gain.linearRampToValueAtTime(vol, t0 + 0.005);
  gain.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  osc.connect(gain).connect(c.destination);
  osc.start(t0);
  osc.stop(t0 + dur + 0.02);
}

export const SFX = {
  setMuted(m) { muted = m; },
  toggleMuted() { muted = !muted; return muted; },
  get muted() { return muted; },
  // toque no Compartilhar no Zap: "notificação fictícia" (ping duplo)
  click() {
    tone(880, { type: 'triangle', dur: 0.07, vol: 0.05 });
    tone(1320, { type: 'triangle', dur: 0.06, vol: 0.04, delay: 0.05 });
  },
  // compra de produtor: cash (moedas)
  buy() {
    tone(520, { type: 'square', dur: 0.06, vol: 0.03 });
    tone(780, { type: 'square', dur: 0.08, vol: 0.03, delay: 0.04 });
  },
  // upgrade: carimbo
  stamp() {
    tone(180, { type: 'sawtooth', dur: 0.12, vol: 0.07, slide: -60 });
  },
  // zap vazado: mensagem
  message() {
    tone(660, { type: 'sine', dur: 0.08, vol: 0.05 });
    tone(990, { type: 'sine', dur: 0.08, vol: 0.04, delay: 0.09 });
  },
  // prestige: o gigante acorda (subida grave)
  giant() {
    tone(70, { type: 'sine', dur: 0.9, vol: 0.12, slide: 180 });
    tone(140, { type: 'triangle', dur: 0.9, vol: 0.05, slide: 360, delay: 0.05 });
  },
};

export default SFX;
