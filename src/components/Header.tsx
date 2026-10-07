import React from 'react';
import { Flame, RotateCcw, Languages } from 'lucide-react';
import { CountryCode } from '../types/fire';
import { Language, TRANSLATIONS } from '../i18n/translations';

interface HeaderProps {
  currentCountry: CountryCode;
  onResetDefaults: () => void;
  lang: Language;
  onLangChange: (lang: Language) => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentCountry,
  onResetDefaults,
  lang,
  onLangChange,
}) => {
  const t = TRANSLATIONS[lang];

  const countryBadge = {
    CAT: { name: lang === 'en' ? 'Catalonia' : 'Catalunya', flag: '🏴󠁥󠁳󠁣󠁴󠁿', border: 'border-amber-500/30 text-amber-300 bg-amber-500/10' },
    IE: { name: lang === 'en' ? 'Ireland' : 'Irlanda', flag: '🇮🇪', border: 'border-emerald-500/30 text-emerald-300 bg-emerald-500/10' },
    AD: { name: 'Andorra', flag: '🇦🇩', border: 'border-blue-500/30 text-blue-300 bg-blue-500/10' },
  }[currentCountry] || { name: 'Catalunya', flag: '🏴󠁥󠁳󠁣󠁴󠁿', border: 'border-amber-500/30 text-amber-300 bg-amber-500/10' };

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-amber-500 via-orange-500 to-rose-600 flex items-center justify-center shadow-lg shadow-orange-500/20 text-white font-bold">
            <Flame className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-1.5">
                {t.appName} <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-amber-200">{t.appBadge}</span>
              </h1>
              <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                v1.2
              </span>
            </div>
            <p className="text-xs text-slate-400">
              {t.appSubtitle}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* Active Jurisdiction Badge */}
          <div className={`hidden md:flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border font-medium ${countryBadge.border}`}>
            <span>{countryBadge.flag}</span>
            <span>{t.activeTax} <strong>{countryBadge.name}</strong></span>
          </div>

          {/* Language Switcher Toggle */}
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-xl p-1 shadow-sm">
            <button
              type="button"
              onClick={() => onLangChange('ca')}
              className={`flex items-center gap-1 px-2.5 py-1 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                lang === 'ca'
                  ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Canviar idioma a Català"
            >
              <span>🏴󠁥󠁳󠁣󠁴󠁿</span>
              <span>CA</span>
            </button>
            <button
              type="button"
              onClick={() => onLangChange('en')}
              className={`flex items-center gap-1 px-2.5 py-1 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                lang === 'en'
                  ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Switch language to English"
            >
              <span>🇬🇧</span>
              <span>EN</span>
            </button>
          </div>

          {/* Reset Values Button */}
          <button
            onClick={onResetDefaults}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 bg-slate-900 hover:bg-slate-800 border border-slate-800 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
            title={t.resetValues}
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">{t.resetValues}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
