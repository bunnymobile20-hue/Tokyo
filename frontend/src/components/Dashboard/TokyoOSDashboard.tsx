import { useEffect, useState } from 'react';

export function TokyoOSDashboard() {
  const [financeStatus, setFinanceStatus] = useState<any>(null);
  const [stockStatus, setStockStatus] = useState<any>(null);
  const [executiveStatus, setExecutiveStatus] = useState<any>(null);
  const [siberianStatus, setSiberianStatus] = useState<any>(null);

  useEffect(() => {
    fetch('/tokyo/dashboard/finance/status').then(r => r.json()).then(setFinanceStatus).catch(() => {});
    fetch('/tokyo/dashboard/stock/status').then(r => r.json()).then(setStockStatus).catch(() => {});
    fetch('/tokyo/dashboard/executive/status').then(r => r.json()).then(setExecutiveStatus).catch(() => {});
    fetch('/tokyo/siberian/status').then(r => r.json()).then(setSiberianStatus).catch(() => {});
  }, []);

  return (
    <div className="flex flex-col gap-4 mb-4">
      {/* BADGES E HEADER TOKYOOS */}
      <div className="flex items-center gap-2 flex-wrap mb-2">
        <span className="px-2 py-1 text-xs rounded-md bg-blue-500/20 text-blue-400 border border-blue-500/30">native_tokyo</span>
        <span className="px-2 py-1 text-xs rounded-md bg-purple-500/20 text-purple-400 border border-purple-500/30">openjarvis_core</span>
        <span className="px-2 py-1 text-xs rounded-md bg-green-500/20 text-green-400 border border-green-500/30">bridged</span>
        <span className="px-2 py-1 text-xs rounded-md bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">read_only</span>
        <span className="px-2 py-1 text-xs rounded-md bg-red-500/20 text-red-400 border border-red-500/30">write_enabled=false</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* SIBERIAN READ ONLY E DATA QUALITY */}
        <div className="p-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-bg-secondary)] flex flex-col gap-2">
          <h2 className="text-sm font-semibold flex items-center justify-between text-[var(--color-text)]">
            Siberian Data Quality
            <span className="px-2 py-0.5 text-[10px] rounded bg-red-500/20 text-red-400 uppercase">blocked</span>
          </h2>
          <div className="text-xs text-[var(--color-text-secondary)]">Status: Aguardando Siberian real</div>
          <div className="text-xs text-[var(--color-text-secondary)]">Fonte: Não configurada</div>
          <div className="text-xs text-[var(--color-text-secondary)]">Seguro para exibir: Não</div>
          <div className="text-xs text-[var(--color-text-secondary)]">Escrita no ERP: Bloqueada</div>
          
          <div className="mt-2 flex gap-2 flex-wrap">
            <span className="px-2 py-1 text-[10px] bg-red-900/40 text-red-400 border border-red-500/50 rounded">SIBERIAN_NOT_CONFIGURED</span>
            <span className="px-2 py-1 text-[10px] bg-orange-900/40 text-orange-400 border border-orange-500/50 rounded">MOCK DATA ACTIVE</span>
            <span className="px-2 py-1 text-[10px] bg-red-900/40 text-red-400 border border-red-500/50 rounded">DATA_SOURCE_NOT_REAL</span>
          </div>
        </div>

        {/* DASHBOARD FINANCEIRO E DRE */}
        <div className="p-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-bg-secondary)] flex flex-col gap-2">
          <h2 className="text-sm font-semibold flex items-center justify-between text-[var(--color-text)]">
            Dashboard Financeiro & DRE
            <span className="px-2 py-0.5 text-[10px] rounded bg-red-500/20 text-red-400 uppercase">safe_to_display=false</span>
          </h2>
          <p className="text-xs text-[var(--color-text-secondary)] mt-1">
            Nenhum número real será exibido sem <code>data_status=real_data</code>.
          </p>
          <div className="text-xs text-[var(--color-text-secondary)] mt-2">
            Status Engine: {financeStatus?.status || 'Aguardando credenciais...'}
          </div>
          <div className="mt-auto pt-2 flex gap-2 flex-wrap">
            <span className="px-2 py-1 text-[10px] bg-yellow-900/40 text-yellow-400 border border-yellow-500/50 rounded">awaiting_real_credentials</span>
          </div>
        </div>
      </div>
    </div>
  );
}
