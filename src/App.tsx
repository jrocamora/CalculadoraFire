import React, { useState, useMemo, useEffect } from 'react';
import {
  FireInputs,
  CalculationMode,
  PortfolioAsset,
  CountryCode,
  TaxSettings,
  MacroScenario,
} from './types/fire';
import { simulateFire } from './utils/fireSimulation';
import { Header } from './components/Header';
import { MetricCards } from './components/MetricCards';
import { BiDirectionalInputs } from './components/BiDirectionalInputs';
import { SafeWithdrawalRateControl } from './components/SafeWithdrawalRateControl';
import { CountryTaxSelector } from './components/CountryTaxSelector';
import { MacroScenarioSelector } from './components/MacroScenarioSelector';
import { FireChart } from './components/FireChart';
import { TaxBreakdownCard } from './components/TaxBreakdownCard';
import { CountryComparisonView } from './components/CountryComparisonView';
import { YearlyProjectionTable } from './components/YearlyProjectionTable';
import { ShieldAlert } from 'lucide-react';
import { Language, TRANSLATIONS } from './i18n/translations';

const INITIAL_ASSETS: PortfolioAsset[] = [
  {
    id: 'asset-1',
    category: 'index_funds',
    name: 'Fons Indexats / ETFs Globals',
    currentAmount: 65000,
    expectedReturnAnnual: 7.0,
    costBasis: 45000,
  },
  {
    id: 'asset-2',
    category: 'individual_stocks',
    name: 'Accions Individuals / Borsa',
    currentAmount: 18000,
    expectedReturnAnnual: 7.0,
    costBasis: 12000,
  },
  {
    id: 'asset-3',
    category: 'cash_deposits',
    name: 'Comptes d’Estalvi & Dipòsits',
    currentAmount: 12000,
    expectedReturnAnnual: 3.0,
    costBasis: 12000,
  },
  {
    id: 'asset-4',
    category: 'real_estate_other',
    name: 'Immobiliari / Fons Alternatius',
    currentAmount: 5000,
    expectedReturnAnnual: 5.5,
    costBasis: 5000,
  },
];

const INITIAL_TAX_SETTINGS: TaxSettings = {
  country: 'CAT',
  cataloniaCapitalGainsRatio: 50,
  cataloniaApplyWealthTax: true,
  irelandAssetType: 'etf_exit_tax',
  irelandSimulateDeemedDisposal: true,
  irelandDeemedDisposalMode: 'staggered_rolling_eighth',
  andorraExemptListedSecurities: true,
  taxReformChangeRate: 0,
  plannedRelocationCountry: 'none',
  plannedRelocationYear: new Date().getFullYear() + 10,
};

const INITIAL_SCENARIO: MacroScenario = {
  id: 'base',
  name: 'Escenari Base',
  description: 'Rendiment històric mitjà de mercat global i inflació moderada.',
  nominalReturn: 7.0,
  inflationRate: 2.5,
};

