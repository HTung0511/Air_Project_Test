import React from 'react';
import {
  X,
  Grid,
  GitBranch,
  Table2,
  ShieldCheck,
  AlertTriangle,
  Lock,
  CheckCircle2,
  Info,
} from 'lucide-react';
import {
  DEMO_DATA,
  PredictionRecord,
  SplitType,
  ThresholdMode,
  getThresholds,
  evaluateOutcome,
  getDailyContext,
  formatDateVN,
  vnNum,
} from '../data/aqiHelpers';

export type DetailTabKey = 'case' | 'pipeline' | 'tables' | 'audit';

interface DetailDrawerModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeTab: DetailTabKey;
  onChangeTab: (tab: DetailTabKey) => void;
  selectedCity: string;
  split: SplitType;
  dateInput: string;
  dateTarget: string;
  record: PredictionRecord | null;
  thresholdMode: ThresholdMode;
  onChangeThresholdMode: (mode: ThresholdMode) => void;
  isRevealed: boolean;
  onToggleReveal: () => void;
}

export const DetailDrawerModal: React.FC<DetailDrawerModalProps> = ({
  isOpen,
  onClose,
  activeTab,
  onChangeTab,
  selectedCity,
  split,
  dateInput,
  dateTarget,
  record,
  thresholdMode,
  onChangeThresholdMode,
  isRevealed,
  onToggleReveal,
}) => {
  if (!isOpen) return null;

  const thr = getThresholds(thresholdMode);
  const dailyT = getDailyContext(selectedCity, dateInput);
  const cityMeta = DEMO_DATA.cities.find((c) => c.id === selectedCity) ?? DEMO_DATA.cities[0];

  // Lấy số liệu tổng hợp TP/FP/FN/TN của toàn tập (Test hoặc Holdout) ở chế độ ngưỡng đang chọn
  const thrTypeKey = thresholdMode === 'f2' ? 'F2' : '201';
  const splitAlertL3 = DEMO_DATA.summaryMetrics.alerts.find(
    (a) => a.split === split && a.model === 'Ridge L3' && a.threshold_type === thrTypeKey
  );
  const splitAlertBase = DEMO_DATA.summaryMetrics.alerts.find(
    (a) => a.split === split && a.model === 'Ngày mai = hôm nay' && a.threshold_type === thrTypeKey
  );

  // Số liệu TP/FP/FN/TN của riêng thành phố đang chọn
  const citySplitStats = cityMeta.splits[split];
  const cityAlertL3 = thresholdMode === 'f2' ? citySplitStats.alerts_f2_l3 : citySplitStats.alerts_201_l3;

  const currentOutcome =
    record && isRevealed ? evaluateOutcome(record.l3, record.y, thr.l3) : null;

  const testModels = DEMO_DATA.summaryMetrics.models.filter((m) => m.split === 'test');

  return (
    <div
      className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-[2px] flex justify-end"
      role="dialog"
      aria-modal="true"
      aria-label="Lớp chi tiết: Giải thích số liệu, phương pháp và hạn chế"
    >
      {/* Nền bấm ra ngoài để đóng và trở về đúng ngữ cảnh */}
      <div className="flex-1" onClick={onClose} />

      <div className="w-full max-w-5xl bg-white h-full shadow-2xl border-l border-slate-200 flex flex-col overflow-hidden">
        {/* Sticky Header giữ nguyên ngữ cảnh Thành phố / Ngày / Giai đoạn đang xem (Y14) */}
        <div className="px-5 py-3.5 bg-slate-900 text-white flex flex-wrap items-center justify-between gap-3 shrink-0">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-extrabold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-400 text-slate-950">
                Lớp 2 · Chi tiết &amp; Kiểm chứng
              </span>
              <h2 className="text-base font-bold">
                Ngữ cảnh đang giữ: <span className="text-amber-300">{selectedCity}</span> ·{' '}
                <code className="font-mono text-sm">t={formatDateVN(dateInput)} → t+1={formatDateVN(dateTarget)}</code> ({split === 'test' ? 'Tập Test' : 'Tập Holdout'})
              </h2>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              Khi đóng cửa sổ này, màn hình chính giữ nguyên thành phố, ngày đích, giai đoạn và trạng thái ẩn/mở thực tế.
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold flex items-center gap-1.5 border border-slate-700 cursor-pointer"
            title="Đóng Lớp Chi Tiết và quay lại màn hình trình chiếu (Phím Esc)"
          >
            <X className="w-4 h-4" />
            <span>Đóng chi tiết (Giữ ngữ cảnh)</span>
          </button>
        </div>

        {/* Thanh điều hướng 4 mục chuyên sâu trong Lớp Chi Tiết */}
        <div className="px-5 py-2 bg-slate-100 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2 shrink-0">
          <div className="flex flex-wrap gap-1.5" role="tablist">
            {(
              [
                { key: 'case', label: '1. Ma trận 2×2 & Giải thích Ca đang chọn', icon: Grid },
                { key: 'pipeline', label: '2. Pipeline & Bậc thang MAE (L1→L3)', icon: GitBranch },
                { key: 'tables', label: '3. Bảng Test / Holdout & Nhóm Thành phố', icon: Table2 },
                { key: 'audit', label: '4. Hạn chế (F01/F02) & Đối soát Dữ liệu', icon: ShieldCheck },
              ] as const
            ).map((t) => {
              const Icon = t.icon;
              const active = activeTab === t.key;
              return (
                <button
                  key={t.key}
                  type="button"
                  role="tab"
                  aria-selected={active}
                  onClick={() => onChangeTab(t.key)}
                  className={`px-3 py-1.5 rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer ${
                    active
                      ? 'bg-slate-900 text-white font-bold shadow-2xs'
                      : 'bg-white text-slate-700 hover:text-slate-900 border border-slate-200 font-medium'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{t.label}</span>
                </button>
              );
            })}
          </div>

          {/* Công tắc 2 chế độ ngưỡng khóa sẵn (Y25) */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-600 font-semibold">Ngưỡng (Y25):</span>
            <button
              type="button"
              onClick={() => onChangeThresholdMode('f2')}
              className={`px-2 py-1 rounded border text-[11px] cursor-pointer ${
                thresholdMode === 'f2'
                  ? 'bg-indigo-900 text-white border-indigo-900 font-bold'
                  : 'bg-white text-slate-700 border-slate-300'
              }`}
            >
              F2 (166 / 160)
            </button>
            <button
              type="button"
              onClick={() => onChangeThresholdMode('201')}
              className={`px-2 py-1 rounded border text-[11px] cursor-pointer ${
                thresholdMode === '201'
                  ? 'bg-indigo-900 text-white border-indigo-900 font-bold'
                  : 'bg-white text-slate-700 border-slate-300'
              }`}
            >
              Cùng 201
            </button>
          </div>
        </div>

        {/* Nội dung cuộn của Lớp Chi Tiết */}
        <div className="p-5 overflow-y-auto flex-1 space-y-5 text-slate-800">
          {/* =====================================================================
              TAB 1: MA TRẬN 2x2 (Y23), SO SÁNH L1-L3 CA ĐANG CHỌN (Y24) & TÍN HIỆU ĐẦU VÀO (Y32)
             ===================================================================== */}
          {activeTab === 'case' && (
            <div className="space-y-5">
              {/* Khối Ma trận 2x2 giải thích 4 trạng thái (Y23) */}
              <div className="bg-slate-50 rounded-xl border border-slate-200 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">
                      Ma trận Nhầm lẫn 2×2 — Phân biệt Ngưỡng Dự báo &amp; Mốc Thực tế Nặng (Y23)
                    </h3>
                    <p className="text-xs text-slate-600 mt-0.5">
                      Hàng = Quyết định phát cảnh báo trên <strong>AQI dự báo</strong> (<code className="font-mono">Ridge L3 ≥ {thr.l3}</code>) · Cột = <strong>AQI thực tế ngày t+1 ≥ 201</strong>.
                    </p>
                  </div>

                  {!isRevealed && record && (
                    <button
                      type="button"
                      onClick={onToggleReveal}
                      className="px-3 py-1.5 rounded-lg bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold text-xs flex items-center gap-1.5 cursor-pointer"
                    >
                      <Lock className="w-3.5 h-3.5" />
                      <span>Đang ẩn kết quả ca này — Bấm để mở ô Ma trận 2×2</span>
                    </button>
                  )}
                </div>

                {/* Bảng 2x2 */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 items-stretch">
                  <div className="lg:col-span-2 overflow-x-auto">
                    <table className="w-full border-collapse text-xs bg-white rounded-lg overflow-hidden border border-slate-300">
                      <thead>
                        <tr className="bg-slate-800 text-white">
                          <th className="p-2.5 border border-slate-700 text-left w-1/3">
                            Quyết định tại ngày t \ Thực tế ngày t+1
                          </th>
                          <th className="p-2.5 border border-slate-700 text-center w-1/3 bg-rose-950">
                            Thực tế Ô nhiễm nặng<br />
                            <span className="font-mono text-amber-300">AQI(t+1) ≥ 201</span>
                          </th>
                          <th className="p-2.5 border border-slate-700 text-center w-1/3 bg-slate-900">
                            Thực tế Chưa tới mức nặng<br />
                            <span className="font-mono text-slate-300">AQI(t+1) &lt; 201</span>
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {/* Hàng 1: Phát cảnh báo */}
                        <tr>
                          <td className="p-3 border border-slate-300 bg-slate-100 font-bold text-slate-900">
                            Phát cảnh báo tại ngày t<br />
                            <span className="font-mono text-indigo-800">Dự báo Ridge L3 ≥ {thr.l3}</span>
                          </td>
                          {/* Ô TP: Báo đúng */}
                          <td
                            className={`p-3 border-2 transition ${
                              currentOutcome?.code === 'TP'
                                ? 'bg-teal-100 border-teal-700 ring-2 ring-teal-600'
                                : 'bg-teal-50/40 border-slate-200'
                            }`}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-extrabold text-teal-950 text-sm">✓ Báo đúng (TP)</span>
                              {currentOutcome?.code === 'TP' && (
                                <span className="px-2 py-0.5 rounded bg-teal-800 text-white text-[10px] font-bold">
                                  ★ CA ĐANG XEM
                                </span>
                              )}
                            </div>
                            <p className="text-[11px] text-slate-600 mb-2">
                              Dự báo ≥ {thr.l3} và ngày mai thực sự ≥ 201.
                            </p>
                            <div className="text-[11px] font-mono bg-white/90 p-1.5 rounded border border-teal-200">
                              <div>Toàn tập {split}: <strong>{splitAlertL3?.TP ?? '—'}</strong> cặp (Base: {splitAlertBase?.TP ?? '—'})</div>
                              <div>Riêng {selectedCity}: <strong>{cityAlertL3.TP}</strong> cặp</div>
                            </div>
                          </td>

                          {/* Ô FP: Báo nhầm */}
                          <td
                            className={`p-3 border-2 transition ${
                              currentOutcome?.code === 'FP'
                                ? 'bg-amber-100 border-amber-700 ring-2 ring-amber-600'
                                : 'bg-amber-50/40 border-slate-200'
                            }`}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-extrabold text-amber-950 text-sm">! Báo nhầm (FP)</span>
                              {currentOutcome?.code === 'FP' && (
                                <span className="px-2 py-0.5 rounded bg-amber-700 text-white text-[10px] font-bold">
                                  ★ CA ĐANG XEM
                                </span>
                              )}
                            </div>
                            <p className="text-[11px] text-slate-600 mb-2">
                              Dự báo ≥ {thr.l3} nhưng ngày mai thực tế &lt; 201.
                            </p>
                            <div className="text-[11px] font-mono bg-white/90 p-1.5 rounded border border-amber-200">
                              <div>Toàn tập {split}: <strong>{splitAlertL3?.FP ?? '—'}</strong> cặp (Base: {splitAlertBase?.FP ?? '—'})</div>
                              <div>Riêng {selectedCity}: <strong>{cityAlertL3.FP}</strong> cặp</div>
                            </div>
                          </td>
                        </tr>

                        {/* Hàng 2: Không cảnh báo */}
                        <tr>
                          <td className="p-3 border border-slate-300 bg-slate-100 font-bold text-slate-900">
                            Không cảnh báo tại ngày t<br />
                            <span className="font-mono text-slate-700">Dự báo Ridge L3 &lt; {thr.l3}</span>
                          </td>
                          {/* Ô FN: Bỏ sót */}
                          <td
                            className={`p-3 border-2 transition ${
                              currentOutcome?.code === 'FN'
                                ? 'bg-rose-100 border-rose-700 ring-2 ring-rose-600'
                                : 'bg-rose-50/40 border-slate-200'
                            }`}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-extrabold text-rose-950 text-sm">▲ Bỏ sót (FN)</span>
                              {currentOutcome?.code === 'FN' && (
                                <span className="px-2 py-0.5 rounded bg-rose-800 text-white text-[10px] font-bold">
                                  ★ CA ĐANG XEM
                                </span>
                              )}
                            </div>
                            <p className="text-[11px] text-slate-600 mb-2">
                              Dự báo &lt; {thr.l3} nhưng ngày mai thực tế vọt lên ≥ 201.
                            </p>
                            <div className="text-[11px] font-mono bg-white/90 p-1.5 rounded border border-rose-200">
                              <div>Toàn tập {split}: <strong>{splitAlertL3?.FN ?? '—'}</strong> cặp (Base: {splitAlertBase?.FN ?? '—'})</div>
                              <div>Riêng {selectedCity}: <strong>{cityAlertL3.FN}</strong> cặp</div>
                            </div>
                          </td>

                          {/* Ô TN: Không cảnh báo đúng */}
                          <td
                            className={`p-3 border-2 transition ${
                              currentOutcome?.code === 'TN'
                                ? 'bg-slate-200 border-slate-700 ring-2 ring-slate-600'
                                : 'bg-slate-50/60 border-slate-200'
                            }`}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-extrabold text-slate-900 text-sm">○ Không cảnh báo đúng (TN)</span>
                              {currentOutcome?.code === 'TN' && (
                                <span className="px-2 py-0.5 rounded bg-slate-800 text-white text-[10px] font-bold">
                                  ★ CA ĐANG XEM
                                </span>
                              )}
                            </div>
                            <p className="text-[11px] text-slate-600 mb-2">
                              Dự báo &lt; {thr.l3} và ngày mai thực tế &lt; 201 (an toàn).
                            </p>
                            <div className="text-[11px] font-mono bg-white/90 p-1.5 rounded border border-slate-200">
                              <div>Toàn tập {split}: <strong>{splitAlertL3?.TN ?? '—'}</strong> cặp (Base: {splitAlertBase?.TN ?? '—'})</div>
                              <div>Riêng {selectedCity}: <strong>{cityAlertL3.TN}</strong> cặp</div>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  {/* Giải thích ý nghĩa ngưỡng F2 (166 / 160) vs Cùng ngưỡng 201 (Y25) */}
                  <div className="bg-white rounded-lg border border-slate-200 p-3.5 flex flex-col justify-between text-xs">
                    <div>
                      <h4 className="font-bold text-slate-900 mb-1.5">
                        Vì sao có hai chế độ ngưỡng 166/160 và 201? (Y25)
                      </h4>
                      <ul className="space-y-1.5 text-slate-700 list-disc pl-4 leading-relaxed">
                        <li>
                          <strong>Định nghĩa ngày nặng thực tế:</strong> cố định ở <code className="font-mono">AQI(t+1) ≥ 201</code> (mức Poor trở lên theo CPCB).
                        </li>
                        <li>
                          <strong>Ngưỡng ưu tiên Recall (F2 với β=2):</strong> Tìm trên dự đoán <em>out-of-fold của tập Train</em> (4.592 dòng, 1.193 ngày nặng — hoàn toàn không nhìn Test). Kết quả: <strong>Ridge L3 = 166</strong>, <strong>Baseline = 160</strong>. Hạ ngưỡng dự báo giúp bắt được các ngày sắp vượt 201 dù mô hình hồi quy có xu hướng dự báo thấp hơn đỉnh.
                        </li>
                        <li>
                          <strong>Lưu ý diễn giải F2:</strong> F2 tăng trọng số cho recall so với precision trong công thức điểm F; <em>không tự diễn dịch thành "chi phí bỏ sót gấp đôi báo nhầm"</em> nếu không có phân tích kinh tế – y tế riêng.
                        </li>
                      </ul>
                    </div>

                    <div className="mt-3 pt-2.5 border-t border-slate-100 text-[11px] text-slate-500">
                      Trên tập Test (389 cặp nặng): ở chế độ F2, L3 bắt <strong>377/389 (recall 96,9%)</strong> với <strong>113</strong> báo nhầm; Baseline bắt <strong>374/389 (recall 96,1%)</strong> với <strong>143</strong> báo nhầm.
                    </div>
                  </div>
                </div>
              </div>

              {/* So sánh dự báo các mô hình cho ngày đang chọn (Y24) & Tín hiệu đầu vào ngày t (Y32) */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Khối Y24 */}
                <div className="bg-white rounded-xl border border-slate-200 p-4">
                  <h3 className="text-sm font-bold text-slate-900 mb-1">
                    So sánh các Mô hình tại ngày đang chọn ({selectedCity}, đích {formatDateVN(dateTarget)}) (Y24)
                  </h3>
                  <p className="text-[11px] text-slate-500 mb-3">
                    Trích xuất trực tiếp từ <code className="font-mono">R2_B04_baseline_predictions.csv</code> (giá trị gốc 6 chữ số thập phân).
                  </p>

                  {!record ? (
                    <div className="p-4 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-900">
                      Tổ hợp ({selectedCity}, đích {formatDateVN(dateTarget)}) khuyết dữ liệu phát lại trong R2_B04.
                    </div>
                  ) : (
                    <div className="space-y-2 text-xs">
                      {[
                        { name: 'Trung bình theo thành phố (Train)', val: record.mean, note: 'Baseline tĩnh' },
                        { name: 'Trung vị cùng tháng (Khí hậu)', val: record.clim, note: 'Baseline mùa vụ' },
                        { name: 'Ngày mai = hôm nay (AQI ngày t)', val: record.aqi, note: 'Baseline quán tính chính' },
                        { name: 'Ridge L1 (Chỉ lịch sử AQI + mùa)', val: record.l1, note: 'alpha = 10' },
                        { name: 'Ridge L2 (+ 5 chất ô nhiễm ngày t)', val: record.l2, note: 'alpha = 0,1' },
                        { name: 'Ridge L3 (+ 9 biến thời tiết đến ngày t)', val: record.l3, note: 'Mô hình chính · alpha = 30', highlight: true },
                        { name: 'Ridge L4 (Cận trên: + thời tiết ngày mai)', val: record.l4, note: 'Chỉ tham chiếu trần lý thuyết' },
                        { name: 'Cây tăng cường HGB L3', val: record.hgb, note: 'Mô hình phi tuyến đối chứng' },
                      ].map((m) => (
                        <div
                          key={m.name}
                          className={`flex items-center justify-between px-3 py-1.5 rounded-lg border ${
                            m.highlight
                              ? 'bg-indigo-50 border-indigo-300 font-bold text-indigo-950'
                              : 'bg-slate-50 border-slate-200 text-slate-800'
                          }`}
                        >
                          <div>
                            <div>{m.name}</div>
                            <div className="text-[10px] text-slate-500 font-normal">{m.note}</div>
                          </div>
                          <div className="text-right font-mono">
                            <span className="text-sm font-bold">{m.val.toFixed(2).replace('.', ',')}</span>
                            <span className="block text-[10px] text-slate-500">gốc: {m.val.toFixed(6).replace('.', ',')}</span>
                          </div>
                        </div>
                      ))}

                      {isRevealed && (
                        <div className="mt-2 px-3 py-2 rounded-lg bg-slate-900 text-white flex items-center justify-between font-mono text-xs">
                          <span className="font-sans font-bold">Thực tế quan trắc AQI(t+1):</span>
                          <span className="text-amber-300 font-bold text-sm">{record.y.toFixed(2).replace('.', ',')}</span>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="mt-3 p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-[11px] text-amber-950 leading-relaxed">
                    <strong>Caveat bắt buộc (Quy tắc #7 &amp; Y24):</strong> Ridge L1, L2, L3 là ba mô hình được <strong>fit riêng biệt</strong> với tập đặc trưng và hệ số chuẩn hóa khác nhau trên thang <code className="font-mono">log(AQI)</code>. <strong>Không diễn giải</strong> chênh lệch dự báo giữa L1, L2, L3 ở một ngày cụ thể như đóng góp nhân quả của chất ô nhiễm hay thời tiết, và không giả định L3 luôn gần thực tế hơn ở mọi ca đơn lẻ.
                  </div>
                </div>

                {/* Khối Y32: Tín hiệu quan trắc đầu vào ngày t */}
                <div className="bg-white rounded-xl border border-slate-200 p-4 flex flex-col justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 mb-1">
                      Bối cảnh Quan trắc Đầu vào tại Ngày <code className="font-mono">t = {formatDateVN(dateInput)}</code> (Y32)
                    </h3>
                    <p className="text-[11px] text-slate-500 mb-3">
                      Trích từ <code className="font-mono">air_quality_8cities_weather.csv</code> cho {selectedCity} tại ngày <code className="font-mono">{formatDateVN(dateInput)}</code>.
                    </p>

                    {dailyT ? (
                      <div className="grid grid-cols-2 gap-2.5 text-xs">
                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                          <div className="text-[10px] font-semibold uppercase text-slate-500">AQI quan trắc ngày t</div>
                          <div className="text-base font-extrabold font-mono text-slate-900 mt-0.5">
                            {dailyT.aqi !== null ? vnNum(dailyT.aqi, 0) : 'Khuyết (NaN)'}
                          </div>
                          <div className="text-[10px] text-slate-500 mt-0.5">
                            Trạng thái: {dailyT.miss ? 'Khuyết gốc (Không nội suy AQI)' : 'Quan trắc CPCB hợp lệ'}
                          </div>
                        </div>

                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                          <div className="text-[10px] font-semibold uppercase text-slate-500">Bụi mịn PM2.5 ngày t</div>
                          <div className="text-base font-extrabold font-mono text-slate-900 mt-0.5">
                            {dailyT.pm25 !== null ? `${vnNum(dailyT.pm25, 2)} µg/m³` : 'Khuyết'}
                          </div>
                          <div className="text-[10px] text-slate-600 mt-0.5">
                            {dailyT.pm25_miss ? (
                              <span className="text-amber-800 font-semibold">
                                Đã nội suy ở bước làm sạch → Đặt lại NaN + ffill≤2d khi dự báo
                              </span>
                            ) : (
                              'Quan trắc trực tiếp (PM2.5_was_missing = False)'
                            )}
                          </div>
                        </div>

                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                          <div className="text-[10px] font-semibold uppercase text-slate-500">Nhiệt độ &amp; Độ ẩm TB (ERA5)</div>
                          <div className="text-sm font-bold font-mono text-slate-900 mt-0.5">
                            {vnNum(dailyT.temp, 1)} °C · {vnNum(dailyT.hum, 1)} %
                          </div>
                          <div className="text-[10px] text-slate-500 mt-0.5">Tái phân tích lưới 0,25° Open-Meteo</div>
                        </div>

                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                          <div className="text-[10px] font-semibold uppercase text-slate-500">Gió TB &amp; Lớp biên BLH</div>
                          <div className="text-sm font-bold font-mono text-slate-900 mt-0.5">
                            {vnNum(dailyT.wind, 2)} m/s · BLH {vnNum(dailyT.blh, 0)} m
                          </div>
                          <div className="text-[10px] text-slate-500 mt-0.5">
                            Mưa ngày t: {vnNum(dailyT.rain, 1)} mm
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="p-3 rounded bg-slate-100 text-xs text-slate-600">
                        Không có bản ghi ngày {formatDateVN(dateInput)}.
                      </div>
                    )}
                  </div>

                  <div className="mt-3 p-2.5 rounded-lg bg-slate-100 border border-slate-200 text-[11px] text-slate-600 leading-relaxed">
                    <strong>Lưu ý diễn giải tín hiệu đầu vào (Y32):</strong> Các giá trị trên là số liệu mô tả tại ngày <code className="font-mono">t</code> (trong mô hình, các chất ô nhiễm được lấy <code className="font-mono">log(1+x)</code>, chuẩn hóa theo trung vị/độ lệch chuẩn của tập Train). Không coi các biến hiển thị ở đây là nguyên nhân trực tiếp hay giải thích đầy đủ cho dự báo.
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* =====================================================================
              TAB 2: SƠ ĐỒ PIPELINE (Y08) & BẬC THANG MAE THEO MÔ HÌNH (Y19)
             ===================================================================== */}
          {activeTab === 'pipeline' && (
            <div className="space-y-5">
              {/* Sơ đồ Pipeline gọn và trung thực (Y08) */}
              <div className="bg-slate-50 rounded-xl border border-slate-200 p-4">
                <h3 className="text-sm font-bold text-slate-900 mb-2">
                  Sơ đồ Pipeline Dự án &amp; Trạng thái Kiểm chứng (Y08)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-2.5 text-xs">
                  <div className="p-3 rounded-lg bg-white border border-slate-200">
                    <div className="text-[10px] font-bold uppercase text-indigo-700 mb-1">Bước 1 · Nguồn Dữ liệu</div>
                    <div className="font-bold text-slate-900 mb-1">CPCB (Kaggle) + ERA5</div>
                    <p className="text-[11px] text-slate-600 leading-snug">
                      8 thành phố Ấn Độ (khoảng chung 14/06/2017–01/07/2020). Khí tượng tái phân tích lưới 0,25° từ Open-Meteo (không phải trạm đo mặt đất).
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-white border border-amber-300">
                    <div className="text-[10px] font-bold uppercase text-amber-800 mb-1">Bước 2 · Làm sạch &amp; Đặc trưng</div>
                    <div className="font-bold text-slate-900 mb-1">Không nội suy AQI · Mask ô nội suy</div>
                    <p className="text-[11px] text-slate-600 leading-snug">
                      Nội suy ≤14 ngày cho EDA hồi cứu; khi tạo đặc trưng dự báo, ô chất ô nhiễm đã nội suy bị đặt lại <code className="font-mono">NaN</code> + <code className="font-mono">ffill≤2d</code>. <em>(F01 vẫn đang mở)</em>.
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-white border border-slate-200">
                    <div className="text-[10px] font-bold uppercase text-indigo-700 mb-1">Bước 3 · Chia theo Ngày đích</div>
                    <div className="font-bold text-slate-900 mb-1">Train / Test / Holdout</div>
                    <p className="text-[11px] text-slate-600 leading-snug">
                      Chia theo <code className="font-mono">Date_target (t+1)</code>: Train ≤30/06/2019 (n=5.741); Test 01/07/2019–29/02/2020 (n=1.947); Holdout ≥01/03/2020 (n=975).
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-white border border-slate-200">
                    <div className="text-[10px] font-bold uppercase text-indigo-700 mb-1">Bước 4 · Chọn Siêu tham số</div>
                    <div className="font-bold text-slate-900 mb-1">TimeSeriesSplit trên Train</div>
                    <p className="text-[11px] text-slate-600 leading-snug">
                      4-fold CV (gap=16 dòng) chỉ trên Train để chọn <code className="font-mono">alpha</code> (L1=10, L2=0,1, L3=30) và ngưỡng F2 trên OOF Train (L3=166, Base=160).
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-white border border-slate-200">
                    <div className="text-[10px] font-bold uppercase text-indigo-700 mb-1">Bước 5 · Đánh giá Hồi cứu</div>
                    <div className="font-bold text-slate-900 mb-1">Bootstrap khối 14 ngày</div>
                    <p className="text-[11px] text-slate-600 leading-snug">
                      Chấm MAE, RMSE, Recall, Precision với KTC 95% bootstrap theo khối lịch 14 ngày chung giữa 8 thành phố (B=4.000, seed=0).
                    </p>
                  </div>
                </div>
              </div>

              {/* Biểu đồ Bậc thang MAE từ Baseline -> L1 -> L2 -> L3 (Y19) */}
              <div className="bg-white rounded-xl border border-slate-200 p-4">
                <h3 className="text-sm font-bold text-slate-900 mb-1">
                  Bậc thang Giảm Sai số MAE trên Tập Test (n = 1.947 cặp · 389 cặp nặng) (Y19)
                </h3>
                <p className="text-xs text-slate-600 mb-4">
                  Đối soát khớp 100% với <code className="font-mono">R2_B04_baseline_metrics.csv</code> và <code className="font-mono">V21_model_test_metrics.csv</code> (thấp hơn là tốt hơn).
                </p>

                <div className="space-y-2.5">
                  {testModels.map((m) => {
                    const widthPct = Math.min(100, (m.MAE / 66) * 100);
                    const isL3 = m.model === 'Ridge L3';
                    const isPersist = m.model === 'Ngày mai = hôm nay';
                    return (
                      <div key={m.model} className="text-xs">
                        <div className="flex items-center justify-between mb-1">
                          <span className={`${isL3 ? 'font-extrabold text-indigo-950' : isPersist ? 'font-bold text-slate-900' : 'font-medium text-slate-700'}`}>
                            {m.model}
                            {isL3 && (
                              <span className="ml-2 px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-900 text-[10px] font-bold">
                                Mô hình chính (-16,8% MAE so với Hôm nay)
                              </span>
                            )}
                          </span>
                          <span className="font-mono text-slate-800">
                            MAE = <strong>{vnNum(m.MAE, 2)}</strong> · RMSE = {vnNum(m.RMSE, 2)} · R² = {vnNum(m.R2, 2)} (Ngày nặng: {vnNum(m.MAE_heavy, 2)})
                          </span>
                        </div>
                        <div className="w-full h-5 bg-slate-100 rounded-md overflow-hidden border border-slate-200 relative">
                          <div
                            style={{ width: `${widthPct}%` }}
                            className={`h-full transition-all ${
                              isL3
                                ? 'bg-indigo-600'
                                : isPersist
                                  ? 'bg-slate-600'
                                  : 'bg-slate-400'
                            }`}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Bảng hiệu số cùng mẫu kèm KTC 95% khối 14 ngày */}
                <div className="mt-4 pt-3 border-t border-slate-200 grid grid-cols-1 md:grid-cols-4 gap-2.5 text-xs">
                  {DEMO_DATA.summaryMetrics.pairedMae
                    .filter((p) => p.split === 'test' && p.block_days === 14)
                    .map((p) => (
                      <div key={`${p.modelA}-${p.modelB}`} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                        <div className="font-bold text-slate-800">
                          {p.modelA} − {p.modelB}
                        </div>
                        <div className="text-sm font-extrabold font-mono text-indigo-900 my-0.5">
                          ΔMAE = {vnNum(p.dMAE, 2)} điểm
                        </div>
                        <div className="text-[11px] font-mono text-slate-600">
                          KTC 95%: [{vnNum(p.lo, 2)}; {vnNum(p.hi, 2)}]
                        </div>
                        <div className="mt-1">
                          <span
                            className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                              p.verdict === 'tách khỏi 0'
                                ? 'bg-teal-100 text-teal-900'
                                : 'bg-amber-100 text-amber-900'
                            }`}
                          >
                            {p.verdict}
                          </span>
                        </div>
                      </div>
                    ))}
                </div>

                <div className="mt-3 p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-950 leading-relaxed">
                  <strong>Diễn giải trung thực (Y19 &amp; Báo cáo RA F03):</strong> Trên tập Test, việc bổ sung chất ô nhiễm (<code className="font-mono">L2 − L1 = -2,02</code>) và thời tiết (<code className="font-mono">L3 − L2 = -1,40</code>) đều giúp giảm MAE có ý nghĩa thống kê. Tuy nhiên, <strong>MAE giảm không chứng minh thời tiết tạo thêm lợi thế ở bước cảnh báo ngưỡng 201</strong> (ở bài toán cảnh báo, L3 so với L2 có chênh lệch recall và precision chứa 0; lợi thế cảnh báo so với baseline chủ yếu đến từ chất ô nhiễm và lịch sử AQI).
                </div>
              </div>
            </div>
          )}

          {/* =====================================================================
              TAB 3: BẢNG ĐỐI CHIẾU TEST / HOLDOUT (Y06, Y22) & NHÓM THÀNH PHỐ (Y18)
             ===================================================================== */}
          {activeTab === 'tables' && (
            <div className="space-y-5">
              {/* Khối so sánh Test vs Holdout + Giải trình 2 phiên bản CI Holdout */}
              <div className="bg-white rounded-xl border border-slate-200 p-4">
                <h3 className="text-sm font-bold text-slate-900 mb-1">
                  Bảng Bằng chứng Tập Test và Tập Holdout kèm Khoảng Tin Cậy (Y06 · Y22)
                </h3>
                <p className="text-xs text-slate-600 mb-3">
                  Tách biệt hoàn toàn hai giai đoạn theo ngày đích <code className="font-mono">t+1</code>; không gộp chung kết quả. Lưu ý: Tập Test đã được dùng cho nhiều phân tích độ nhạy trong quá trình nghiên cứu.
                </p>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs border-collapse border border-slate-200">
                    <thead>
                      <tr className="bg-slate-100 text-slate-800">
                        <th className="p-2 border border-slate-200 text-left">Giai đoạn (theo ngày đích t+1)</th>
                        <th className="p-2 border border-slate-200 text-right">Cỡ mẫu (cặp)</th>
                        <th className="p-2 border border-slate-200 text-right">Cặp ngày nặng (≥201)</th>
                        <th className="p-2 border border-slate-200 text-right">MAE Hôm nay (Baseline)</th>
                        <th className="p-2 border border-slate-200 text-right">MAE Ridge L3</th>
                        <th className="p-2 border border-slate-200 text-right">ΔMAE (L3 − Hôm nay)</th>
                        <th className="p-2 border border-slate-200 text-center">KTC 95% (Khối 14 ngày)</th>
                        <th className="p-2 border border-slate-200 text-left">Kết luận thống kê</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="bg-white">
                        <td className="p-2 border border-slate-200 font-bold">
                          Tập Test chính (01/07/2019 – 29/02/2020)
                        </td>
                        <td className="p-2 border border-slate-200 text-right font-mono">1.947</td>
                        <td className="p-2 border border-slate-200 text-right font-mono font-bold">389 (20,0%)</td>
                        <td className="p-2 border border-slate-200 text-right font-mono">23,47</td>
                        <td className="p-2 border border-slate-200 text-right font-mono font-bold text-indigo-900">19,52</td>
                        <td className="p-2 border border-slate-200 text-right font-mono font-bold text-teal-800">-3,95</td>
                        <td className="p-2 border border-slate-200 text-center font-mono">[-5,40; -2,56]</td>
                        <td className="p-2 border border-slate-200">
                          <span className="px-2 py-0.5 rounded bg-teal-100 text-teal-900 font-bold">
                            Cải thiện rõ (Tách khỏi 0)
                          </span>
                        </td>
                      </tr>
                      <tr className="bg-indigo-50/40">
                        <td className="p-2 border border-slate-200 font-bold">
                          Holdout toàn kỳ (01/03/2020 – 01/07/2020)
                        </td>
                        <td className="p-2 border border-slate-200 text-right font-mono">975</td>
                        <td className="p-2 border border-slate-200 text-right font-mono font-bold">18 (1,8%)</td>
                        <td className="p-2 border border-slate-200 text-right font-mono">14,80</td>
                        <td className="p-2 border border-slate-200 text-right font-mono font-bold text-indigo-900">13,78</td>
                        <td className="p-2 border border-slate-200 text-right font-mono font-bold">-1,02</td>
                        <td className="p-2 border border-slate-200 text-center font-mono">
                          [-2,70; +0,48] <span className="text-[10px] text-slate-500">(RA/DA)</span><br />
                          <span className="text-[10px] text-slate-500">hoặc [-2,80; +0,50] (script)</span>
                        </td>
                        <td className="p-2 border border-slate-200">
                          <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-950 font-bold">
                            Chưa đủ bằng chứng về lợi thế (Chứa 0)
                          </span>
                        </td>
                      </tr>
                      {/* Hai giai đoạn con của Holdout theo V24_model_holdout_by_period.csv */}
                      {DEMO_DATA.summaryMetrics.holdoutSubperiods.map((sub) => (
                        <tr key={sub.period} className="bg-slate-50/70 text-slate-600">
                          <td className="p-2 border border-slate-200 pl-5">
                            ↳ {sub.period}
                          </td>
                          <td className="p-2 border border-slate-200 text-right font-mono">{sub.n}</td>
                          <td className="p-2 border border-slate-200 text-right font-mono">{sub.heavy}</td>
                          <td className="p-2 border border-slate-200 text-right font-mono">{vnNum(sub.mae_base, 2)}</td>
                          <td className="p-2 border border-slate-200 text-right font-mono">{vnNum(sub.mae_l3, 2)}</td>
                          <td className="p-2 border border-slate-200 text-right font-mono">{vnNum(sub.d_l3_base, 2)}</td>
                          <td className="p-2 border border-slate-200 text-center font-mono">
                            [{vnNum(sub.d_l3_base_lo, 2)}; {vnNum(sub.d_l3_base_hi, 2)}]
                          </td>
                          <td className="p-2 border border-slate-200 text-[11px]">
                            Phân kỳ theo mốc phong tỏa toàn quốc 25/03/2020 (V24)
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Hộp đối chiếu minh bạch 2 phiên bản KTC Holdout theo yêu cầu #4 của Prompt */}
                <div className="mt-3 p-3 rounded-lg bg-indigo-50 border border-indigo-200 text-xs text-indigo-950 leading-relaxed">
                  <div className="font-bold mb-1">
                    Đối chiếu phương pháp / phiên bản Khoảng tin cậy Holdout (Yêu cầu #4):
                  </div>
                  <p>
                    • <strong>Báo cáo RA &amp; Artifact DA (<code className="font-mono">R2_B04_baseline_paired_mae.csv</code> / <code className="font-mono">V24</code>):</strong> cho <code className="font-mono font-bold">[-2,70; +0,48]</code> (chính xác <code className="font-mono">[-2,702124; +0,483098]</code>), tính bằng hàm <code className="font-mono">block_boot</code> chuẩn của dự án (<code className="font-mono">src/model_utils.py</code>: chia 9 khối lịch 14 ngày từ 01/03/2020, <code className="font-mono">B=4.000, seed=0</code>, lấy tổng sai số chia tổng số dòng thực tế trong mẫu bootstrap).<br />
                    • <strong>Biến thể Script trong hồ sơ rà soát:</strong> cho <code className="font-mono font-bold">[-2,80; +0,50]</code> khi lấy trung bình không trọng số giữa các khối (do khối thứ 9 ở cuối kỳ và 9 ngày khuyết tại Amritsar có số dòng ít hơn các khối 14 ngày đầy đủ).<br />
                    • <strong>Kết luận chung:</strong> Cả hai phiên bản đều chứa 0 (và cũng chứa 0 khi thử khối 7 ngày <code className="font-mono">[-2,59; +0,46]</code> hay 28 ngày <code className="font-mono">[-2,55; +0,53]</code> ở S06). Do đó cần diễn đạt chính xác là <strong>"chưa đủ bằng chứng về lợi thế trên holdout"</strong>, không kết luận hai mô hình tương đương hay mô hình chắc chắn vô ích.
                  </p>
                </div>
              </div>

              {/* Khối Ngữ cảnh cỡ mẫu cảnh báo theo 3 Nhóm Thành phố (Y18) */}
              <div className="bg-white rounded-xl border border-slate-200 p-4">
                <h3 className="text-sm font-bold text-slate-900 mb-1">
                  Bảng Cảnh báo theo 3 Nhóm Thành phố trên Tập Test &amp; Quy ước Cỡ mẫu &lt; 30 (Y18)
                </h3>
                <p className="text-xs text-slate-600 mb-3">
                  Đối soát với Notebook 06 (Cell 40). <strong>Quy ước thận trọng của dự án (W12):</strong> Nhóm có dưới 30 cặp ngày nặng trong tập đánh giá thì <strong>không báo tỷ lệ recall/precision</strong> (ghi <code className="font-mono">NaN</code>) để tránh suy diễn từ cỡ mẫu quá nhỏ.
                </p>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs border-collapse border border-slate-200">
                    <thead>
                      <tr className="bg-slate-100 text-slate-800">
                        <th className="p-2 border border-slate-200 text-left">Nhóm thành phố (Gộp trên Tập Test)</th>
                        <th className="p-2 border border-slate-200 text-right">Tổng cặp (n)</th>
                        <th className="p-2 border border-slate-200 text-right">Cặp ngày nặng (≥201)</th>
                        <th className="p-2 border border-slate-200 text-center">Baseline @201 (Rec / Prec)</th>
                        <th className="p-2 border border-slate-200 text-center">Baseline @160 (Rec / Prec)</th>
                        <th className="p-2 border border-slate-200 text-center">Ridge L3 @201 (Rec / Prec)</th>
                        <th className="p-2 border border-slate-200 text-center">Ridge L3 @166 (Rec / Prec)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {DEMO_DATA.summaryMetrics.cityGroups.map((g) => (
                        <tr key={g.groupKey} className="bg-white">
                          <td className="p-2 border border-slate-200 font-bold">{g.groupName}</td>
                          <td className="p-2 border border-slate-200 text-right font-mono">{g.test.n}</td>
                          <td className="p-2 border border-slate-200 text-right font-mono font-bold">
                            {g.test.heavy}{' '}
                            {!g.test.enoughSample30 && (
                              <span className="text-[10px] px-1 py-0.2 rounded bg-rose-100 text-rose-800">
                                &lt; 30
                              </span>
                            )}
                          </td>
                          {g.test.enoughSample30 ? (
                            <>
                              <td className="p-2 border border-slate-200 text-center font-mono">
                                {vnNum(g.test.base_201.recall, 2)} / {vnNum(g.test.base_201.precision, 2)}
                              </td>
                              <td className="p-2 border border-slate-200 text-center font-mono">
                                {vnNum(g.test.base_f2.recall, 2)} / {vnNum(g.test.base_f2.precision, 2)}
                              </td>
                              <td className="p-2 border border-slate-200 text-center font-mono">
                                {vnNum(g.test.l3_201.recall, 2)} / {vnNum(g.test.l3_201.precision, 2)}
                              </td>
                              <td className="p-2 border border-slate-200 text-center font-mono font-bold text-indigo-900">
                                {vnNum(g.test.l3_f2.recall, 2)} / {vnNum(g.test.l3_f2.precision, 2)}
                              </td>
                            </>
                          ) : (
                            <td colSpan={4} className="p-2 border border-slate-200 text-center text-rose-800 bg-rose-50/50 font-medium">
                              NaN — Chỉ có {g.test.heavy} cặp ngày nặng (&lt; 30): Không đủ cỡ mẫu đánh giá tỷ lệ cảnh báo ở Nam Ấn
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Bảng chi tiết từng thành phố (V23_model_by_city.csv) */}
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mt-4 mb-2">
                  Chi tiết Sai số từng Thành phố trên Tập Test (<code className="font-mono">V23_model_by_city.csv</code>) &amp; Holdout:
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs border-collapse border border-slate-200">
                    <thead>
                      <tr className="bg-slate-50 text-slate-700">
                        <th className="p-2 border border-slate-200 text-left">Thành phố</th>
                        <th className="p-2 border border-slate-200 text-right">Test: n (nặng)</th>
                        <th className="p-2 border border-slate-200 text-right">Test: MAE Hôm nay</th>
                        <th className="p-2 border border-slate-200 text-right">Test: MAE L3</th>
                        <th className="p-2 border border-slate-200 text-center">Test: ΔMAE L3−Base [KTC 95%]</th>
                        <th className="p-2 border border-slate-200 text-right">Holdout: n (nặng)</th>
                        <th className="p-2 border border-slate-200 text-right">Holdout: MAE Base → L3</th>
                      </tr>
                    </thead>
                    <tbody>
                      {DEMO_DATA.cities.map((c) => (
                        <tr
                          key={c.id}
                          className={c.id === selectedCity ? 'bg-indigo-50/70 font-semibold' : 'bg-white'}
                        >
                          <td className="p-2 border border-slate-200 font-bold">
                            {c.id === selectedCity ? `★ ${c.name}` : c.name}
                          </td>
                          <td className="p-2 border border-slate-200 text-right font-mono">
                            {c.splits.test.n} ({c.splits.test.heavy})
                          </td>
                          <td className="p-2 border border-slate-200 text-right font-mono">
                            {vnNum(c.splits.test.mae_base, 2)}
                          </td>
                          <td className="p-2 border border-slate-200 text-right font-mono font-bold text-indigo-900">
                            {vnNum(c.splits.test.mae_l3, 2)}
                          </td>
                          <td className="p-2 border border-slate-200 text-center font-mono">
                            {vnNum(c.splits.test.d_l3_base, 2)} [{vnNum(c.splits.test.d_l3_base_lo, 2)}; {vnNum(c.splits.test.d_l3_base_hi, 2)}]
                          </td>
                          <td className="p-2 border border-slate-200 text-right font-mono">
                            {c.splits.holdout.n} ({c.splits.holdout.heavy})
                          </td>
                          <td className="p-2 border border-slate-200 text-right font-mono">
                            {vnNum(c.splits.holdout.mae_base, 2)} → {vnNum(c.splits.holdout.mae_l3, 2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="mt-2.5 flex items-start gap-1.5 text-[11px] text-slate-600">
                  <Info className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
                  <span>
                    <strong>Caveat bắt buộc (Quy tắc #7):</strong> Không gán recall/precision của nhóm thành phố thành kết quả riêng của từng thành phố. Ngưỡng &lt;30 là quy ước thận trọng của dự án, không phải định lý thống kê phổ quát. Không xem khoảng tin cậy của MAE là khoảng dự báo cho từng ngày.
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* =====================================================================
              TAB 4: HẠN CHẾ PHƯƠNG PHÁP (F01 / F02) & HỒ SƠ ĐỐI SOÁT DỮ LIỆU (Y40, Y42)
             ===================================================================== */}
          {activeTab === 'audit' && (
            <div className="space-y-5">
              {/* Trạng thái thật của F01 & F02 */}
              <div className="bg-amber-50/80 rounded-xl border border-amber-300 p-4 space-y-3">
                <div className="flex items-center gap-2 text-amber-950">
                  <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0" />
                  <h3 className="text-sm font-bold">
                    Báo cáo Trung thực về Hạn chế Phương pháp &amp; Rò rỉ Dữ liệu (Quy tắc #7 · F01 / F02 · Y40)
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  <div className="p-3.5 rounded-lg bg-white border border-amber-200">
                    <div className="font-bold text-rose-900 mb-1">
                      1. Trạng thái P0 / F01 — Chưa tuyên bố hết rò rỉ dữ liệu (Leakage) đầu–cuối:
                    </div>
                    <p className="text-slate-700 leading-relaxed">
                      • Trong mã nguồn baseline (<code className="font-mono">src/model_utils.py</code>), tham số <code className="font-mono">as_of</code> cắt trên <strong>bảng đã làm sạch hồi cứu</strong> (<code className="font-mono">air_quality_8cities.csv</code> — vốn đã dùng nội suy tuyến tính ≤14 ngày và gắn cờ ngoại lai theo tháng trên toàn chuỗi), nên chưa chứng minh nhân quả hoàn toàn từ dữ liệu thô (<code className="font-mono">city_day.csv</code>).<br />
                      • Khi DA kiểm thử walk-forward từ dữ liệu thô cắt tại <code className="font-mono">t</code> (<code className="font-mono">V07</code>), có <strong>57/8.912 dòng</strong> đặc trưng thay đổi (40 dòng nằm trong tập Train trước 12/2018; 0 dòng trong Test/Holdout). Biến thể feature-as-of cho MAE Test L3 là <strong>19,517</strong> so với <strong>19,519</strong> của baseline.<br />
                      • Trong Notebook 06 (Phần I, Y40), thử nghiệm độ nhạy tĩnh giữa đặt lại <code className="font-mono">NaN</code> ô nội suy (<code className="font-mono">mask_interp=True</code>, MAE L3 = 19,52) và giữ ô nội suy (<code className="font-mono">mask_interp=False</code>, MAE L3 = 19,55) chỉ đổi 1,1% số dòng và chênh 0,03 điểm MAE. Đây là kiểm tra độ nhạy tĩnh, <strong>không phải công tắc bật/tắt rò rỉ</strong> và <strong>không đóng F01</strong>.
                    </p>
                  </div>

                  <div className="p-3.5 rounded-lg bg-white border border-amber-200">
                    <div className="font-bold text-slate-900 mb-1">
                      2. Các giới hạn phạm vi &amp; vận hành khác đã ghi nhận trong báo cáo RA:
                    </div>
                    <ul className="space-y-1.5 text-slate-700 list-disc pl-4 leading-relaxed">
                      <li>
                        <strong>P0 / F02 (Tái lập chuỗi Notebook 04):</strong> Bản gốc NB04 gọi API mạng dù đã có cache và bản sửa tạm vướng cú pháp f-string trên Python 3.11; nhánh ứng viên PR #4 của Dev chưa được DA/RA nghiệm thu đóng.
                      </li>
                      <li>
                        <strong>Đánh giá hồi cứu, không phải thời gian thực:</strong> Chưa có dữ liệu về giờ công bố AQI thực tế của CPCB trong ngày và độ trễ phát hành ERA5 (thường trễ 5 ngày); mọi kết quả là phát lại hồi cứu trên dữ liệu đã hoàn chỉnh.
                      </li>
                      <li>
                        <strong>Tương quan không gian Delhi – Gurugram:</strong> Hai thành phố nằm ở hai ô lưới ERA5 sát nhau (tương quan thời tiết ngày 0,95–0,999), không phải hai bằng chứng độc lập hoàn toàn (khi bỏ Gurugram, L3 vẫn giảm MAE -3,36 [-4,63; -2,11]).
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Bảng biên bản đối soát dữ liệu Demo (Y42) */}
              <div className="bg-white rounded-xl border border-slate-200 p-4">
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-teal-700" />
                    <h3 className="text-sm font-bold text-slate-900">
                      Biên bản Đối soát Dữ liệu Demo với Nguồn Dự án (<code className="font-mono">scripts/verify_demo_data.py</code> · Y42)
                    </h3>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-teal-100 text-teal-900 border border-teal-300">
                    Đã kiểm thực tế: PASS 100%
                  </span>
                </div>

                <p className="text-xs text-slate-600 mb-3">
                  Mọi con số trong demo được trích xuất trực tiếp từ các artifact đã ghim commit dưới đây (không tự tạo dự báo thay thế dữ liệu thiếu). Lưu ý: Khớp artifact đảm bảo tính chính xác của bản phát lại, không đồng nghĩa đã đóng F01.
                </p>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs border-collapse border border-slate-200">
                    <thead>
                      <tr className="bg-slate-100 text-slate-800">
                        <th className="p-2 border border-slate-200 text-left">Hạng mục đối soát</th>
                        <th className="p-2 border border-slate-200 text-left">File nguồn &amp; Commit SHA</th>
                        <th className="p-2 border border-slate-200 text-left">Kết quả đối soát</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="p-2 border border-slate-200 font-semibold">Dự báo từng ngày (Test + Holdout)</td>
                        <td className="p-2 border border-slate-200 font-mono text-[11px]">
                          {DEMO_DATA.provenance.predictions_artifact}<br />
                          Commit: <strong>{DEMO_DATA.provenance.predictions_commit.slice(0, 12)}</strong><br />
                          SHA256: {DEMO_DATA.provenance.predictions_sha256.slice(0, 24)}…
                        </td>
                        <td className="p-2 border border-slate-200">
                          <strong>2.922 dòng</strong>: 1.947 cặp Test (đích 01/07/2019–29/02/2020, 389 nặng) + 975 cặp Holdout (đích 01/03/2020–01/07/2020, 18 nặng).
                        </td>
                      </tr>
                      <tr>
                        <td className="p-2 border border-slate-200 font-semibold">Đối chiếu chéo Tập Test với V21 (v1.1)</td>
                        <td className="p-2 border border-slate-200 font-mono text-[11px]">
                          {DEMO_DATA.provenance.v21_crosscheck_artifact}<br />
                          Commit: <strong>{DEMO_DATA.provenance.v21_crosscheck_commit.slice(0, 12)}</strong>
                        </td>
                        <td className="p-2 border border-slate-200">
                          Khớp 1.947/1.947 khóa <code className="font-mono">(City, Date, Date_target)</code>; độ lệch tuyệt đối lớn nhất <code className="font-mono">5,00e-07</code> (do làm tròn 6 chữ số thập phân CSV).
                        </td>
                      </tr>
                      <tr>
                        <td className="p-2 border border-slate-200 font-semibold">Chuỗi AQI lịch thực &amp; Khí tượng ngày</td>
                        <td className="p-2 border border-slate-200 font-mono text-[11px]">
                          {DEMO_DATA.provenance.daily_aq_artifact}<br />
                          Commit: <strong>{DEMO_DATA.provenance.daily_aq_commit}</strong><br />
                          SHA256: {DEMO_DATA.provenance.daily_aq_sha256.slice(0, 24)}…
                        </td>
                        <td className="p-2 border border-slate-200">
                          Xác nhận đúng các ngày khuyết AQI tại Amritsar (3 ngày trong kỳ Test làm khuyết 5 cặp dự báo; 7 ngày trong kỳ Holdout làm khuyết 9 cặp dự báo). 7 thành phố còn lại đủ 100%.
                        </td>
                      </tr>
                      <tr>
                        <td className="p-2 border border-slate-200 font-semibold">MAE &amp; Ma trận cảnh báo (TP/FP/FN/TN)</td>
                        <td className="p-2 border border-slate-200 font-mono text-[11px]">
                          R2_B04_baseline_metrics.csv &amp; R2_B04_baseline_alerts.csv
                        </td>
                        <td className="p-2 border border-slate-200">
                          Test MAE L3 = <code className="font-mono">19,519018</code> (Base <code className="font-mono">23,466359</code>); Holdout MAE L3 = <code className="font-mono">13,783362</code> (Base <code className="font-mono">14,803077</code>). Test L3 @166: TP=377, FP=113, FN=12, TN=1445.
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
