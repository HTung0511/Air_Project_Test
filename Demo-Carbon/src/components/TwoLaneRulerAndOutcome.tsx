import React from 'react';
import {
  Eye,
  EyeOff,
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  SlidersHorizontal,
  ArrowUpRight,
  HelpCircle,
} from 'lucide-react';
import {
  PredictionRecord,
  ThresholdMode,
  SplitType,
  DEMO_DATA,
  getThresholds,
  evaluateOutcome,
  getAqiBucket,
  getDailyContext,
  formatDateVN,
  formatAqiSmart,
  isNearThreshold,
  vnNum,
} from '../data/aqiHelpers';

interface TwoLaneRulerAndOutcomeProps {
  selectedCity: string;
  split: SplitType;
  dateInput: string;
  dateTarget: string;
  record: PredictionRecord | null;
  thresholdMode: ThresholdMode;
  onChangeThresholdMode: (mode: ThresholdMode) => void;
  isRevealed: boolean;
  onToggleReveal: () => void;
  autoReveal: boolean;
  onToggleAutoReveal: () => void;
  onOpenDetailLayer: (initialTab?: 'case' | 'pipeline' | 'tables' | 'audit') => void;
  onSelectDateTarget: (dt: string) => void;
}

/**
 * Quy đổi điểm AQI sang vị trí % trên thước hai làn:
 * - Từ 0 đến 500: chiếm 82% chiều dài thước (đúng tỷ lệ tuyến tính).
 * - Trên 500 (tới 660): nằm trong vùng vượt trục 18% bên phải (từ 82% đến 98%).
 */
function aqiToPercent(val: number): number {
  if (val <= 0) return 0;
  if (val <= 500) {
    return (val / 500) * 82;
  }
  const capped = Math.min(val, 660);
  return 82 + ((capped - 500) / 160) * 16;
}

