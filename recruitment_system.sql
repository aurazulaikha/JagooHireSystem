-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 30, 2025 at 06:45 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `recruitment_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `aptitude_tests`
--

CREATE TABLE `aptitude_tests` (
  `id` int(11) NOT NULL,
  `request_candidate_id` int(11) NOT NULL,
  `test_date` date DEFAULT NULL,
  `must_have_skill` varchar(255) DEFAULT NULL,
  `motivation` enum('green_flag','red_flag') DEFAULT 'green_flag',
  `aptitude_score` decimal(5,2) DEFAULT NULL,
  `continue_next` enum('ya','tidak') DEFAULT 'tidak',
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `aptitude_tests`
--

INSERT INTO `aptitude_tests` (`id`, `request_candidate_id`, `test_date`, `must_have_skill`, `motivation`, `aptitude_score`, `continue_next`, `notes`, `created_at`) VALUES
(1, 1, '2025-10-23', 'Python, SQL', 'green_flag', 85.00, 'ya', 'Candidate is motivated', '2025-10-29 03:47:12'),
(2, 2, '2025-11-20', 'Bootstrap, CSS, Tailwind', 'green_flag', 90.00, 'ya', 'belajar lagi', '2025-10-30 17:06:21'),
(3, 3, '2025-10-21', 'Javascript', 'red_flag', 70.00, 'tidak', 'belajar lagi ya', '2025-10-30 17:10:07');

-- --------------------------------------------------------

--
-- Table structure for table `audit_logs`
--

CREATE TABLE `audit_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `action` text DEFAULT NULL,
  `table_name` varchar(100) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `audit_logs`
--

INSERT INTO `audit_logs` (`id`, `user_id`, `action`, `table_name`, `timestamp`) VALUES
(1, 1, 'tambah kandidat Andi Pratama', 'candidates', '2025-10-29 03:19:56'),
(2, 1, 'update kandidat id=1', 'candidates', '2025-10-29 03:27:13'),
(3, 1, 'tambah request role=Backend Developer', 'requests', '2025-10-29 03:28:18'),
(4, 1, 'update request id=1', 'requests', '2025-10-29 03:28:50'),
(5, 1, 'assign candidate_id=1 to request_id=1', 'request_candidates', '2025-10-29 03:29:35'),
(6, 1, 'create aptitude_test for rc_id=1', 'aptitude_tests', '2025-10-29 03:47:12'),
(7, 2, 'create technical_test for rc_id=1', 'technical_tests', '2025-10-29 03:48:55'),
(8, 3, 'create professional_test for rc_id=1', 'professional_tests', '2025-10-29 03:59:02'),
(9, 1, 'update kandidat id=1', 'candidates', '2025-10-29 04:20:13'),
(10, 1, 'update kandidat id=1', 'candidates', '2025-10-29 04:20:24'),
(11, 1, 'update kandidat id=1', 'candidates', '2025-10-29 04:20:32'),
(12, 1, 'update kandidat id=1', 'candidates', '2025-10-29 04:20:33'),
(13, 1, 'update kandidat id=1', 'candidates', '2025-10-29 04:20:42'),
(14, 1, 'update kandidat id=1', 'candidates', '2025-10-29 04:20:50'),
(15, 1, 'update kandidat id=1', 'candidates', '2025-10-29 04:20:58'),
(16, 1, 'update kandidat id=1', 'candidates', '2025-10-29 04:21:06'),
(17, 1, 'update kandidat id=1', 'candidates', '2025-10-29 04:21:14'),
(18, 1, 'tambah request role=tes', 'requests', '2025-10-29 06:59:41'),
(19, 1, 'hapus request id=2', 'requests', '2025-10-29 07:00:06'),
(20, 1, 'update request id=1', 'requests', '2025-10-29 07:04:51'),
(21, 1, 'tambah request role=Frontend Developer', 'requests', '2025-10-30 16:52:50'),
(22, 1, 'tambah kandidat Caca', 'candidates', '2025-10-30 17:04:19'),
(23, 1, 'update kandidat id=2', 'candidates', '2025-10-30 17:07:59'),
(24, 1, 'tambah kandidat Alif', 'candidates', '2025-10-30 17:08:52'),
(25, 1, 'update request id=3', 'requests', '2025-10-30 17:14:01'),
(26, 1, 'update request id=3', 'requests', '2025-10-30 17:14:23'),
(27, 1, 'update kandidat id=3', 'candidates', '2025-10-30 17:16:19'),
(28, 1, 'tambah kandidat tes', 'candidates', '2025-10-30 17:17:02'),
(29, 1, 'hapus kandidat id=4', 'candidates', '2025-10-30 17:17:09'),
(30, 1, 'tambah request role=bdf', 'requests', '2025-10-30 17:17:40'),
(31, 1, 'update request id=1', 'requests', '2025-10-30 17:18:02'),
(32, 1, 'hapus request id=4', 'requests', '2025-10-30 17:18:10');

