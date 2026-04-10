-- ============================================================
-- Schema: GitHub Miner - Nuevas Tablas
-- MySQL 8.0+
-- ============================================================

-- ------------------------------------------------------------
-- Tabla: llx_git_users
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_users`;
CREATE TABLE `llx_git_users` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `github_id` BIGINT UNSIGNED NOT NULL UNIQUE COMMENT 'ID único de GitHub',
  `login` VARCHAR(255) NOT NULL COMMENT 'Nombre de usuario único',
  `name` VARCHAR(255) DEFAULT NULL COMMENT 'Nombre completo',
  `avatar_url` TEXT DEFAULT NULL COMMENT 'URL del avatar',
  `html_url` VARCHAR(500) DEFAULT NULL COMMENT 'URL del perfil',
  `bio` TEXT DEFAULT NULL COMMENT 'Biografía',
  `company` VARCHAR(255) DEFAULT NULL COMMENT 'Empresa',
  `blog` VARCHAR(500) DEFAULT NULL COMMENT 'Blog personal',
  `type` ENUM('User', 'Organization') DEFAULT 'User' COMMENT 'Tipo de cuenta',
  `location` VARCHAR(255) DEFAULT NULL COMMENT 'Ubicación',
  `country` VARCHAR(100) DEFAULT NULL COMMENT 'País',
  `city` VARCHAR(100) DEFAULT NULL COMMENT 'Ciudad',
  `timezone` VARCHAR(50) DEFAULT NULL COMMENT 'Zona horaria',
  `email` VARCHAR(255) DEFAULT NULL COMMENT 'Email público',
  `twitter` VARCHAR(100) DEFAULT NULL COMMENT 'Twitter username',
  `linkedin` VARCHAR(255) DEFAULT NULL COMMENT 'LinkedIn URL',
  `website` VARCHAR(500) DEFAULT NULL COMMENT 'Sitio web',
  `hireable` TINYINT(1) DEFAULT 0 COMMENT 'Disponible para contratar',
  `followers` INT UNSIGNED DEFAULT 0 COMMENT 'Seguidores',
  `following` INT UNSIGNED DEFAULT 0 COMMENT 'Siguiendo',
  `public_repos` INT UNSIGNED DEFAULT 0 COMMENT 'Repos públicos',
  `public_gists` INT UNSIGNED DEFAULT 0 COMMENT 'Gists públicos',
  `created_at` DATETIME DEFAULT NULL COMMENT 'Fecha de creación',
  `updated_at` DATETIME DEFAULT NULL COMMENT 'Última actualización',
  PRIMARY KEY (`rowid`),
  KEY `idx_github_id` (`github_id`),
  KEY `idx_login` (`login`),
  KEY `idx_country` (`country`),
  KEY `idx_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Usuarios de GitHub';

