import React from 'react';
import { Percent, Activity, Zap, TrendingDown } from 'lucide-react';
import { MacroScenario } from '../types/fire';
import { Language, TRANSLATIONS } from '../i18n/translations';

interface MacroScenarioSelectorProps {
  scenario: MacroScenario;
  onChange: (sc: MacroScenario) => void;
  lang: Language;
}

export const MacroScenarioSelector: React.FC<MacroScenarioSelectorProps> = ({
  scenario,
  onChange,
  lang,
}) => {
  const t = TRANATIONS_HELPER(lang);
  const trans = TRANSLATIONS[lang];

  const realReturnRate =
    ((1 + scenario.nominalReturn / 100) / (1 + scenario.inflationRate / 100) - 1) * 100;

  const presetScenarios: MacroScenario[] = [
    {
      id: 'base',
      name: trans.scenarioBaseName,
      description: trans.scenarioBaseDesc,
      nominalReturn: 7.0,
      inflationRate: 2.5,
    },
    {
      id: 'optimistic',
      name: trans.scenarioOptimisticName,
      description: trans.scenarioOptimisticDesc,
      nominalReturn: 9.0,
      inflationRate: 2.0,
    },
    {
      id: 'conservative',
      name: trans.scenarioConservativeName,
      description: trans.scenarioConservativeDesc,
      nominalReturn: 5.0,
      inflationRate: 3.5,
    },
    {
      id: 'stress_test',
      name: trans.scenarioStressName,
      description: trans.scenarioStressDesc,
      nominalReturn: 7.0,
      inflationRate: 2.5,
      stressDropFirstYears: 15,
    },
  ];

  const handleSelectPreset = (p: MacroScenario) => {
    onChange(p);
  };

  const handleCustomNominal = (val: number) => {
    onChange({
      ...scenario,
      id: 'custom',
      name: trans.scenarioCustomName,
      nominalReturn: val,
    });
  };

  const handleCustomInflation = (val: number) => {
    onChange({
      ...scenario,
      id: 'custom',
      name: trans.scenarioCustomName,
      inflationRate: val,
    });
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-sm space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              {trans.macroTitle}
            </h3>
            <p className="text-xs text-slate-400">
              {trans.macroSubtitle}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
          <span className="text-[11px] text-slate-400">{trans.realReturnLabel}</span>
          <span
            className={`text-sm font-black font-mono ${
              realReturnRate >= 5 ? 'text-emerald-400' : realReturnRate >= 2 ? 'text-cyan-400' : 'text-amber-400'
            }`}
          >
            {realReturnRate >= 0 ? `+${realReturnRate.toFixed(2)}%` : `${realReturnRate.toFixed(2)}%`}
          </span>
        </div>
      </div>

      {/* Preset Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        {presetScenarios.map((p) => {
          const isSelected = scenario.id === p.id;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => handleSelectPreset(p)}
              className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                isSelected
                  ? 'bg-purple-500/15 border-purple-500/50 shadow-md shadow-purple-500/10'
                  : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`text-xs font-bold ${isSelected ? 'text-purple-300' : 'text-slate-200'}`}>
                  {p.name}
                </span>
                {p.stressDropFirstYears && (
                  <span className="text-[10px] text-rose-400 bg-rose-500/10 px-1 rounded flex items-center gap-0.5">
                    <TrendingDown className="w-2.5 h-2.5" /> -15%
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2 text-[11px] font-mono text-slate-300 mb-1">
                <span>{trans.returnNominalShort} <strong>{p.nominalReturn}%</strong></span>
                <span className="text-slate-600">|</span>
                <span>{trans.inflationShort} <strong>{p.inflationRate}%</strong></span>
              </div>
              <p className="text-[10px] text-slate-400 leading-tight">
                {p.description}
              </p>
            </button>
          );
        })}
      </div>

      {/* Sliders for fine-tuning */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-300 font-semibold flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-purple-400" /> {trans.nominalReturnLabel}
            </span>
            <span className="font-mono font-bold text-purple-400">{scenario.nominalReturn.toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min={2.0}
            max={14.0}
            step={0.25}
            value={scenario.nominalReturn}
            onChange={(e) => handleCustomNominal(Number(e.target.value))}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>2%</span>
            <span>7% (MSCI World)</span>
            <span>14%</span>
          </div>
        </div>

        <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-300 font-semibold flex items-center gap-1.5">
              <Percent className="w-3.5 h-3.5 text-amber-400" /> {trans.inflationLabel}
            </span>
            <span className="font-mono font-bold text-amber-400">{scenario.inflationRate.toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min={0.5}
            max={8.0}
            step={0.25}
            value={scenario.inflationRate}
            onChange={(e) => handleCustomInflation(Number(e.target.value))}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>0.5%</span>
            <span>2.5% (ECB target)</span>
            <span>8%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

function TRANATIONS_HELPER(lang: Language) {
  return TRANSLATIONS[lang];
}
