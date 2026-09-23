/**
 * VFX — partículas/floaters leves do núcleo (spec §118, §188 object pooling).
 * iOS de número flutuante + celularzinho voando no clique. Sem libs.
 */
export function spawnFloater(container, text, { x, y, cls = '' } = {}) {
  const el = document.createElement('div');
  el.className = 'floater ' + cls;
  el.textContent = text;
  el.style.left = `${x}px`;
  el.style.top = `${y}px`;
  container.appendChild(el);
  el.addEventListener('animationend', () => el.remove());
}

export function spawnPhone(container, { x, y } = {}) {
  const el = document.createElement('div');
  el.className = 'phone';
  el.textContent = '📱';
  el.style.left = `${x}px`;
  el.style.top = `${y}px`;
  container.appendChild(el);
  el.addEventListener('animationend', () => el.remove());
}

export default { spawnFloater, spawnPhone };
