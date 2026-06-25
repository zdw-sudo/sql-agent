-- Sample e-commerce analytics database for SQL Agent demo

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    amount REAL NOT NULL,
    order_date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO users (id, name, city, created_at) VALUES
(1, '张三', '上海', '2023-06-01'),
(2, '李四', '北京', '2023-07-15'),
(3, '王五', '深圳', '2023-08-20'),
(4, '赵六', '上海', '2023-09-10'),
(5, '钱七', '杭州', '2023-10-05'),
(6, '孙八', '北京', '2023-11-12'),
(7, '周九', '成都', '2024-01-08'),
(8, '吴十', '深圳', '2024-02-18');

INSERT INTO products (id, name, category, price) VALUES
(1, '无线耳机', '数码', 299.0),
(2, '机械键盘', '数码', 459.0),
(3, '运动水杯', '生活', 89.0),
(4, '笔记本电脑', '数码', 5999.0),
(5, '咖啡机', '家电', 1299.0),
(6, '跑步鞋', '运动', 399.0),
(7, '蓝牙音箱', '数码', 199.0),
(8, '护眼台灯', '家电', 259.0);

INSERT INTO orders (id, user_id, product_id, quantity, amount, order_date) VALUES
(1, 1, 1, 2, 598.0, '2024-01-05'),
(2, 1, 4, 1, 5999.0, '2024-01-12'),
(3, 2, 2, 1, 459.0, '2024-01-08'),
(4, 3, 6, 2, 798.0, '2024-01-15'),
(5, 4, 3, 3, 267.0, '2024-01-20'),
(6, 5, 5, 1, 1299.0, '2024-01-22'),
(7, 2, 7, 1, 199.0, '2024-01-25'),
(8, 6, 1, 1, 299.0, '2024-01-28'),
(9, 7, 8, 2, 518.0, '2024-02-01'),
(10, 8, 6, 1, 399.0, '2024-02-05'),
(11, 1, 2, 1, 459.0, '2024-02-10'),
(12, 3, 4, 1, 5999.0, '2024-02-12'),
(13, 4, 1, 1, 299.0, '2024-02-15'),
(14, 5, 3, 2, 178.0, '2024-02-18'),
(15, 6, 5, 1, 1299.0, '2024-02-20'),
(16, 2, 6, 1, 399.0, '2024-02-22'),
(17, 7, 7, 2, 398.0, '2024-02-25'),
(18, 8, 2, 1, 459.0, '2024-03-01'),
(19, 1, 8, 1, 259.0, '2024-03-05'),
(20, 3, 3, 5, 445.0, '2024-03-08');
