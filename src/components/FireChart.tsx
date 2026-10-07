import React, { useState, useId } from 'react';
import { YearProjection } from '../types/fire';
import { TrendingUp, Eye, Flame } from 'lucide-react';
import { Language, TRANSLATIONS } from '../i18n/translations';

interface FireChartProps {
  projections: YearProjection[];
  fireNumberNominal: number;
  retirementAge: number;
  lang: Language;
}

export const FireChart: React.FC<FireChartProps> = ({
  projections,
  fireNumberNominal,
  retirementAge,
  lang,
}) => {
  const t = TRANSLATIONS[lang];
  const locale = lang === 'en' ? 'en-US' : 'ca-ES';
  const gradientId = useId();
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [showRealCurve, setShowRealCurve] = useState<boolean>(true);

  if (!projections || projections.length === 0) {
    return null;
  }

  // SVG dimensions
  const width = 800;
  const height = 360;
  const padding = { top: 30, right: 30, bottom: 50, left: 75 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Maximum scales
  const maxPortfolio = Math.max(
    fireNumberNominal * 1.25,
    ...projections.map((p) => p.endingPortfolio),
    ...projections.map((p) => (showRealCurve ? p.endingPortfolioReal : 0)),
    100000
  );

  const totalPoints = projections.length;

  const getX = (index: number) => padding.left + (index / (totalPoints - 1 || 1)) * chartWidth;
  const getY = (val: number) => padding.top + chartHeight - (Math.max(0, val) / maxPortfolio) * chartHeight;

  // Nominal points and area
  const pointsNominal = projections.map((p, i) => `${getX(i)},${getY(p.endingPortfolio)}`).join(' ');
  const areaNominal = `${getX(0)},${getY(0)} ${pointsNominal} ${getX(totalPoints - 1)},${getY(0)}`;

  // Real curve
  const pointsReal = projections.map((p, i) => `${getX(i)},${getY(p.endingPortfolioReal)}`).join(' ');

  // Retirement index
  const retirementIndex = projections.findIndex((p) => p.age === retirementAge);
  const retirementX = retirementIndex !== -1 ? getX(retirementIndex) : null;

  // Fire number line
  const fireNumberY = getY(fireNumberNominal);

  // Y ticks
  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((ratio) => {
    const val = maxPortfolio * ratio;
    return {
      value: val,
      y: getY(val),
    };
  });

  // X ticks
  const step = Math.max(1, Math.floor(totalPoints / 7));
  const xTicks = projections
    .map((p, i) => ({ ...p, index: i }))
    .filter((_, i) => i % step === 0 || i === totalPoints - 1);

  const hoveredData = hoveredIndex !== null ? projections[hoveredIndex] : null;

  const formatCurrency = (val: number) => {
    if (val >= 1000000) return `${(val / 1000000).toFixed(2)} M€`;
    if (val >= 1000) return `${Math.round(val / 1000)} k€`;
    return `${Math.round(val)} €`;
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-sm space-y-4">
      {/* Chart Header */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pb-2 border-b border-slate-800">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            {t.chartTitle}
          </h3>
          <p className="text-xs text-slate-400">
            {t.chartSubtitle}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setShowRealCurve(!showRealCurve)}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all cursor-pointer ${
              showRealCurve
                ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-300'
                : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>{t.chartRealPurchasingPower}</span>
          </button>
        </div>
      </div>

      {/* Legend & Key Indicators */}
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400 px-1">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50"></span>
            <span className="text-slate-300 font-medium">{t.chartNominalLegend}</span>
          </div>
          {showRealCurve && (
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 border-t-2 border-dashed border-cyan-400"></span>
              <span className="text-cyan-300 font-medium">{t.chartRealLegend}</span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 border-t-2 border-dotted border-orange-400"></span>
            <span className="text-orange-400 font-medium">{t.chartFireTargetLegend} ({formatCurrency(fireNumberNominal)})</span>
          </div>
        </div>

        {retirementX !== null && (
          <div className="flex items-center gap-1 text-[11px] text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 font-medium">
            <Flame className="w-3 h-3 text-amber-400" />
            <span>{t.chartRetirementAt} {retirementAge} {t.chartYearsOld}</span>
          </div>
        )}
      </div>

      {/* Responsive SVG Chart */}
      <div className="relative w-full overflow-hidden">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto select-none"
          onMouseLeave={() => setHoveredIndex(null)}
        >
          <defs>
            <linearGradient id={`grad-nominal-${gradientId}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.35" />
              <stop offset="70%" stopColor="#059669" stopOpacity="0.08" />
              <stop offset="100%" stopColor="#047857" stopOpacity="0.0" />
            </linearGradient>

            <linearGradient id={`grad-real-${gradientId}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#0891b2" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Background Grid Lines (Horizontal) */}
          {yTicks.map((tItem, idx) => (
            <g key={idx}>
              <line
                x1={padding.left}
                y1={tItem.y}
                x2={width - padding.right}
                y2={tItem.y}
                stroke="#334155"
                strokeWidth="0.8"
                strokeDasharray="3 3"
                opacity="0.4"
              />
              <text
                x={padding.left - 10}
                y={tItem.y + 4}
                fill="#94a3b8"
                fontSize="10"
                textAnchor="end"
                fontFamily="JetBrains Mono, monospace"
              >
                {formatCurrency(tItem.value)}
              </text>
            </g>
          ))}

          {/* Retirement Phase Shading */}
          {retirementX !== null && (
            <rect
              x={retirementX}
              y={padding.top}
              width={width - padding.right - retirementX}
              height={chartHeight}
              fill="#f59e0b"
              fillOpacity="0.04"
            />
          )}

          {/* Target FIRE Reference Line */}
          {fireNumberY >= padding.top && fireNumberY <= height - padding.bottom && (
            <g>
              <line
                x1={padding.left}
                y1={fireNumberY}
                x2={width - padding.right}
                y2={fireNumberY}
                stroke="#f97316"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                opacity="0.8"
              />
              <text
                x={width - padding.right - 8}
                y={fireNumberY - 6}
                fill="#fb923c"
                fontSize="10"
                fontWeight="700"
                textAnchor="end"
              >
                {t.chartFireTargetLegend}: {formatCurrency(fireNumberNominal)}
              </text>
            </g>
          )}

          {/* Nominal Area & Curve */}
          <polygon points={areaNominal} fill={`url(#grad-nominal-${gradientId})`} />
          <polyline
            points={pointsNominal}
            fill="none"
            stroke="#10b981"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Real Curve */}
          {showRealCurve && (
            <polyline
              points={pointsReal}
              fill="none"
              stroke="#22d3ee"
              strokeWidth="2"
              strokeDasharray="4 3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}

          {/* Retirement Vertical Line Marker */}
          {retirementX !== null && (
            <g>
              <line
                x1={retirementX}
                y1={padding.top}
                x2={retirementX}
                y2={height - padding.bottom}
                stroke="#f59e0b"
                strokeWidth="1.8"
                strokeDasharray="3 3"
                opacity="0.9"
              />
              <circle cx={retirementX} cy={getY(projections[retirementIndex]?.endingPortfolio || 0)} r="5" fill="#f59e0b" />
            </g>
          )}

          {/* X Axis Labels */}
          {xTicks.map((tick, idx) => {
            const x = getX(tick.index);
            return (
              <g key={idx}>
                <line
                  x1={x}
                  y1={height - padding.bottom}
                  x2={x}
                  y2={height - padding.bottom + 5}
                  stroke="#475569"
                />
                <text
                  x={x}
                  y={height - padding.bottom + 18}
                  fill="#94a3b8"
                  fontSize="10"
                  textAnchor="middle"
                  fontWeight="600"
                >
                  {tick.age} {t.chartYearsOld}
                </text>
                <text
                  x={x}
                  y={height - padding.bottom + 30}
                  fill="#64748b"
                  fontSize="9"
                  textAnchor="middle"
                >
                  {tick.calendarYear}
                </text>
              </g>
            );
          })}

          {/* Interactive Mouse Hover Overlay Columns */}
          {projections.map((p, i) => {
            const x = getX(i);
            const colWidth = chartWidth / totalPoints;
            return (
              <rect
                key={i}
                x={x - colWidth / 2}
                y={padding.top}
                width={colWidth}
                height={chartHeight}
                fill="transparent"
                className="cursor-pointer"
                onMouseEnter={() => setHoveredIndex(i)}
              />
            );
          })}

          {/* Hover Crosshair & Dot Indicator */}
          {hoveredIndex !== null && hoveredData && (
            <g>
              <line
                x1={getX(hoveredIndex)}
                y1={padding.top}
                x2={getX(hoveredIndex)}
                y2={height - padding.bottom}
                stroke="#e2e8f0"
                strokeWidth="1"
                strokeDasharray="2 2"
                opacity="0.7"
              />
              <circle
                cx={getX(hoveredIndex)}
                cy={getY(hoveredData.endingPortfolio)}
                r="6"
                fill="#10b981"
                stroke="#ffffff"
                strokeWidth="2"
              />
              {showRealCurve && (
                <circle
                  cx={getX(hoveredIndex)}
                  cy={getY(hoveredData.endingPortfolioReal)}
                  r="5"
                  fill="#22d3ee"
                  stroke="#ffffff"
                  strokeWidth="1.5"
                />
              )}
            </g>
          )}
        </svg>

        {/* Floating Tooltip Box */}
        {hoveredData && hoveredIndex !== null && (
          <div
            className="absolute top-2 right-4 pointer-events-none bg-slate-950/95 border border-slate-700/80 rounded-xl p-3 shadow-2xl backdrop-blur-md text-xs space-y-1.5 z-20 min-w-56"
          >
            <div className="flex items-center justify-between pb-1.5 border-b border-slate-800">
              <span className="font-bold text-white text-sm">
                {hoveredData.age} {t.chartYearsOld} ({hoveredData.calendarYear})
              </span>
              <span
                className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                  hoveredData.isRetired
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                }`}
              >
                {hoveredData.isRetired ? t.chartPhaseRetirement : t.chartPhaseAccumulation}
              </span>
            </div>

            <div className="space-y-1 pt-0.5">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">{t.chartNominalNetWorth}</span>
                <span className="font-bold font-mono text-emerald-400">
                  {Math.round(hoveredData.endingPortfolio).toLocaleString(locale)} €
                </span>
              </div>

              {showRealCurve && (
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">{t.chartRealNetWorth}</span>
                  <span className="font-bold font-mono text-cyan-400">
                    {Math.round(hoveredData.endingPortfolioReal).toLocaleString(locale)} €
                  </span>
                </div>
              )}

              {!hoveredData.isRetired ? (
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">{t.chartContributionYear}</span>
                  <span className="font-mono text-slate-200">
                    +{Math.round(hoveredData.contribution).toLocaleString(locale)} €
                  </span>
                </div>
              ) : (
                <>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">{t.chartGrossWithdrawal}</span>
                    <span className="font-mono text-orange-400">
                      -{Math.round(hoveredData.grossWithdrawal).toLocaleString(locale)} €
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">{t.chartEstimatedTax}</span>
                    <span className="font-mono text-rose-400">
                      -{Math.round(hoveredData.taxPaid).toLocaleString(locale)} €
                    </span>
                  </div>
                  <div className="flex justify-between items-center pt-1 border-t border-slate-800 font-bold">
                    <span className="text-slate-300">{t.chartNetDisposable}</span>
                    <span className="font-mono text-emerald-400">
                      {Math.round(hoveredData.netDisposableIncome).toLocaleString(locale)} €
                    </span>
                  </div>
                </>
              )}

              {hoveredData.taxNotes && (
                <div className="pt-1.5 text-[10px] text-amber-300 font-medium">
                  {hoveredData.taxNotes}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
