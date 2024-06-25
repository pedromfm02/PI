USE Detibot;

-- Creates update_time table
CREATE TABLE IF NOT EXISTS update_time (
    id INT PRIMARY KEY,
    period_date VARCHAR(20),
    update_period VARCHAR(30)
);

-- Creates table that saves url metadata
CREATE TABLE IF NOT EXISTS url_source (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url_link VARCHAR(255) UNIQUE,
    paths VARCHAR(255),
    descript VARCHAR(255),
    wait_time INT,
    recursive_url BOOLEAN,
    update_period_str VARCHAR(255),
    update_period_id INT,
    FOREIGN KEY (update_period_id) REFERENCES update_time (id)
);

-- Creates table that saves child urls
CREATE TABLE IF NOT EXISTS url_child_source (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url_link VARCHAR(255),
    parent_id INT,
    FOREIGN KEY (parent_id) REFERENCES url_source (id) ON DELETE CASCADE
);

-- Creates table that saves metadata of files
CREATE TABLE IF NOT EXISTS file_source (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) UNIQUE,
    file_path VARCHAR(255),
    loader_type VARCHAR(255),
    descript VARCHAR(255)
);

-- Creates table that saves metadata of faqs
CREATE TABLE IF NOT EXISTS faq_source (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(255) UNIQUE,
    answer VARCHAR(255) 
);

-- inserts the predefined rows of update_time
INSERT INTO update_time (id,period_date, update_period) VALUES (1,'Daily', '2024-03-22 00:00:00');
INSERT INTO update_time (id,period_date, update_period) VALUES (2,'Weekly', '2024-03-22 00:00:00');
INSERT INTO update_time (id,period_date, update_period) VALUES (3,'Monthly', '2024-03-22 00:00:00');
INSERT INTO update_time (id,period_date, update_period) VALUES (4,'Quarter', '2024-03-22 00:00:00');