-- ------------------------------------------------------------
-- Tabla: llx_git_repositories
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_repositories`;
CREATE TABLE `llx_git_repositories` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `github_id` BIGINT UNSIGNED NOT NULL UNIQUE COMMENT 'ID único de GitHub',
  `name` VARCHAR(255) NOT NULL COMMENT 'Nombre del repositorio',
  `full_name` VARCHAR(500) NOT NULL COMMENT 'Nombre completo (owner/repo)',
  `fk_owner` BIGINT UNSIGNED DEFAULT NULL COMMENT 'FK al usuario propietario',
  `description` TEXT DEFAULT NULL COMMENT 'Descripción',
  `stars` INT UNSIGNED DEFAULT 0 COMMENT 'Estrellas',
  `forks` INT UNSIGNED DEFAULT 0 COMMENT 'Forks',
  `watchers` INT UNSIGNED DEFAULT 0 COMMENT 'Watchers',
  `open_issues` INT UNSIGNED DEFAULT 0 COMMENT 'Issues abiertos',
  `language` VARCHAR(100) DEFAULT NULL COMMENT 'Lenguaje principal',
  `license` VARCHAR(100) DEFAULT NULL COMMENT 'Licencia',
  `url` VARCHAR(500) NOT NULL COMMENT 'URL del repositorio',
  `homepage` VARCHAR(500) DEFAULT NULL COMMENT 'Página web',
  `topics` JSON DEFAULT NULL COMMENT 'Topics/Tags',
  `created_at` DATETIME DEFAULT NULL COMMENT 'Fecha de creación',
  `updated_at` DATETIME DEFAULT NULL COMMENT 'Última actualización',
  `pushed_at` DATETIME DEFAULT NULL COMMENT 'Último push',
  PRIMARY KEY (`rowid`),
  KEY `idx_github_id` (`github_id`),
  KEY `idx_full_name` (`full_name`),
  KEY `idx_language` (`language`),
  KEY `idx_stars` (`stars`),
  KEY `idx_fk_owner` (`fk_owner`),
  CONSTRAINT `fk_llx_git_repositories_owner` FOREIGN KEY (`fk_owner`) REFERENCES `llx_git_users` (`rowid`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Repositorios de GitHub';

-- ------------------------------------------------------------
-- Tabla: llx_git_technologies
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_technologies`;
CREATE TABLE `llx_git_technologies` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL UNIQUE COMMENT 'Nombre del lenguaje/tecnología',
  `repositories_count` INT UNSIGNED DEFAULT 0 COMMENT 'Cantidad de repositorios',
  `users_count` INT UNSIGNED DEFAULT 0 COMMENT 'Cantidad de usuarios',
  PRIMARY KEY (`rowid`),
  KEY `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Lenguajes y tecnologías';

-- ------------------------------------------------------------
-- Tabla: llx_git_user_repositories (Repos que posee un usuario)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_user_repositories`;
CREATE TABLE `llx_git_user_repositories` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `fk_user` BIGINT UNSIGNED NOT NULL COMMENT 'FK al usuario',
  `fk_repository` BIGINT UNSIGNED NOT NULL COMMENT 'FK al repositorio',
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_user_repo` (`fk_user`, `fk_repository`),
  KEY `idx_fk_user` (`fk_user`),
  KEY `idx_fk_repository` (`fk_repository`),
  CONSTRAINT `fk_llx_git_user_repos_user` FOREIGN KEY (`fk_user`) REFERENCES `llx_git_users` (`rowid`) ON DELETE CASCADE,
  CONSTRAINT `fk_llx_git_user_repos_repo` FOREIGN KEY (`fk_repository`) REFERENCES `llx_git_repositories` (`rowid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Relación usuario - repositorios propios';

