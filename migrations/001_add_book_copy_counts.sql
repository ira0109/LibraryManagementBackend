ALTER TABLE books
    ADD COLUMN total_copies INT NOT NULL DEFAULT 1,
    ADD COLUMN available_copies INT NOT NULL DEFAULT 1;

UPDATE books
SET available_copies = CASE
    WHEN UPPER(status) = 'ISSUED' THEN 0
    ELSE 1
END;