-- --------------------------------------------------------

--
-- Table structure for table `candidates`
--

CREATE TABLE `candidates` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL,
  `email` varchar(150) DEFAULT NULL,
  `no_telp` varchar(20) DEFAULT NULL,
  `domisili` varchar(255) NOT NULL,
  `applied_role` varchar(100) DEFAULT NULL,
  `status` enum('FCFS','Unconfirmed','Not Available','Onboarding','ASAP','Few Weeks','1 Month Notice','2 Month Notice') DEFAULT 'Unconfirmed',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `candidates`
--

INSERT INTO `candidates` (`id`, `name`, `email`, `no_telp`, `domisili`, `applied_role`, `status`, `created_at`) VALUES
(1, 'Andi P.', 'andi_p@gmail.com', '08133456789', 'Padang', 'Backend Developer', 'Onboarding', '2025-10-29 03:19:56'),
(2, 'Caca', 'caca@gmail.com', '0812347272', 'Bandung', 'Frontend Developer', 'ASAP', '2025-10-30 17:04:19'),
(3, 'Alif', 'alif@gmail.com', '08776754565', 'Bogor', 'Backend Developer', 'ASAP', '2025-10-30 17:08:52');

-- --------------------------------------------------------

--
-- Table structure for table `competency_levels`
--

