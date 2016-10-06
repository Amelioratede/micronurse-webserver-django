DROP DATABASE IF EXISTS MicroNurse;
CREATE DATABASE MicroNurse DEFAULT CHARACTER SET utf8;

DROP USER 'MicroNurse'@'localhost';
CREATE USER 'MicroNurse'@'localhost' IDENTIFIED BY '7824af5833060c92e8e4wefb7a44c110ee47';
GRANT ALL ON MicroNurse.* TO 'MicroNurse'@'localhost';
