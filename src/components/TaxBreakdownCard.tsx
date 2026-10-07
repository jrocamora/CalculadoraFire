import React from 'react';
import {
  FireCalculationResult,
  TaxSettings,
} from '../types/fire';
import { computeAnnualTaxForWithdrawal } from '../utils/taxCalculators';
import { Receipt, Info, Wallet, ArrowDownRight } from 'lucide-react';
import { Language, TRANSLATIONS } from '../i18n/translations';

interface TaxBreakdownCardProps {
  result: FireCalculationResult;
  taxSettings: TaxSettings;
  lang: Language;
}

export const TaxBreakdownCard: React.FC<TaxBreakdownCardProps> = ({
  result,
  taxSettings,
  lang,
}) => {
  const t = TRANSLATIONS[lang];
  const locale = lang === 'en' ? 'en-US' : 'ca-ES';
  const { annualGrossWithdrawalNeeded, annualTaxAtRetirement, monthlyDisposableTarget } = result;

  const annualNet = monthlyDisposableTarget * 12;
  const taxComputation = computeAnnualTaxForWithdrawal(
    annualGrossWithdrawalNeeded,
    taxSettings,
    result.fireNumberNominal,
    lang
  );

  const gross = Math.max(1, annualGrossWithdrawalNeeded);
  const netRatio = Math.min(100, Math.max(0, (annualNet / gross) * 100));
  const taxRatio = Math.min(100, Math.max(0, (annualTaxAtRetirement / gross) * 100));

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
            <Receipt className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">{t.breakdownTitle}</h3>
            <p className="text-xs text-slate-400">
              {t.breakdownSubtitle}
            </p>
          </div>
        </div>

        <div className="text-right">
          <span className="text-xs font-semibold text-slate-400 block">{t.grossAnnualWithdrawal}</span>
          <span className="text-base font-black text-white font-mono">
            {Math.round(annualGrossWithdrawalNeeded).toLocaleString(locale)} €{t.perYear}
          </span>
        </div>
      </div>

      {/* Visual Proportional Bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs font-semibold">
          <span className="text-emerald-400 flex items-center gap-1">
            <Wallet className="w-3.5 h-3.5" />
            {t.netInPocket} {netRatio.toFixed(1)}% ({Math.round(annualNet).toLocaleString(locale)} €)
          </span>
          <span className="text-rose-400 flex items-center gap-1">
            <ArrowDownRight className="w-3.5 h-3.5" />
            {t.taxesPaid} {taxRatio.toFixed(1)}% ({Math.round(annualTaxAtRetirement).toLocaleString(locale)} €)
          </span>
        </div>

        <div className="w-full h-4 bg-slate-950 rounded-full overflow-hidden flex border border-slate-800">
          <div
            style={{ width: `${netRatio}%` }}
            className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500"
          />
          <div
            style={{ width: `${taxRatio}%` }}
            className="h-full bg-gradient-to-r from-rose-500 to-red-600 transition-all duration-500"
          />
        </div>
      </div>

      {/* Narrative explanation */}
      <div className="p-3.5 bg-slate-950/70 border border-slate-800 rounded-xl space-y-2 text-xs">
        <div className="flex items-start gap-2">
          <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
          <p className="text-slate-300 leading-relaxed">
            {taxComputation.explanation}
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800 text-[11px]">
          <div>
            <span className="text-slate-500 block">{t.taxableGains}</span>
            <span className="font-bold text-slate-200 font-mono">
              {Math.round(taxComputation.taxableGains).toLocaleString(locale)} €
            </span>
          </div>
          <div>
            <span className="text-slate-500 block">{t.irpfQuota}</span>
            <span className="font-bold text-amber-400 font-mono">
              {Math.round(taxComputation.irpfTax).toLocaleString(locale)} €
            </span>
          </div>
          <div>
            <span className="text-slate-500 block">
              {taxSettings.country === 'CAT' && taxComputation.wealthTax > 0
                ? t.cataloniaWealthQuota
                : t.totalEffectiveRate}
            </span>
            <span className="font-bold text-rose-400 font-mono">
              {taxSettings.country === 'CAT' && taxComputation.wealthTax > 0
                ? `${Math.round(taxComputation.wealthTax).toLocaleString(locale)} €`
                : `${(taxComputation.effectiveTaxRate * 100).toFixed(1)}%`}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block">{t.netWithdrawalPerMonth}</span>
            <span className="font-bold text-emerald-400 font-mono">
              {Math.round(monthlyDisposableTarget).toLocaleString(locale)} €{t.perMonth}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
