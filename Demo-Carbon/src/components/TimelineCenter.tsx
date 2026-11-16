import React, { useState } from 'react';
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Bookmark,
  AlertCircle,
  ArrowRight,
  Layers,
} from 'lucide-react';
import {
  DEMO_DATA,
  SplitType,
  ThresholdMode,
  STORY_BOOKMARKS,
  StoryBookmark,
  getCityQuickCases,
  getPredictionRecord,
  formatDateVN,
  formatShortDateVN,
  getThresholds,
} from '../data/aqiHelpers';

interface TimelineCenterProps {
  selectedCity: string;
  split: SplitType;
  dateInput: string;
  dateTarget: string;
  thresholdMode: ThresholdMode;
  isRevealed: boolean;
  hideSpoilersOnBookmarks: boolean;
  onSelectBookmark: (city: string, split: SplitType, dateTarget: string, bookmarkId?: string) => void;
  onChangeSplit: (newSplit: SplitType) => void;
  onChangeDateTarget: (newDateTarget: string) => void;
  activeBookmarkId: string | null;
}

export const TimelineCenter: React.FC<TimelineCenterProps> = ({
  selectedCity,
  split,
  dateInput,
  dateTarget,
  thresholdMode,
  isRevealed,
  hideSpoilersOnBookmarks,
  onSelectBookmark,
  onChangeSplit,
  onChangeDateTarget,
  activeBookmarkId,
}) => {
  const [presetTab, setPresetTab] = useState<'story' | 'city'>('story');

  const calendarDates = DEMO_DATA.calendar[split];
  const currentIndex = Math.max(0, calendarDates.indexOf(dateTarget));
  const currentRecord = getPredictionRecord(selectedCity, dateTarget);
  const isCurrentMissing = currentRecord === null;

  // Tìm danh sách các ngày đích thiếu dữ liệu của thành phố đang chọn trong giai đoạn hiện tại
  const missingDatesForCity = calendarDates.filter((dt) => !getPredictionRecord(selectedCity, dt));

  const cityQuick = getCityQuickCases(selectedCity, split, thresholdMode);
  const thrInfo = getThresholds(thresholdMode);

  const handleStep = (delta: number) => {
    const nextIdx = currentIndex + delta;
    if (nextIdx >= 0 && nextIdx < calendarDates.length) {
      onChangeDateTarget(calendarDates[nextIdx]);
    }
  };

  return (
    <section
      aria-label="Trục thời gian t sang t+1 và bộ chọn ca tiêu biểu"
      className="bg-white rounded-xl border border-slate-200 shadow-xs p-3.5"
    >
      {/* Hàng 1: Chọn Giai đoạn Đánh giá (Test vs Holdout) + Hiển thị rõ cặp ngày t -> t+1 */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 pb-3 border-b border-slate-100">
        {/* Công tắc Test / Holdout (Kèm nhãn phạm vi ngày đích & cỡ mẫu rõ ràng) */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
            <Layers className="w-3.5 h-3.5" />
            Kỳ đánh giá (theo ngày đích t+1):
          </span>
          <div className="inline-flex rounded-lg bg-slate-100 p-1 border border-slate-200" role="group" aria-label="Chọn giai đoạn đánh giá">
            <button
              type="button"
              onClick={() => onChangeSplit('test')}
              className={`px-3 py-1.5 rounded-md text-xs transition cursor-pointer flex items-center gap-1.5 ${
                split === 'test'
                  ? 'bg-slate-900 text-white font-bold shadow-2xs'
                  : 'text-slate-700 hover:text-slate-900 font-medium'
              }`}
            >
              <span>Tập Test chính</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${split === 'test' ? 'bg-slate-700 text-amber-300' : 'bg-slate-200 text-slate-600'}`}>
                01/07/2019–29/02/2020 · n=1.947 (389 nặng)
              </span>
            </button>
            <button
              type="button"
              onClick={() => onChangeSplit('holdout')}
              className={`px-3 py-1.5 rounded-md text-xs transition cursor-pointer flex items-center gap-1.5 ${
                split === 'holdout'
                  ? 'bg-indigo-950 text-white font-bold shadow-2xs'
                  : 'text-slate-700 hover:text-slate-900 font-medium'
              }`}
            >
              <span>Holdout đối chiếu</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${split === 'holdout' ? 'bg-indigo-800 text-indigo-100' : 'bg-slate-200 text-slate-600'}`}>
                01/03–01/07/2020 · n=975 (18 nặng)
              </span>
            </button>
          </div>
        </div>

        {/* Khối phân biệt rõ Ngày đầu vào t và Ngày dự báo / Ngày đích t+1 */}
        <div className="flex items-center gap-2 bg-slate-50 border border-slate-200/90 rounded-lg px-3 py-1.5">
          <div className="text-left">
            <div className="text-[10px] font-semibold uppercase text-slate-500">
              Ngày đầu vào <code className="font-mono font-bold text-slate-800">t</code> (Khóa đầu vào)
            </div>
            <div className="text-sm font-bold text-slate-900 font-mono">
              {formatDateVN(dateInput)}
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400 shrink-0 mx-1" />
          <div className="text-left pl-2 border-l border-slate-200">
            <div className="text-[10px] font-semibold uppercase text-indigo-700">
              Ngày dự báo / Đích <code className="font-mono font-bold text-indigo-900">t+1</code>
            </div>
            <div className="text-sm font-bold text-indigo-950 font-mono flex items-center gap-1.5">
              <span>{formatDateVN(dateTarget)}</span>
              {isCurrentMissing && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-100 text-rose-800 border border-rose-300 font-sans font-bold">
                  Khuyết DL
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Ghi chú ngữ cảnh khi đang ở chế độ Holdout (Không gọi toàn bộ từ 01/03 là phong tỏa) */}
      {split === 'holdout' && (
        <div className="mt-2.5 px-3 py-1.5 rounded-lg bg-indigo-50/90 border border-indigo-200 text-indigo-950 text-xs flex flex-wrap items-center justify-between gap-2">
          <span>
            <strong>Chế độ Holdout (Giai đoạn giữ lại cuối):</strong> Chỉ dùng đối chiếu hồi cứu, <em>không dùng để chọn mô hình hay ngưỡng</em>. Lưu ý: 01/03–24/03/2020 là <strong>trước phong tỏa toàn quốc</strong> (n=190, 6 cặp nặng); từ <strong>25/03/2020</strong> mới bắt đầu phong tỏa toàn quốc (n=785, 12 cặp nặng).
          </span>
          <span className="font-mono text-[11px] bg-white px-2 py-0.5 rounded border border-indigo-200 font-semibold">
            {dateTarget < '2020-03-25' ? 'Đang xem: Trước phong tỏa (01–24/03)' : 'Đang xem: Từ ngày phong tỏa (≥25/03)'}
          </span>
        </div>
      )}

      {/* Hàng 2: Thanh kéo Timeline tương tác + Nút tiến/lùi từng ngày lịch + Chọn ngày tự do */}
      <div className="mt-3 flex flex-col md:flex-row items-stretch md:items-center gap-3">
        <div className="flex items-center gap-1.5 shrink-0">
          <button
            type="button"
            onClick={() => handleStep(-1)}
            disabled={currentIndex <= 0}
            className="px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed text-xs font-semibold text-slate-800 flex items-center gap-1 cursor-pointer"
            title="Lùi 1 ngày lịch (Phím mũi tên trái ←)"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Ngày trước</span>
          </button>
          <button
            type="button"
            onClick={() => handleStep(1)}
            disabled={currentIndex >= calendarDates.length - 1}
            className="px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed text-xs font-semibold text-slate-800 flex items-center gap-1 cursor-pointer"
            title="Tiến 1 ngày lịch (Phím mũi tên phải →)"
          >
            <span>Ngày tiếp</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Thanh kéo ngày đích t+1 kèm vạch đánh dấu khoảng trống thật (nếu có) */}
        <div className="flex-1 flex flex-col justify-center">
          <div className="flex items-center justify-between text-[11px] text-slate-600 mb-1">
            <span>
              Đích bắt đầu: <strong className="font-mono text-slate-800">{formatDateVN(calendarDates[0])}</strong>
            </span>
            <span className="font-medium text-slate-700">
              Ngày lịch thứ <strong>{currentIndex + 1}</strong> / {calendarDates.length} tại <strong>{selectedCity}</strong>
              {missingDatesForCity.length > 0 && (
                <span className="ml-1.5 text-rose-700 font-semibold">
                  ({missingDatesForCity.length} ngày đích khuyết phát lại được đánh dấu đỏ trên trục)
                </span>
              )}
            </span>
            <span>
              Đích kết thúc: <strong className="font-mono text-slate-800">{formatDateVN(calendarDates[calendarDates.length - 1])}</strong>
            </span>
          </div>

          <div className="relative flex items-center">
            <input
              type="range"
              min={0}
              max={calendarDates.length - 1}
              value={currentIndex}
              onChange={(e) => {
                const idx = Number(e.target.value);
                if (calendarDates[idx]) {
                  onChangeDateTarget(calendarDates[idx]);
                }
              }}
              aria-label="Kéo chọn ngày đích t+1 trên trục thời gian"
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-900"
            />
            {/* Đánh dấu vị trí các ngày thiếu dữ liệu thực tế trên thanh timeline (cho Amritsar) */}
            {missingDatesForCity.map((mDate) => {
              const mIdx = calendarDates.indexOf(mDate);
              if (mIdx < 0) return null;
              const leftPct = (mIdx / Math.max(1, calendarDates.length - 1)) * 100;
              return (
                <span
                  key={mDate}
                  style={{ left: `${leftPct}%` }}
                  className="pointer-events-none absolute -top-1 w-1.5 h-4 bg-rose-600 rounded-xs border border-white"
                  title={`Ngày đích thiếu dữ liệu phát lại: ${formatDateVN(mDate)}`}
                />
              );
            })}
          </div>
        </div>

        {/* Bộ chọn ngày đích tự do bằng input date */}
        <div className="flex items-center gap-1.5 shrink-0">
          <label htmlFor="free-target-date" className="text-xs font-semibold text-slate-700 flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5 text-slate-500" />
            <span>Chọn đích t+1:</span>
          </label>
          <input
            id="free-target-date"
            type="date"
            min={calendarDates[0]}
            max={calendarDates[calendarDates.length - 1]}
            value={dateTarget}
            onChange={(e) => {
              const val = e.target.value;
              if (calendarDates.includes(val)) {
                onChangeDateTarget(val);
              }
            }}
            className="px-2 py-1 text-xs font-mono font-semibold border border-slate-300 rounded-lg bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900"
          />
        </div>
      </div>

      {/* Hàng 3: Các mốc tiêu biểu đã kiểm chứng (Y02, Y37) */}
      <div className="mt-3 pt-2.5 border-t border-slate-100">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-1.5">
            <div className="inline-flex rounded-lg bg-slate-100 p-0.5 border border-slate-200 text-xs">
              <button
                type="button"
                onClick={() => setPresetTab('story')}
                className={`px-2.5 py-1 rounded-md transition flex items-center gap-1 cursor-pointer ${
                  presetTab === 'story' ? 'bg-white text-slate-900 font-bold shadow-2xs' : 'text-slate-600 hover:text-slate-900 font-medium'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                <span>Kịch bản thuyết trình (Báo đúng → Bỏ sót → Báo nhầm + Ca biên)</span>
              </button>
              <button
                type="button"
                onClick={() => setPresetTab('city')}
                className={`px-2.5 py-1 rounded-md transition flex items-center gap-1 cursor-pointer ${
                  presetTab === 'city' ? 'bg-white text-slate-900 font-bold shadow-2xs' : 'text-slate-600 hover:text-slate-900 font-medium'
                }`}
              >
                <Bookmark className="w-3.5 h-3.5 text-indigo-600" />
                <span>Ca minh họa riêng của {selectedCity} ({split === 'test' ? 'Test' : 'Holdout'})</span>
              </button>
            </div>
          </div>

          <span className="text-[11px] text-slate-500 italic flex items-center gap-1">
            <AlertCircle className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span>Các ca dưới đây là ví dụ minh họa có thật đã kiểm chứng, <strong>không đại diện toàn bộ tập</strong>.</span>
          </span>
        </div>

        {presetTab === 'story' ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-1.5">
            {STORY_BOOKMARKS.map((bm: StoryBookmark) => {
              const isActive =
                activeBookmarkId === bm.id ||
                (selectedCity === bm.city && dateTarget === bm.dateTarget && split === bm.split);
              const showNeutral = hideSpoilersOnBookmarks && !isRevealed;

              return (
                <button
                  key={bm.id}
                  type="button"
                  onClick={() => onSelectBookmark(bm.city, bm.split, bm.dateTarget, bm.id)}
                  className={`p-2 rounded-lg border text-left transition flex flex-col justify-between cursor-pointer ${
                    isActive
                      ? 'bg-slate-900 text-white border-slate-900 ring-2 ring-slate-900/20'
                      : 'bg-slate-50/80 hover:bg-slate-100 text-slate-800 border-slate-200'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between gap-1 text-[10px] font-bold uppercase tracking-tight mb-0.5">
                      <span className={isActive ? 'text-amber-300' : 'text-slate-500'}>{bm.stepBadge}</span>
                      <span className={`font-mono px-1 rounded ${isActive ? 'bg-slate-800 text-slate-200' : 'bg-slate-200/80 text-slate-700'}`}>
                        {bm.city}
                      </span>
                    </div>
                    <div className="text-xs font-bold leading-snug line-clamp-2">
                      {showNeutral ? bm.titleNeutral : bm.titleRevealed}
                    </div>
                  </div>
                  <div className={`text-[10px] font-mono mt-1 pt-1 border-t ${isActive ? 'border-slate-700 text-slate-300' : 'border-slate-200/80 text-slate-500'}`}>
                    t={formatShortDateVN(bm.dateInput)} → t+1={formatDateVN(bm.dateTarget)}
                  </div>
                </button>
              );
            })}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2">
            {(
              [
                { key: 'TP', label: '✓ Báo đúng (TP)', rec: cityQuick.TP, desc: `Dự báo ≥ ${thrInfo.l3} & Thực tế ≥ 201` },
                { key: 'FN', label: '▲ Bỏ sót (FN)', rec: cityQuick.FN, desc: `Dự báo < ${thrInfo.l3} nhưng Thực tế ≥ 201` },
                { key: 'FP', label: '! Báo nhầm (FP)', rec: cityQuick.FP, desc: `Dự báo ≥ ${thrInfo.l3} nhưng Thực tế < 201` },
                { key: 'TN', label: '○ Không cảnh báo đúng (TN)', rec: cityQuick.TN, desc: `Dự báo < ${thrInfo.l3} & Thực tế < 201` },
              ] as const
            ).map((item) => {
              const r = item.rec;
              const isSel = r && r.c === selectedCity && r.t1 === dateTarget;
              return (
                <button
                  key={item.key}
                  type="button"
                  disabled={!r}
                  onClick={() => {
                    if (r) onSelectBookmark(r.c, r.s, r.t1);
                  }}
                  className={`p-2 rounded-lg border text-left transition flex flex-col justify-between ${
                    !r
                      ? 'bg-slate-50 text-slate-400 border-slate-200 cursor-not-allowed'
                      : isSel
                        ? 'bg-slate-900 text-white border-slate-900 cursor-pointer font-semibold'
                        : 'bg-white hover:bg-slate-50 text-slate-800 border-slate-200 cursor-pointer'
                  }`}
                >
                  <div>
                    <div className="text-xs font-bold">
                      {hideSpoilersOnBookmarks && !isRevealed ? `Ca mẫu (${item.key}) tại ${selectedCity}` : item.label}
                    </div>
                    <div className={`text-[10px] mt-0.5 ${isSel ? 'text-slate-300' : 'text-slate-500'}`}>
                      {r ? item.desc : `Không có ca ${item.key} cho ${selectedCity} ở tập ${split}`}
                    </div>
                  </div>
                  {r && (
                    <div className={`text-[11px] font-mono mt-1.5 pt-1 border-t ${isSel ? 'border-slate-700 text-amber-300' : 'border-slate-100 text-slate-700'}`}>
                      t={formatShortDateVN(r.t)} → t+1={formatDateVN(r.t1)}
                    </div>
                  )}
                </button>
              );
            })}

            {/* Ô nhảy tới ngày thiếu dữ liệu của thành phố hiện tại (nếu có — tức Amritsar) */}
            <button
              type="button"
              disabled={!cityQuick.missingTargetDate}
              onClick={() => {
                if (cityQuick.missingTargetDate) {
                  onSelectBookmark(selectedCity, split, cityQuick.missingTargetDate);
                }
              }}
              className={`p-2 rounded-lg border text-left transition flex flex-col justify-between ${
                !cityQuick.missingTargetDate
                  ? 'bg-slate-50 text-slate-400 border-slate-200 cursor-not-allowed'
                  : dateTarget === cityQuick.missingTargetDate
                    ? 'bg-rose-900 text-white border-rose-900 cursor-pointer'
                    : 'bg-rose-50/70 hover:bg-rose-100/80 text-rose-950 border-rose-200 cursor-pointer'
              }`}
            >
              <div>
                <div className="text-xs font-bold">⊘ Ngày khuyết phát lại</div>
                <div className={`text-[10px] mt-0.5 ${dateTarget === cityQuick.missingTargetDate ? 'text-rose-200' : 'text-slate-500'}`}>
                  {cityQuick.missingTargetDate
                    ? `${selectedCity} có ${missingDatesForCity.length} ngày đích khuyết ở ${split}`
                    : `${selectedCity} đủ 100% ngày ở tập ${split}`}
                </div>
              </div>
              {cityQuick.missingTargetDate && (
                <div className="text-[11px] font-mono mt-1.5 pt-1 border-t border-rose-200/60 font-semibold">
                  Đích t+1 = {formatDateVN(cityQuick.missingTargetDate)}
                </div>
              )}
            </button>
          </div>
        )}
      </div>
    </section>
  );
};
