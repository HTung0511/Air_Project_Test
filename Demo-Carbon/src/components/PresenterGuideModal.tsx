import React, { useState } from 'react';
import { X, FileText, CheckSquare, Play, AlertCircle } from 'lucide-react';
import { STORY_BOOKMARKS, SplitType, formatDateVN } from '../data/aqiHelpers';

interface PresenterGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
  isRevealed: boolean;
  onLoadCase: (city: string, split: SplitType, dateTarget: string, bookmarkId: string) => void;
}

export const PresenterGuideModal: React.FC<PresenterGuideModalProps> = ({
  isOpen,
  onClose,
  isRevealed,
  onLoadCase,
}) => {
  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});

  if (!isOpen) return null;

  const checklist = [
    'Kiểm tra chạy Offline thực tế trên máy trình chiếu (tắt thử mạng sau khi mở bản build để xác nhận SVG bản đồ Ấn Độ và 2.922 cặp dữ liệu hoạt động độc lập).',
    'Kiểm tra độ phân giải máy chiếu (1280×720 / 1920×1080): xác nhận hai làn của Thước quyết định AQI và cụm phóng to NCR (Delhi – Gurugram) đọc rõ, không chồng chữ.',
    'Xác nhận chế độ khởi động Chống lộ đáp án (Anti-spoiler): nút "Ẩn thực tế t+1" đang bật và Mini Map đang để ở "AQI ngày t" để màu bản đồ không tiết lộ kết quả ngày mai.',
    'Kiểm tra phím tắt bàn phím: phím ← / → để đổi ngày lịch, phím Space để Mở/Ẩn thực tế t+1, phím D để mở/đóng Lớp Chi Tiết mà vẫn giữ nguyên thành phố & ngày.',
    'Nắm vững 4 điểm trung thực phương pháp khi vấn đáp: (1) F01 chưa đóng (as_of cắt bảng đã làm sạch hồi cứu); (2) Holdout ΔMAE = -1,02, KTC [-2,70; +0,48] chứa 0 → chưa đủ bằng chứng kết luận L3 cải thiện MAE, không chứng minh tương đương; (3) Quy ước <30 ngày nặng cho nhóm thành phố; (4) Không diễn giải nhân quả giữa L1, L2, L3.',
  ];

  return (
    <div
      className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-[2px] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-label="Tài liệu hỗ trợ người thuyết trình: Ghi chú lời nói và Checklist"
    >
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden">
        <div className="px-5 py-3.5 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-amber-300" />
            <h2 className="text-sm font-bold">
              Tài liệu Hỗ trợ Thuyết trình Riêng (Y07 · Y35 · Y37) — Lưu tại <code className="font-mono text-amber-300">deliverables/GHI_CHU_THUYET_TRINH_VA_CHECKLIST.md</code>
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs font-bold flex items-center gap-1 cursor-pointer"
          >
            <X className="w-4 h-4" />
            <span>Đóng</span>
          </button>
        </div>

        <div className="p-5 overflow-y-auto space-y-5 text-xs text-slate-800">
          <div className="p-3 rounded-lg bg-slate-100 border border-slate-200 flex items-start gap-2 text-slate-700">
            <AlertCircle className="w-4 h-4 text-slate-600 shrink-0 mt-0.5" />
            <span>
              Theo đúng nguyên tắc Y07 và Y35, ghi chú lời nói (2–3 câu mỗi ca) và checklist trước buổi chiếu được tách thành tài liệu riêng (<code className="font-mono">deliverables/GHI_CHU_THUYET_TRINH_VA_CHECKLIST.md</code>) để không làm chật màn hình chính hoặc vô tình lộ trên máy chiếu. Bạn có thể xem nhanh hoặc nạp từng ca từ đây trước giờ báo cáo.
            </span>
          </div>

          {/* Kịch bản lời nói từng tình huống (Y07, Y37) */}
          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-2.5">
              1. Kịch bản Thuyết trình Tuần tự &amp; Ghi chú Lời nói (2–3 câu mỗi ca)
            </h3>
            <div className="space-y-2.5">
              {STORY_BOOKMARKS.map((bm) => (
                <div
                  key={bm.id}
                  className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-3"
                >
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-slate-900 text-amber-300 font-bold text-[10px] uppercase">
                        {bm.stepBadge}
                      </span>
                      <span className="font-bold text-slate-900 text-xs">
                        {isRevealed ? bm.titleRevealed : bm.titleNeutral}
                      </span>
                      <span className="font-mono text-[11px] text-slate-600">
                        ({bm.city}: t={formatDateVN(bm.dateInput)} → t+1={formatDateVN(bm.dateTarget)})
                      </span>
                    </div>
                    {isRevealed ? (
                      <>
                        <p className="text-[11px] text-slate-600 font-medium"><strong>Số liệu:</strong> {bm.summaryNote}</p>
                        <p className="text-xs text-indigo-950 bg-indigo-50/80 px-2.5 py-1.5 rounded border border-indigo-200/80 italic">“{bm.presenterScript}”</p>
                      </>
                    ) : <p className="text-[11px] text-slate-600">Nội dung ca được ẩn cho đến khi mở kết quả.</p>}
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      onLoadCase(bm.city, bm.split, bm.dateTarget, bm.id);
                      onClose();
                    }}
                    className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shrink-0 flex items-center gap-1 cursor-pointer self-start md:self-center"
                  >
                    <Play className="w-3 h-3" />
                    <span>Nạp ca này</span>
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Checklist trước trình chiếu (Y35) */}
          <div className="pt-3 border-t border-slate-200">
            <h3 className="text-sm font-bold text-slate-900 mb-1 flex items-center gap-1.5">
              <CheckSquare className="w-4 h-4 text-teal-700" />
              <span>2. Checklist tự kiểm trước buổi trình chiếu (Y35)</span>
            </h3>
            <p className="text-[11px] text-slate-500 mb-2.5">
              Lưu ý: Đánh dấu dưới đây giúp người trình bày rà soát quy trình chuẩn bị, không thay thế việc kiểm thử trực tiếp trên máy chiếu thật.
            </p>
            <div className="space-y-2">
              {checklist.map((item, idx) => (
                <label
                  key={idx}
                  className="flex items-start gap-2.5 p-2.5 rounded-lg border border-slate-200 bg-slate-50/70 hover:bg-slate-100 cursor-pointer select-none"
                >
                  <input
                    type="checkbox"
                    checked={Boolean(checkedItems[idx])}
                    onChange={() => setCheckedItems((prev) => ({ ...prev, [idx]: !prev[idx] }))}
                    className="mt-0.5 rounded accent-teal-700"
                  />
                  <span className={checkedItems[idx] ? 'line-through text-slate-400' : 'text-slate-800'}>
                    {item}
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
