import rawData from './aqiDemoData.json';

export type SplitType = 'test' | 'holdout';
export type ThresholdMode = 'f2' | '201';
export type MapValueMode = 'aqi_t' | 'pred_l3' | 'actual_t1';
export type OutcomeCode = 'TP' | 'FN' | 'FP' | 'TN';

export interface PredictionRecord {
  c: string;      // City
  t: string;      // Date input (t)
  t1: string;     // Date target (t+1)
  s: SplitType;   // 'test' | 'holdout'
  aqi: number;    // Observed AQI at t (= Persistence baseline "Ngày mai = hôm nay")
  y: number;      // Actual observed AQI at t+1
  l1: number;     // Ridge L1 prediction
  l2: number;     // Ridge L2 prediction
  l3: number;     // Ridge L3 prediction (primary model)
  l4: number;     // Ridge L4 reference (uses target-day t+1 weather; reference only)
  hgb: number;    // HGB L3 prediction
  clim: number;   // Monthly median climatology baseline
  mean: number;   // City mean baseline
}

export interface DailyContextItem {
  aqi: number | null;
  miss: boolean;
  susp: boolean;
  pm25: number | null;
  pm25_miss: boolean;
  temp: number | null;
  hum: number | null;
  wind: number | null;
  blh: number | null;
  rain: number | null;
}

export interface AlertCountSummary {
  TP: number;
  FP: number;
  FN: number;
  TN: number;
  recall: number | null;
  precision: number | null;
  F1: number | null;
}

export interface CityInfo {
  id: string;
  name: string;
  region: string;
  groupKey: 'north_heavy' | 'northwest_mid' | 'south_low';
  groupLabel: string;
  smallSampleWarning: boolean;
  requested_lat: number;
  requested_lon: number;
  era5_grid_lat: number;
  era5_grid_lon: number;
  elevation_m: number;
  splits: {
    train: { n: number; heavy: number };
    test: {
      n: number;
      heavy: number;
      aqi_mean: number;
      mae_base: number;
      mae_l1: number;
      mae_l2: number;
      mae_l3: number;
      mae_hgb: number;
      rmse_base: number;
      rmse_l3: number;
      d_l3_base: number;
      d_l3_base_lo: number;
      d_l3_base_hi: number;
      d_l3_l2: number;
      d_l3_l2_lo: number;
      d_l3_l2_hi: number;
      pct_reduction: number;
      bias_l3: number;
      alerts_f2_l3: AlertCountSummary;
      alerts_f2_base: AlertCountSummary;
      alerts_201_l3: AlertCountSummary;
      alerts_201_base: AlertCountSummary;
    };
    holdout: {
      n: number;
      heavy: number;
      aqi_mean: number;
      mae_base: number;
      mae_l1: number;
      mae_l2: number;
      mae_l3: number;
      mae_hgb: number;
      d_l3_base: number;
      pct_reduction: number;
      alerts_f2_l3: AlertCountSummary;
      alerts_f2_base: AlertCountSummary;
      alerts_201_l3: AlertCountSummary;
      alerts_201_base: AlertCountSummary;
    };
  };
}

export const DEMO_DATA = rawData as unknown as {
  provenance: typeof rawData.provenance;
  cities: CityInfo[];
  calendar: {
    test: string[];
    holdout: string[];
  };
  summaryMetrics: typeof rawData.summaryMetrics;
  records: PredictionRecord[];
  daily: Record<string, Record<string, DailyContextItem>>;
};

// Fast lookup map: `${city}|${date_target}` -> PredictionRecord
const RECORD_BY_CITY_TARGET = new Map<string, PredictionRecord>();
for (const rec of DEMO_DATA.records) {
  RECORD_BY_CITY_TARGET.set(`${rec.c}|${rec.t1}`, rec);
}

export function getPredictionRecord(city: string, dateTarget: string): PredictionRecord | null {
  return RECORD_BY_CITY_TARGET.get(`${city}|${dateTarget}`) ?? null;
}

export function getDailyContext(city: string, dateStr: string): DailyContextItem | null {
  return DEMO_DATA.daily[city]?.[dateStr] ?? null;
}