export const TwoLaneRulerAndOutcome: React.FC<TwoLaneRulerAndOutcomeProps> = ({
  selectedCity,
  split,
  dateInput,
  dateTarget,
  record,
  thresholdMode,
  onChangeThresholdMode,
  isRevealed,
  onToggleReveal,
  autoReveal,
  onToggleAutoReveal,
  onOpenDetailLayer,
  onSelectDateTarget,
}) => {
  const thr = getThresholds(thresholdMode);
  const dailyT = getDailyContext(selectedCity, dateInput);
  const dailyT1 = getDailyContext(selectedCity, dateTarget);

  // Tìm ngày hợp lệ liền trước và liền sau nếu đang ở ngày thiếu dữ liệu
  const findNearestValidDates = () => {
    const cal = DEMO_DATA.calendar[split];
    const idx = cal.indexOf(dateTarget);
    let prevValid: string | null = null;
    let nextValid: string | null = null;
    for (let i = idx - 1; i >= 0; i--) {
      if (DEMO_DATA.records.some((r) => r.c === selectedCity && r.t1 === cal[i])) {
        prevValid = cal[i];
        break;
      }
    }
    for (let i = idx + 1; i < cal.length; i++) {
      if (DEMO_DATA.records.some((r) => r.c === selectedCity && r.t1 === cal[i])) {
        nextValid = cal[i];
        break;
      }
    }
    return { prevValid, nextValid };
  };

  // TRẠNG THÁI THIẾU BẢN GHI DỰ BÁO TRONG ARTIFACT PHÁT LẠI (Y26, Y29) — Không suy diễn nguyên nhân, vẫn tôn trọng giấu kết quả t+1
  if (!record) {
    const { prevValid, nextValid } = findNearestValidDates();
    const hasAqiT = dailyT && dailyT.aqi !== null;
    const hasAqiT1 = dailyT1 && dailyT1.aqi !== null;

    return (
      <section
        aria-label="Trạng thái thiếu bản ghi dự báo trong artifact phát lại"
        className="bg-white rounded-xl border-2 border-dashed border-rose-300 shadow-xs p-5"
      >
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-4 border-b border-rose-100">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-100 text-rose-800 flex items-center justify-center shrink-0 font-bold text-lg">
              ⊘
            </div>
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-900 border border-rose-300 mb-1">
                <span>Không có bản ghi dự báo trong artifact phát lại cho cặp ngày này.</span>
              </div>
              <h2 className="text-base font-bold text-slate-900">
                {selectedCity} · Ngày đầu vào <code className="font-mono">t={formatDateVN(dateInput)}</code> → Ngày đích <code className="font-mono">t+1={formatDateVN(dateTarget)}</code> ({split === 'test' ? 'Giai đoạn kiểm thử' : 'Holdout đánh giá bổ sung'})
              </h2>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={onToggleReveal}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                isRevealed
                  ? 'bg-slate-800 hover:bg-slate-700 text-white'
                  : 'bg-indigo-600 hover:bg-indigo-700 text-white'
              }`}
              title="Bật/tắt hiển thị dữ liệu ngày đích t+1 trong bảng hồi cứu"
            >
              {isRevealed ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              <span>{isRevealed ? 'Ẩn trạng thái t+1' : 'Mở thực tế & Đối chiếu (t+1)'}</span>
            </button>
            {prevValid && (
              <button
                type="button"
                onClick={() => onSelectDateTarget(prevValid)}
                className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold cursor-pointer"
              >
                ← Ngày có bản ghi trước ({formatDateVN(prevValid)})
              </button>
            )}
            {nextValid && (
              <button
                type="button"
                onClick={() => onSelectDateTarget(nextValid)}
                className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold cursor-pointer"
              >
                Ngày có bản ghi tiếp ({formatDateVN(nextValid)}) →
              </button>
            )}
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
            <div className="font-bold text-slate-800 mb-1.5">
              1. Trạng thái kiểm tra trực tiếp tại ngày đầu vào <code className="font-mono">t = {formatDateVN(dateInput)}</code>:
            </div>
            <ul className="text-slate-700 leading-relaxed space-y-1">
              <li>
                • Bản ghi dự báo trong <code className="font-mono">R2_B04_baseline_predictions.csv</code>: <strong>Không có dòng cho cặp (t, t+1) này</strong>.
              </li>
              <li>
                • Giá trị <code className="font-mono">AQI(t)</code> trong bảng dữ liệu hồi cứu: <strong>{hasAqiT ? vnNum(dailyT?.aqi, 0) : 'Khuyết (null)'}</strong>.
              </li>
              <li>
                • Cờ thiếu gốc <code className="font-mono">AQI_was_missing(t)</code>: <code className="font-mono font-semibold">{dailyT ? String(dailyT.miss) : 'Không có dòng ngày t'}</code>.
              </li>
            </ul>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
            <div className="font-bold text-slate-800 mb-1.5">
              2. Trạng thái kiểm tra trực tiếp tại ngày đích <code className="font-mono">t+1 = {formatDateVN(dateTarget)}</code>:
            </div>
            {!isRevealed ? (
              <div className="text-slate-700 leading-relaxed space-y-2">
                <p>
                  Đang ở chế độ <strong>giấu kết quả ngày đích <code className="font-mono">t+1</code></strong> nên không hiển thị AQI thực tế ngày đích.
                </p>
                <label className="inline-flex items-center gap-1.5 cursor-pointer select-none text-[11px] text-slate-600">
                  <input
                    type="checkbox"
                    checked={autoReveal}
                    onChange={onToggleAutoReveal}
                    className="rounded border-slate-400 accent-indigo-600"
                  />
                  <span>Tự động hiện thực tế khi đổi thành phố/ngày/split</span>
                </label>
              </div>
            ) : (
              <ul className="text-slate-700 leading-relaxed space-y-1">
                <li>
                  • Giá trị <code className="font-mono">AQI(t+1)</code> trong bảng dữ liệu hồi cứu: <strong>{hasAqiT1 ? vnNum(dailyT1?.aqi, 0) : 'Khuyết (null)'}</strong>.
                </li>
                <li>
                  • Cờ thiếu gốc <code className="font-mono">AQI_was_missing(t+1)</code>: <code className="font-mono font-semibold">{dailyT1 ? String(dailyT1.miss) : 'Không có dòng ngày t+1'}</code>.
                </li>
                <li>
                  • Đối chiếu dự báo – thực tế: <strong>Không chấm đúng/sai do không có bản ghi dự báo trong artifact phát lại</strong>.
                </li>
              </ul>
            )}
          </div>
        </div>

        <p className="mt-3 text-[11px] text-slate-500">
          *Giao diện giữ nguyên thành phố ({selectedCity}) và cặp ngày đang chọn (<code className="font-mono">t={formatDateVN(dateInput)} → t+1={formatDateVN(dateTarget)}</code>), chỉ trình bày các trạng thái kiểm tra trực tiếp được trong dữ liệu mà không suy diễn nguyên nhân thiếu bản ghi.
        </p>
      </section>
    );
  }

  // KHI CÓ DỮ LIỆU ĐẦY ĐỦ TRONG R2_B04
  const l3Alert = record.l3 >= thr.l3;
  const baseAlert = record.aqi >= thr.base;
  const actualHeavy = record.y >= thr.heavyActual;

  const l3Outcome = evaluateOutcome(record.l3, record.y, thr.l3);
  const baseOutcome = evaluateOutcome(record.aqi, record.y, thr.base);

  const nearL3 = isNearThreshold(record.l3, thr.l3, 1.5);
  const nearBase = isNearThreshold(record.aqi, thr.base, 1.5);

  const hasOverflow =
    record.l3 > 500 || record.aqi > 500 || (isRevealed && record.y > 500);

  const signedDiffL3 = record.l3 - record.y;
  const absErrorBase = Math.abs(record.aqi - record.y);

  const bucketT = getAqiBucket(record.aqi);
  const bucketPredL3 = getAqiBucket(record.l3);
  const bucketActual = getAqiBucket(record.y);

  return (
    <section
      aria-label="Thước quyết định hai làn và kết quả đối chiếu cảnh báo"
      className="bg-white rounded-xl border border-slate-200 shadow-xs p-4 flex flex-col gap-3.5"
    >
      {/* Thanh tiêu đề + Chế độ ngưỡng + Nút Mở/Ẩn thực tế t+1 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-3 border-b border-slate-100">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-base font-bold text-slate-900">
              {selectedCity} · Dự báo từ <span className="font-mono text-slate-700">t={formatDateVN(dateInput)}</span> cho đích <span className="font-mono text-indigo-900">t+1={formatDateVN(dateTarget)}</span>
            </h2>
            <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
              {split === 'test' ? 'Giai đoạn kiểm thử (Test)' : 'Holdout đánh giá bổ sung'}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            {thr.shortDesc} · Quyết định tính trên <strong>giá trị gốc</strong> (không làm tròn trước).
          </p>
        </div>

        {/* Cụm nút Chế độ ngưỡng (Y25) & Nút Mở/Ẩn thực tế (Y04) */}
        <div className="flex flex-wrap items-center gap-2 shrink-0">
          <div className="inline-flex rounded-lg bg-slate-100 p-0.5 border border-slate-200 text-[11px]" role="group" aria-label="Chế độ ngưỡng cảnh báo">
            <button
              type="button"
              onClick={() => onChangeThresholdMode('f2')}
              className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
                thresholdMode === 'f2'
                  ? 'bg-white text-slate-900 font-bold shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900 font-medium'
              }`}
              title="Chế độ ưu tiên Recall (chọn bằng F2 trên OOF Train): Mô hình ≥ 166, Baseline ≥ 160"
            >
              Ngưỡng F2 (166 / 160)
            </button>
            <button
              type="button"
              onClick={() => onChangeThresholdMode('201')}
              className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
                thresholdMode === '201'
                  ? 'bg-white text-slate-900 font-bold shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900 font-medium'
              }`}
              title="Chế độ so sánh cùng ngưỡng nghĩa đen 201 cho cả dự báo và thực tế"
            >
              Cùng ngưỡng (201 / 201)
            </button>
          </div>

          <button
            type="button"
            onClick={onToggleReveal}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-2xs cursor-pointer ${
              isRevealed
                ? 'bg-slate-800 hover:bg-slate-700 text-white'
                : 'bg-indigo-600 hover:bg-indigo-700 text-white ring-2 ring-indigo-600/25'
            }`}
            title="Phím tắt: Space để bật/tắt kết quả thực tế t+1"
          >
            {isRevealed ? (
              <>
                <EyeOff className="w-3.5 h-3.5" />
                <span>Ẩn thực tế t+1</span>
              </>
            ) : (
              <>
                <Eye className="w-3.5 h-3.5" />
                <span>Mở thực tế &amp; Đối chiếu (t+1)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* 3 Thẻ số liệu tóm tắt: Baseline AQI(t) | Dự báo Ridge L3 (t+1) | Thực tế AQI(t+1) & Kết luận */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Thẻ 1: Baseline "Ngày mai = hôm nay" = AQI(t) */}
        <div className="p-3 rounded-xl bg-slate-50/90 border border-slate-200 flex flex-col justify-between">
          <div className="flex items-center justify-between gap-1">
            <span className="text-xs font-bold text-slate-600">
              1. Baseline (Ngày mai = hôm nay)
            </span>
            <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded border ${bucketT?.bgSoft}`}>
              AQI(t): {bucketT?.labelVN}
            </span>
          </div>

          <div className="my-2 flex items-baseline justify-between gap-2">
            <div>
              <span className="text-2xl font-extrabold font-mono text-slate-900">
                {formatAqiSmart(record.aqi, thr.base)}
              </span>
              <span className="text-[11px] text-slate-500 ml-1.5 font-mono">
                (gốc: {record.aqi.toFixed(2).replace('.', ',')})
              </span>
            </div>
            <span
              className={`text-[11px] font-bold px-2 py-0.5 rounded border ${
                baseAlert
                  ? 'bg-amber-100 text-amber-950 border-amber-400'
                  : 'bg-slate-200/80 text-slate-700 border-slate-300'
              }`}
            >
              {baseAlert ? `BÁO (≥ ${thr.base})` : `KHÔNG BÁO (< ${thr.base})`}
            </span>
          </div>

          <div className="text-[11px] text-slate-500 flex items-center justify-between border-t border-slate-200/70 pt-1.5">
            <span>Ngưỡng baseline: <strong className="font-mono text-slate-700">{thr.base}</strong></span>
            {isRevealed ? (
              <span className="font-semibold text-slate-800">
                Đối chiếu: <strong>{baseOutcome.symbol} {baseOutcome.label}</strong> (|e|={vnNum(absErrorBase, 1)})
              </span>
            ) : (
              <span className="italic text-slate-400">Chờ mở thực tế t+1...</span>
            )}
          </div>
        </div>

        {/* Thẻ 2: Dự báo Mô hình chính Ridge L3 cho ngày t+1 */}
        <div className="p-3 rounded-xl bg-indigo-50/50 border-2 border-indigo-600/80 flex flex-col justify-between relative">
          <div className="flex items-center justify-between gap-1">
            <span className="text-xs font-bold text-indigo-950 flex items-center gap-1">
              <span>2. Dự báo Ridge L3 cho t+1</span>
            </span>
            <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded border ${bucketPredL3?.bgSoft}`}>
              {bucketPredL3?.labelVN}
            </span>
          </div>

          <div className="my-2 flex items-baseline justify-between gap-2">
            <div>
              <span className="text-2xl font-extrabold font-mono text-indigo-950">
                {formatAqiSmart(record.l3, thr.l3)}
              </span>
              <span className="text-[11px] text-indigo-700/80 ml-1.5 font-mono">
                (gốc: {record.l3.toFixed(6).replace('.', ',')})
              </span>
            </div>
            <span
              className={`text-[11px] font-bold px-2 py-0.5 rounded border ${
                l3Alert
                  ? 'bg-indigo-900 text-amber-300 border-indigo-950'
                  : 'bg-slate-200 text-slate-800 border-slate-300'
              }`}
            >
              {l3Alert ? `PHÁT CẢNH BÁO (≥ ${thr.l3})` : `KHÔNG BÁO (< ${thr.l3})`}
            </span>
          </div>

          <div className="text-[11px] text-indigo-900/80 flex items-center justify-between border-t border-indigo-200/70 pt-1.5">
            <span>Ngưỡng cảnh báo L3: <strong className="font-mono">{thr.l3}</strong></span>
            <span>
              Chênh so với hôm nay: <strong className="font-mono">{record.l3 - record.aqi >= 0 ? '+' : ''}{vnNum(record.l3 - record.aqi, 1)}</strong>
            </span>
          </div>
        </div>

        {/* Thẻ 3: Thực tế Quan trắc t+1 & Nhãn kết quả tiếng Việt (Y04, Y13, Y36) */}
        {!isRevealed ? (
          <div className="p-3 rounded-xl bg-slate-900 text-white border border-slate-800 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-300">
                3. Thực tế ngày đích t+1 ({formatDateVN(dateTarget)})
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-amber-300 font-semibold">
                Đang ẩn để thuyết trình
              </span>
            </div>

            <div className="my-2 flex items-center justify-between gap-2">
              <p className="text-xs text-slate-300 leading-snug">
                Đã khóa dự báo tại cuối ngày <code className="font-mono">t</code>. Bấm để mở AQI thực tế ngày <code className="font-mono">t+1</code> và kết luận cảnh báo.
              </p>
              <button
                type="button"
                onClick={onToggleReveal}
                className="px-3 py-2 rounded-lg bg-amber-400 hover:bg-amber-300 text-slate-950 font-extrabold text-xs shrink-0 cursor-pointer shadow-sm"
              >
                Mở kết quả t+1
              </button>
            </div>

            <div className="pt-1.5 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
              <label className="inline-flex items-center gap-1.5 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={autoReveal}
                  onChange={onToggleAutoReveal}
                  className="rounded border-slate-600 accent-amber-400"
                />
                <span>Luôn hiện sẵn thực tế khi đổi ngày (Y28)</span>
              </label>
            </div>
          </div>
        ) : (
          <div className={`p-3 rounded-xl border-2 flex flex-col justify-between ${l3Outcome.bgClass} ${l3Outcome.borderClass}`}>
            <div className="flex items-center justify-between gap-1">
              <span className={`text-xs font-bold ${l3Outcome.textClass}`}>
                3. Thực tế t+1 ({formatDateVN(dateTarget)})
              </span>
              {/* Nhãn kết quả tiếng Việt duy nhất đang xảy ra (Y13) — Phân biệt bằng chữ + ký hiệu + viền */}
              <span className={`text-xs font-extrabold px-2.5 py-0.5 rounded-md border flex items-center gap-1 shadow-2xs ${l3Outcome.badgeClass}`}>
                <span className="font-mono text-sm leading-none">{l3Outcome.symbol}</span>
                <span>{l3Outcome.label} ({l3Outcome.code})</span>
              </span>
            </div>

            <div className="my-2 flex items-baseline justify-between gap-2">
              <div>
                <span className={`text-2xl font-extrabold font-mono ${l3Outcome.textClass}`}>
                  {formatAqiSmart(record.y)}
                </span>
                <span className="text-xs font-semibold ml-1.5 text-slate-700">
                  ({ record.y >= 201 ? '≥ 201: Ngày ô nhiễm nặng' : '< 201: Chưa tới mức nặng' })
                </span>
              </div>
              <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded border ${bucketActual?.bgSoft}`}>
                {bucketActual?.labelVN}
              </span>
            </div>

            {/* Hiển thị sai lệch có dấu Dự báo - Thực tế (Y36) + Nút mở Ma trận 2x2 */}
            <div className="text-[11px] text-slate-700 flex flex-wrap items-center justify-between gap-1 border-t border-slate-300/70 pt-1.5">
              <span title="Sai lệch của riêng ca này (Dự báo Ridge L3 trừ Thực tế y); không nhầm với MAE toàn tập">
                Lệch (Dự báo − Thực tế):{' '}
                <strong className="font-mono text-slate-900">
                  {signedDiffL3 >= 0 ? '+' : ''}
                  {vnNum(signedDiffL3, 2)} điểm
                </strong>
              </span>
              <button
                type="button"
                onClick={() => onOpenDetailLayer('case')}
                className="text-indigo-800 hover:text-indigo-950 font-bold underline inline-flex items-center gap-0.5 cursor-pointer"
              >
                <span>Ma trận 2×2</span>
                <ArrowUpRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Cảnh báo đặc biệt khi giá trị dự báo nằm SÁT NGƯỠNG (Quy tắc #6: như Amritsar 165,973826 vs 166) */}
      {(nearL3 || nearBase) && (
        <div className="px-3.5 py-2.5 rounded-lg bg-amber-50 border border-amber-300 text-amber-950 text-xs flex items-start gap-2.5">
          <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong>Ca biên sát ngưỡng cảnh báo (Quy tắc #6 — Không làm tròn trước khi quyết định):</strong>{' '}
            {nearL3 && (
              <span>
                Dự báo gốc của <strong>Ridge L3</strong> là{' '}
                <code className="font-mono font-bold bg-white px-1.5 py-0.5 rounded border border-amber-300">
                  {record.l3.toFixed(6).replace('.', ',')}
                </code>{' '}
                so với ngưỡng <code className="font-mono font-bold">{thr.l3},000000</code> (chênh{' '}
                <code className="font-mono font-bold">
                  {(record.l3 - thr.l3 >= 0 ? '+' : '') + (record.l3 - thr.l3).toFixed(6).replace('.', ',')}
                </code>
                ). Nếu làm tròn số nguyên thành <code className="font-mono">{Math.round(record.l3)}</code> trước sẽ gây hiểu nhầm; hệ thống so sánh trên <strong>giá trị gốc</strong> nên kết luận là{' '}
                <strong>{l3Alert ? 'PHÁT CẢNH BÁO' : 'KHÔNG PHÁT CẢNH BÁO'}</strong>.
              </span>
            )}
          </div>
        </div>
      )}

      {/* Cảnh báo đặc biệt khi có điểm VƯỢT TRỤC 500 (Overflow > 500) */}
      {hasOverflow && (
        <div className="px-3.5 py-2 rounded-lg bg-rose-50 border border-rose-300 text-rose-950 text-xs flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-700 shrink-0" />
            <span>
              <strong>Điểm vượt thang chuẩn 500:</strong> Dự án không cắt trần AQI ở 500. Giá trị thật:{' '}
              <strong>AQI(t) = {vnNum(record.aqi, 1)}</strong> ·{' '}
              <strong>Dự báo L3 = {vnNum(record.l3, 2)}</strong>
              {isRevealed && (
                <>
                  {' '}· <strong>Thực tế AQI(t+1) = {vnNum(record.y, 1)}</strong>
                </>
              )}
              . Điểm vượt 500 được đặt trong <em>Vùng mở rộng &gt;500</em> bên phải thước.
            </span>
          </div>
        </div>
      )}

      {/* THƯỚC QUYẾT ĐỊNH HAI LÀN (Y27 — Two-Lane Decision Ruler) */}
      <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/90">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5">
          <div className="flex items-center gap-1.5">
            <SlidersHorizontal className="w-4 h-4 text-slate-700" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Thước Quyết định Hai Làn trên cùng thang AQI (Phân vai Ngưỡng Dự báo &amp; Mốc Thực tế)
            </h3>
          </div>
          <div className="flex items-center gap-3 text-[11px]">
            <span className="inline-flex items-center gap-1 font-semibold text-indigo-900">
              <span className="w-3 h-3 rounded-xs bg-indigo-700 inline-block border border-white" />
              <span>Dự báo Ridge L3 (t+1)</span>
            </span>
            <span className="inline-flex items-center gap-1 font-semibold text-slate-700">
              <span className="w-3 h-3 rounded-full bg-white inline-block border-2 border-slate-700" />
              <span>Baseline Hôm nay AQI(t)</span>
            </span>
            <span className="inline-flex items-center gap-1 font-semibold text-emerald-900">
              <span className="w-3 h-3 rotate-45 bg-slate-900 inline-block border border-white" />
              <span>Thực tế AQI(t+1)</span>
            </span>
          </div>
        </div>

        {/* Thang nền màu CPCB 0..500 (82%) + Vùng vượt trục >500..660 (18%) */}
        <div className="relative pt-1 pb-2">
          {/* Thanh dải bậc chất lượng không khí tham chiếu trên đỉnh */}
          <div className="h-2.5 w-full rounded-full overflow-hidden flex border border-slate-300/80 mb-1">
            <div style={{ width: '8.2%' }} className="bg-green-600/80" title="0–50: Tốt" />
            <div style={{ width: '8.2%' }} className="bg-lime-600/80" title="51–100: Đạt" />
            <div style={{ width: '16.4%' }} className="bg-amber-500/80" title="101–200: Trung bình" />
            <div style={{ width: '16.4%' }} className="bg-orange-600/85" title="201–300: Kém (Bắt đầu Ô nhiễm nặng ≥201)" />
            <div style={{ width: '16.4%' }} className="bg-red-600/85" title="301–400: Rất kém (Ô nhiễm nặng)" />
            <div style={{ width: '16.4%' }} className="bg-rose-900/90" title="401–500: Nguy hại (Ô nhiễm nặng)" />
            <div
              style={{
                width: '18%',
                backgroundImage:
                  'repeating-linear-gradient(45deg, #4c0519, #4c0519 4px, #881337 4px, #881337 8px)',
              }}
              title=">500 (tới 660): Vùng vượt thang chuẩn CPCB"
            />
          </div>

          {/* Nhãn mốc số AQI trên trục */}
          <div className="relative h-4 text-[10px] font-mono text-slate-500 select-none mb-2">
            {[0, 50, 100, 160, 201, 300, 400, 500].map((tick) => (
              <span
                key={tick}
                style={{ left: `${aqiToPercent(tick)}%` }}
                className={`absolute -translate-x-1/2 ${
                  tick === 201 ? 'font-bold text-rose-800' : tick === 160 ? 'text-slate-600' : ''
                }`}
              >
                {tick}
              </span>
            ))}
            <span style={{ left: '91%' }} className="absolute -translate-x-1/2 font-bold text-rose-900">
              &gt;500 (tới 660)
            </span>
          </div>

          {/* ================= LÀN 1: DỰ BÁO & NGƯỠNG VẬN HÀNH (Tại cuối ngày t) ================= */}
          <div className="relative bg-white rounded-lg border border-slate-200 p-2.5 mb-2.5">
            <div className="flex items-center justify-between text-[11px] mb-2">
              <span className="font-bold text-slate-800">
                Làn 1 — Quyết định trên Dự báo (Tại cuối ngày <code className="font-mono">t</code>):
              </span>
              <span className="text-slate-600 font-medium">
                Ngưỡng mô hình L3: <strong className="font-mono text-indigo-800">≥ {thr.l3}</strong> · Ngưỡng Baseline: <strong className="font-mono text-slate-700">≥ {thr.base}</strong>
              </span>
            </div>

            <div className="relative h-12 bg-slate-100 rounded-md border border-slate-200 overflow-visible">
              {/* Vùng tô màu từ ngưỡng L3 trở lên trên Làn 1 */}
              <div
                style={{
                  left: `${aqiToPercent(thr.l3)}%`,
                  width: `${100 - aqiToPercent(thr.l3)}%`,
                }}
                className="absolute inset-y-0 bg-indigo-100/60 border-l-2 border-indigo-700"
              />

              {/* Vạch chia ranh giới 500 */}
              <div
                style={{ left: '82%' }}
                className="absolute inset-y-0 border-l border-dashed border-rose-400"
              />

              {/* Vạch ngưỡng Baseline (160 khi ở chế độ F2) */}
              {thresholdMode === 'f2' && (
                <div
                  style={{ left: `${aqiToPercent(thr.base)}%` }}
                  className="absolute inset-y-0 border-l-2 border-dashed border-slate-500"
                  title={`Ngưỡng F2 của Baseline: ${thr.base}`}
                >
                  <span className="absolute -bottom-4 -translate-x-1/2 text-[9px] font-mono font-bold text-slate-600 bg-white/90 px-1 rounded">
                    Base≥160
                  </span>
                </div>
              )}

              {/* Vạch ngưỡng Mô hình L3 (166 hoặc 201) */}
              <div
                style={{ left: `${aqiToPercent(thr.l3)}%` }}
                className="absolute inset-y-0 border-l-2 border-indigo-700 z-10"
              >
                <span className="absolute -top-4 -translate-x-1/2 text-[10px] font-mono font-bold text-white bg-indigo-700 px-1.5 py-0.2 rounded shadow-2xs whitespace-nowrap">
                  Ngưỡng L3 ≥ {thr.l3}
                </span>
              </div>

              {/* Điểm đánh dấu Baseline AQI(t) (Hình tròn trắng viền đậm ở nửa dưới Làn 1) */}
              <div
                style={{ left: `${aqiToPercent(record.aqi)}%` }}
                className="absolute bottom-1.5 -translate-x-1/2 z-20 flex flex-col items-center group"
                title={`Baseline (Ngày mai = hôm nay): ${record.aqi}`}
              >
                <div className="w-4 h-4 rounded-full bg-white border-2 border-slate-800 shadow-xs" />
                <span className="mt-0.5 text-[10px] font-mono font-bold text-slate-700 bg-white/95 px-1 rounded border border-slate-200 whitespace-nowrap">
                  Base: {vnNum(record.aqi, 0)}
                </span>
              </div>

              {/* Điểm đánh dấu Dự báo Ridge L3 (Hình vuông xanh đậm ở nửa trên Làn 1) */}
              <div
                style={{ left: `${aqiToPercent(record.l3)}%` }}
                className="absolute top-1.5 -translate-x-1/2 z-30 flex flex-col items-center"
                title={`Dự báo Ridge L3 (t+1): ${record.l3.toFixed(6)}`}
              >
                <span className=" -mt-4 mb-0.5 text-[10px] font-mono font-extrabold text-white bg-indigo-900 px-1.5 py-0.2 rounded shadow-xs whitespace-nowrap">
                  L3: {formatAqiSmart(record.l3, thr.l3)}
                </span>
                <div className="w-4 h-4 rounded-xs bg-indigo-700 border-2 border-white shadow-sm" />
              </div>
            </div>
          </div>

          {/* ================= LÀN 2: THỰC TẾ QUAN TRẮC t+1 & MỐC NGÀY NẶNG ≥ 201 ================= */}
          <div className="relative bg-white rounded-lg border border-slate-200 p-2.5">
            <div className="flex items-center justify-between text-[11px] mb-2">
              <span className="font-bold text-slate-800">
                Làn 2 — Thực tế Quan trắc (Tại ngày đích <code className="font-mono">t+1</code>):
              </span>
              <span className="text-rose-800 font-semibold">
                Định nghĩa ngày ô nhiễm nặng thực tế: <strong className="font-mono">AQI(t+1) ≥ 201</strong>
              </span>
            </div>

            <div className="relative h-12 bg-slate-100 rounded-md border border-slate-200 overflow-visible">
              {/* Vùng ngày ô nhiễm nặng thực tế >= 201 */}
              <div
                style={{
                  left: `${aqiToPercent(201)}%`,
                  width: `${100 - aqiToPercent(201)}%`,
                }}
                className="absolute inset-y-0 bg-rose-100/70 border-l-2 border-rose-700"
              />

              {/* Vạch chia ranh giới 500 */}
              <div
                style={{ left: '82%' }}
                className="absolute inset-y-0 border-l border-dashed border-rose-400"
              />

              {/* Vạch mốc ngày nặng thực tế >= 201 */}
              <div
                style={{ left: `${aqiToPercent(201)}%` }}
                className="absolute inset-y-0 border-l-2 border-rose-700 z-10"
              >
                <span className="absolute -top-4 -translate-x-1/2 text-[10px] font-mono font-bold text-white bg-rose-700 px-1.5 py-0.2 rounded shadow-2xs whitespace-nowrap">
                  Mốc thực tế nặng ≥ 201
                </span>
              </div>

              {!isRevealed ? (
                /* Màn che chống lộ kết quả trước khi bấm Mở thực tế */
                <div className="absolute inset-0 bg-slate-800/90 backdrop-blur-[1px] rounded-md z-20 flex items-center justify-between px-4 text-white">
                  <span className="text-xs font-medium text-slate-200">
                    Thực tế ngày <code className="font-mono">t+1 ({formatDateVN(dateTarget)})</code> đang ẩn để phục vụ nhịp kể chuyện thuyết trình.
                  </span>
                  <button
                    type="button"
                    onClick={onToggleReveal}
                    className="px-3 py-1 rounded bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold text-xs cursor-pointer shrink-0"
                  >
                    Mở thực tế ngay
                  </button>
                </div>
              ) : (
                <>
                  {/* Đường nối thể hiện độ lệch giữa Dự báo L3 và Thực tế y(t+1) */}
                  <div
                    style={{
                      left: `${Math.min(aqiToPercent(record.l3), aqiToPercent(record.y))}%`,
                      width: `${Math.abs(aqiToPercent(record.y) - aqiToPercent(record.l3))}%`,
                    }}
                    className="absolute top-1/2 -translate-y-1/2 h-1 bg-slate-500/50 z-10"
                  />

                  {/* Điểm đánh dấu Thực tế AQI(t+1) (Hình thoi xoay 45 độ) */}
                  <div
                    style={{ left: `${aqiToPercent(record.y)}%` }}
                    className="absolute top-2.5 -translate-x-1/2 z-30 flex flex-col items-center"
                    title={`Thực tế AQI(t+1): ${record.y}`}
                  >
                    <div
                      className={`w-4 h-4 rotate-45 border-2 border-white shadow-sm ${
                        actualHeavy ? 'bg-rose-700' : 'bg-teal-700'
                      }`}
                    />
                    <span className="mt-1 text-[10px] font-mono font-extrabold text-white bg-slate-900 px-1.5 py-0.2 rounded shadow-xs whitespace-nowrap">
                      Thực tế: {vnNum(record.y, 0)}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Dòng kết luận ngắn gọn cuối thước */}
        <div className="mt-2 pt-2 border-t border-slate-200/80 flex flex-wrap items-center justify-between gap-2 text-xs">
          {!isRevealed ? (
            <span className="text-slate-600">
              Trạng thái tại <code className="font-mono">t</code>: Mô hình Ridge L3 dự báo{' '}
              <strong className="font-mono text-indigo-900">{formatAqiSmart(record.l3, thr.l3)}</strong> →{' '}
              <strong>{l3Alert ? `Phát cảnh báo (≥ ${thr.l3})` : `Không phát cảnh báo (< ${thr.l3})`}</strong>.
            </span>
          ) : (
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1 font-bold text-slate-900">
                <CheckCircle2 className="w-4 h-4 text-teal-700" />
                <span>Kết luận ca này ({thr.modeName}):</span>
              </span>
              <span className={`px-2 py-0.5 rounded font-bold text-xs border ${l3Outcome.badgeClass}`}>
                Ridge L3: {l3Outcome.symbol} {l3Outcome.label}
              </span>
              <span className="text-slate-600">so với</span>
              <span className="px-2 py-0.5 rounded font-semibold text-xs bg-slate-200 text-slate-800 border border-slate-300">
                Baseline: {baseOutcome.symbol} {baseOutcome.label}
              </span>
              <span className="text-slate-500 text-[11px]">
                ({l3Outcome.shortRule})
              </span>
            </div>
          )}

          <button
            type="button"
            onClick={() => onOpenDetailLayer('case')}
            className="text-xs font-bold text-indigo-700 hover:text-indigo-900 inline-flex items-center gap-1 cursor-pointer"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Giải thích số liệu, phương pháp &amp; hạn chế (Lớp 2)</span>
          </button>
        </div>
      </div>
    </section>
  );
};
