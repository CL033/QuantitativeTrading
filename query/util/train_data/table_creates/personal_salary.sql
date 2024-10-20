CREATE TABLE `personal_salary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `com_code` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `company_name` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `year` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `development_salary` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `sale_salary` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `manage_salary` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `number` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `development_personnal` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `sale_personnal` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `finance_personnal` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `administrative_personnal` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `manage_personal` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21405 DEFAULT CHARSET=utf8 COLLATE=utf8_bin