export function getInputDateFromTarget(dateTarget: string): string {
  const [y, m, d] = dateTarget.split('-').map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  dt.setUTCDate(dt.getUTCDate() - 1);
  return dt.toISOString().slice(0, 10);
}

export function addDaysISO(dateStr: string, offset: number): string {
  const [y, m, d] = dateStr.split('-').map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  dt.setUTCDate(dt.getUTCDate() + offset);
  return dt.toISOString().slice(0, 10);
}

export function formatDateVN(dateStr: string): string {
  if (!dateStr) return '—';
  const [y, m, d] = dateStr.split('-');
  return `${d}/${m}/${y}`;
}

export function formatShortDateVN(dateStr: string): string {
  if (!dateStr) return '—';
  const [, m, d] = dateStr.split('-');
  return `${d}/${m}`;
}

export function vnNum(val: number | null | undefined, digits = 1): string {
  if (val === null || val === undefined || Number.isNaN(val)) return '—';
  return val.toFixed(digits).replace('.', ',');
}

export function getThresholds(mode: ThresholdMode): {
  l3: number;
  base: number;
  heavyActual: number;
  modeName: string;
  shortDesc: string;
} {
  if (mode === 'f2') {
    return {
      l3: 166,
      base: 160,
      heavyActual: 201,
      modeName: 'Chế độ ưu tiên Recall (F2 trên OOF Train)',
      shortDesc: 'Ngưỡng dự báo: Ridge L3 ≥ 166 · Baseline ≥ 160 | Ngày nặng thực tế: AQI(t+1) ≥ 201',
    };
  }
  return {
    l3: 201,
    base: 201,
    heavyActual: 201,
    modeName: 'Chế độ cùng ngưỡng nghĩa đen (201 / 201)',
    shortDesc: 'Ngưỡng dự báo: Ridge L3 ≥ 201 · Baseline ≥ 201 | Ngày nặng thực tế: AQI(t+1) ≥ 201',
  };
}

/**
 * Kiểm tra giá trị dự báo có nằm sát ngưỡng cảnh báo không (±1,5 điểm AQI).
 * Khi sát ngưỡng (ví dụ 165,973826 so với 166), giao diện hiển thị đủ 6 chữ số thập phân gốc.
 */
export function isNearThreshold(val: number, threshold: number, margin = 1.5): boolean {
  return Math.abs(val - threshold) <= margin;
}

export function formatAqiSmart(val: number | null | undefined, threshold?: number): string {
  if (val === null || val === undefined || Number.isNaN(val)) return '—';
  if (threshold !== undefined && isNearThreshold(val, threshold, 1.5) && !Number.isInteger(val)) {
    return val.toFixed(6).replace('.', ',');
  }
  if (Number.isInteger(val)) {
    return val.toFixed(0);
  }
  return val.toFixed(2).replace('.', ',');
}

export interface OutcomeInfo {
  code: OutcomeCode;
  label: string;          // Đúng 1 trong 4 nhãn tiếng Việt ngắn theo Y13
  shortRule: string;
  symbol: string;         // Ký hiệu hình học không phụ thuộc màu
  bgClass: string;
  textClass: string;
  borderClass: string;
  badgeClass: string;
}

export const OUTCOME_META: Record<OutcomeCode, OutcomeInfo> = {
  TP: {
    code: 'TP',
    label: 'Báo đúng',
    shortRule: 'Dự báo ≥ ngưỡng cảnh báo VÀ Thực tế t+1 ≥ 201 (bắt đúng ngày ô nhiễm nặng)',
    symbol: '✓',
    bgClass: 'bg-teal-50/90',
    textClass: 'text-teal-900',
    borderClass: 'border-teal-600',
    badgeClass: 'bg-teal-700 text-white border-teal-800',
  },
  FN: {
    code: 'FN',
    label: 'Bỏ sót',
    shortRule: 'Dự báo < ngưỡng cảnh báo NHƯNG Thực tế t+1 ≥ 201 (bỏ lỡ ngày ô nhiễm nặng)',
    symbol: '▲',
    bgClass: 'bg-rose-50/95',
    textClass: 'text-rose-950',
    borderClass: 'border-rose-600',
    badgeClass: 'bg-rose-700 text-white border-rose-800',
  },
  FP: {
    code: 'FP',
    label: 'Báo nhầm',
    shortRule: 'Dự báo ≥ ngưỡng cảnh báo NHƯNG Thực tế t+1 < 201 (cảnh báo thừa ngày chưa nặng)',
    symbol: '!',
    bgClass: 'bg-amber-50/95',
    textClass: 'text-amber-950',
    borderClass: 'border-amber-600',
    badgeClass: 'bg-amber-600 text-white border-amber-700',
  },
  TN: {
    code: 'TN',
    label: 'Không cảnh báo đúng',
    shortRule: 'Dự báo < ngưỡng cảnh báo VÀ Thực tế t+1 < 201 (không báo đúng ngày bình thường)',
    symbol: '○',
    bgClass: 'bg-slate-50',
    textClass: 'text-slate-800',
    borderClass: 'border-slate-400',
    badgeClass: 'bg-slate-700 text-white border-slate-800',
  },
};

