import React from 'react';
import {
  Wallet,
  Target,
  PiggyBank,
  TrendingUp,
  PieChart,
  Info,
  Layers,
} from 'lucide-react';
import { CalculationMode, PortfolioAsset, AssetCategory } from '../types/fire';
import { Language, TRANSLATIONS } from '../i18n/translations';

interface BiDirectionalInputsProps {
  mode: CalculationMode;
  onModeChange: (mode: CalculationMode) => void;
  targetMonthlyDisposableIncome: number;
  onTargetMonthlyIncomeChange: (val: number) => void;
  assets: PortfolioAsset[];
  onAssetsChange: (assets: PortfolioAsset[]) => void;
  monthlySavings: number;
  onMonthlySavingsChange: (val: number) => void;
  annualSavingsIncreaseRate: number;
  onSavingsIncreaseRateChange: (val: number) => void;
  currentAge: number;
  onCurrentAgeChange: (val: number) => void;
  targetRetirementAge: number;
  onTargetRetirementAgeChange: (val: number) => void;
  lifeExpectancy: number;
  onLifeExpectancyChange: (val: number) => void;
  lang: Language;
}

export const BiDirectionalInputs: React.FC<BiDirectionalInputsProps> = ({
  mode,
  onModeChange,
  targetMonthlyDisposableIncome,
  onTargetMonthlyIncomeChange,
  assets,
  onAssetsChange,
  monthlySavings,
  onMonthlySavingsChange,
  annualSavingsIncreaseRate,
  onSavingsIncreaseRateChange,
  currentAge,
  onCurrentAgeChange,
  targetRetirementAge,
  onTargetRetirementAgeChange,
  lifeExpectancy,
  onLifeExpectancyChange,
  lang,
}) => {
  const t = TRANSLATIONS[lang];
  const locale = lang === 'en' ? 'en-US' : 'ca-ES';
  const totalAssets = assets.reduce((sum, a) => sum + (Number(a.currentAmount) || 0), 0);

  const categoryLabels: Record<AssetCategory, { label: string; icon: string; color: string }> = {
    index_funds: { label: t.categoryIndexFunds, icon: '📈', color: 'text-indigo-400 bg-indigo-500/10' },
    individual_stocks: { label: t.categoryIndividualStocks, icon: '🏢', color: 'text-emerald-400 bg-emerald-500/10' },
    cash_deposits: { label: t.categoryCashDeposits, icon: '💶', color: 'text-amber-400 bg-amber-500/10' },
    real_estate_other: { label: t.categoryRealEstateOther, icon: '🏡', color: 'text-purple-400 bg-purple-500/10' },
  };

  const handleUpdateAssetAmount = (id: string, amount: number) => {
    onAssetsChange(
      assets.map((a) => (a.id === id ? { ...a, currentAmount: Math.max(0, amount) } : a))
    );
  };

  const handleUpdateAssetReturn = (id: string, ret: number) => {
    onAssetsChange(
      assets.map((a) => (a.id === id ? { ...a, expectedReturnAnnual: ret } : a))
    );
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
      {/* Mode Switcher Tabs */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 text-indigo-400">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">{t.inputModeTitle}</h2>
            <p className="text-xs text-slate-400">
              {t.inputModeSubtitle}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 p-1 bg-slate-950 border border-slate-800 rounded-xl gap-1">
          <button
            type="button"
            onClick={() => onModeChange('target_spending')}
            className={`flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
              mode === 'target_spending'
                ? 'bg-gradient-to-r from-orange-500 to-amber-500 text-slate-950 shadow-md shadow-orange-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Target className="w-3.5 h-3.5" />
            <span>{t.modeTargetSpending}</span>
          </button>
          <button
            type="button"
            onClick={() => onModeChange('current_portfolio')}
            className={`flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
              mode === 'current_portfolio'
                ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-md shadow-emerald-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Wallet className="w-3.5 h-3.5" />
            <span>{t.modeCurrentPortfolio}</span>
          </button>
        </div>
      </div>

      {/* Main Mode Body */}
      <div className="pt-5 space-y-6">
        {mode === 'target_spending' ? (
          /* MODE A: Target Spending */
          <div className="space-y-4">
            <div className="p-4 bg-orange-500/5 border border-orange-500/20 rounded-xl">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <label className="text-sm font-semibold text-orange-200 flex items-center gap-2">
                    <Target className="w-4 h-4 text-orange-400" />
                    {t.targetDisposableQuestion}
                  </label>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {t.targetDisposableHelp}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-black text-white tracking-tight">
                    {targetMonthlyDisposableIncome.toLocaleString(locale)} €
                  </span>
                  <span className="block text-xs text-orange-400 font-medium">
                    = {(targetMonthlyDisposableIncome * 12).toLocaleString(locale)} € {t.netPerYearEquivalent}
                  </span>
                </div>
              </div>

              {/* Slider for monthly income */}
              <div className="mt-4">
                <input
                  type="range"
                  min={1000}
                  max={10000}
                  step={100}
                  value={targetMonthlyDisposableIncome}
                  onChange={(e) => onTargetMonthlyIncomeChange(Number(e.target.value))}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-orange-500"
                />
                <div className="flex justify-between text-[11px] text-slate-500 mt-1">
                  <span>1.000 €{t.perMonth}</span>
                  <span>{t.commonTarget}</span>
                  <span>{t.fatFire}</span>
                  <span>10.000 €{t.perMonth}</span>
                </div>
              </div>

              {/* Direct quick input */}
              <div className="mt-3 flex items-center gap-3">
                <span className="text-xs text-slate-400">{t.enterExactValue}</span>
                <div className="relative w-40">
                  <input
                    type="number"
                    value={targetMonthlyDisposableIncome}
                    onChange={(e) => onTargetMonthlyIncomeChange(Math.max(500, Number(e.target.value)))}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-sm font-semibold text-white focus:outline-none focus:border-orange-500 pr-8"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500 font-medium">€{t.perMonth}</span>
                </div>
              </div>
            </div>

            {/* Current savings and contributions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-3.5 bg-slate-950/70 border border-slate-800/80 rounded-xl space-y-2">
                <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <PiggyBank className="w-4 h-4 text-emerald-400" />
                  {t.accumulatedCapitalLabel}
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={assets[0]?.currentAmount || 0}
                    onChange={(e) => handleUpdateAssetAmount(assets[0]?.id || '1', Number(e.target.value))}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm font-bold text-white focus:outline-none focus:border-emerald-500 pr-8"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 font-medium">€</span>
                </div>
                <p className="text-[11px] text-slate-500">
                  {t.accumulatedCapitalHelp}
                </p>
              </div>

              <div className="p-3.5 bg-slate-950/70 border border-slate-800/80 rounded-xl space-y-2">
                <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <TrendingUp className="w-4 h-4 text-cyan-400" />
                  {t.monthlySavingsLabel}
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={monthlySavings}
                    onChange={(e) => onMonthlySavingsChange(Math.max(0, Number(e.target.value)))}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm font-bold text-white focus:outline-none focus:border-cyan-500 pr-12"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 font-medium">€{t.perMonth}</span>
                </div>
                <p className="text-[11px] text-slate-500">
                  {(monthlySavings * 12).toLocaleString(locale)} € {t.monthlySavingsHelp}
                </p>
              </div>
            </div>
          </div>
        ) : (
          /* MODE B: Current Portfolio & Where it is held */
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
              <div className="flex items-center gap-2">
                <PieChart className="w-5 h-5 text-emerald-400" />
                <div>
                  <h3 className="text-sm font-bold text-white">{t.portfolioTotal} {totalAssets.toLocaleString(locale)} €</h3>
                  <p className="text-xs text-slate-400">{t.portfolioAssetSubtitle}</p>
                </div>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                {assets.length} {t.assetsCount}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {assets.map((asset) => {
                const meta = categoryLabels[asset.category];
                return (
                  <div
                    key={asset.id}
                    className="p-3.5 bg-slate-950/70 border border-slate-800 rounded-xl space-y-2 hover:border-slate-700 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                        <span>{meta.icon}</span>
                        {meta.label}
                      </span>
                      <span className="text-[11px] text-slate-400">
                        {totalAssets > 0 ? ((asset.currentAmount / totalAssets) * 100).toFixed(1) : 0}%
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="text-[10px] text-slate-400 block mb-0.5">{t.currentCapital}</label>
                        <input
                          type="number"
                          value={asset.currentAmount}
                          onChange={(e) => handleUpdateAssetAmount(asset.id, Number(e.target.value))}
                          className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-bold text-white focus:outline-none focus:border-emerald-500"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-slate-400 block mb-0.5">{t.expectedReturn}</label>
                        <div className="relative">
                          <input
                            type="number"
                            step="0.5"
                            value={asset.expectedReturnAnnual}
                            onChange={(e) => handleUpdateAssetReturn(asset.id, Number(e.target.value))}
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-bold text-white focus:outline-none focus:border-emerald-500 pr-6"
                          />
                          <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-slate-400">%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Savings and target retirement age */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
              <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  {t.additionalMonthlySavings}
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={monthlySavings}
                    onChange={(e) => onMonthlySavingsChange(Math.max(0, Number(e.target.value)))}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-sm font-bold text-white focus:outline-none focus:border-teal-500 pr-12"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400">€{t.perMonth}</span>
                </div>
              </div>

              <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-semibold text-slate-300">
                    {t.targetRetirementAgeLabel}
                  </label>
                  <span className="text-xs font-bold text-teal-400">{targetRetirementAge} {t.years}</span>
                </div>
                <input
                  type="range"
                  min={Math.max(currentAge, 35)}
                  max={75}
                  value={targetRetirementAge}
                  onChange={(e) => onTargetRetirementAgeChange(Number(e.target.value))}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-teal-500"
                />
                <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                  <span>{currentAge} {t.todayAge}</span>
                  <span>50 {t.years}</span>
                  <span>65 {t.statePensionAge}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Global Age & Life Horizon Settings */}
        <div className="p-3.5 bg-slate-950/40 border border-slate-800/60 rounded-xl flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div>
              <label className="text-[11px] font-medium text-slate-400 block mb-1">{t.currentAgeLabel}</label>
              <input
                type="number"
                min={18}
                max={75}
                value={currentAge}
                onChange={(e) => onCurrentAgeChange(Math.max(18, Math.min(75, Number(e.target.value))))}
                className="w-20 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="text-[11px] font-medium text-slate-400 block mb-1">{t.lifeExpectancyLabel}</label>
              <input
                type="number"
                min={currentAge + 1}
                max={105}
                value={lifeExpectancy}
                onChange={(e) => onLifeExpectancyChange(Math.max(currentAge + 5, Number(e.target.value)))}
                className="w-20 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="text-[11px] font-medium text-slate-400 block mb-1">{t.annualSavingsIncreaseRateLabel}</label>
              <div className="relative">
                <input
                  type="number"
                  step="0.5"
                  min={0}
                  max={15}
                  value={annualSavingsIncreaseRate}
                  onChange={(e) => onSavingsIncreaseRateChange(Math.max(0, Number(e.target.value)))}
                  className="w-20 bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs font-bold text-white text-center focus:outline-none focus:border-indigo-500 pr-5"
                />
                <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-slate-400">%</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Info className="w-3.5 h-3.5 text-indigo-400" />
            <span>{t.horizonLabel} <strong>{lifeExpectancy - currentAge} {t.years}</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
};
