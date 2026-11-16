import React from 'react';
import { Lock, MapPin, AlertTriangle, Info, Eye } from 'lucide-react';
import {
  CityInfo,
  DEMO_DATA,
  MapValueMode,
  CPCB_BUCKETS,
  getAqiBucket,
  getPredictionRecord,
  getDailyContext,
  formatDateVN,
  vnNum,
} from '../data/aqiHelpers';

interface IndiaMiniMapProps {
  selectedCity: string;
  onSelectCity: (city: string) => void;
  dateInput: string;
  dateTarget: string;
  isRevealed: boolean;
  mapValueMode: MapValueMode;
  onChangeMapValueMode: (mode: MapValueMode) => void;
}

/**
 * Phép chiếu tọa độ địa lý (lat, lon) sang khung SVG Bản đồ Ấn Độ (360 x 400)
 * Phạm vi chuẩn Ấn Độ: Lon 68.0°E -> 97.5°E, Lat 7.5°N -> 37.2°N
 */
const LON_MIN = 68.0;
const LON_MAX = 97.5;
const LAT_MIN = 7.5;
const LAT_MAX = 37.2;
const SVG_W = 360;
const SVG_H = 400;
const PAD_X = 22;
const PAD_Y = 18;

function projectCoord(lat: number, lon: number): { x: number; y: number } {
  const usableW = SVG_W - PAD_X * 2;
  const usableH = SVG_H - PAD_Y * 2;
  const x = PAD_X + ((lon - LON_MIN) / (LON_MAX - LON_MIN)) * usableW;
  const y = PAD_Y + ((LAT_MAX - lat) / (LAT_MAX - LAT_MIN)) * usableH;
  return { x: Number(x.toFixed(1)), y: Number(y.toFixed(1)) };
}

/**
 * Để xử lý cặp thành phố rất gần nhau về địa lý là Delhi (28.61°N, 77.21°E) và Gurugram (28.46°N, 77.03°E),
 * chấm tương tác trên bản đồ chính được tách nhẹ có đường dẫn nối về đúng tâm tọa độ thật,
 * đồng thời có thêm khung phóng to NCR (Delhi – Gurugram) ở góc phải bản đồ để chọn chính xác 100%.
 */
const VISUAL_MARKER_OFFSET: Record<string, { dx: number; dy: number; labelPos: 'right' | 'left' | 'top' | 'bottom' }> = {
  Amritsar: { dx: 0, dy: 0, labelPos: 'left' },
  Delhi: { dx: 11, dy: -9, labelPos: 'right' },
  Gurugram: { dx: -13, dy: 9, labelPos: 'left' },
  Jaipur: { dx: -4, dy: 4, labelPos: 'left' },
  Lucknow: { dx: 0, dy: 0, labelPos: 'right' },
  Hyderabad: { dx: 0, dy: 0, labelPos: 'right' },
  Bengaluru: { dx: 0, dy: 0, labelPos: 'left' },
  Chennai: { dx: 0, dy: 0, labelPos: 'right' },
};

/**
 * Đường viền khái quát lãnh thổ Ấn Độ (tọa độ lat/lon chuẩn hóa sang SVG) giúp hiển thị nhẹ, 100% offline.
 */
const INDIA_OUTLINE_COORDS: Array<[number, number]> = [
  [37.0, 74.6], [35.5, 76.9], [34.3, 78.9], [32.7, 79.4], [31.0, 79.8],
  [30.2, 81.0], [28.2, 81.0], [27.5, 83.9], [26.8, 88.1], [27.9, 88.7],
  [27.2, 89.0], [26.8, 92.1], [27.9, 93.5], [29.2, 96.1], [27.7, 97.1],
  [25.6, 95.1], [23.9, 93.3], [22.0, 92.6], [23.8, 91.2], [25.2, 89.8],
  [26.2, 88.2], [24.5, 88.8], [22.2, 89.0], [21.6, 87.5], [20.2, 86.7],
  [19.3, 85.0], [17.7, 83.3], [16.3, 81.8], [15.5, 80.1], [13.1, 80.3],
  [11.4, 79.8], [10.3, 79.9], [9.3, 79.1], [8.1, 77.5], [9.9, 76.2],
  [11.9, 75.3], [14.8, 74.1], [17.9, 73.0], [19.1, 72.8], [21.1, 72.6],
  [20.7, 70.9], [22.3, 69.0], [23.7, 68.4], [24.4, 71.1], [26.8, 69.5],
  [28.0, 70.7], [30.0, 73.9], [31.6, 74.5], [32.9, 74.7], [34.6, 73.9],
  [36.0, 74.1],
];