/**
 * Phân loại kết quả cảnh báo dựa trên GIÁ TRỊ GỐC (không làm tròn trước).
 */
export function evaluateOutcome(rawPred: number, rawActualY: number, predThreshold: number): OutcomeInfo {
  const alertFired = rawPred >= predThreshold;
  const actualHeavy = rawActualY >= 201.0;
  if (alertFired && actualHeavy) return OUTCOME_META.TP;
  if (!alertFired && actualHeavy) return OUTCOME_META.FN;
  if (alertFired && !actualHeavy) return OUTCOME_META.FP;
  return OUTCOME_META.TN;
}

export interface AqiBucketInfo {
  key: string;
  labelVN: string;
  labelEN: string;
  rangeText: string;
  min: number;
  max: number;
  hex: string;
  textHex: string;
  bgSoft: string;
  borderSoft: string;
  isHeavy: boolean;
}

export const CPCB_BUCKETS: AqiBucketInfo[] = [
  {
    key: 'Good',
    labelVN: 'Tốt',
    labelEN: 'Good',
    rangeText: '0–50',
    min: 0,
    max: 50,
    hex: '#16a34a',
    textHex: '#14532d',
    bgSoft: 'bg-green-50 text-green-900 border-green-300',
    borderSoft: '#86efac',
    isHeavy: false,
  },
  {
    key: 'Satisfactory',
    labelVN: 'Đạt',
    labelEN: 'Satisfactory',
    rangeText: '51–100',
    min: 51,
    max: 100,
    hex: '#65a30d',
    textHex: '#365314',
    bgSoft: 'bg-lime-50 text-lime-900 border-lime-300',
    borderSoft: '#bef264',
    isHeavy: false,
  },
  {
    key: 'Moderate',
    labelVN: 'Trung bình',
    labelEN: 'Moderate',
    rangeText: '101–200',
    min: 101,
    max: 200,
    hex: '#d97706',
    textHex: '#78350f',
    bgSoft: 'bg-amber-50 text-amber-900 border-amber-300',
    borderSoft: '#fcd34d',
    isHeavy: false,
  },
  {
    key: 'Poor',
    labelVN: 'Kém (Nặng)',
    labelEN: 'Poor',
    rangeText: '201–300',
    min: 201,
    max: 300,
    hex: '#ea580c',
    textHex: '#7c2d12',
    bgSoft: 'bg-orange-50 text-orange-950 border-orange-300',
    borderSoft: '#fdba74',
    isHeavy: true,
  },
  {
    key: 'Very Poor',
    labelVN: 'Rất kém (Nặng)',
    labelEN: 'Very Poor',
    rangeText: '301–400',
    min: 301,
    max: 400,
    hex: '#dc2626',
    textHex: '#7f1d1d',
    bgSoft: 'bg-red-50 text-red-950 border-red-300',
    borderSoft: '#fca5a5',
    isHeavy: true,
  },
  {
    key: 'Severe',
    labelVN: 'Nguy hại (Nặng)',
    labelEN: 'Severe',
    rangeText: '401–500+',
    min: 401,
    max: 9999,
    hex: '#881337',
    textHex: '#4c0519',
    bgSoft: 'bg-rose-100 text-rose-950 border-rose-400',
    borderSoft: '#fda4af',
    isHeavy: true,
  },
];

