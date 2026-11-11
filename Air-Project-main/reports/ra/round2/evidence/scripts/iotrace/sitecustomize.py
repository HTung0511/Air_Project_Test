"""DA vòng 2 — theo dõi I/O và chặn mạng cho mọi tiến trình Python (kể cả kernel của notebook).

Kích hoạt bằng biến môi trường, không sửa mã được kiểm:
  PYTHONPATH=<thư mục này>          để Python tự nạp file này lúc khởi động
  DA_IO_TRACE=<file .jsonl>          nơi ghi sự kiện (mỗi dòng một JSON)
  DA_IO_ROOT=<thư mục bản sao>       chỉ ghi các file nằm dưới thư mục này
  DA_NET_BLOCK=1                     chặn mọi kết nối không phải loopback (ném OSError), và ghi lại lần thử
Ghi: sự kiện "open" (đường dẫn, đọc/ghi, sha256 của file tại lúc mở để đọc) và "net" (địa chỉ, bị chặn hay không).
SHA của file được GHI lấy sau khi chạy xong, bằng r2_iotrace_summary.py.
"""
import os, sys

_LOG, _ROOT = os.environ.get("DA_IO_TRACE"), os.environ.get("DA_IO_ROOT")
_BLOCK = os.environ.get("DA_NET_BLOCK") == "1"
if _LOG:
    import hashlib, json, time
    _root = os.path.realpath(_ROOT) if _ROOT else None
    _fd = os.open(_LOG, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    _busy = [False]
    _seen = set()
    _proc = " ".join(sys.argv[:3]) if hasattr(sys, "argv") else ""

    def _emit(rec):
        rec.update(ts=round(time.time(), 3), pid=os.getpid())
        os.write(_fd, (json.dumps(rec, ensure_ascii=False) + "\n").encode())

    def _sha(path):
        h = hashlib.sha256()
        f = os.open(path, os.O_RDONLY)                       # os.open cũng phát sự kiện "open": đã chặn lặp bằng _busy
        try:
            while True:
                b = os.read(f, 1 << 20)
                if not b:
                    break
                h.update(b)
        finally:
            os.close(f)
        return h.hexdigest()

    def _hook(event, args):
        if _busy[0]:
            return
        if event == "open":
            path, mode, flags = args
            if not isinstance(path, (str, bytes)):
                return
            _busy[0] = True
            try:
                p = os.path.realpath(os.fsdecode(path))
                if _root and not p.startswith(_root + os.sep):
                    return
                if "__pycache__" in p or ".ipynb_checkpoints" in p:
                    return
                if mode is None:
                    write = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
                else:
                    write = any(ch in mode for ch in "wax+")
                key = (p, write)
                if key in _seen:
                    return
                _seen.add(key)
                rec = {"ev": "open", "path": p, "kind": "write" if write else "read", "argv": _proc}
                if not write:
                    try:
                        rec["sha256_at_open"] = _sha(p) if os.path.isfile(p) else None
                    except OSError as e:
                        rec["sha256_at_open"] = None; rec["err"] = type(e).__name__
                _emit(rec)
            finally:
                _busy[0] = False
        elif event in ("socket.connect", "socket.getaddrinfo"):
            addr = args[1] if event == "socket.connect" else (args[0], args[1])
            host = addr[0] if isinstance(addr, tuple) else None           # AF_UNIX: addr là đường dẫn -> coi là cục bộ
            if isinstance(host, bytes):
                host = host.decode("ascii", "replace")
            local = host is None or host in ("localhost", "::1", "", "0.0.0.0") or str(host).startswith("127.")
            if local:
                return
            _busy[0] = True
            try:
                _emit({"ev": "net", "what": event, "addr": repr(addr), "blocked": _BLOCK, "argv": _proc})
            finally:
                _busy[0] = False
            if _BLOCK:
                raise OSError(f"[DA] mạng bị tắt trong phép thử: {event} {addr!r}")

    sys.addaudithook(_hook)
