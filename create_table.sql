CREATE TABLE IF NOT EXISTS `ad_1a5ec1448f739c0`.`request_recorder` (
  `ID` INT NOT NULL AUTO_INCREMENT COMMENT '',
  `timestamp` INT NOT NULL COMMENT '',
  `current_request_count` INT NOT NULL COMMENT '',
  `max_possible_count` INT NOT NULL COMMENT '',
  PRIMARY KEY (`ID`)  COMMENT '',
  UNIQUE INDEX `timestamp_UNIQUE` (`timestamp` ASC)  COMMENT '')
ENGINE = InnoDB;