import React from 'react';
import {
  Flame,
  CalendarCheck,
  Coins,
  Receipt,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react';
import { FireCalculationResult, CountryCode } from '../types/fire';
import { Language, TRANSLATIONS } from '../i18n/translations';

interface MetricCardsProps {
  result: FireCalculationResult;
  safeWithdrawalRate: number;
  country: CountryCode;
  lang: Language;
}

export const MetricCards: React.FC<MetricCardsProps> = ({
  result,
  safeWithdrawalRate,
  country,
  lang,
}) => {
  const t = TRANSLATIONS[lang];
  const {
    fireNumberNominal,
    monthlyDisposableTarget,
    annualGrossWithdrawalNeeded,
    annualTaxAtRetirement,
    effectiveTaxRateAtRetirement,
    yearsToFire,
    ageAtFire,
    calendarYearAtFire,
    isAlreadyFire,
    currentTotalNetWorth,
    isSustainable,
    portfolioSurvivalYears,
  } = result;

  const countryName = {
    CAT: lang === 'en' ? 'Catalonia 🏴󠁥󠁳󠁣󠁴󠁿' : 'Catalunya 🏴󠁥󠁳󠁣󠁴󠁿',
    IE: lang === 'en' ? 'Ireland 🇮🇪' : 'Irlanda 🇮🇪',
    AD: 'Andorra 🇦🇩',
  }[country] || (lang === 'en' ? 'Catalonia 🏴󠁥󠁳󠁣󠁴󠁿' : 'Catalunya 🏴󠁥󠁳󠁣󠁴󠁿');

  const locale = lang === 'en' ? 'en-US' : 'ca-ES';

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. FIRE NUMBER */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-amber-500/15 via-orange-500/10 to-slate-900 border border-orange-500/30 p-5 shadow-lg backdrop-blur-sm">
        <div className="absolute top-3 right-3 p-2 rounded-xl bg-orange-500/20 text-orange-400">
          <Flame className="w-5 h-5" />
        </div>
        <span className="text-xs font-bold text-orange-400 uppercase tracking-wider block mb-1">
          {t.fireNumberTitle}
        </span>
        <div className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          {Math.round(fireNumberNominal).toLocaleString(locale)} €
        </div>
        <p className="text-[11px] text-slate-300 mt-2 flex items-center gap-1 font-medium">
          <span>{safeWithdrawalRate.toFixed(1)}% SWR</span>
          <span className="text-slate-500">•</span>
          <span>{(100 / safeWithdrawalRate).toFixed(1)}x {t.swrMultiplierSuffix}</span>
        </p>
        <div className="mt-2.5 text-[10px] text-slate-400 pt-2 border-t border-orange-500/20">
          {t.currentNetWorthLabel} {Math.round(currentTotalNetWorth).toLocaleString(locale)} € ({((currentTotalNetWorth / (fireNumberNominal || 1)) * 100).toFixed(0)}%)
        </div>
      </div>

      {/* 2. TIME TO FIRE */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-500/15 via-teal-500/10 to-slate-900 border border-emerald-500/30 p-5 shadow-lg backdrop-blur-sm">
        <div className="absolute top-3 right-3 p-2 rounded-xl bg-emerald-500/20 text-emerald-400">
          <CalendarCheck className="w-5 h-5" />
        </div>
        <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider block mb-1">
          {t.timeToFireTitle}
        </span>
        <div className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          {isAlreadyFire ? (
            <span className="text-emerald-400">{t.alreadyFire}</span>
          ) : (
            `${yearsToFire} ${t.years}`
          )}
        </div>
        <p className="text-[11px] text-slate-300 mt-2 font-medium">
          {isAlreadyFire ? (
            t.canRetireNow
          ) : (
            <>
              {t.retireAtAge} <strong>{ageAtFire} {t.years}</strong> ({t.inYear} <strong>{calendarYearAtFire}</strong>)
            </>
          )}
        </p>
        <div className="mt-2.5 text-[10px] text-slate-400 pt-2 border-t border-emerald-500/20">
          {t.survivalEstimated} {portfolioSurvivalYears} {t.planYears}
        </div>
      </div>

      {/* 3. DISPOSABLE INCOME */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-cyan-500/15 via-blue-500/10 to-slate-900 border border-cyan-500/30 p-5 shadow-lg backdrop-blur-sm">
        <div className="absolute top-3 right-3 p-2 rounded-xl bg-cyan-500/20 text-cyan-400">
          <Coins className="w-5 h-5" />
        </div>
        <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider block mb-1">
          {t.disposableIncomeTitle}
        </span>
        <div className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          {Math.round(monthlyDisposableTarget).toLocaleString(locale)} €
          <span className="text-sm font-normal text-slate-400">{t.perMonth}</span>
        </div>
        <p className="text-[11px] text-slate-300 mt-2 font-medium">
          = {Math.round(monthlyDisposableTarget * 12).toLocaleString(locale)} € {t.netPerYear}
        </p>
        <div className="mt-2.5 text-[10px] text-slate-400 pt-2 border-t border-cyan-500/20">
          {t.grossWithdrawalNeeded} {Math.round(annualGrossWithdrawalNeeded).toLocaleString(locale)} €{t.perYear}
        </div>
      </div>

      {/* 4. TAXATION */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-purple-500/15 via-indigo-500/10 to-slate-900 border border-purple-500/30 p-5 shadow-lg backdrop-blur-sm">
        <div className="absolute top-3 right-3 p-2 rounded-xl bg-purple-500/20 text-purple-400">
          <Receipt className="w-5 h-5" />
        </div>
        <span className="text-xs font-bold text-purple-400 uppercase tracking-wider block mb-1">
          {t.taxationTitle} ({countryName})
        </span>
        <div className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          {Math.round(annualTaxAtRetirement).toLocaleString(locale)} €
          <span className="text-sm font-normal text-slate-400">{t.perYear}</span>
        </div>
        <p className="text-[11px] text-slate-300 mt-2 font-medium">
          {t.effectiveTaxRate} <strong>{(effectiveTaxRateAtRetirement * 100).toFixed(1)}%</strong>
        </p>
        <div className="mt-2.5 text-[10px] text-slate-400 pt-2 border-t border-purple-500/20 flex items-center justify-between">
          <span>{t.planStatus}</span>
          {isSustainable ? (
            <span className="text-emerald-400 flex items-center gap-1 font-bold">
              <CheckCircle className="w-3 h-3" /> {t.sustainable}
            </span>
          ) : (
            <span className="text-rose-400 flex items-center gap-1 font-bold">
              <AlertTriangle className="w-3 h-3" /> {t.depletionRisk}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