export function getAqiBucket(aqi: number | null | undefined): AqiBucketInfo | null {
  if (aqi === null || aqi === undefined || Number.isNaN(aqi)) return null;
  if (aqi <= 50) return CPCB_BUCKETS[0];
  if (aqi <= 100) return CPCB_BUCKETS[1];
  if (aqi < 201) return CPCB_BUCKETS[2];
  if (aqi <= 300) return CPCB_BUCKETS[3];
  if (aqi <= 400) return CPCB_BUCKETS[4];
  return CPCB_BUCKETS[5];
}

export interface StoryBookmark {
  id: string;
  stepBadge: string;
  titleNeutral: string;     // Nhãn trung tính khi đang ẩn thực tế (không lộ đáp án)
  titleRevealed: string;    // Nhãn đầy đủ khi mở thực tế
  city: string;
  dateTarget: string;       // t+1
  dateInput: string;        // t
  split: SplitType;
  category: 'TP' | 'FN' | 'FP' | 'TN' | 'OVERFLOW' | 'MISSING' | 'HOLDOUT';
  summaryNote: string;
  presenterScript: string;
}

/**
 * Kịch bản thuyết trình tuần tự 3 ca chính + các ca đặc biệt đã kiểm chứng từ R2_B04_baseline_predictions.csv (Y02, Y37).
 */
