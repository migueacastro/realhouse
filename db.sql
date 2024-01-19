
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    hash TEXT NOT NULL,
    phone TEXT NOT NULL
);

CREATE TABLE deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    state TEXT NOT NULL,
    placetype TEXT NOT NULL,
    rooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    stories INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    squaremeters INTEGER NOT NULL,
    image TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,

    FOREIGN KEY(deal_id) REFERENCES deals(id)
);

