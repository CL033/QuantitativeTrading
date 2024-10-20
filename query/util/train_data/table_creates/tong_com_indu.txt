CREATE TABLE `tong_com_indu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `com_code` varchar(255) DEFAULT NULL,
  `com_name` varchar(255) DEFAULT NULL,
  `fir_indu` varchar(255) DEFAULT NULL,
  `sec_indu` varchar(255) DEFAULT NULL,
  `tir_indu` varchar(255) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `fir_indu_code` varchar(255) DEFAULT NULL,
  `sec_indu_code` varchar(255) DEFAULT NULL,
  `tir_indu_code` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `id` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5396 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='上市公司申万行业分类'