"""Chặn mạng ở mức socket cho một tiến trình Python (dùng khi kiểm "cache đủ thì không gọi mạng").

Python tự nạp module tên `sitecustomize` lúc khởi động nếu thư mục chứa nó nằm trong PYTHONPATH. `tools/run_notebook.py
--block-network` thêm thư mục này vào PYTHONPATH của kernel và đặt AIR_BLOCK_NETWORK=1. Khi đó mọi kết nối ra ngoài máy
(kể cả tra DNS) bị từ chối và được ghi vào file AIR_NET_ATTEMPT_LOG; kết nối nội bộ (127.0.0.1, ::1, socket Unix) vẫn chạy
vì kernel Jupyter cần chúng. Không đặt AIR_BLOCK_NETWORK thì module này không làm gì.
"""
import os
import socket

if os.environ.get("AIR_BLOCK_NETWORK") == "1":
    _LOCAL = {"127.0.0.1", "::1", "localhost", "0.0.0.0", ""}
    _log_path = os.environ.get("AIR_NET_ATTEMPT_LOG")
    _connect, _connect_ex, _getaddrinfo = socket.socket.connect, socket.socket.connect_ex, socket.getaddrinfo

    def _note(what):
        if _log_path:
            with open(_log_path, "a", encoding="utf-8") as f:
                f.write(f"pid={os.getpid()} {what}\n")

    def _host(address):
        return address[0] if isinstance(address, tuple) else None           # socket Unix: địa chỉ là chuỗi đường dẫn

    def _guard_connect(self, address):
        h = _host(address)
        if h is None or h in _LOCAL:
            return _connect(self, address)
        _note(f"connect {address!r}")
        raise OSError(f"MẠNG BỊ VÔ HIỆU HOÁ ĐỂ KIỂM THỬ: connect {address!r}")

    def _guard_connect_ex(self, address):
        h = _host(address)
        if h is None or h in _LOCAL:
            return _connect_ex(self, address)
        _note(f"connect_ex {address!r}")
        raise OSError(f"MẠNG BỊ VÔ HIỆU HOÁ ĐỂ KIỂM THỬ: connect_ex {address!r}")

    def _guard_getaddrinfo(host, *args, **kwargs):
        h = host.decode() if isinstance(host, bytes) else host
        if h is None or h in _LOCAL:
            return _getaddrinfo(host, *args, **kwargs)
        _note(f"getaddrinfo {h!r}")
        raise socket.gaierror(f"MẠNG BỊ VÔ HIỆU HOÁ ĐỂ KIỂM THỬ: tra DNS {h!r}")

    socket.socket.connect = _guard_connect
    socket.socket.connect_ex = _guard_connect_ex
    socket.getaddrinfo = _guard_getaddrinfo