export const STORY_BOOKMARKS: StoryBookmark[] = [
  {
    id: 'story-1-tp',
    stepBadge: 'Ca 1',
    titleNeutral: 'Ca 1 · Gurugram (t=19/11 → t+1=20/11/2019)',
    titleRevealed: 'Ca 1: Báo đúng — L3 phát cảnh báo trước ngày vượt 201 (Baseline không báo)',
    city: 'Gurugram',
    dateInput: '2019-11-19',
    dateTarget: '2019-11-20',
    split: 'test',
    category: 'TP',
    summaryNote: 'AQI(t)=148 (<160, Baseline không báo) · Dự báo L3=219,35 (≥166 & ≥201, Phát cảnh báo) · Thực tế t+1=223 (≥201, Ngày nặng).',
    presenterScript:
      'Tại Gurugram ngày đầu vào t = 19/11/2019, AQI(t) là 148 nên baseline "ngày mai = hôm nay" không phát cảnh báo. Từ tập đặc trưng đến hết ngày t, Ridge L3 dự báo AQI ngày đích t+1 = 20/11/2019 ở mức 219,35 (phát cảnh báo); thực tế ngày đích ghi nhận 223 (Báo đúng).',
  },
  {
    id: 'story-2-fn-near',
    stepBadge: 'Ca 2',
    titleNeutral: 'Ca 2 · Amritsar (t=03/01 → t+1=04/01/2020)',
    titleRevealed: 'Ca 2: Bỏ sót & Sát ngưỡng — Dự báo gốc 165,973826 < 166',
    city: 'Amritsar',
    dateInput: '2020-01-03',
    dateTarget: '2020-01-04',
    split: 'test',
    category: 'FN',
    summaryNote: 'Dự báo gốc L3 = 165,973826 (< 166,000000 đúng 0,026 điểm). Xét trên giá trị gốc không làm tròn trước → Không báo · Thực tế t+1 = 221 (Bỏ sót).',
    presenterScript:
      'Ca Amritsar ngày đầu vào t = 03/01/2020 minh họa nguyên tắc phân loại trên số gốc chưa làm tròn: dự báo gốc L3 cho ngày đích t+1 = 04/01/2020 là 165,973826 (< 166) nên không phát cảnh báo, dù hiển thị làm tròn 1 chữ số là 166,0. Thực tế ngày đích là 221 (Bỏ sót ở chế độ F2).',
  },
  {
    id: 'story-3-fp',
    stepBadge: 'Ca 3',
    titleNeutral: 'Ca 3 · Delhi (t=18/10 → t+1=19/10/2019)',
    titleRevealed: 'Ca 3: Báo nhầm — Dự báo vượt ngưỡng nhưng thực tế t+1 dưới 201',
    city: 'Delhi',
    dateInput: '2019-10-18',
    dateTarget: '2019-10-19',
    split: 'test',
    category: 'FP',
    summaryNote: 'AQI(t)=265 · Dự báo L3=232,73 (≥166 & ≥201, Phát cảnh báo) · Thực tế t+1=170 (<201) → Báo nhầm (cả L3 và Baseline).',
    presenterScript:
      'Tại Delhi ngày đầu vào t = 18/10/2019 (AQI ngày t = 265), cả Ridge L3 (dự báo 232,73) và baseline đều phát cảnh báo cho ngày đích t+1 = 19/10/2019. Thực tế ngày đích ghi nhận AQI = 170 (< 201), nên cả hai cùng rơi vào nhóm Báo nhầm.',
  },
  {
    id: 'story-4-tn-avoid-fp',
    stepBadge: 'Ca 4',
    titleNeutral: 'Ca 4 · Delhi (t=15/07 → t+1=16/07/2019)',
    titleRevealed: 'Ca 4: Không cảnh báo đúng — L3 không báo ở ca Baseline báo nhầm (chế độ F2)',
    city: 'Delhi',
    dateInput: '2019-07-15',
    dateTarget: '2019-07-16',
    split: 'test',
    category: 'TN',
    summaryNote: 'AQI(t)=180 (≥160, Baseline phát cảnh báo ở chế độ F2) · Dự báo L3=144,04 (<166, Không báo) · Thực tế t+1=117 (<201) → L3 Không cảnh báo đúng.',
    presenterScript:
      'Trong phép so sánh trên giai đoạn kiểm thử ở chế độ ngưỡng F2, L3 đạt recall 96,9% (377/389), baseline đạt 96,1% (374/389); L3 có ít báo nhầm hơn (113 so với 143). Các số liệu này chưa tự chứng minh chênh lệch recall có ý nghĩa thống kê. Ở ca minh họa này, AQI ngày t là 180 (≥160 nên baseline báo nhầm), L3 dự báo 144,04 (<166 nên không cảnh báo), và thực tế ngày t+1 là 117 (<201).',
  },
  {
    id: 'story-5-overflow',
    stepBadge: 'Ca 5',
    titleNeutral: 'Ca 5 · Delhi (t=02/11 → t+1=03/11/2019)',
    titleRevealed: 'Ca 5: Điểm vượt mốc 500 — Thực tế AQI(t+1) = 659,0',
    city: 'Delhi',
    dateInput: '2019-11-02',
    dateTarget: '2019-11-03',
    split: 'test',
    category: 'OVERFLOW',
    summaryNote: 'AQI(t)=473 · Dự báo L3=440,75 · Thực tế t+1=659,0 (vượt mốc 500 của thang chuẩn, hiển thị trong vùng mở rộng >500, không cắt trần).',
    presenterScript:
      'Dự án không cắt trần nhãn AQI ở 500. Trong giai đoạn kiểm thử có 18 cặp có giá trị vượt 500; cao nhất là Delhi ngày đích t+1 = 03/11/2019 với AQI thực tế 659,0 (ngày kế tiếp t+1 = 04/11 dự báo L3 đạt 650,96). Thước hiển thị vùng mở rộng >500 kèm giá trị số thật.',
  },
  {
    id: 'story-6-missing',
    stepBadge: 'Ca 6',
    titleNeutral: 'Ca 6 · Amritsar (t=25/08 → t+1=26/08/2019)',
    titleRevealed: 'Ca 6: Không có bản ghi dự báo trong artifact phát lại (Amritsar)',
    city: 'Amritsar',
    dateInput: '2019-08-25',
    dateTarget: '2019-08-26',
    split: 'test',
    category: 'MISSING',
    summaryNote: 'Không có bản ghi dự báo trong artifact phát lại cho cặp ngày t=25/08/2019 → t+1=26/08/2019 tại Amritsar (bảng hồi cứu: AQI(t)=80, AQI(t+1) khuyết).',
    presenterScript:
      'Không có bản ghi dự báo trong artifact phát lại cho cặp ngày này. Ứng dụng giữ nguyên thành phố và cặp ngày đang chọn, chỉ hiển thị các trạng thái kiểm tra trực tiếp được từ dữ liệu mà không suy đoán nguyên nhân lọc dòng, đồng thời vẫn ẩn dữ liệu ngày đích t+1 khi đang ở chế độ giấu kết quả.',
  },
  {
    id: 'story-7-holdout',
    stepBadge: 'Ca 7',
    titleNeutral: 'Ca 7 · Lucknow (t=26/05 → t+1=27/05/2020 · Holdout)',
    titleRevealed: 'Ca 7: Giai đoạn đánh giá bổ sung Holdout (18 cặp ngày nặng toàn kỳ)',
    city: 'Lucknow',
    dateInput: '2020-05-26',
    dateTarget: '2020-05-27',
    split: 'holdout',
    category: 'HOLDOUT',
    summaryNote: 'Holdout đánh giá bổ sung (n=975, 18 cặp nặng): AQI(t)=147 · Dự báo L3=170,47 · Thực tế t+1=205. Toàn kỳ: ΔMAE ≈ −1,02, KTC 95% [−2,70; +0,48] chứa 0.',
    presenterScript:
      'Holdout (ngày đích t+1: 01/03 – 01/07/2020) là giai đoạn đánh giá bổ sung, không dùng để chọn ngưỡng hay mô hình. Toàn kỳ chỉ có 18 cặp ngày nặng; chênh lệch MAE L3 − baseline trên holdout khoảng −1,02 điểm AQI, khoảng tin cậy bootstrap 95% [−2,70; +0,48]. Khoảng chứa 0 nên chưa đủ bằng chứng kết luận L3 cải thiện MAE trên giai đoạn này.',
  },
];

