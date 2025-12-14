-- transfers tablosuna AUTO_INCREMENT eklemek için migration script
-- Bu script'i çalıştırmadan önce veritabanı yedeği alın!

-- transfer_id sütununa AUTO_INCREMENT ekle
ALTER TABLE transfers 
MODIFY COLUMN transfer_id INT AUTO_INCREMENT;

-- Not: MySQL otomatik olarak mevcut MAX(transfer_id) değerinden devam eder
-- Eğer tablo boşsa, 1'den başlar

