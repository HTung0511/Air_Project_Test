import { useState, useEffect, useCallback } from 'react';
import {
  Wind,
  BookOpen,
  FileText,
  Eye,
  EyeOff,
  CheckCircle2,
  Sliders,
  ShieldAlert,
} from 'lucide-react';
import {
  DEMO_DATA,
  SplitType,
  ThresholdMode,
  MapValueMode,
  STORY_BOOKMARKS,
  getPredictionRecord,
  getInputDateFromTarget,
  getThresholds,
  formatDateVN,
} from './data/aqiHelpers';
import { IndiaMiniMap } from './components/IndiaMiniMap';
import { TimelineCenter } from './components/TimelineCenter';
import { TwoLaneRulerAndOutcome } from './components/TwoLaneRulerAndOutcome';
import { HistoricalStripChart } from './components/HistoricalStripChart';
import { DetailDrawerModal, DetailTabKey } from './components/DetailDrawerModal';
import { PresenterGuideModal } from './components/PresenterGuideModal';

export function App() {
  // Khởi tạo ở Ca 1 tiêu biểu đã kiểm chứng: Gurugram t=19/11/2019 -> t+1=20/11/2019 (Tập Test)
  const [selectedCity, setSelectedCity] = useState<string>('Gurugram');
  const [split, setSplit] = useState<SplitType>('test');
  const [dateTarget, setDateTarget] = useState<string>('2019-11-20');
  // Lưu nhớ ngày đang xem gần nhất của từng tập để khi chuyển qua lại Test <-> Holdout vẫn mượt
  const [lastDateBySplit, setLastDateBySplit] = useState<Record<SplitType, string>>({
    test: '2019-11-20',
    holdout: '2020-05-27',
  });

  const [thresholdMode, setThresholdMode] = useState<ThresholdMode>('f2');
  const [isRevealed, setIsRevealed] = useState<boolean>(false);
  const [autoReveal, setAutoReveal] = useState<boolean>(false);
  const [mapValueMode, setMapValueMode] = useState<MapValueMode>('aqi_t');
  const [activeBookmarkId, setActiveBookmarkId] = useState<string | null>('story-1-tp');

  // Lớp 2 (Ngăn Chi Tiết & Kiểm Chứng) và Tài liệu người thuyết trình
  const [isDetailOpen, setIsDetailOpen] = useState<boolean>(false);
  const [detailTab, setDetailTab] = useState<DetailTabKey>('case');
  const [isGuideOpen, setIsGuideOpen] = useState<boolean>(false);

  const dateInput = getInputDateFromTarget(dateTarget);
  const currentRecord = getPredictionRecord(selectedCity, dateTarget);
  const thrInfo = getThresholds(thresholdMode);

  // Reset nhất quán trạng thái hiện thực tế và chế độ bản đồ khi chưa bật tự động hiện
  const resetRevealIfNeeded = useCallback(() => {
    setIsRevealed(autoReveal);
    if (!autoReveal) {
      setMapValueMode((prev) => (prev === 'actual_t1' ? 'aqi_t' : prev));
    }
  }, [autoReveal]);

  const handleToggleReveal = useCallback(() => {
    setIsRevealed(!isRevealed);
    if (isRevealed) {
      setMapValueMode((m) => (m === 'actual_t1' ? 'aqi_t' : m));
    }
  }, [isRevealed]);

  const handleToggleAutoReveal = useCallback(() => {
    const next = !autoReveal;
    setAutoReveal(next);
    setIsRevealed(next);
    if (!next) {
      setMapValueMode((m) => (m === 'actual_t1' ? 'aqi_t' : m));
    }
  }, [autoReveal]);

  // Đổi thành phố (từ Mini Map hoặc bộ chọn): giữ nguyên ngày đích & giai đoạn đang xem, reset reveal nếu không bật tự động hiện
  const handleSelectCity = useCallback(
    (cityId: string) => {
      setSelectedCity(cityId);
      setActiveBookmarkId(null);
      resetRevealIfNeeded();
    },
    [resetRevealIfNeeded]
  );

  // Đổi ngày đích trên timeline
  const handleChangeDateTarget = useCallback(
    (newDateTarget: string) => {
      setDateTarget(newDateTarget);
      setLastDateBySplit((prev) => ({ ...prev, [split]: newDateTarget }));
      setActiveBookmarkId(null);
      resetRevealIfNeeded();
    },
    [split, resetRevealIfNeeded]
  );

  // Đổi giai đoạn đánh giá (Test <-> Holdout)
  const handleChangeSplit = useCallback(
    (newSplit: SplitType) => {
      if (newSplit === split) return;
      setSplit(newSplit);
      const targetToUse = lastDateBySplit[newSplit] || DEMO_DATA.calendar[newSplit][0];
      setDateTarget(targetToUse);
      setActiveBookmarkId(null);
      resetRevealIfNeeded();
    },
    [split, lastDateBySplit, resetRevealIfNeeded]
  );

  // Chọn nhanh một ca tiêu biểu (từ thanh kịch bản hoặc ca riêng thành phố)
  const handleSelectBookmark = useCallback(
    (city: string, bmSplit: SplitType, bmDateTarget: string, bookmarkId?: string) => {
      setSelectedCity(city);
      setSplit(bmSplit);
      setDateTarget(bmDateTarget);
      setLastDateBySplit((prev) => ({ ...prev, [bmSplit]: bmDateTarget }));
      setActiveBookmarkId(bookmarkId ?? null);
      resetRevealIfNeeded();
    },
    [resetRevealIfNeeded]
  );

  // Mở lớp chi tiết ở tab chỉ định (giữ nguyên toàn bộ ngữ cảnh)
  const handleOpenDetailLayer = useCallback((tab: DetailTabKey = 'case') => {
    setDetailTab(tab);
    setIsDetailOpen(true);
  }, []);

  // Hỗ trợ bàn phím cho trình chiếu (← / → đổi ngày, Space mở/ẩn thực tế, D mở/đóng chi tiết, Esc đóng modal)
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return;

      if (e.key === 'Escape') {
        if (isGuideOpen) setIsGuideOpen(false);
        else if (isDetailOpen) setIsDetailOpen(false);
        return;
      }

      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        const cal = DEMO_DATA.calendar[split];
        const idx = cal.indexOf(dateTarget);
        if (idx > 0) handleChangeDateTarget(cal[idx - 1]);
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        const cal = DEMO_DATA.calendar[split];
        const idx = cal.indexOf(dateTarget);
        if (idx >= 0 && idx < cal.length - 1) handleChangeDateTarget(cal[idx + 1]);
      } else if (e.key === ' ' && !isDetailOpen && !isGuideOpen) {
        e.preventDefault();
        handleToggleReveal();
      } else if ((e.key === 'd' || e.key === 'D') && !isGuideOpen) {
        e.preventDefault();
        setIsDetailOpen((prev) => !prev);
      }
    };

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [split, dateTarget, isDetailOpen, isGuideOpen, handleChangeDateTarget, handleToggleReveal]);

  const activeStory = STORY_BOOKMARKS.find(
    (b) => b.id === activeBookmarkId || (b.city === selectedCity && b.dateTarget === dateTarget && b.split === split)
  );

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 flex flex-col">
      {/* ================= THANH ĐẦU TRANG GỌN NHẸ CHO BUỔI THUYẾT TRÌNH ================= */}
      <header className="bg-slate-900 text-white border-b border-slate-800 px-4 py-2.5 sticky top-0 z-30 shadow-xs">
        <div className="max-w-[1440px] mx-auto flex flex-wrap items-center justify-between gap-3">
          {/* Tên dự án & Bản sắc thị giác */}
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-400 text-slate-950 flex items-center justify-center font-extrabold shadow-xs">
              <Wind className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm sm:text-base font-extrabold tracking-tight">
                  Air Project · Demo Phát lại Dự báo AQI Lịch sử (<code className="font-mono text-amber-300">t → t+1</code>) cho 8 Thành phố Ấn Độ
                </h1>
                <span className="hidden md:inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-teal-900/90 text-teal-200 border border-teal-700">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Artifact phát lại: R2_B04 (13e93ae)</span>
                </span>
              </div>
              <p className="text-[11px] text-slate-300 hidden sm:block">
                Phát lại dự báo hồi cứu (không phải hệ dự báo thời gian thực) · Đối chiếu <strong>Ridge L3</strong> với Baseline <strong>“Ngày mai = hôm nay”</strong> · Ngày nặng <code className="font-mono">AQI(t+1) ≥ 201</code>
              </p>
            </div>
          </div>

          {/* Cụm nút điều khiển Lớp 2 (Chi tiết & Phương pháp) + Chế độ ẩn kết quả + Tài liệu thuyết trình */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Công tắc Chế độ Giấu kết quả vs Chế độ khám phá (tự động hiện) */}
            <button
              type="button"
              onClick={handleToggleAutoReveal}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-medium border transition flex items-center gap-1 cursor-pointer ${
                !autoReveal
                  ? 'bg-slate-800 text-amber-300 border-amber-400/50'
                  : 'bg-teal-900/80 text-teal-100 border-teal-500/60 hover:text-white'
              }`}
              title="Mặc định giấu kết quả ngày đích t+1 và nhãn đáp án cho tới khi bấm Mở thực tế; bật Chế độ khám phá để tự động hiện kết quả khi đổi thành phố/ngày/split/ca"
            >
              {!autoReveal ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              <span>{!autoReveal ? 'Chế độ: Giấu kết quả' : 'Chế độ khám phá: Tự hiện'}</span>
            </button>

            {/* Nút mở Tài liệu lời nói & Checklist riêng (Y07, Y35) */}
            <button
              type="button"
              onClick={() => setIsGuideOpen(true)}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 cursor-pointer"
              title="Xem kịch bản lời nói 2–3 câu mỗi ca và Checklist trước buổi trình chiếu (File riêng Y07/Y35)"
            >
              <FileText className="w-3.5 h-3.5 text-amber-300" />
              <span>Lời dẫn &amp; Checklist</span>
            </button>

            {/* Nút mở Lớp 2: Chi tiết số liệu, Pipeline, Ma trận 2x2 & Hạn chế F01 (Y14) */}
            <button
              type="button"
              onClick={() => handleOpenDetailLayer('case')}
              className="px-3.5 py-1.5 rounded-lg bg-amber-400 hover:bg-amber-300 text-slate-950 font-extrabold text-xs flex items-center gap-1.5 shadow-xs cursor-pointer"
              title="Mở Lớp Chi Tiết (Phím tắt: D) — Giữ nguyên thành phố và ngày đang chọn"
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Mở Lớp Chi Tiết &amp; Phương pháp (Lớp 2)</span>
            </button>
          </div>
        </div>
      </header>

      {/* ================= LỚP 1: MÀN HÌNH TRÌNH CHIẾU CHÍNH (GỌN, TRỰC QUAN) ================= */}
      <main className="max-w-[1440px] w-full mx-auto px-3 sm:px-4 py-3 flex-1 flex flex-col gap-3">
        {/* Khối 1: Trục thời gian trung tâm t -> t+1, Chọn Test/Holdout & Các mốc tiêu biểu */}
        <TimelineCenter
          selectedCity={selectedCity}
          split={split}
          dateInput={dateInput}
          dateTarget={dateTarget}
          thresholdMode={thresholdMode}
          isRevealed={isRevealed}
          onSelectBookmark={handleSelectBookmark}
          onChangeSplit={handleChangeSplit}
          onChangeDateTarget={handleChangeDateTarget}
          activeBookmarkId={activeBookmarkId}
        />

        {/* Khối 2: Bố cục 2 cột đồng bộ — Trái: Mini Map Ấn Độ 8 chấm (Y45) | Phải: Thước 2 làn & Dải lịch sử */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 items-start">
          {/* Cột trái (4/12): Mini Map Ấn Độ 8 thành phố đồng bộ 2 chiều */}
          <div className="lg:col-span-4">
            <IndiaMiniMap
              selectedCity={selectedCity}
              onSelectCity={handleSelectCity}
              dateInput={dateInput}
              dateTarget={dateTarget}
              isRevealed={isRevealed}
              mapValueMode={mapValueMode}
              onChangeMapValueMode={setMapValueMode}
            />
          </div>

          {/* Cột phải (8/12): Thước quyết định hai làn (Y27) + Dải lịch sử thực tế 7 ngày (Y05/Y44) + Tóm tắt nhanh */}
          <div className="lg:col-span-8 flex flex-col gap-3">
            {/* Thước quyết định hai làn + 4 nhãn kết quả tiếng Việt */}
            <TwoLaneRulerAndOutcome
              selectedCity={selectedCity}
              split={split}
              dateInput={dateInput}
              dateTarget={dateTarget}
              record={currentRecord}
              thresholdMode={thresholdMode}
              onChangeThresholdMode={setThresholdMode}
              isRevealed={isRevealed}
              onToggleReveal={handleToggleReveal}
              autoReveal={autoReveal}
              onToggleAutoReveal={handleToggleAutoReveal}
              onOpenDetailLayer={handleOpenDetailLayer}
              onSelectDateTarget={handleChangeDateTarget}
            />

            {/* Dải lịch sử AQI thực tế 7 ngày đến t và vùng t+1 mở sau (Y05, Y44) */}
            <HistoricalStripChart
              selectedCity={selectedCity}
              dateInput={dateInput}
              dateTarget={dateTarget}
              record={currentRecord}
              isRevealed={isRevealed}
              thresholdL3={thrInfo.l3}
            />

            {/* Thanh tóm tắt kết quả nghiên cứu gọn + Lối tắt mở thẳng từng tab của Lớp Chi Tiết */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs">
              <div className="space-y-0.5">
                {activeStory ? (
                  <div className="text-slate-700">
                    <span className="font-bold text-slate-900">{activeStory.stepBadge}:</span>{' '}
                    <span>{isRevealed ? activeStory.summaryNote : `Đang xem dự báo tại cuối ngày đầu vào t=${formatDateVN(dateInput)} (đích t+1=${formatDateVN(dateTarget)}). Bấm "Mở thực tế & Đối chiếu (t+1)" để xem kết quả.`}</span>
                  </div>
                ) : (
                  <div className="text-slate-700">
                    <strong>Tổng hợp dự án:</strong> Giai đoạn kiểm thử (n=1.947): MAE Ridge L3 <strong>19,52</strong> vs Baseline <strong>23,47</strong> (<code className="font-mono">Δ=-3,95 [-5,40; -2,56]</code>). Holdout đánh giá bổ sung (n=975): chênh lệch MAE L3 − baseline khoảng <strong>−1,02</strong> điểm AQI, KTC bootstrap 95% <code className="font-mono">[-2,70; +0,48]</code> chứa 0 nên <em>chưa đủ bằng chứng kết luận L3 cải thiện MAE trên giai đoạn này</em>.
                  </div>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-1.5 shrink-0">
                <button
                  type="button"
                  onClick={() => handleOpenDetailLayer('pipeline')}
                  className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold inline-flex items-center gap-1 cursor-pointer"
                >
                  <Sliders className="w-3.5 h-3.5 text-indigo-700" />
                  <span>Pipeline &amp; Bậc thang MAE</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleOpenDetailLayer('tables')}
                  className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold inline-flex items-center gap-1 cursor-pointer"
                >
                  <span>Bảng Kiểm thử / Holdout &amp; Nhóm TP</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleOpenDetailLayer('audit')}
                  className="px-2.5 py-1 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-950 border border-amber-200 font-semibold inline-flex items-center gap-1 cursor-pointer"
                >
                  <ShieldAlert className="w-3.5 h-3.5 text-amber-700" />
                  <span>Hạn chế F01 &amp; Kiểm dữ liệu</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Chân trang ngắn gọn ghi nguồn dữ liệu & phím tắt */}
      <footer className="bg-white border-t border-slate-200 px-4 py-2 text-[11px] text-slate-500">
        <div className="max-w-[1440px] mx-auto flex flex-wrap items-center justify-between gap-2">
          <span>
            <strong>Nguồn dữ liệu:</strong> CPCB qua Kaggle (<code className="font-mono">city_day.csv</code>) &amp; Open-Meteo ERA5 (CC BY 4.0) · Artifact phát lại: <code className="font-mono">R2_B04_baseline_predictions.csv</code> (commit <code className="font-mono">13e93ae</code>; hạn chế F01 vẫn đang mở).
          </span>
          <span>
            <strong>Phím tắt trình chiếu:</strong> <kbd className="px-1 py-0.2 bg-slate-100 border border-slate-300 rounded font-mono">←</kbd> <kbd className="px-1 py-0.2 bg-slate-100 border border-slate-300 rounded font-mono">→</kbd> Đổi ngày · <kbd className="px-1 py-0.2 bg-slate-100 border border-slate-300 rounded font-mono">Space</kbd> Mở/Ẩn thực tế · <kbd className="px-1 py-0.2 bg-slate-100 border border-slate-300 rounded font-mono">D</kbd> Lớp chi tiết
          </span>
        </div>
      </footer>

      {/* ================= LỚP 2: NGĂN CHI TIẾT & KIỂM CHỨNG (GIỮ NGUYÊN NGỮ CẢNH) ================= */}
      <DetailDrawerModal
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        activeTab={detailTab}
        onChangeTab={setDetailTab}
        selectedCity={selectedCity}
        split={split}
        dateInput={dateInput}
        dateTarget={dateTarget}
        record={currentRecord}
        thresholdMode={thresholdMode}
        onChangeThresholdMode={setThresholdMode}
        isRevealed={isRevealed}
        onToggleReveal={handleToggleReveal}
      />

      {/* ================= MODAL TÀI LIỆU LỜI NÓI & CHECKLIST RIÊNG (Y07, Y35) ================= */}
      <PresenterGuideModal
        isRevealed={isRevealed}
        isOpen={isGuideOpen}
        onClose={() => setIsGuideOpen(false)}
        onLoadCase={(city, bmSplit, bmDateTarget, bmId) => {
          handleSelectBookmark(city, bmSplit, bmDateTarget, bmId);
        }}
      />
    </div>
  );
}

export default App;