/**
 * Tìm nhanh các ca tiêu biểu (Báo đúng, Bỏ sót, Báo nhầm, Không cảnh báo đúng, Thiếu dữ liệu)
 * cho ĐÚNG thành phố, giai đoạn (test/holdout) và chế độ ngưỡng (f2/201) đang chọn (Y02).
 */
export function getCityQuickCases(
  city: string,
  split: SplitType,
  thresholdMode: ThresholdMode
): {
  TP: PredictionRecord | null;
  FN: PredictionRecord | null;
  FP: PredictionRecord | null;
  TN: PredictionRecord | null;
  missingTargetDate: string | null;
} {
  const { l3: thrL3, base: thrBase } = getThresholds(thresholdMode);
  const cityRecs = DEMO_DATA.records.filter((r) => r.c === city && r.s === split);

  // Prefer TP where L3 beats Baseline (Baseline < thrBase), otherwise any TP
  const tpBeatBase = cityRecs.find((r) => r.y >= 201 && r.l3 >= thrL3 && r.aqi < thrBase);
  const tpAny = cityRecs.find((r) => r.y >= 201 && r.l3 >= thrL3);

  // Prefer near-threshold FN if Amritsar in test, else FN with largest spike
  const fnNear = cityRecs.find((r) => r.y >= 201 && r.l3 < thrL3 && isNearThreshold(r.l3, thrL3, 1.5));
  const fnAny = cityRecs.find((r) => r.y >= 201 && r.l3 < thrL3);

  // FP
  const fpAny = cityRecs.find((r) => r.y < 201 && r.l3 >= thrL3);

  // Prefer TN where Baseline had a false alarm (aqi >= thrBase), else TN with high AQI(t)
  const tnBeatBase = cityRecs.find((r) => r.y < 201 && r.l3 < thrL3 && r.aqi >= thrBase);
  const tnAny = [...cityRecs]
    .filter((r) => r.y < 201 && r.l3 < thrL3)
    .sort((a, b) => b.aqi - a.aqi)[0] ?? null;

  // Missing target date in calendar
  const cal = DEMO_DATA.calendar[split];
  const presentSet = new Set(cityRecs.map((r) => r.t1));
  const missingTargetDate = cal.find((dt) => !presentSet.has(dt)) ?? null;

  return {
    TP: tpBeatBase ?? tpAny ?? null,
    FN: fnNear ?? fnAny ?? null,
    FP: fpAny ?? null,
    TN: tnBeatBase ?? tnAny ?? null,
    missingTargetDate,
  };
}