export default function App() {
  const currentYear = new Date().getFullYear();

  // Language state (default: Catalan, supports English)
  const [lang, setLang] = useState<Language>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('fire_calculator_lang');
      if (saved === 'en' || saved === 'ca') return saved;
    }
    return 'ca';
  });

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('fire_calculator_lang', lang);
    }
    document.documentElement.lang = lang;
  }, [lang]);

  const t = TRANSLATIONS[lang];

  // Inputs principals
  const [mode, setMode] = useState<CalculationMode>('target_spending');
  const [currentAge, setCurrentAge] = useState<number>(32);
  const [targetRetirementAge, setTargetRetirementAge] = useState<number>(48);
  const [lifeExpectancy, setLifeExpectancy] = useState<number>(88);
  const [targetMonthlyDisposableIncome, setTargetMonthlyDisposableIncome] = useState<number>(2500);
  const [assets, setAssets] = useState<PortfolioAsset[]>(INITIAL_ASSETS);
  const [monthlySavings, setMonthlySavings] = useState<number>(900);
  const [annualSavingsIncreaseRate, setAnnualSavingsIncreaseRate] = useState<number>(2.0);
  const [safeWithdrawalRate, setSafeWithdrawalRate] = useState<number>(3.5);
  const [scenario, setScenario] = useState<MacroScenario>(INITIAL_SCENARIO);
  const [taxSettings, setTaxSettings] = useState<TaxSettings>(INITIAL_TAX_SETTINGS);

  // Active view tab for detailed analysis
  const [activeAnalysisTab, setActiveAnalysisTab] = useState<'chart' | 'country_compare' | 'table'>('chart');

  // Preparar objecte inputs
  const fireInputs: FireInputs = useMemo(
    () => ({
      mode,
      currentAge,
      targetRetirementAge,
      lifeExpectancy,
      targetMonthlyDisposableIncome,
      assets,
      monthlySavings,
      annualSavingsIncreaseRate,
      safeWithdrawalRate,
      scenario,
      taxSettings,
    }),
    [
      mode,
      currentAge,
      targetRetirementAge,
      lifeExpectancy,
      targetMonthlyDisposableIncome,
      assets,
      monthlySavings,
      annualSavingsIncreaseRate,
      safeWithdrawalRate,
      scenario,
      taxSettings,
    ]
  );

  // Simulació FIRE reactiva amb suport d'idioma
  const result = useMemo(() => simulateFire(fireInputs, lang), [fireInputs, lang]);

  const handleResetDefaults = () => {
    setMode('target_spending');
    setCurrentAge(32);
    setTargetRetirementAge(48);
    setLifeExpectancy(88);
    setTargetMonthlyDisposableIncome(2500);
    setAssets(INITIAL_ASSETS);
    setMonthlySavings(900);
    setAnnualSavingsIncreaseRate(2.0);
    setSafeWithdrawalRate(3.5);
    setScenario(INITIAL_SCENARIO);
    setTaxSettings(INITIAL_TAX_SETTINGS);
  };

  const handleApplyCountryFromComparison = (countryCode: CountryCode) => {
    setTaxSettings((prev) => ({
      ...prev,
      country: countryCode,
    }));
    setActiveAnalysisTab('chart');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header
        currentCountry={taxSettings.country}
        onResetDefaults={handleResetDefaults}
        lang={lang}
        onLangChange={setLang}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Metric Cards Top Overview */}
        <MetricCards
          result={result}
          safeWithdrawalRate={safeWithdrawalRate}
          country={taxSettings.country}
          lang={lang}
        />

        {/* Workspace: 2-Column Responsive Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Interactive Controls (Inputs, SWR, Country Tax, Macro) */}
          <div className="lg:col-span-5 space-y-6">
            {/* 1. Bidirectional Inputs */}
            <BiDirectionalInputs
              mode={mode}
              onModeChange={setMode}
              targetMonthlyDisposableIncome={targetMonthlyDisposableIncome}
              onTargetMonthlyIncomeChange={setTargetMonthlyDisposableIncome}
              assets={assets}
              onAssetsChange={setAssets}
              monthlySavings={monthlySavings}
              onMonthlySavingsChange={setMonthlySavings}
              annualSavingsIncreaseRate={annualSavingsIncreaseRate}
              onSavingsIncreaseRateChange={setAnnualSavingsIncreaseRate}
              currentAge={currentAge}
              onCurrentAgeChange={setCurrentAge}
              targetRetirementAge={targetRetirementAge}
              onTargetRetirementAgeChange={setTargetRetirementAge}
              lifeExpectancy={lifeExpectancy}
              onLifeExpectancyChange={setLifeExpectancy}
              lang={lang}
            />

            {/* 2. Safe Withdrawal Rate (SWR) */}
            <SafeWithdrawalRateControl
              safeWithdrawalRate={safeWithdrawalRate}
              onChange={setSafeWithdrawalRate}
              lang={lang}
            />

            {/* 3. Country & Tax Legislation Selector */}
            <CountryTaxSelector
              taxSettings={taxSettings}
              onChange={setTaxSettings}
              currentYear={currentYear}
              lang={lang}
            />

            {/* 4. Macroeconomic Scenario */}
            <MacroScenarioSelector
              scenario={scenario}
              onChange={setScenario}
              lang={lang}
            />
          </div>

          {/* Right Column: Visualizations, Breakdown & Comparisons */}
          <div className="lg:col-span-7 space-y-6">
            {/* Navigation Tabs for Right Column */}
            <div className="flex items-center justify-between bg-slate-900/90 border border-slate-800 p-1.5 rounded-2xl">
              <button
                type="button"
                onClick={() => setActiveAnalysisTab('chart')}
                className={`flex-1 py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer ${
                  activeAnalysisTab === 'chart'
                    ? 'bg-slate-800 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {t.tabChart}
              </button>
              <button
                type="button"
                onClick={() => setActiveAnalysisTab('country_compare')}
                className={`flex-1 py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer ${
                  activeAnalysisTab === 'country_compare'
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {t.tabComparison}
              </button>
              <button
                type="button"
                onClick={() => setActiveAnalysisTab('table')}
                className={`flex-1 py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer ${
                  activeAnalysisTab === 'table'
                    ? 'bg-slate-800 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {t.tabTable}
              </button>
            </div>

            {/* Active Content based on Tab */}
            {activeAnalysisTab === 'chart' && (
              <div className="space-y-6">
                <FireChart
                  projections={result.projections}
                  fireNumberNominal={result.fireNumberNominal}
                  retirementAge={result.ageAtFire}
                  lang={lang}
                />
                <TaxBreakdownCard result={result} taxSettings={taxSettings} lang={lang} />
              </div>
            )}

            {activeAnalysisTab === 'country_compare' && (
              <div className="space-y-6">
                <CountryComparisonView
                  currentInputs={fireInputs}
                  onApplyCountry={handleApplyCountryFromComparison}
                  lang={lang}
                />
                <TaxBreakdownCard result={result} taxSettings={taxSettings} lang={lang} />
              </div>
            )}

            {activeAnalysisTab === 'table' && (
              <YearlyProjectionTable projections={result.projections} lang={lang} />
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 space-y-1">
          <p className="flex items-center justify-center gap-1.5 font-medium text-slate-400">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-500" />
            {t.footerTitle}
          </p>
          <p className="text-[11px] text-slate-600">
            {t.footerDisclaimer}
          </p>
        </div>
      </footer>
    </div>
  );
}