-- ------------------------------------------------------------
-- Tabla: llx_git_user_contributions (Repos a los que contribuye un usuario)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_user_contributions`;
CREATE TABLE `llx_git_user_contributions` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `fk_user` BIGINT UNSIGNED NOT NULL COMMENT 'FK al usuario',
  `fk_repository` BIGINT UNSIGNED NOT NULL COMMENT 'FK al repositorio',
  `contributions` INT UNSIGNED DEFAULT 0 COMMENT 'Número de contribuciones',
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_user_contrib` (`fk_user`, `fk_repository`),
  KEY `idx_fk_user` (`fk_user`),
  KEY `idx_fk_repository` (`fk_repository`),
  CONSTRAINT `fk_llx_git_contrib_user` FOREIGN KEY (`fk_user`) REFERENCES `llx_git_users` (`rowid`) ON DELETE CASCADE,
  CONSTRAINT `fk_llx_git_contrib_repo` FOREIGN KEY (`fk_repository`) REFERENCES `llx_git_repositories` (`rowid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Relación usuario - repositorios contribuidores';

-- ------------------------------------------------------------
-- Tabla: llx_git_repo_contributors (Contribuidores de un repositorio)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_repo_contributors`;
CREATE TABLE `llx_git_repo_contributors` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `fk_repository` BIGINT UNSIGNED NOT NULL COMMENT 'FK al repositorio',
  `fk_user` BIGINT UNSIGNED NOT NULL COMMENT 'FK al usuario contribuidor',
  `contributions` INT UNSIGNED DEFAULT 0 COMMENT 'Número de contribuciones',
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_repo_contributor` (`fk_repository`, `fk_user`),
  KEY `idx_fk_repository` (`fk_repository`),
  KEY `idx_fk_user` (`fk_user`),
  CONSTRAINT `fk_llx_git_repo_contrib_repo` FOREIGN KEY (`fk_repository`) REFERENCES `llx_git_repositories` (`rowid`) ON DELETE CASCADE,
  CONSTRAINT `fk_llx_git_repo_contrib_user` FOREIGN KEY (`fk_user`) REFERENCES `llx_git_users` (`rowid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Contribuidores por repositorio';

-- ------------------------------------------------------------
-- Tabla: llx_git_user_technologies (Tecnologías que usa un usuario)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_user_technologies`;
CREATE TABLE `llx_git_user_technologies` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `fk_user` BIGINT UNSIGNED NOT NULL COMMENT 'FK al usuario',
  `fk_technology` BIGINT UNSIGNED NOT NULL COMMENT 'FK a la tecnología',
  `repos_count` INT UNSIGNED DEFAULT 0 COMMENT 'Repos que usan esta tecnología',
  `total_stars` INT UNSIGNED DEFAULT 0 COMMENT 'Estrellas totales en esos repos',
  `total_forks` INT UNSIGNED DEFAULT 0 COMMENT 'Forks totales en esos repos',
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_user_tech` (`fk_user`, `fk_technology`),
  KEY `idx_fk_user` (`fk_user`),
  KEY `idx_fk_technology` (`fk_technology`),
  CONSTRAINT `fk_llx_git_user_tech_user` FOREIGN KEY (`fk_user`) REFERENCES `llx_git_users` (`rowid`) ON DELETE CASCADE,
  CONSTRAINT `fk_llx_git_user_tech_tech` FOREIGN KEY (`fk_technology`) REFERENCES `llx_git_technologies` (`rowid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tecnologías por usuario';

-- ------------------------------------------------------------
-- Tabla: llx_git_repo_technologies (Tecnologías usadas en un repositorio)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_repo_technologies`;
CREATE TABLE `llx_git_repo_technologies` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `fk_repository` BIGINT UNSIGNED NOT NULL COMMENT 'FK al repositorio',
  `fk_technology` BIGINT UNSIGNED NOT NULL COMMENT 'FK a la tecnología',
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_repo_tech` (`fk_repository`, `fk_technology`),
  KEY `idx_fk_repository` (`fk_repository`),
  KEY `idx_fk_technology` (`fk_technology`),
  CONSTRAINT `fk_llx_git_repo_tech_repo` FOREIGN KEY (`fk_repository`) REFERENCES `llx_git_repositories` (`rowid`) ON DELETE CASCADE,
  CONSTRAINT `fk_llx_git_repo_tech_tech` FOREIGN KEY (`fk_technology`) REFERENCES `llx_git_technologies` (`rowid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tecnologías por repositorio';

-- ------------------------------------------------------------
-- Tabla: llx_git_user_scores (Puntuaciones de usuarios)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_user_scores`;
CREATE TABLE `llx_git_user_scores` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `fk_user` BIGINT UNSIGNED NOT NULL UNIQUE COMMENT 'FK al usuario',
  `influence_score` INT UNSIGNED DEFAULT 0 COMMENT 'Puntuación de influencia',
  `activity_score` INT UNSIGNED DEFAULT 0 COMMENT 'Puntuación de actividad',
  `tech_diversity` INT UNSIGNED DEFAULT 0 COMMENT 'Diversidad tecnológica',
  `community_score` INT UNSIGNED DEFAULT 0 COMMENT 'Puntuación comunitaria',
  `contact_completeness` TINYINT UNSIGNED DEFAULT 0 COMMENT 'Completitud de contacto (0-3)',
  PRIMARY KEY (`rowid`),
  KEY `idx_fk_user` (`fk_user`),
  CONSTRAINT `fk_llx_git_user_scores_user` FOREIGN KEY (`fk_user`) REFERENCES `llx_git_users` (`rowid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Puntuaciones de usuarios';

-- ------------------------------------------------------------
-- Tabla: llx_git_repo_scores (Puntuaciones de repositorios)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_repo_scores`;
CREATE TABLE `llx_git_repo_scores` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `fk_repository` BIGINT UNSIGNED NOT NULL UNIQUE COMMENT 'FK al repositorio',
  `popularity_score` INT UNSIGNED DEFAULT 0 COMMENT 'Puntuación de popularidad',
  `engagement_score` INT UNSIGNED DEFAULT 0 COMMENT 'Puntuación de engagement',
  `quality_score` INT UNSIGNED DEFAULT 0 COMMENT 'Puntuación de calidad',
  PRIMARY KEY (`rowid`),
  KEY `idx_fk_repository` (`fk_repository`),
  CONSTRAINT `fk_llx_git_repo_scores_repo` FOREIGN KEY (`fk_repository`) REFERENCES `llx_git_repositories` (`rowid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Puntuaciones de repositorios';

-- ------------------------------------------------------------
-- Tabla: llx_git_tech_scores (Puntuaciones de tecnologías)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_tech_scores`;
CREATE TABLE `llx_git_tech_scores` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `fk_technology` BIGINT UNSIGNED NOT NULL UNIQUE COMMENT 'FK a la tecnología',
  `popularity_score` INT UNSIGNED DEFAULT 0 COMMENT 'Puntuación de popularidad',
  `total_stars` INT UNSIGNED DEFAULT 0 COMMENT 'Estrellas totales',
  `total_repos` INT UNSIGNED DEFAULT 0 COMMENT 'Total de repos',
  `total_users` INT UNSIGNED DEFAULT 0 COMMENT 'Total de usuarios',
  PRIMARY KEY (`rowid`),
  KEY `idx_fk_technology` (`fk_technology`),
  CONSTRAINT `fk_llx_git_tech_scores_tech` FOREIGN KEY (`fk_technology`) REFERENCES `llx_git_technologies` (`rowid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Puntuaciones de tecnologías';

-- ------------------------------------------------------------
-- Tabla: llx_git_countries (Países)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_countries`;
CREATE TABLE `llx_git_countries` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL UNIQUE COMMENT 'Nombre del país',
  `code` VARCHAR(3) DEFAULT NULL COMMENT 'Código ISO',
  `users_count` INT UNSIGNED DEFAULT 0 COMMENT 'Cantidad de usuarios',
  PRIMARY KEY (`rowid`),
  KEY `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Países';

-- ------------------------------------------------------------
-- Tabla: llx_git_user_countries (Relación usuario - país)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_user_countries`;
CREATE TABLE `llx_git_user_countries` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `fk_user` BIGINT UNSIGNED NOT NULL COMMENT 'FK al usuario',
  `fk_country` BIGINT UNSIGNED NOT NULL COMMENT 'FK al país',
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_user_country` (`fk_user`, `fk_country`),
  KEY `idx_fk_user` (`fk_user`),
  KEY `idx_fk_country` (`fk_country`),
  CONSTRAINT `fk_llx_git_user_country_user` FOREIGN KEY (`fk_user`) REFERENCES `llx_git_users` (`rowid`) ON DELETE CASCADE,
  CONSTRAINT `fk_llx_git_user_country_country` FOREIGN KEY (`fk_country`) REFERENCES `llx_git_countries` (`rowid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Relación usuario - país';

-- ------------------------------------------------------------
-- Tabla: llx_git_fetch_metadata (Metadatos de las búsquedas)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `llx_git_fetch_metadata`;
CREATE TABLE `llx_git_fetch_metadata` (
  `rowid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `query` VARCHAR(500) NOT NULL COMMENT 'Query original',
  `query_name` VARCHAR(255) DEFAULT NULL COMMENT 'Nombre de la query',
  `fetched_at` DATETIME NOT NULL COMMENT 'Fecha de obtención',
  `total_repos_fetched` INT UNSIGNED DEFAULT 0 COMMENT 'Total repos obtenidos',
  `total_users_found` INT UNSIGNED DEFAULT 0 COMMENT 'Total usuarios encontrados',
  PRIMARY KEY (`rowid`),
  KEY `idx_query` (`query`),
  KEY `idx_fetched_at` (`fetched_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Metadatos de búsquedas';

-- ============================================================
-- Fin del schema
-- ============================================================