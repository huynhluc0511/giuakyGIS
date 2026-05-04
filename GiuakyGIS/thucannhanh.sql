CREATE TABLE san_pham (
    san_pham_id SERIAL PRIMARY KEY,
    ten_san_pham VARCHAR(255) NOT NULL,
    gia NUMERIC(12,2) NOT NULL,
    don_vi VARCHAR(50),
    mo_ta TEXT,
    trang_thai BOOLEAN DEFAULT TRUE
);
CREATE TABLE kho_hang (
    kho_id SERIAL PRIMARY KEY,
    san_pham_id INT REFERENCES san_pham(san_pham_id),
    so_luong INT NOT NULL,
    ngay_cap_nhat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE nhap_hang (
    nhap_id SERIAL PRIMARY KEY,
    san_pham_id INT REFERENCES san_pham(san_pham_id),
    so_luong INT NOT NULL,
    ngay_nhap TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE xuat_hang (
    xuat_id SERIAL PRIMARY KEY,
    san_pham_id INT REFERENCES san_pham(san_pham_id),
    so_luong INT NOT NULL,
    ngay_xuat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE shipper (
    shipper_id SERIAL PRIMARY KEY,
    ho_ten VARCHAR(255),
    so_dien_thoai VARCHAR(20),
    trang_thai VARCHAR(50) -- rảnh, đang giao
);
CREATE TABLE don_hang (
    don_hang_id SERIAL PRIMARY KEY,
    khach_hang VARCHAR(255),
    dia_chi_giao TEXT,
    trang_thai VARCHAR(50), 
    -- Chưa giao | Đang giao | Đã giao
    shipper_id INT REFERENCES shipper(shipper_id),
    ngay_tao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE chi_tiet_don_hang (
    ct_id SERIAL PRIMARY KEY,
    don_hang_id INT REFERENCES don_hang(don_hang_id),
    san_pham_id INT REFERENCES san_pham(san_pham_id),
    so_luong INT,
    don_gia NUMERIC(12,2)
);
CREATE TABLE lo_trinh_shipper (
    lo_trinh_id SERIAL PRIMARY KEY,
    shipper_id INT REFERENCES shipper(shipper_id),
    don_hang_id INT REFERENCES don_hang(don_hang_id),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    thoi_gian TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO san_pham (ten_san_pham, gia, don_vi, mo_ta)
VALUES
('Hamburger bò', 35000, 'cái', 'Hamburger bò truyền thống'),
('Gà rán', 45000, 'phần', 'Gà rán giòn cay'),
('Khoai tây chiên', 25000, 'phần', 'Khoai tây chiên giòn'),
('Coca Cola', 15000, 'chai', 'Nước ngọt Coca 330ml');
INSERT INTO kho_hang (san_pham_id, so_luong)
VALUES
(1, 100),
(2, 80),
(3, 150),
(4, 200);
INSERT INTO nhap_hang (san_pham_id, so_luong)
VALUES
(1, 50),
(2, 40),
(3, 100),
(4, 120);
INSERT INTO xuat_hang (san_pham_id, so_luong)
VALUES
(1, 10),
(2, 5),
(3, 15),
(4, 20);
INSERT INTO shipper (ho_ten, so_dien_thoai, trang_thai)
VALUES
('Nguyễn Văn A', '0901234567', 'đang giao'),
('Trần Văn B', '0912345678', 'rảnh');
INSERT INTO don_hang (khach_hang, dia_chi_giao, trang_thai, shipper_id)
VALUES
('Lê Thị Mai', '123 Lê Lợi, Quận 1', 'Đang giao', 1),
('Phạm Văn Hùng', '45 Nguyễn Trãi, Quận 5', 'Chưa giao', 2);
INSERT INTO chi_tiet_don_hang (don_hang_id, san_pham_id, so_luong, don_gia)
VALUES
(1, 1, 2, 35000),
(1, 3, 1, 25000),
(1, 4, 2, 15000),
(2, 2, 1, 45000),
(2, 4, 1, 15000);
INSERT INTO lo_trinh_shipper (shipper_id, don_hang_id, latitude, longitude)
VALUES
(1, 1, 10.776889, 106.700806), -- điểm xuất phát (quán)
(1, 1, 10.777500, 106.701200),
(1, 1, 10.778200, 106.702100),
(1, 1, 10.779000, 106.703000); -- gần tới khách
SELECT latitude, longitude, thoi_gian
FROM lo_trinh_shipper
WHERE don_hang_id = 1
ORDER BY thoi_gian;
