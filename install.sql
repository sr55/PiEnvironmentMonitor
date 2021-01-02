CREATE TABLE environment_data
    ( 
        `room` TEXT NOT NULL , 
        `datetime` DATETIME NOT NULL , 
        `temp` DECIMAL(10,2) NOT NULL , 
        `pressure` DECIMAL(10,2) NOT NULL , 
        `humidity` DECIMAL(10,2) NOT NULL , 
        `air_quality` DECIMAL(20,2) NULL
    );
