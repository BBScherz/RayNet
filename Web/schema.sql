CREATE TABLE user (
    id INTEGER NOT NULL,
    username VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password VARCHAR(150) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (username),
    UNIQUE (email)
);
CREATE TABLE upload (
    id INTEGER NOT NULL,
    filename VARCHAR(100) NOT NULL,
    data BLOB NOT NULL,
    upload_date DATETIME,
    user_id INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES user (id)
);