CREATE TABLE `competency_levels` (
  `id` int(11) NOT NULL,
  `level_name` enum('incompetent','developing','advance') NOT NULL,
  `numeric_value` int(2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `feedbacks`
--

CREATE TABLE `feedbacks` (
  `id` int(11) NOT NULL,
  `candidate_id` int(11) NOT NULL,
  `given_by` int(11) NOT NULL,
  `rating` decimal(3,2) DEFAULT NULL,
  `comment` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `professional_tests`
--

CREATE TABLE `professional_tests` (
  `id` int(11) NOT NULL,
  `request_candidate_id` int(11) NOT NULL,
  `test_date` date DEFAULT NULL,
  `aptitude_score` decimal(5,2) DEFAULT NULL,
  `programming_fundamentals` decimal(5,2) DEFAULT NULL,
  `software_engineering` enum('incompetent','developing','advance') DEFAULT NULL,
  `portfolio_eval` enum('incompetent','developing','advance') DEFAULT NULL,
  `communication` enum('incompetent','developing','advance') DEFAULT NULL,
  `adaptability` enum('incompetent','developing','advance') DEFAULT NULL,
  `discipline` enum('incompetent','developing','advance') DEFAULT NULL,
  `commitment` enum('incompetent','developing','advance') DEFAULT NULL,
  `final_result` enum('lulus','tidak_lulus') DEFAULT 'tidak_lulus',
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `professional_tests`
--

INSERT INTO `professional_tests` (`id`, `request_candidate_id`, `test_date`, `aptitude_score`, `programming_fundamentals`, `software_engineering`, `portfolio_eval`, `communication`, `adaptability`, `discipline`, `commitment`, `final_result`, `notes`, `created_at`) VALUES
(1, 1, '2025-10-29', 85.00, 80.00, 'developing', 'advance', 'advance', 'advance', 'advance', 'advance', 'lulus', 'Candidate performed well', '2025-10-29 03:59:02');

-- --------------------------------------------------------

--
-- Table structure for table `requests`
--

CREATE TABLE `requests` (
  `id` int(11) NOT NULL,
  `role` varchar(100) NOT NULL,
  `company_name` varchar(150) NOT NULL,
  `duration` varchar(50) DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  `max_salary` decimal(15,2) DEFAULT NULL,
  `location` varchar(150) DEFAULT NULL,
  `work_method` enum('onsite','remote','hybrid') DEFAULT 'onsite',
  `work_schedule` varchar(100) DEFAULT NULL,
  `est_start_date` date DEFAULT NULL,
  `level` varchar(50) DEFAULT NULL,
  `job_description` text DEFAULT NULL,
  `current_stage` enum('New Request','Aptitude','Technical','Professional','Trial','Onboarding','Finish') DEFAULT 'New Request',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `requests`
--

INSERT INTO `requests` (`id`, `role`, `company_name`, `duration`, `quantity`, `max_salary`, `location`, `work_method`, `work_schedule`, `est_start_date`, `level`, `job_description`, `current_stage`, `created_at`) VALUES
(1, 'Backend Developer', 'Sagara', '3 months', 2, 10000000.00, 'Jakarta', 'onsite', 'Fulltime', '2025-11-01', 'Junior', 'Frontend Developer', 'Onboarding', '2025-10-29 03:28:18'),
(3, 'Frontend Developer', 'Neuron', '3 Month', 3, 10000000.00, 'Bandung', 'remote', 'Fulltime', '2025-12-30', 'Middle', 'tes', 'New Request', '2025-10-30 16:52:50');

-- --------------------------------------------------------

--
-- Table structure for table `request_candidates`
--

CREATE TABLE `request_candidates` (
  `id` int(11) NOT NULL,
  `request_id` int(11) NOT NULL,
  `candidate_id` int(11) NOT NULL,
  `assigned_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `request_candidates`
--

INSERT INTO `request_candidates` (`id`, `request_id`, `candidate_id`, `assigned_at`) VALUES
(1, 1, 1, '2025-10-29 03:29:35'),
(2, 3, 2, '2025-10-30 17:04:58'),
(3, 1, 3, '2025-10-30 17:09:13');

-- --------------------------------------------------------

--
-- Table structure for table `technical_tests`
--

CREATE TABLE `technical_tests` (
  `id` int(11) NOT NULL,
  `request_candidate_id` int(11) NOT NULL,
  `test_date` date DEFAULT NULL,
  `aptitude_score` decimal(5,2) DEFAULT NULL,
  `domain12_score` decimal(5,2) DEFAULT NULL,
  `stack_eval` enum('incompetent','developing','advance') DEFAULT 'developing',
  `portfolio_eval` enum('incompetent','developing','advance') DEFAULT NULL,
  `continue_next` enum('ya','tidak') DEFAULT 'tidak',
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `technical_tests`
--

INSERT INTO `technical_tests` (`id`, `request_candidate_id`, `test_date`, `aptitude_score`, `domain12_score`, `stack_eval`, `portfolio_eval`, `continue_next`, `notes`, `created_at`) VALUES
(1, 1, '2025-10-27', 85.00, 90.00, 'advance', 'advance', 'ya', 'Strong candidate', '2025-10-29 03:48:55'),
(2, 2, '2025-12-01', 88.00, 90.00, 'advance', 'developing', 'ya', 'mantap', '2025-10-30 17:10:59');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('HCM','AM','Director') NOT NULL,
  `email` varchar(150) DEFAULT NULL,
  `telp` varchar(20) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `role`, `email`, `telp`, `created_at`) VALUES
(1, 'HCM', '$2y$10$H1btdVycvxO0Cauz78/mou8z.QvhARAseoTNspAYvAkp2MSUEQr2u', 'HCM', 'hcm@gmail.com', '081234567890', '2025-10-29 03:08:22'),
(2, 'AM', '$2y$10$wNY5zJOCWeTPRzTuRGdjoOWtf4Hczw0apEYvML6FnXAVK9Z73DyXy', 'AM', 'am@gmail.com', '081123456789', '2025-10-29 03:08:22'),
(3, 'Director', '$2y$10$XMK1/NImx2WN/4BOTkMKK.E9aS/6/mGeggFUA3ihaXK.K00xqNaO2', 'Director', 'director@gmail.com', '082234567890', '2025-10-29 03:08:22');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `aptitude_tests`
--
ALTER TABLE `aptitude_tests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_aptitude_request_candidate` (`request_candidate_id`);

--
-- Indexes for table `audit_logs`
--
ALTER TABLE `audit_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_audit_user` (`user_id`);

--
-- Indexes for table `candidates`
--
ALTER TABLE `candidates`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_candidate` (`email`,`no_telp`);

--
-- Indexes for table `competency_levels`
--
ALTER TABLE `competency_levels`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `feedbacks`
--
ALTER TABLE `feedbacks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_feedback_candidate` (`candidate_id`),
  ADD KEY `fk_feedback_user` (`given_by`);

--
-- Indexes for table `professional_tests`
--
ALTER TABLE `professional_tests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_professional_request_candidate` (`request_candidate_id`);

--
-- Indexes for table `requests`
--
ALTER TABLE `requests`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `request_candidates`
--
ALTER TABLE `request_candidates`
  ADD PRIMARY KEY (`id`),
  ADD KEY `request_id` (`request_id`),
  ADD KEY `candidate_id` (`candidate_id`);

--
-- Indexes for table `technical_tests`
--
ALTER TABLE `technical_tests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_technical_request_candidate` (`request_candidate_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `aptitude_tests`
--
ALTER TABLE `aptitude_tests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `audit_logs`
--
ALTER TABLE `audit_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `candidates`
--
ALTER TABLE `candidates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `competency_levels`
--
ALTER TABLE `competency_levels`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `feedbacks`
--
ALTER TABLE `feedbacks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `professional_tests`
--
ALTER TABLE `professional_tests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `requests`
--
ALTER TABLE `requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `request_candidates`
--
ALTER TABLE `request_candidates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `technical_tests`
--
ALTER TABLE `technical_tests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `aptitude_tests`
--
ALTER TABLE `aptitude_tests`
  ADD CONSTRAINT `fk_aptitude_request_candidate` FOREIGN KEY (`request_candidate_id`) REFERENCES `request_candidates` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `audit_logs`
--
ALTER TABLE `audit_logs`
  ADD CONSTRAINT `fk_audit_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `feedbacks`
--
ALTER TABLE `feedbacks`
  ADD CONSTRAINT `fk_feedback_candidate` FOREIGN KEY (`candidate_id`) REFERENCES `candidates` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_feedback_user` FOREIGN KEY (`given_by`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `professional_tests`
--
ALTER TABLE `professional_tests`
  ADD CONSTRAINT `fk_professional_request_candidate` FOREIGN KEY (`request_candidate_id`) REFERENCES `request_candidates` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `request_candidates`
--
ALTER TABLE `request_candidates`
  ADD CONSTRAINT `fk_candidate` FOREIGN KEY (`candidate_id`) REFERENCES `candidates` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_request` FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `technical_tests`
--
ALTER TABLE `technical_tests`
  ADD CONSTRAINT `fk_technical_request_candidate` FOREIGN KEY (`request_candidate_id`) REFERENCES `request_candidates` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
