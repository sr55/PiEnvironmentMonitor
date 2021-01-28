CREATE TABLE environment_data
    ( 
        `room` TEXT NOT NULL , 
        `datetime` DATETIME NOT NULL , 
        `temp` DECIMAL(10,2) DEFAULT NULL , 
        `pressure` DECIMAL(10,2) DEFAULT NULL , 
        `humidity` DECIMAL(10,2) DEFAULT NULL , 
        `air_quality` DECIMAL(20,2) DEFAULT NULL ,
        `light` DECIMAL(10,2) DEFAULT NULL
    );