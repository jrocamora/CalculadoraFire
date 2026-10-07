import React, { useState } from 'react';
import { YearProjection } from '../types/fire';
import { Table, Download, ChevronLeft, ChevronRight } from 'lucide-react';
import { Language, TRANSLATIONS } from '../i18n/translations';

interface YearlyProjectionTableProps {
  projections: YearProjection[];
  lang: Language;
}

export const YearlyProjectionTable: React.FC<YearlyProjectionTableProps> = ({ projections, lang }) => {
  const t = TRANSLATIONS[lang];
  const isEn = lang === 'en';
  const locale = isEn ? 'en-US' : 'ca-ES';
  const [filterPhase, setFilterPhase] = useState<'all' | 'accumulation' | 'retirement'>('all');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pageSize = 12;

  const filtered = projections.filter((p) => {
    if (filterPhase === 'accumulation') return !p.isRetired;
    if (filterPhase === 'retirement') return p.isRetired;
    return true;
  });

  const totalPages = Math.ceil(filtered.length / pageSize) || 1;
  const paginatedData = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const handleExportCSV = () => {
    const headers = isEn
      ? [
          'Year',
          'Age',
          'Phase',
          'Starting Wealth (€)',
          'Market Return (€)',
          'Deposit (€)',
          'Gross Withdrawal (€)',
          'Taxes (€)',
          'Net Disposable (€)',
          'Ending Wealth (€)',
          'Real Wealth Adjusted (€)',
          'Notes',
        ]
      : [
          'Any',
          'Edat',
          'Fase',
          'Patrimoni Inicial (€)',
          'Rendiment Mercat (€)',
          'Aportacio (€)',
          'Retirada Bruta (€)',
          'Impostos (€)',
          'Net Disponible (€)',
          'Patrimoni Final (€)',
          'Patrimoni Real Ajustat (€)',
          'Notes',
        ];

    const rows = projections.map((p) => [
      p.calendarYear,
      p.age,
      p.isRetired ? (isEn ? 'Retirement (FIRE)' : 'Retirada (FIRE)') : (isEn ? 'Accumulation' : 'Acumulacio'),
      Math.round(p.startingPortfolio),
      Math.round(p.startingPortfolio * p.grossReturn),
      Math.round(p.contribution),
      Math.round(p.grossWithdrawal),
      Math.round(p.taxPaid),
      Math.round(p.netDisposableIncome),
      Math.round(p.endingPortfolio),
      Math.round(p.endingPortfolioReal),
      `"${p.taxNotes || ''}"`,
    ]);

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `fire_projection_${new Date().getFullYear()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-sm space-y-4">
      {/* Table Header & Controls */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-slate-800 text-slate-300">
            <Table className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              {t.tableTitle}
            </h3>
            <p className="text-xs text-slate-400">
              {t.tableSubtitle}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Phase Filter */}
          <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              type="button"
              onClick={() => {
                setFilterPhase('all');
                setCurrentPage(1);
              }}
              className={`px-2.5 py-1 rounded-lg font-medium cursor-pointer ${
                filterPhase === 'all' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {t.tableFilterAll}
            </button>
            <button
              type="button"
              onClick={() => {
                setFilterPhase('accumulation');
                setCurrentPage(1);
              }}
              className={`px-2.5 py-1 rounded-lg font-medium cursor-pointer ${
                filterPhase === 'accumulation' ? 'bg-emerald-600/30 text-emerald-300' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {t.tableFilterAccumulation}
            </button>
            <button
              type="button"
              onClick={() => {
                setFilterPhase('retirement');
                setCurrentPage(1);
              }}
              className={`px-2.5 py-1 rounded-lg font-medium cursor-pointer ${
                filterPhase === 'retirement' ? 'bg-amber-600/30 text-amber-300' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {t.tableFilterRetirement}
            </button>
          </div>

          {/* CSV Export */}
          <button
            type="button"
            onClick={handleExportCSV}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">{t.tableExportCsv}</span>
          </button>
        </div>
      </div>

      {/* Table Container */}
      <div className="overflow-x-auto rounded-xl border border-slate-800">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px] font-semibold border-b border-slate-800">
            <tr>
              <th className="px-3.5 py-3">{t.tableColYearAge}</th>
              <th className="px-3.5 py-3">{t.tableColPhase}</th>
              <th className="px-3.5 py-3 text-right">{t.tableColInitialCapital}</th>
              <th className="px-3.5 py-3 text-right">{t.tableColContributionWithdrawal}</th>
              <th className="px-3.5 py-3 text-right">{t.tableColTaxes}</th>
              <th className="px-3.5 py-3 text-right">{t.tableColNetDisposable}</th>
              <th className="px-3.5 py-3 text-right">{t.tableColEndingCapital}</th>
              <th className="px-3.5 py-3 text-right">{t.tableColRealCapital}</th>
              <th className="px-3.5 py-3">{t.tableColNotes}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {paginatedData.map((row) => (
              <tr
                key={row.yearIndex}
                className={`transition-colors hover:bg-slate-800/40 ${
                  row.taxNotes ? 'bg-amber-500/5' : ''
                }`}
              >
                <td className="px-3.5 py-2.5 font-bold text-white whitespace-nowrap font-sans">
                  {row.calendarYear} <span className="text-slate-500 font-normal">({row.age} {t.years})</span>
                </td>
                <td className="px-3.5 py-2.5 whitespace-nowrap font-sans">
                  <span
                    className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                      row.isRetired
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    }`}
                  >
                    {row.isRetired ? t.tableFireBadge : t.tableSavingsBadge}
                  </span>
                </td>
                <td className="px-3.5 py-2.5 text-right text-slate-300">
                  {Math.round(row.startingPortfolio).toLocaleString(locale)} €
                </td>
                <td className="px-3.5 py-2.5 text-right">
                  {!row.isRetired ? (
                    <span className="text-emerald-400 font-semibold">
                      +{Math.round(row.contribution).toLocaleString(locale)} €
                    </span>
                  ) : (
                    <span className="text-orange-400 font-semibold">
                      -{Math.round(row.grossWithdrawal).toLocaleString(locale)} €
                    </span>
                  )}
                </td>
                <td className="px-3.5 py-2.5 text-right text-rose-400">
                  {row.taxPaid > 0 ? `-${Math.round(row.taxPaid).toLocaleString(locale)} €` : '0 €'}
                </td>
                <td className="px-3.5 py-2.5 text-right font-bold text-slate-100">
                  {row.isRetired ? (
                    `${Math.round(row.netDisposableIncome).toLocaleString(locale)} €`
                  ) : (
                    <span className="text-slate-500">-</span>
                  )}
                </td>
                <td className="px-3.5 py-2.5 text-right font-bold text-emerald-400">
                  {Math.round(row.endingPortfolio).toLocaleString(locale)} €
                </td>
                <td className="px-3.5 py-2.5 text-right text-cyan-400">
                  {Math.round(row.endingPortfolioReal).toLocaleString(locale)} €
                </td>
                <td className="px-3.5 py-2.5 text-[11px] text-amber-300 font-sans whitespace-nowrap">
                  {row.taxNotes || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between text-xs text-slate-400 pt-2">
        <span>
          {t.tableShowingPage} <strong>{currentPage}</strong> {t.tableOf} <strong>{totalPages}</strong> ({filtered.length} {t.tableYearsCount})
        </span>
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={currentPage <= 1}
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            className="p-1.5 rounded-lg border border-slate-800 bg-slate-950 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            type="button"
            disabled={currentPage >= totalPages}
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            className="p-1.5 rounded-lg border border-slate-800 bg-slate-950 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 cursor-pointer"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