const INDIA_SVG_PATH =
  INDIA_OUTLINE_COORDS.map(([lat, lon], idx) => {
    const { x, y } = projectCoord(lat, lon);
    return `${idx === 0 ? 'M' : 'L'} ${x} ${y}`;
  }).join(' ') + ' Z';

export const IndiaMiniMap: React.FC<IndiaMiniMapProps> = ({
  selectedCity,
  onSelectCity,
  dateInput,
  dateTarget,
  isRevealed,
  mapValueMode,
  onChangeMapValueMode,
}) => {
  // Nếu chưa mở thực tế t+1 mà mapValueMode đang ở 'actual_t1', tự động lùi về 'aqi_t' để chống lộ kết quả
  const effectiveMode: MapValueMode = !isRevealed && mapValueMode === 'actual_t1' ? 'aqi_t' : mapValueMode;

  const getCityMapValue = (cityId: string): {
    value: number | null;
    isMissing: boolean;
    missingReason: string;
  } => {
    const rec = getPredictionRecord(cityId, dateTarget);
    const dailyT = getDailyContext(cityId, dateInput);
    const dailyT1 = getDailyContext(cityId, dateTarget);

    if (effectiveMode === 'aqi_t') {
      if (rec) {
        return { value: rec.aqi, isMissing: false, missingReason: '' };
      }
      if (dailyT && dailyT.aqi !== null) {
        return { value: dailyT.aqi, isMissing: false, missingReason: '' };
      }
      return {
        value: null,
        isMissing: true,
        missingReason: `Thiếu AQI quan trắc ngày t (${formatDateVN(dateInput)})`,
      };
    }

    if (effectiveMode === 'pred_l3') {
      if (rec) {
        return { value: rec.l3, isMissing: false, missingReason: '' };
      }
      return {
        value: null,
        isMissing: true,
        missingReason: `Không có dự báo phát lại cho đích ${formatDateVN(dateTarget)}`,
      };
    }

    // actual_t1 (chỉ khi đã mở thực tế)
    if (rec) {
      return { value: rec.y, isMissing: false, missingReason: '' };
    }
    if (dailyT1 && dailyT1.aqi !== null) {
      return { value: dailyT1.aqi, isMissing: false, missingReason: '' };
    }
    return {
      value: null,
      isMissing: true,
      missingReason: `Thiếu AQI thực tế ngày t+1 (${formatDateVN(dateTarget)})`,
    };
  };

  const modeTitleMap: Record<MapValueMode, { title: string; dateBadge: string }> = {
    aqi_t: {
      title: 'AQI quan sát ngày đầu vào t (Mặc định · Không lộ kết quả)',
      dateBadge: `Ngày t: ${formatDateVN(dateInput)}`,
    },
    pred_l3: {
      title: 'Dự báo Ridge L3 cho ngày đích t+1',
      dateBadge: `Đích t+1: ${formatDateVN(dateTarget)}`,
    },
    actual_t1: {
      title: 'Thực tế quan trắc ngày đích t+1 (Đã mở đối chiếu)',
      dateBadge: `Đích t+1: ${formatDateVN(dateTarget)}`,
    },
  };

  const selectedCityObj = DEMO_DATA.cities.find((c) => c.id === selectedCity) ?? DEMO_DATA.cities[0];
  const selectedCityVal = getCityMapValue(selectedCity);

  return (
    <section
      aria-label="Mini Map Ấn Độ 8 thành phố trong dự án"
      className="bg-white rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between overflow-hidden"
    >
      {/* Header Bản đồ + Bộ chọn loại giá trị hiển thị */}
      <div className="p-3.5 border-b border-slate-100 bg-slate-50/70">
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-1.5">
            <MapPin className="w-4 h-4 text-slate-700 shrink-0" />
            <h2 className="text-sm font-bold text-slate-900 tracking-tight">
              Mini Map Ấn Độ · 8 Thành phố Dự án
            </h2>
          </div>
          <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-slate-200/80 text-slate-800">
            {modeTitleMap[effectiveMode].dateBadge}
          </span>
        </div>

        {/* Nút chuyển loại giá trị trên bản đồ (chống lộ kết quả t+1 khi đang ẩn) */}
        <div className="grid grid-cols-3 gap-1 bg-slate-200/70 p-1 rounded-lg text-[11px]" role="radiogroup" aria-label="Loại giá trị hiển thị trên bản đồ">
          <button
            type="button"
            onClick={() => onChangeMapValueMode('aqi_t')}
            className={`px-2 py-1.5 rounded-md font-medium transition text-center cursor-pointer ${
              effectiveMode === 'aqi_t'
                ? 'bg-white text-slate-900 shadow-2xs font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
            title="Hiển thị AQI quan trắc tại ngày đầu vào t"
          >
            AQI ngày t
          </button>
          <button
            type="button"
            onClick={() => onChangeMapValueMode('pred_l3')}
            className={`px-2 py-1.5 rounded-md font-medium transition text-center cursor-pointer ${
              effectiveMode === 'pred_l3'
                ? 'bg-white text-slate-900 shadow-2xs font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
            title="Hiển thị AQI dự báo của mô hình Ridge L3 cho ngày t+1"
          >
            Dự báo t+1
          </button>
          <button
            type="button"
            disabled={!isRevealed}
            onClick={() => {
              if (isRevealed) onChangeMapValueMode('actual_t1');
            }}
            className={`px-2 py-1.5 rounded-md font-medium transition flex items-center justify-center gap-1 ${
              !isRevealed
                ? 'text-slate-400 bg-slate-100/50 cursor-not-allowed'
                : effectiveMode === 'actual_t1'
                  ? 'bg-white text-slate-900 shadow-2xs font-semibold cursor-pointer'
                  : 'text-slate-600 hover:text-slate-900 cursor-pointer'
            }`}
            title={
              isRevealed
                ? 'Hiển thị AQI thực tế quan trắc ngày t+1'
                : 'Đang khóa để không tiết lộ kết quả thực tế t+1 trước khi bấm Mở đối chiếu'
            }
          >
            {!isRevealed ? <Lock className="w-3 h-3 shrink-0" /> : <Eye className="w-3 h-3 shrink-0" />}
            <span>Thực tế t+1</span>
          </button>
        </div>

        <p className="text-[11px] text-slate-600 mt-1.5 flex items-center justify-between">
          <span>Đang tô màu: <strong className="text-slate-800">{modeTitleMap[effectiveMode].title}</strong></span>
        </p>
      </div>

      {/* Khung SVG Bản đồ Ấn Độ + Cụm phóng to NCR (Delhi - Gurugram) */}
      <div className="relative px-2 py-1 flex items-center justify-center bg-gradient-to-b from-sky-50/40 via-white to-slate-50/40">
        <svg
          viewBox={`0 0 ${SVG_W} ${SVG_H}`}
          className="w-full max-w-[350px] h-auto select-none"
          role="img"
          aria-label="Bản đồ vị trí địa lý 8 thành phố Ấn Độ trong phạm vi dữ liệu dự án"
        >
          <defs>
            <pattern id="missingHatch" width="6" height="6" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
              <line x1="0" y1="0" x2="0" y2="6" stroke="#64748b" strokeWidth="1.5" />
            </pattern>
            <filter id="selectedGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feDropShadow dx="0" dy="1" stdDeviation="2.5" floodColor="#0f172a" floodOpacity="0.35" />
            </filter>
          </defs>

          {/* Lưới kinh vĩ độ tham chiếu nhẹ */}
          {[10, 15, 20, 25, 30, 35].map((lat) => {
            const { y } = projectCoord(lat, LON_MIN);
            return (
              <g key={`lat-${lat}`}>
                <line x1={PAD_X} y1={y} x2={SVG_W - PAD_X} y2={y} stroke="#e2e8f0" strokeDasharray="3 3" strokeWidth="0.8" />
                <text x={PAD_X - 2} y={y + 3} fontSize="8" fill="#94a3b8" textAnchor="end">
                  {lat}°N
                </text>
              </g>
            );
          })}
          {[70, 75, 80, 85, 90, 95].map((lon) => {
            const { x } = projectCoord(LAT_MIN, lon);
            return (
              <g key={`lon-${lon}`}>
                <line x1={x} y1={PAD_Y} x2={x} y2={SVG_H - PAD_Y} stroke="#e2e8f0" strokeDasharray="3 3" strokeWidth="0.8" />
                <text x={x} y={SVG_H - 5} fontSize="8" fill="#94a3b8" textAnchor="middle">
                  {lon}°E
                </text>
              </g>
            );
          })}

          {/* Hình dáng lãnh thổ Ấn Độ */}
          <path
            d={INDIA_SVG_PATH}
            fill="#f8fafc"
            stroke="#cbd5e1"
            strokeWidth="1.5"
            strokeLinejoin="round"
          />

          {/* Vòng khoanh vùng NCR (Delhi - Gurugram) dẫn sang ô phóng to */}
          {(() => {
            const dPt = projectCoord(28.61, 77.21);
            return (
              <g>
                <circle
                  cx={dPt.x}
                  cy={dPt.y}
                  r={22}
                  fill="none"
                  stroke="#64748b"
                  strokeWidth="1"
                  strokeDasharray="2 2"
                />
                <line
                  x1={dPt.x + 18}
                  y1={dPt.y - 12}
                  x2={232}
                  y2={58}
                  stroke="#94a3b8"
                  strokeWidth="1"
                  strokeDasharray="2 2"
                />
              </g>
            );
          })()}

          {/* Vẽ 8 chấm thành phố trên bản đồ chính */}
          {DEMO_DATA.cities.map((city: CityInfo) => {
            const truePt = projectCoord(city.requested_lat, city.requested_lon);
            const offset = VISUAL_MARKER_OFFSET[city.id] ?? { dx: 0, dy: 0, labelPos: 'right' };
            const cx = truePt.x + offset.dx;
            const cy = truePt.y + offset.dy;
            const isSelected = city.id === selectedCity;
            const { value, isMissing } = getCityMapValue(city.id);
            const bucket = getAqiBucket(value);
            const fillColor = isMissing ? 'url(#missingHatch)' : bucket?.hex ?? '#94a3b8';

            const r = isSelected ? 10.5 : 7.5;
            const labelX = offset.labelPos === 'left' ? cx - (r + 5) : cx + (r + 5);
            const textAnchor = offset.labelPos === 'left' ? 'end' : 'start';

            return (
              <g
                key={city.id}
                role="button"
                tabIndex={0}
                aria-label={`Chọn thành phố ${city.name}, tọa độ ${city.requested_lat}°B, ${city.requested_lon}°Đ, ${
                  isMissing ? 'Thiếu dữ liệu' : `giá trị AQI ${vnNum(value, 0)}`
                }${isSelected ? ' (Đang chọn)' : ''}`}
                onClick={() => onSelectCity(city.id)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onSelectCity(city.id);
                  }
                }}
                className="cursor-pointer focus:outline-none group"
              >
                {/* Nếu có offset tách điểm gần nhau (Delhi/Gurugram), vẽ chấm tâm thật + đoạn nối */}
                {(offset.dx !== 0 || offset.dy !== 0) && (
                  <>
                    <line
                      x1={truePt.x}
                      y1={truePt.y}
                      x2={cx}
                      y2={cy}
                      stroke="#475569"
                      strokeWidth="1.2"
                    />
                    <circle cx={truePt.x} cy={truePt.y} r="2" fill="#334155" />
                  </>
                )}

                {/* Vòng ngoài biểu thị ĐƯỢC CHỌN (tách biệt hoàn toàn với màu mức AQI bên trong) */}
                {isSelected && (
                  <>
                    <circle
                      cx={cx}
                      cy={cy}
                      r={r + 5.5}
                      fill="none"
                      stroke="#0f172a"
                      strokeWidth="2.2"
                      filter="url(#selectedGlow)"
                    />
                    <circle
                      cx={cx}
                      cy={cy}
                      r={r + 2.5}
                      fill="none"
                      stroke="#ffffff"
                      strokeWidth="2"
                    />
                  </>
                )}

                {/* Chấm tròn thành phố (Màu = mức AQI; Viền nét đứt + gạch chéo = Thiếu dữ liệu) */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={r}
                  fill={fillColor}
                  stroke={isMissing ? '#334155' : isSelected ? '#0f172a' : '#ffffff'}
                  strokeWidth={isSelected ? '2.2' : '1.6'}
                  strokeDasharray={isMissing ? '3 2' : undefined}
                />

                {/* Ký hiệu gạch chéo nếu thiếu dữ liệu (không phụ thuộc màu, không tô như AQI = 0) */}
                {isMissing && (
                  <line
                    x1={cx - 4.5}
                    y1={cy - 4.5}
                    x2={cx + 4.5}
                    y2={cy + 4.5}
                    stroke="#0f172a"
                    strokeWidth="1.8"
                  />
                )}

                {/* Nhãn tên thành phố + giá trị */}
                <g transform={`translate(${labelX}, ${cy})`}>
                  <rect
                    x={offset.labelPos === 'left' ? -82 : -2}
                    y={-10}
                    width={84}
                    height={19}
                    rx={4}
                    fill={isSelected ? '#0f172a' : 'rgba(255,255,255,0.92)'}
                    stroke={isSelected ? '#0f172a' : '#cbd5e1'}
                    strokeWidth={isSelected ? '1.2' : '0.8'}
                  />
                  <text
                    x={offset.labelPos === 'left' ? -4 : 3}
                    y={3}
                    textAnchor={textAnchor}
                    fontSize={isSelected ? '9.5' : '8.8'}
                    fontWeight={isSelected ? '700' : '600'}
                    fill={isSelected ? '#ffffff' : '#0f172a'}
                  >
                    {isSelected ? `★ ${city.name}` : city.name}{' '}
                    <tspan
                      fontWeight="700"
                      fill={isSelected ? '#fde047' : isMissing ? '#dc2626' : '#334155'}
                    >
                      ({isMissing ? 'Thiếu' : vnNum(value, 0)})
                    </tspan>
                  </text>
                </g>
              </g>
            );
          })}

          {/* Ô PHÓNG TO CỤM NCR: DELHI & GURUGRAM (giúp bấm chọn tách biệt 100%) */}
          <g transform="translate(222, 16)">
            <rect
              x={0}
              y={0}
              width={128}
              height={84}
              rx={7}
              fill="#ffffff"
              stroke="#64748b"
              strokeWidth="1.2"
            />
            <text x={8} y={14} fontSize="8.5" fontWeight="700" fill="#334155">
              Phóng to cụm NCR (~25km)
            </text>
            {(['Delhi', 'Gurugram'] as const).map((cid, idx) => {
              const cObj = DEMO_DATA.cities.find((c) => c.id === cid)!;
              const isSel = selectedCity === cid;
              const { value, isMissing } = getCityMapValue(cid);
              const bucket = getAqiBucket(value);
              const iy = 33 + idx * 32;
              return (
                <g
                  key={`inset-${cid}`}
                  role="button"
                  tabIndex={0}
                  onClick={() => onSelectCity(cid)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onSelectCity(cid);
                    }
                  }}
                  className="cursor-pointer"
                >
                  <rect
                    x={6}
                    y={iy - 12}
                    width={116}
                    height={25}
                    rx={5}
                    fill={isSel ? '#0f172a' : '#f8fafc'}
                    stroke={isSel ? '#0f172a' : '#cbd5e1'}
                    strokeWidth={isSel ? '1.5' : '1'}
                  />
                  <circle
                    cx={20}
                    cy={iy}
                    r={isSel ? 7 : 5.5}
                    fill={isMissing ? 'url(#missingHatch)' : bucket?.hex ?? '#94a3b8'}
                    stroke="#ffffff"
                    strokeWidth="1.5"
                  />
                  <text
                    x={32}
                    y={iy + 3}
                    fontSize="9"
                    fontWeight="700"
                    fill={isSel ? '#ffffff' : '#0f172a'}
                  >
                    {isSel ? `★ ${cObj.name}` : cObj.name}: {isMissing ? 'Thiếu' : vnNum(value, 0)}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>
      </div>

      {/* Bộ chọn thành phố thay thế dạng nút phẳng (hỗ trợ bàn phím & máy chiếu) */}
      <div className="px-3.5 py-2.5 bg-slate-50 border-t border-slate-200/80">
        <div className="flex items-center justify-between text-[11px] text-slate-600 mb-1.5">
          <span className="font-semibold text-slate-700">Bộ chọn nhanh 8 thành phố (Đồng bộ 2 chiều):</span>
          <span className="text-[10px] text-slate-500">
            Tọa độ {selectedCityObj.name}: {selectedCityObj.requested_lat}°N, {selectedCityObj.requested_lon}°E ({selectedCityObj.elevation_m}m)
          </span>
        </div>
        <div className="grid grid-cols-4 gap-1.5" role="group" aria-label="Bộ chọn thay thế 8 thành phố">
          {DEMO_DATA.cities.map((city) => {
            const isSel = city.id === selectedCity;
            const { value, isMissing } = getCityMapValue(city.id);
            const bucket = getAqiBucket(value);
            return (
              <button
                key={city.id}
                type="button"
                onClick={() => onSelectCity(city.id)}
                className={`px-2 py-1.5 rounded-lg text-left transition flex items-center justify-between gap-1 border cursor-pointer ${
                  isSel
                    ? 'bg-slate-900 text-white border-slate-900 ring-2 ring-slate-900/20 font-bold'
                    : 'bg-white text-slate-800 border-slate-200 hover:border-slate-400 font-medium'
                }`}
              >
                <span className="text-[11px] truncate">{city.name}</span>
                <span className="flex items-center gap-1 shrink-0">
                  <span
                    className="w-2.5 h-2.5 rounded-full inline-block border border-white/60"
                    style={{ backgroundColor: isMissing ? '#94a3b8' : bucket?.hex ?? '#94a3b8' }}
                  />
                  <span className={`text-[10px] font-mono ${isSel ? 'text-amber-300' : isMissing ? 'text-rose-600 font-bold' : 'text-slate-600'}`}>
                    {isMissing ? 'Thiếu' : vnNum(value, 0)}
                  </span>
                </span>
              </button>
            );
          })}
        </div>

        {/* Chú giải thang màu CPCB 6 bậc + Tách biệt dấu hiệu Đang chọn */}
        <div className="mt-2.5 pt-2 border-t border-slate-200/80">
          <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-[10px] text-slate-700">
            <span className="font-semibold text-slate-800">Thang AQI:</span>
            {CPCB_BUCKETS.map((b) => (
              <span key={b.key} className="inline-flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: b.hex }} />
                <span>{b.rangeText} ({b.labelVN.split(' ')[0]})</span>
              </span>
            ))}
            <span className="inline-flex items-center gap-1 font-medium text-slate-700">
              <span className="w-2.5 h-2.5 rounded-full inline-block border border-dashed border-slate-700 bg-slate-200 text-[8px] leading-none text-center">
                /
              </span>
              <span>Thiếu DL</span>
            </span>
          </div>

          <div className="mt-1.5 flex items-start gap-1.5 text-[10px] text-slate-500 leading-snug">
            <Info className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
            <span>
              <strong>Viền kép ★ + cỡ lớn</strong> = thành phố đang chọn; <strong>Màu chấm</strong> = mức AQI. 8 chấm là dữ liệu cấp thành phố (trung bình trạm CPCB & lưới ERA5 0,25°), <em>không suy rộng thành vùng ô nhiễm liên tục</em>.
            </span>
          </div>

          {/* Cảnh báo cỡ mẫu nhỏ cho nhóm thành phố nếu đang chọn Nhóm 2 hoặc Nhóm 3 (Y18) */}
          {selectedCityObj.smallSampleWarning && (
            <div className="mt-1.5 px-2 py-1 rounded bg-amber-50 border border-amber-200/80 flex items-center gap-1.5 text-[10px] text-amber-900">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
              <span>
                <strong>Lưu ý cỡ mẫu ({selectedCityObj.name}):</strong> {selectedCityObj.region}. Xem quy ước &lt;30 ngày nặng ở Lớp Chi Tiết.
              </span>
            </div>
          )}

          {selectedCityVal.isMissing && (
            <div className="mt-1.5 px-2 py-1 rounded bg-rose-50 border border-rose-200 flex items-center gap-1.5 text-[10px] text-rose-900 font-medium">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
              <span>
                {selectedCityObj.name}: {selectedCityVal.missingReason} (không tô như AQI = 0).
              </span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
