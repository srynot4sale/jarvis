Database structure:

<code>

CREATE TABLE IF NOT EXISTS `function_calendar_events` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `datetime` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `datetime` (`datetime`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;

CREATE TABLE IF NOT EXISTS `function_list_items` (
  `listname` varchar(255) CHARACTER SET utf8 NOT NULL,
  `item` varchar(255) CHARACTER SET utf8 NOT NULL,
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `item` (`item`),
  KEY `listname` (`listname`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 ;

</code>
