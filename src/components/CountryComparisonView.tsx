import React from 'react';
import {
  FireInputs,
  CountryCode,
  TaxSettings,
} from '../types/fire';
import { simulateFire } from '../utils/fireSimulation';
import { Scale, Check, ArrowRight } from 'lucide-react';
import { Language, TRANSLATIONS } from '../i18n/translations';

interface CountryComparisonViewProps {
  currentInputs: FireInputs;
  onApplyCountry: (c: CountryCode) => void;
  lang: Language;
}

export const CountryComparisonView: React.FC<CountryComparisonViewProps> = ({
  currentInputs,
  onApplyCountry,
  lang,
}) => {
  const t = TRANSLATIONS[lang];
  const isEn = lang === 'en';
  const locale = isEn ? 'en-US' : 'ca-ES';

  const countries: { code: CountryCode; name: string; flag: string; specificNote: string }[] = [
    {
      code: 'CAT',
      name: isEn ? 'Catalonia' : 'Catalunya',
      flag: '🏴󠁥󠁳󠁣󠁴󠁿',
      specificNote: isEn
        ? 'Savings Tax 19-28% on gains + Catalonia Wealth Tax (€500k exemption). Complete tax-deferred fund roll-over.'
        : 'IRPF Estalvi 19-28% sobre guanys + Impost sobre el Patrimoni català (mínim exempt 500k €). Traspàs de fons exempt.',
    },
    {
      code: 'IE',
      name: isEn ? 'Ireland' : 'Irlanda',
      flag: '🇮🇪',
      specificNote: isEn
        ? `41% Exit Tax on ETFs with Deemed Disposal (${
            (currentInputs.taxSettings.irelandDeemedDisposalMode || 'staggered_rolling_eighth') ===
            'staggered_rolling_eighth'
              ? '1/8th annual rolling DCA'
              : '8-year lump sum cliff'
          }), or 33% CGT on individual equities.`
        : `Exit Tax 41% en ETFs amb Deemed Disposal (${
            (currentInputs.taxSettings.irelandDeemedDisposalMode || 'staggered_rolling_eighth') ===
            'staggered_rolling_eighth'
              ? '1/8 anual suavitzat DCA'
              : 'en bloc cada 8 anys'
          }), o 33% CGT en borsa.`,
    },
    {
      code: 'AD',
      name: 'Andorra',
      flag: '🇦🇩',
      specificNote: isEn
        ? '0% tax on gains from international listed equities/funds (<25% ownership) or flat 10% with €3k exemption.'
        : '0% en compravenda de borsa cotitzada (<25%) o tipus únic del 10% amb 3k€ exempts.',
    },
  ];

  const results = countries.map((c) => {
    const customTax: TaxSettings = {
      ...currentInputs.taxSettings,
      country: c.code,
      cataloniaCapitalGainsRatio: 50,
      cataloniaApplyWealthTax: true,
      irelandAssetType: 'etf_exit_tax',
      irelandSimulateDeemedDisposal: true,
      irelandDeemedDisposalMode:
        currentInputs.taxSettings.irelandDeemedDisposalMode || 'staggered_rolling_eighth',
      andorraExemptListedSecurities: true,
      taxReformChangeRate: 0,
      plannedRelocationCountry: 'none',
    };

    const sim = simulateFire(
      {
        ...currentInputs,
        taxSettings: customTax,
      },
      lang
    );

    return {
      country: c,
      sim,
    };
  });

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-sm space-y-4">
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500/20 to-indigo-500/20 border border-blue-500/30 text-blue-400">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              {t.compareTitle}
              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20 font-medium">
                {t.compareSameGoalBadge}
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              {t.compareSubtitle}
            </p>
          </div>
        </div>
      </div>

      {/* Grid of 3 Countries */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {results.map(({ country, sim }) => {
          const isCurrentActive = currentInputs.taxSettings.country === country.code;
          return (
            <div
              key={country.code}
              className={`rounded-xl border p-4 transition-all relative flex flex-col justify-between ${
                isCurrentActive
                  ? 'bg-blue-950/30 border-blue-500/50 ring-1 ring-blue-500/40 shadow-lg shadow-blue-500/10'
                  : 'bg-slate-950/70 border-slate-800/90 hover:border-slate-700'
              }`}
            >
              {isCurrentActive && (
                <span className="absolute -top-2.5 right-4 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-blue-600 text-white shadow">
                  {t.compareCurrentlyActive}
                </span>
              )}

              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{country.flag}</span>
                  <div>
                    <h4 className="text-sm font-bold text-white">{country.name}</h4>
                    <span className="text-[11px] text-slate-400">{t.compareJurisdiction}</span>
                  </div>
                </div>

                <div className="p-3 bg-slate-900/80 rounded-lg space-y-2 border border-slate-800">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                      {t.compareRequiredFireCapital}
                    </span>
                    <span className="text-lg font-black text-white font-mono">
                      {Math.round(sim.fireNumberNominal).toLocaleString(locale)} €
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-slate-800">
                    <div>
                      <span className="text-[10px] text-slate-400 block">{t.compareYearsToFire}</span>
                      <span className="font-bold text-emerald-400 font-mono">
                        {sim.isAlreadyFire ? t.alreadyFire : `${sim.yearsToFire} ${t.years}`}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block">{t.compareRetirementAge}</span>
                      <span className="font-bold text-slate-200 font-mono">
                        {sim.ageAtFire} {t.years}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-slate-800">
                    <div>
                      <span className="text-[10px] text-slate-400 block">{t.compareAnnualTaxes}</span>
                      <span className="font-bold text-rose-400 font-mono">
                        {Math.round(sim.annualTaxAtRetirement).toLocaleString(locale)} €
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block">{t.compareEffectiveRate}</span>
                      <span className="font-bold text-purple-400 font-mono">
                        {(sim.effectiveTaxRateAtRetirement * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                <p className="text-[11px] text-slate-400 leading-relaxed italic">
                  {country.specificNote}
                </p>
              </div>

              <div className="pt-3 mt-3 border-t border-slate-800">
                {!isCurrentActive ? (
                  <button
                    type="button"
                    onClick={() => onApplyCountry(country.code)}
                    className="w-full flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-xs font-semibold bg-slate-850 hover:bg-slate-800 text-slate-300 border border-slate-700 hover:border-slate-600 transition-colors cursor-pointer"
                  >
                    <span>{t.compareActivateTaxation} {country.name}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <div className="text-center text-[11px] text-blue-400 font-bold flex items-center justify-center gap-1">
                    <Check className="w-3.5 h-3.5" /> {t.compareActiveInSimulation}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
