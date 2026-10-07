import React from 'react';
import { ShieldCheck } from 'lucide-react';
import { Language, TRANSLATIONS } from '../i18n/translations';

interface SafeWithdrawalRateControlProps {
  safeWithdrawalRate: number;
  onChange: (val: number) => void;
  lang: Language;
}

export const SafeWithdrawalRateControl: React.FC<SafeWithdrawalRateControlProps> = ({
  safeWithdrawalRate,
  onChange,
  lang,
}) => {
  const t = TRANSLATIONS[lang];
  const currentMultiplier = (100 / safeWithdrawalRate).toFixed(1);

  const presets = [
    {
      rate: 3.0,
      label: '3.0%',
      badge: t.swrUltraSafe,
      desc: t.swrUltraSafeDesc,
      multiplier: `33.3x ${t.swrAnnualExpenses}`,
    },
    {
      rate: 3.5,
      label: '3.5%',
      badge: t.swrEuropeanFire,
      desc: t.swrEuropeanFireDesc,
      multiplier: `28.6x ${t.swrAnnualExpenses}`,
    },
    {
      rate: 4.0,
      label: '4.0%',
      badge: t.swrTrinityRule,
      desc: t.swrTrinityRuleDesc,
      multiplier: `25x ${t.swrAnnualExpenses}`,
    },
    {
      rate: 4.5,
      label: '4.5%',
      badge: t.swrLeanDynamic,
      desc: t.swrLeanDynamicDesc,
      multiplier: `22.2x ${t.swrAnnualExpenses}`,
    },
  ];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              {t.swrTitle}
              <span className="text-xs font-normal text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-full">
                Safe Withdrawal Rate
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              {t.swrSubtitle}
            </p>
          </div>
        </div>

        <div className="text-right">
          <span className="text-2xl font-black text-amber-400 tracking-tight">
            {safeWithdrawalRate.toFixed(1)}%
          </span>
          <span className="block text-[11px] text-slate-400 font-mono">
            {currentMultiplier}x {t.swrAnnualExpenses}
          </span>
        </div>
      </div>

      {/* Slider */}
      <div className="pt-4 space-y-3">
        <input
          type="range"
          min={2.5}
          max={5.5}
          step={0.1}
          value={safeWithdrawalRate}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
        />

        {/* Quick Presets */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
          {presets.map((p) => {
            const isSelected = Math.abs(safeWithdrawalRate - p.rate) < 0.05;
            return (
              <button
                key={p.rate}
                type="button"
                onClick={() => onChange(p.rate)}
                className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-amber-500/15 border-amber-500/50 shadow-md shadow-amber-500/10'
                    : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`text-sm font-black ${isSelected ? 'text-amber-400' : 'text-slate-200'}`}>
                    {p.label}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-medium">
                    {p.badge}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 leading-snug line-clamp-2">
                  {p.desc}
                </p>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
