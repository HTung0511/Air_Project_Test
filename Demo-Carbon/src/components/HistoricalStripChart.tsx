import React from 'react';
import { Activity, Info } from 'lucide-react';
import {
  PredictionRecord,
  addDaysISO,
  getDailyContext,
  getAqiBucket,
  formatShortDateVN,
  formatDateVN,
  vnNum,
} from '../data/aqiHelpers';

interface HistoricalStripChartProps {
  selectedCity: string;
  dateInput: string;
  dateTarget: string;
  record: PredictionRecord | null;
  isRevealed: boolean;
  thresholdL3: number;
}

export const HistoricalStripChart: React.FC<HistoricalStripChartProps> = ({
  selectedCity,
  dateInput,
  dateTarget,
  record,
  isRevealed,
  thresholdL3,
}) => {
  // Chuỗi 7 ngày lịch thực tế đến hết ngày đầu vào t: t-6, t-5, t-4, t-3, t-2, t-1, t
  const historyDays = [-6, -5, -4, -3, -2, -1, 0].map((offset) => {
    const dt = addDaysISO(dateInput, offset);
    const ctx = getDailyContext(selectedCity, dt);
    return {
      offset,
      date: dt,
      label: offset === 0 ? 'Hôm nay (t)' : `t${offset}`,
      aqi: ctx?.aqi ?? null,
      wasMissing: ctx?.miss ?? (ctx?.aqi === null),
      suspect: ctx?.susp ?? false,
    };
  });

  const ctxT1 = getDailyContext(selectedCity, dateTarget);
  const actualT1 = record ? record.y : ctxT1?.aqi ?? null;
  const predL3 = record ? record.l3 : null;

  // Tìm đỉnh để chuẩn hóa chiều cao cột (tối thiểu 300 để ngưỡng 201 và 166 luôn nhìn rõ đúng tỷ lệ)
  const allVals = [
    ...historyDays.map((d) => d.aqi ?? 0),
    predL3 ?? 0,
    isRevealed && actualT1 !== null ? actualT1 : 0,
    300,
  ];
  const maxChartAqi = Math.max(...allVals, 300);

  const heightPct = (val: number | null) => {
    if (val === null || val <= 0) return 0;
    return Math.min(100, Math.max(6, (val / maxChartAqi) * 100));
  };

  const line201Pct = (201 / maxChartAqi) * 100;
  const lineThrPct = (thresholdL3 / maxChartAqi) * 100;

  return (
    <section
      aria-label="Dải lịch sử AQI thực tế đến ngày t và vùng đối chiếu t+1"
      className="bg-white rounded-xl border border-slate-200 shadow-xs p-3.5"
    >
      <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5">
        <div className="flex items-center gap-1.5">
          <Activity className="w-4 h-4 text-slate-700" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
            Diễn biến AQI Lịch thực 7 ngày đến <code className="font-mono">t ({formatDateVN(dateInput)})</code> &amp; Vùng Đích <code className="font-mono">t+1 ({formatDateVN(dateTarget)})</code>
          </h3>
        </div>
        <div className="flex items-center gap-3 text-[11px] text-slate-600">
          <span className="inline-flex items-center gap-1">
            <span className="w-3 h-0.5 bg-rose-600 inline-block" />
            <span>Mốc thực tế nặng ≥ 201</span>
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="w-3 h-0.5 bg-indigo-600 border-b border-dashed border-indigo-600 inline-block" />
            <span>Ngưỡng dự báo L3 ≥ {thresholdL3}</span>
          </span>
        </div>
      </div>

      {/* Khu vực vẽ cột chuỗi lịch thực t-6 .. t và ô t+1 */}
      <div className="relative h-36 pt-5 pb-2 px-2 bg-slate-50/80 rounded-lg border border-slate-200/80 flex items-end gap-2">
        {/* Đường ngang mốc ngày nặng 201 */}
        <div
          style={{ bottom: `calc(${line201Pct}% + 8px)` }}
          className="pointer-events-none absolute inset-x-2 border-t border-rose-500/80 z-10"
        >
          <span className="absolute right-1 -top-3.5 text-[9px] font-mono font-bold text-rose-700 bg-rose-50/90 px-1 rounded">
            AQI = 201
          </span>
        </div>

        {/* Đường ngang ngưỡng vận hành L3 (nếu khác 201) */}
        {thresholdL3 !== 201 && (
          <div
            style={{ bottom: `calc(${lineThrPct}% + 8px)` }}
            className="pointer-events-none absolute inset-x-2 border-t border-dashed border-indigo-500/70 z-10"
          >
            <span className="absolute left-1 -top-3.5 text-[9px] font-mono font-semibold text-indigo-700 bg-indigo-50/90 px-1 rounded">
              Ngưỡng L3 = {thresholdL3}
            </span>
          </div>
        )}

        {/* 7 Cột lịch sử thực tế từ t-6 đến t */}
        {historyDays.map((item) => {
          const bucket = getAqiBucket(item.aqi);
          const isToday = item.offset === 0;
          return (
            <div
              key={item.date}
              className={`flex-1 h-full flex flex-col justify-end items-center relative z-20 ${
                isToday ? 'bg-slate-200/50 rounded-md px-0.5' : ''
              }`}
            >
              {item.aqi !== null ? (
                <>
                  <span
                    className={`text-[10px] font-mono mb-0.5 ${
                      isToday ? 'font-extrabold text-slate-950' : 'font-semibold text-slate-700'
                    }`}
                  >
                    {vnNum(item.aqi, 0)}
                  </span>
                  <div
                    style={{
                      height: `${heightPct(item.aqi)}%`,
                      backgroundColor: bucket?.hex ?? '#64748b',
                    }}
                    className={`w-full max-w-[34px] rounded-t transition-all ${
                      isToday ? 'ring-2 ring-slate-900' : 'opacity-90'
                    }`}
                    title={`${selectedCity} ngày ${formatDateVN(item.date)}: AQI = ${item.aqi} (${bucket?.labelVN})`}
                  />
                </>
              ) : (
                /* Khoảng trống thật khi khuyết AQI — Không nội suy AQI */
                <div
                  className="w-full max-w-[34px] h-4/5 rounded-t border-2 border-dashed border-rose-400 bg-rose-50/50 flex flex-col items-center justify-center p-0.5 text-center"
                  title={`Ngày ${formatDateVN(item.date)}: Khuyết AQI quan trắc (Dự án không nội suy AQI)`}
                >
                  <span className="text-[9px] font-bold text-rose-800 leading-tight">Khuyết AQI</span>
                </div>
              )}

              <div className="mt-1 text-center leading-tight">
                <div className={`text-[10px] font-mono ${isToday ? 'font-extrabold text-slate-900' : 'text-slate-600'}`}>
                  {formatShortDateVN(item.date)}
                </div>
                <div className={`text-[9px] ${isToday ? 'font-bold text-slate-900' : 'text-slate-400'}`}>
                  {item.label}
                </div>
              </div>
            </div>
          );
        })}

        {/* Vách ngăn Thời điểm dự báo t -> t+1 */}
        <div className="h-full border-l-2 border-dashed border-slate-400 mx-0.5 self-stretch" />

        {/* Ô thứ 8: Ngày đích t+1 (Gồm cột Dự báo L3 và cột Thực tế t+1 mở sau) */}
        <div className="flex-[1.45] h-full flex flex-col justify-end items-center bg-indigo-50/50 rounded-md px-1.5 border border-indigo-200/80 relative z-20">
          <div className="w-full h-full flex items-end justify-center gap-2">
            {/* Cột Dự báo Ridge L3 */}
            <div className="flex-1 h-full flex flex-col justify-end items-center">
              {predL3 !== null ? (
                <>
                  <span className="text-[10px] font-mono font-extrabold text-indigo-900 mb-0.5">
                    {vnNum(predL3, 0)}
                  </span>
                  <div
                    style={{ height: `${heightPct(predL3)}%` }}
                    className="w-full max-w-[28px] rounded-t bg-indigo-700 border border-indigo-950"
                    title={`Dự báo Ridge L3 ngày t+1 (${formatDateVN(dateTarget)}): ${predL3.toFixed(6)}`}
                  />
                </>
              ) : (
                <div className="w-full max-w-[28px] h-3/5 rounded-t border border-dashed border-slate-400 flex items-center justify-center">
                  <span className="text-[8px] text-slate-500">Thiếu</span>
                </div>
              )}
            </div>

            {/* Cột Thực tế t+1 (Ẩn trước khi đối chiếu, hiện sau khi bấm Mở thực tế) */}
            <div className="flex-1 h-full flex flex-col justify-end items-center">
              {!isRevealed ? (
                <div
                  className="w-full max-w-[28px] h-3/4 rounded-t border-2 border-dashed border-slate-400 bg-slate-200/60 flex items-center justify-center"
                  title="Thực tế t+1 đang ẩn"
                >
                  <span className="text-[9px] font-bold text-slate-600">Ẩn</span>
                </div>
              ) : actualT1 !== null ? (
                <>
                  <span className="text-[10px] font-mono font-extrabold text-slate-900 mb-0.5">
                    {vnNum(actualT1, 0)}
                  </span>
                  <div
                    style={{
                      height: `${heightPct(actualT1)}%`,
                      backgroundColor: getAqiBucket(actualT1)?.hex ?? '#0f172a',
                    }}
                    className="w-full max-w-[28px] rounded-t ring-2 ring-slate-900"
                    title={`Thực tế AQI(t+1) ngày ${formatDateVN(dateTarget)}: ${actualT1}`}
                  />
                </>
              ) : (
                <div className="w-full max-w-[28px] h-3/4 rounded-t border-2 border-dashed border-rose-400 bg-rose-50 flex items-center justify-center">
                  <span className="text-[8px] font-bold text-rose-700">Khuyết</span>
                </div>
              )}
            </div>
          </div>

          <div className="mt-1 text-center leading-tight w-full">
            <div className="text-[10px] font-mono font-extrabold text-indigo-950">
              {formatShortDateVN(dateTarget)} (Đích t+1)
            </div>
            <div className="text-[9px] font-semibold text-indigo-800 flex justify-around">
              <span>Dự báo</span>
              <span>{isRevealed ? 'Thực tế' : 'Đang ẩn'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Ghi chú trung thực về chuỗi 7 ngày vs 4 biến trễ và không nội suy AQI */}
      <div className="mt-2 flex items-start gap-1.5 text-[11px] text-slate-500">
        <Info className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
        <span>
          <strong>Lưu ý dữ liệu (Y05/Y44):</strong> Dải trên hiển thị chuỗi AQI quan trắc lịch thực từng ngày từ <code className="font-mono">air_quality_8cities_weather.csv</code>; dự án <strong>không nội suy AQI</strong> nên ngày khuyết (như tại Amritsar) được giữ nguyên khoảng trống thật. Không đồng nhất dải 7 ngày này với 4 đặc trưng trễ của mô hình (<code className="font-mono">aqi_0</code> hôm nay, <code className="font-mono">aqi_1</code> hôm qua, <code className="font-mono">aqi_2</code> hôm kia và <code className="font-mono">aqi_wk</code> log trung bình 7 ngày trước t).
        </span>
      </div>
    </section>
  );
};
