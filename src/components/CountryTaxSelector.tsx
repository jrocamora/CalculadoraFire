import React from 'react';
import {
  Landmark,
  Scale,
  AlertTriangle,
  CheckCircle2,
  Sliders,
  PlaneTakeoff,
} from 'lucide-react';
import { CountryCode, TaxSettings } from '../types/fire';
import { getSupportedCountries } from '../utils/taxCalculators';
import { Language, TRANSLATIONS } from '../i18n/translations';

interface CountryTaxSelectorProps {
  taxSettings: TaxSettings;
  onChange: (settings: TaxSettings) => void;
  currentYear: number;
  lang: Language;
}

export const CountryTaxSelector: React.FC<CountryTaxSelectorProps> = ({
  taxSettings,
  onChange,
  currentYear,
  lang,
}) => {
  const t = TRANSLATIONS[lang];
  const supportedCountries = getSupportedCountries(lang);
  const selectedCountryMeta = supportedCountries.find((c) => c.code === taxSettings.country);

  const handleCountrySelect = (code: CountryCode) => {
    onChange({
      ...taxSettings,
      country: code,
    });
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-sm space-y-5">
      {/* Title & Country Tabs */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <Landmark className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              {t.countryTaxTitle}
            </h3>
            <p className="text-xs text-slate-400">
              {t.countryTaxSubtitle}
            </p>
          </div>
        </div>

        {/* 3 Country Selectors */}
        <div className="grid grid-cols-3 p-1 bg-slate-950 border border-slate-800 rounded-xl gap-1">
          {supportedCountries.map((c) => {
            const isSelected = taxSettings.country === c.code;
            return (
              <button
                key={c.code}
                type="button"
                onClick={() => handleCountrySelect(c.code)}
                className={`flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <span>{c.flag}</span>
                <span>{c.name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Country Context Card */}
      {selectedCountryMeta && (
        <div className="p-3.5 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-2">
          <p className="text-xs text-slate-300 leading-relaxed font-medium">
            {selectedCountryMeta.summary}
          </p>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-1.5 pt-1 text-[11px] text-slate-400">
            {selectedCountryMeta.highlights.map((h, i) => (
              <li key={i} className="flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
                <span>{h}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Jurisdictional Specific Controls */}
      {taxSettings.country === 'CAT' && (
        <div className="p-4 bg-amber-500/5 border border-amber-500/20 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
              <Scale className="w-4 h-4" /> {t.cataloniaSpecificTitle}
            </h4>
            <span className="text-[10px] font-semibold bg-amber-500/15 text-amber-300 px-2 py-0.5 rounded-full border border-amber-500/30">
              {t.cataloniaSpecificBadge}
            </span>
          </div>

          {/* Capital Gains Ratio */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <label className="text-slate-300 font-medium flex items-center gap-1.5">
                {t.capitalGainsRatioLabel}
              </label>
              <span className="font-bold text-amber-400 font-mono">
                {taxSettings.cataloniaCapitalGainsRatio ?? 50}% {t.capitalGainsRatioSuffix}
              </span>
            </div>
            <input
              type="range"
              min={10}
              max={100}
              step={5}
              value={taxSettings.cataloniaCapitalGainsRatio ?? 50}
              onChange={(e) =>
                onChange({ ...taxSettings, cataloniaCapitalGainsRatio: Number(e.target.value) })
              }
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
            <p className="text-[11px] text-slate-400 leading-normal">
              {t.cataloniaGainsHelp}
            </p>
          </div>

          {/* Catalonia Wealth Tax Toggle & Details */}
          <div className="p-3 bg-amber-500/10 border border-amber-500/25 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-amber-200 block">
                  {t.cataloniaWealthTaxTitle}
                </span>
                <span className="text-[11px] text-amber-300/80">
                  {t.cataloniaWealthTaxBadge}
                </span>
              </div>
              <input
                type="checkbox"
                checked={taxSettings.cataloniaApplyWealthTax}
                onChange={(e) =>
                  onChange({ ...taxSettings, cataloniaApplyWealthTax: e.target.checked })
                }
                className="w-4 h-4 accent-amber-500 rounded cursor-pointer"
              />
            </div>
            <p className="text-[11px] text-slate-300 leading-relaxed pt-1 border-t border-amber-500/20">
              {t.cataloniaWealthTaxDesc}
            </p>
          </div>
        </div>
      )}

      {taxSettings.country === 'IE' && (
        <div className="p-4 bg-emerald-500/5 border border-emerald-500/20 rounded-xl space-y-4">
          <h4 className="text-xs font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
            <Scale className="w-4 h-4" /> {t.irelandSpecificTitle}
          </h4>

          {/* Asset Type Selector */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 block">
              {t.irelandInvestmentType}
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <label
                className={`p-3 rounded-xl border flex items-start gap-2.5 cursor-pointer transition-all ${
                  taxSettings.irelandAssetType === 'etf_exit_tax'
                    ? 'bg-emerald-500/15 border-emerald-500/50 text-emerald-200'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <input
                  type="radio"
                  name="irelandAssetType"
                  value="etf_exit_tax"
                  checked={taxSettings.irelandAssetType === 'etf_exit_tax'}
                  onChange={() => onChange({ ...taxSettings, irelandAssetType: 'etf_exit_tax' })}
                  className="mt-1 accent-emerald-500"
                />
                <div>
                  <span className="text-xs font-bold block">{t.irelandEtfsExitTax}</span>
                  <span className="text-[11px] leading-tight block text-slate-400">
                    {t.irelandEtfsExitTaxSub}
                  </span>
                </div>
              </label>

              <label
                className={`p-3 rounded-xl border flex items-start gap-2.5 cursor-pointer transition-all ${
                  taxSettings.irelandAssetType === 'individual_shares_cgt'
                    ? 'bg-emerald-500/15 border-emerald-500/50 text-emerald-200'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <input
                  type="radio"
                  name="irelandAssetType"
                  value="individual_shares_cgt"
                  checked={taxSettings.irelandAssetType === 'individual_shares_cgt'}
                  onChange={() =>
                    onChange({ ...taxSettings, irelandAssetType: 'individual_shares_cgt' })
                  }
                  className="mt-1 accent-emerald-500"
                />
                <div>
                  <span className="text-xs font-bold block">{t.irelandIndividualShares}</span>
                  <span className="text-[11px] leading-tight block text-slate-400">
                    {t.irelandIndividualSharesSub}
                  </span>
                </div>
              </label>
            </div>
          </div>

          {/* Deemed Disposal Settings */}
          {taxSettings.irelandAssetType === 'etf_exit_tax' && (
            <div className="p-3.5 bg-red-500/10 border border-red-500/30 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-red-300 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    {t.irelandDeemedDisposalTitle}
                  </span>
                  <span className="text-[11px] text-red-200/70 block mt-0.5">
                    {t.irelandDeemedDisposalSub}
                  </span>
                </div>
                <input
                  type="checkbox"
                  checked={taxSettings.irelandSimulateDeemedDisposal}
                  onChange={(e) =>
                    onChange({ ...taxSettings, irelandSimulateDeemedDisposal: e.target.checked })
                  }
                  className="w-4 h-4 accent-red-500 rounded cursor-pointer shrink-0"
                />
              </div>

              {taxSettings.irelandSimulateDeemedDisposal && (
                <div className="pt-2 border-t border-red-500/20 space-y-2">
                  <label className="text-[11px] font-bold text-slate-200 block">
                    {t.irelandDeemedDisposalModelLabel}
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <label
                      className={`p-2.5 rounded-xl border flex items-start gap-2 cursor-pointer transition-all ${
                        (taxSettings.irelandDeemedDisposalMode || 'staggered_rolling_eighth') ===
                        'staggered_rolling_eighth'
                          ? 'bg-red-500/20 border-red-500/50 text-white'
                          : 'bg-slate-950/70 border-slate-800 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <input
                        type="radio"
                        name="irelandDeemedDisposalMode"
                        value="staggered_rolling_eighth"
                        checked={
                          (taxSettings.irelandDeemedDisposalMode || 'staggered_rolling_eighth') ===
                          'staggered_rolling_eighth'
                        }
                        onChange={() =>
                          onChange({
                            ...taxSettings,
                            irelandDeemedDisposalMode: 'staggered_rolling_eighth',
                          })
                        }
                        className="mt-1 accent-red-500"
                      />
                      <div>
                        <span className="text-xs font-bold block text-red-200">
                          {t.irelandDeemedDisposalRolling}
                        </span>
                        <span className="text-[10px] leading-tight block text-slate-300 mt-0.5">
                          {t.irelandDeemedDisposalRollingDesc}
                        </span>
                      </div>
                    </label>

                    <label
                      className={`p-2.5 rounded-xl border flex items-start gap-2 cursor-pointer transition-all ${
                        taxSettings.irelandDeemedDisposalMode === 'lump_sum_8y'
                          ? 'bg-red-500/20 border-red-500/50 text-white'
                          : 'bg-slate-950/70 border-slate-800 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <input
                        type="radio"
                        name="irelandDeemedDisposalMode"
                        value="lump_sum_8y"
                        checked={taxSettings.irelandDeemedDisposalMode === 'lump_sum_8y'}
                        onChange={() =>
                          onChange({
                            ...taxSettings,
                            irelandDeemedDisposalMode: 'lump_sum_8y',
                          })
                        }
                        className="mt-1 accent-red-500"
                      />
                      <div>
                        <span className="text-xs font-bold block text-red-200">
                          {t.irelandDeemedDisposalLumpSum}
                        </span>
                        <span className="text-[10px] leading-tight block text-slate-300 mt-0.5">
                          {t.irelandDeemedDisposalLumpSumDesc}
                        </span>
                      </div>
                    </label>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {taxSettings.country === 'AD' && (
        <div className="p-4 bg-indigo-500/5 border border-indigo-500/20 rounded-xl space-y-3">
          <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-1.5">
            <Scale className="w-4 h-4" /> {t.andorraSpecificTitle}
          </h4>

          <div className="flex items-start justify-between gap-4 p-3 bg-slate-950/70 border border-indigo-500/20 rounded-xl">
            <div>
              <span className="text-xs font-bold text-white block">
                {t.andorraExemptTitle}
              </span>
              <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">
                {t.andorraExemptDesc}
              </p>
            </div>
            <input
              type="checkbox"
              checked={taxSettings.andorraExemptListedSecurities}
              onChange={(e) =>
                onChange({ ...taxSettings, andorraExemptListedSecurities: e.target.checked })
              }
              className="w-4 h-4 accent-indigo-500 rounded cursor-pointer mt-1"
            />
          </div>

          {!taxSettings.andorraExemptListedSecurities && (
            <div className="text-[11px] text-indigo-300/80 bg-indigo-500/10 p-2.5 rounded-lg">
              {t.andorraGeneralRegimeNote}
            </div>
          )}
        </div>
      )}

      {/* Escenaris de Reforma Fiscal & Canvis Futurs */}
      <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-purple-400" />
            <h4 className="text-xs font-bold text-slate-200">
              {t.taxReformTitle}
            </h4>
          </div>
          <span className="text-xs font-mono font-bold text-purple-400">
            {taxSettings.taxReformChangeRate > 0 ? `+${taxSettings.taxReformChangeRate}%` : `${taxSettings.taxReformChangeRate}%`}
          </span>
        </div>

        <p className="text-[11px] text-slate-400">
          {t.taxReformDesc}
        </p>

        <input
          type="range"
          min={-5}
          max={10}
          step={1}
          value={taxSettings.taxReformChangeRate}
          onChange={(e) =>
            onChange({ ...taxSettings, taxReformChangeRate: Number(e.target.value) })
          }
          className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
        />
        <div className="flex justify-between text-[10px] text-slate-500">
          <span>{t.taxReformCut}</span>
          <span>{t.taxReformCurrent}</span>
          <span>{t.taxReformModerate}</span>
          <span>{t.taxReformHigh}</span>
        </div>

        {/* Optional Relocation */}
        <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <PlaneTakeoff className="w-4 h-4 text-cyan-400" />
            <div>
              <span className="text-xs font-semibold text-slate-200 block">
                {t.relocationTitle}
              </span>
              <span className="text-[10px] text-slate-400">
                {t.relocationSub}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={taxSettings.plannedRelocationCountry || 'none'}
              onChange={(e) =>
                onChange({
                  ...taxSettings,
                  plannedRelocationCountry: e.target.value as CountryCode | 'none',
                  plannedRelocationYear:
                    e.target.value !== 'none'
                      ? taxSettings.plannedRelocationYear || currentYear + 10
                      : undefined,
                })
              }
              className="bg-slate-900 border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="none">{t.relocationNone}</option>
              <option value="AD">{t.relocateToAndorra}</option>
              <option value="CAT">{t.relocateToCatalonia}</option>
              <option value="IE">{t.relocateToIreland}</option>
            </select>

            {taxSettings.plannedRelocationCountry && taxSettings.plannedRelocationCountry !== 'none' && (
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-slate-400">{t.relocationYear}</span>
                <input
                  type="number"
                  min={currentYear}
                  max={currentYear + 40}
                  value={taxSettings.plannedRelocationYear || currentYear + 10}
                  onChange={(e) =>
                    onChange({
                      ...taxSettings,
                      plannedRelocationYear: Number(e.target.value),
                    })
                  }
                  className="w-18 bg-slate-900 border border-slate-700 text-xs rounded-lg px-2 py-1 text-white text-center focus:outline-none focus:border-cyan-500"
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
