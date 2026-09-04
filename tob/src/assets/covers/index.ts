import c1 from './cover1.svg';
import c2 from './cover2.svg';
import c3 from './cover3.svg';
import c4 from './cover4.svg';
import c5 from './cover5.svg';

export const COVER_PRESETS = ['preset:1', 'preset:2', 'preset:3', 'preset:4', 'preset:5'];

const MAP = [c1, c2, c3, c4, c5];

export function presetSrc(cover?: string | null): string {
  const n = parseInt((cover || '').split(':')[1] || '1', 10);
  return MAP[Math.min(Math.max(n, 1), 5) - 1];
}

export function isPreset(cover?: string | null): boolean {
  return !!cover && cover.startsWith('preset:');
}

// trigger hmr
